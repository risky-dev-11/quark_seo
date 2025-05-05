import datetime
from bs4 import BeautifulSoup
from models import AnalyzedWebsite
from fetcher import format_url, fetch_website_content
from card_builders import build_all_cards, build_serp_preview, build_overall_results
import time
from text_snippet_functions import (
    get_content_length_comment, get_website_response_time_text, get_file_size_text, get_media_count_text, get_link_count_text
)

def analyze_website(user_uuid, url, db, is_premium_user, send_progress=None):
    start_time = time.time()
    
    def progress(step, message):
        if send_progress:
            yield f"data: {step}|{message}\n\n"
        else:
            pass  # do nothing if no callback is provided

    formatted_url = format_url(url)

    if send_progress:
        yield from progress(5, "Fetching website content...")
    response, page_source, screenshot = fetch_website_content(formatted_url)

    if send_progress:
        yield from progress(20, "Parsing website content...")
    soup = BeautifulSoup(page_source, 'html.parser')

    website_response_time = response.elapsed.total_seconds()
    file_size = len(response.content)
    word_count = len(soup.get_text().split())
    media_count = len(soup.find_all('img')) + len(soup.find_all('video')) + len(soup.find_all('audio'))
    internal_link_count = len([link for link in soup.find_all('a', href=True) if not link['href'].startswith('http') or (link['href'].startswith('http') and formatted_url in link['href'])])
    external_link_count = len([link for link in soup.find_all('a', href=True) if link['href'].startswith('http') and formatted_url not in link['href']])

    results = {}
    results['general_results'] = {
        'isCard': False,
        'website_response_time': website_response_time,
        'website_response_time_text': get_website_response_time_text(website_response_time),
        'file_size': f"{file_size / 1000:.1f} kB",
        'file_size_text': get_file_size_text(file_size),
        'word_count': word_count,
        'word_count_text': get_content_length_comment(word_count),
        'media_count': media_count,
        'media_count_text': get_media_count_text(media_count),
        'link_count': f"{internal_link_count} Intern / {external_link_count} Extern",
        'link_count_text': get_link_count_text(internal_link_count, external_link_count),
    }

    if send_progress:
        yield from build_all_cards(results, soup, formatted_url, response, is_premium_user)
    else:
        # Fallback: collect all yields to exhaust the generator
        for _ in build_all_cards(results, soup, formatted_url, response, is_premium_user):
            pass
    if send_progress:
        yield from progress(90, "Building SERP preview and calculating overall results")
    results['serp_preview'] = build_serp_preview(soup, formatted_url, response)
    results['overall_results'] = build_overall_results(results)

    if send_progress:
            yield from progress(100, "Analysis complete. Saving results to database.")

    computation_time = f"{time.time() - start_time:.2f} Sekunden"

    basic_url = formatted_url.split("://")[1].lstrip("www.").rstrip("/")
    analysis_results = AnalyzedWebsite(
        user_uuid=user_uuid,
        url=basic_url,
        results=results,
        computation_time=computation_time,
        time=datetime.datetime.now(),
        screenshot=screenshot
    )
    db.session.add(analysis_results)
    db.session.commit()
    
    if send_progress:
        yield f"data: DONE|{analysis_results.uuid}\n\n"
    else:
        return analysis_results.uuid