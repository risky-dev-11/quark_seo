from bs4 import BeautifulSoup
from models import AnalyzedWebsite, calculate_improvement_count, calculate_overall_points
from fetcher import format_url, fetch_website_content
from card_builders import build_all_cards, build_serp_preview, build_overall_results
from text_snippet_functions import (
    get_content_length_comment, get_website_response_time_text, get_file_size_text, get_media_count_text, get_link_count_text
)

def analyze_website(user_uuid, url, db):
    # URL korrekt formatieren
    formatted_url = format_url(url)
    
    # Website-Inhalt abrufen (HTTP-Antwort, HTML-Quelltext, Screenshot)
    response, page_source, screenshot = fetch_website_content(formatted_url)
    
    # HTML parsen
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Allgemeine Kennzahlen berechnen
    website_response_time = response.elapsed.total_seconds()
    file_size = len(response.content)
    word_count = len(soup.get_text().split())
    media_count = len(soup.find_all('img')) + len(soup.find_all('video')) + len(soup.find_all('audio'))
    internal_link_count = len([link for link in soup.find_all('a', href=True) if formatted_url in link['href']])
    external_link_count = len([link for link in soup.find_all('a', href=True) if formatted_url not in link['href']])
    
    # General Results mit den entsprechenden Texten füllen
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
    
    # Weitere Karten (Metadaten, Seitenqualität, Seitenstruktur, Links, Server, KI-Analyse) erstellen
    build_all_cards(results, soup, formatted_url, response)
    
    # SERP-Vorschau und Gesamtbewertung erstellen
    results['serp_preview'] = build_serp_preview(soup, formatted_url, response)
    results['overall_results'] = build_overall_results(results)
    
    # Analyseergebnis in der Datenbank speichern
    analysis_results = AnalyzedWebsite(user_uuid=user_uuid, url=formatted_url, results=results)
    db.session.add(analysis_results)
    db.session.commit()
    
    return analysis_results.uuid
