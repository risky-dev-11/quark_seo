# ############################################################################ #
#                                  IMPORTS                                     #
# ############################################################################ #

# Standard Library Imports
import asyncio
import json
import socket
import os
import re
from urllib.parse import urlparse, urljoin

# Third-Party Imports
import requests
from bs4 import BeautifulSoup, Tag # Added Tag for type hinting
from langdetect import detect_langs, DetectorFactory, LangDetectException
import dotenv

# Local Application/Library Specific Imports
# NOTE: text_snippet_functions are no longer used directly.
#       English text is generated inline in this file.
from backend.models.models import Card, Category, calculate_improvement_count, calculate_overall_points
from backend.analysis.ai_analyzer import ai_analyzer # Assuming ai_analyzer is an async function

# ############################################################################ #
#                              ENVIRONMENT SETUP                               #
# ############################################################################ #

dotenv.load_dotenv()
GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")

# ############################################################################ #
#                                 CONSTANTS                                    #
# ############################################################################ #

# --- Performance Thresholds ---
LCP_THRESHOLD_SECONDS = 2.5
FCP_THRESHOLD_SECONDS = 1.8
TBT_THRESHOLD_MS = 200.0
CLS_THRESHOLD = 0.1
SPEED_INDEX_THRESHOLD_SECONDS = 4.3
TTFB_THRESHOLD_SECONDS = 0.8 # Common threshold for Time To First Byte

# Performance Budget (Example values, adjust as needed)
MAX_PAGE_SIZE_KB = 1500 # Max total page size in KB
MAX_REQUESTS = 75       # Max number of requests

# --- Metadata Thresholds ---
TITLE_MIN_LENGTH = 50
TITLE_MAX_LENGTH = 60
AVG_CHAR_WIDTH_PX = 6.19
DESC_MIN_LENGTH_PX = 800
DESC_MAX_LENGTH_PX = 960

# --- Content & Linking Thresholds ---
MIN_CONTENT_WORD_COUNT = 300
MAX_LINK_TEXT_LENGTH = 30 # Threshold for link text length

# --- AI Analysis Thresholds ---
AI_RATING_THRESHOLD = 80 # Minimum rating (out of 100) to be considered "good"

# --- SERP Preview Approx Pixel Width ---
SERP_DESC_AVG_CHAR_WIDTH_PX = AVG_CHAR_WIDTH_PX
SERP_DESC_MIN_LENGTH_PX = 500 # Optimal min length for SERP description
SERP_DESC_MAX_LENGTH_PX = 960 # Optimal max length for SERP description
SERP_DESC_ACCEPTABLE_MIN_PX = 200 # Acceptable min length range
SERP_DESC_ACCEPTABLE_MAX_PX = 1260 # Acceptable max length range (truncated but has content)
SERP_TITLE_MIN_LENGTH = 50
SERP_TITLE_MAX_LENGTH = 60
SERP_TITLE_ACCEPTABLE_MIN = 25
SERP_TITLE_ACCEPTABLE_MAX = 85 # Truncated but likely has keywords

# --- Technical & Accessibility ---
ARIA_LANDMARKS = ['banner', 'navigation', 'main', 'complementary', 'contentinfo', 'form', 'search', 'region']
SECURITY_HEADERS = [
    'Strict-Transport-Security', 'Content-Security-Policy', 'X-Frame-Options',
    'X-Content-Type-Options', 'Referrer-Policy', 'Permissions-Policy'
]
FORM_ELEMENTS_NEEDING_LABEL = ['input', 'textarea', 'select']
# Headings should not skip levels (e.g., h1 -> h3)
HEADING_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

# --- API Endpoints ---
GOOGLE_PAGESPEED_API_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
IP_API_URL_TEMPLATE = "http://ip-api.com/json/{ip}"

# ############################################################################ #
#                             MAIN ORCHESTRATOR                              #
# ############################################################################ #

def build_all_cards(results: dict, soup: BeautifulSoup, url: str, response: requests.Response, is_premium_user: bool):
    """
    Builds and adds all the SEO analysis card sections to the results dictionary
    using the revised structure. Includes added checks from Lighthouse audits.

    Args:
        results (dict): The dictionary where card results will be stored.
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page.
        response (requests.Response): The response object from the initial request.
        is_premium_user (bool): Flag indicating if the user has premium access.
    """
    pagespeed_data = None
    lighthouse_metrics = None
    stack_packs = None

    yield "data: 25|Computing Lighthouse metrics (approx. 30sec)...\n\n"

    # Fetch PageSpeed data once if premium (needed for Performance, Technical, Accessibility)
    if is_premium_user:
        try:
            pagespeed_data = fetch_pagespeed_data(url)
            if pagespeed_data:
                lighthouse_metrics = pagespeed_data.get("lighthouseResult", {}).get("audits", {})
                stack_packs = pagespeed_data.get("lighthouseResult", {}).get("stackPacks", [])
        except Exception as e:
            raise RuntimeError(f"Error fetching PageSpeed data: {e}")
            
    yield "data: 40|Analyzing Content Quality and Social Tags...\n\n"
    build_meta_social_card(soup, url).add_to_results(results, index=1)
    build_content_quality_card(soup).add_to_results(results, index=2)

    yield "data: 45|Analyzing Structured Data, Links, and Accessibility...\n\n"
    build_structured_data_card(soup, url).add_to_results(results, index=3)
    build_linking_card(soup, url).add_to_results(results, index=4)
    build_mobile_accessibility_card(soup, lighthouse_metrics).add_to_results(results, index=5) # Pass metrics

    yield "data: 55|Analyzing Core Web Vitals...\n\n"
    # --- Performance Card (Premium) ---
    if is_premium_user:
        performance_card = build_performance_card(url, soup, response, pagespeed_data, lighthouse_metrics) # Pass metrics
        performance_card.add_to_results(results, index=6)
    else:
        build_not_available_card(
            title='Performance',
            category_title='Performance Data Not Available',
            message='Performance metrics, including Core Web Vitals and PageSpeed insights, are only available for premium users.'
        ).add_to_results(results, manual_points=100, index=6)

    yield "data: 70|Analyzing Technical Configuration...\n\n"
    # --- Technical Configuration Card ---
    build_technical_config_card(url, response, lighthouse_metrics, stack_packs).add_to_results(results, index=7) # Pass metrics & stacks

    yield "data: 75|Conducting AI Analysis...\n\n"
    # --- AI Analysis Card (Premium) ---
    if is_premium_user:
        build_ai_card(soup).add_to_results(results, index=8)
    else:
        build_not_available_card(
            title='AI Analysis',
            category_title='AI Analysis Not Available',
            message='AI Analysis is only available for premium users. Please upgrade your subscription.'
        ).add_to_results(results, manual_points=100, index=8)

# ############################################################################ #
#                        PAGESPEED DATA FETCHER                             #
# ############################################################################ #

def fetch_pagespeed_data(url: str) -> dict | None:
    """Fetches data from Google PageSpeed Insights API."""
    if not GOOGLE_PAGESPEED_API_KEY:
        print("Warning: GOOGLE_PAGESPEED_API_KEY not set. Cannot fetch PageSpeed data.")
        return None

    params = {
        "url": url,
        "key": GOOGLE_PAGESPEED_API_KEY,
        "strategy": "desktop", # Consider running mobile as well if needed
        "category": ["performance", "accessibility", "best-practices", "seo"] # Fetch relevant categories
    }
    try:
        response = requests.get(GOOGLE_PAGESPEED_API_URL, params=params, timeout=45)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PageSpeed data for {url}: {e}")
        raise ConnectionError(f"PageSpeed API request failed: {e}") from e
    except Exception as e:
        print(f"Unexpected error processing PageSpeed data: {e}")
        raise RuntimeError(f"PageSpeed processing failed: {e}") from e

# ############################################################################ #
#                        AUDIT HELPER FUNCTIONS                              #
# ############################################################################ #

def get_audit_details(metrics: dict | None, audit_id: str) -> dict:
    """Safely retrieves an audit dictionary from Lighthouse metrics."""
    if not metrics:
        return {}
    return metrics.get(audit_id, {})

def format_bytes(size_bytes: int | float | None) -> str:
    """Formats bytes into KiB."""
    if size_bytes is None or size_bytes == float('inf') or size_bytes < 0:
        return "N/A"
    return f"{size_bytes / 1024:.1f} KiB"

def format_ms(time_ms: int | float | None) -> str:
    """Formats milliseconds."""
    if time_ms is None or time_ms == float('inf') or time_ms < 0:
        return "N/A"
    return f"{time_ms:.0f} ms"

def get_audit_score(audit: dict) -> float | None:
    """Gets the score (0-1) from an audit, returns None if not applicable."""
    mode = audit.get('scoreDisplayMode')
    if mode in ['numeric', 'binary']:
        return audit.get('score') # Should be 0-1
    return None # Informative, manual, notApplicable, error audits don't have a comparable score

# ############################################################################ #
#                            CARD BUILDER FUNCTIONS                            #
# ############################################################################ #

# --- Meta & Social Card (No changes needed for new integrations) ---
def build_meta_social_card(soup: BeautifulSoup, url: str) -> Card:
    # (This function remains the same as in the previous version)
    card = Card('Meta & Social Tags')
    parsed_url = urlparse(url)

    # --- Title ---
    title_category = Category('Title Tag')
    title_tag = soup.title
    title_text = title_tag.string.strip() if title_tag and title_tag.string else ""
    is_title_missing = not bool(title_text)

    title_category.add_content(not is_title_missing, "Title tag is present." if not is_title_missing else "Title tag is missing.")
    if is_title_missing:
        title_category.add_content("improvement", "Add a descriptive and relevant <title> tag to your page.")
    else:
        title_length = len(title_text)
        is_title_length_correct = TITLE_MIN_LENGTH <= title_length <= TITLE_MAX_LENGTH
        has_domain_in_title = parsed_url.netloc in title_text
        title_words = title_text.lower().split()
        word_counts = {word: title_words.count(word) for word in set(title_words)}
        repeated_words = [word for word, count in word_counts.items() if count > 1]
        has_title_word_repetitions = len(repeated_words) > 0

        title_category.add_content('', f'Title: "{title_text}"')
        title_category.add_content(is_title_length_correct,
            f"Title length is {title_length} characters (optimal: {TITLE_MIN_LENGTH}-{TITLE_MAX_LENGTH})." if is_title_length_correct
            else f"Title length is {title_length} characters. Recommended length is {TITLE_MIN_LENGTH}-{TITLE_MAX_LENGTH} characters.")
        if not is_title_length_correct:
            title_category.add_content("improvement", f"Adjust title length to be between {TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters for optimal display in search results.")

        title_category.add_content(not has_title_word_repetitions,
            "No significant word repetitions found in the title." if not has_title_word_repetitions
            else f"Word repetitions found in title: {', '.join(repeated_words)}.")
        if has_title_word_repetitions:
            title_category.add_content("improvement", f"Avoid repeating words like '{', '.join(repeated_words)}' in the title. Keep it concise and informative.")
    card.add_category(title_category)

    # --- Description ---
    description_category = Category('Meta Description')
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description_content = description_tag.get('content', '').strip() if description_tag else ""
    is_description_missing = not bool(description_content)
    description_category.add_content(not is_description_missing, "Meta description is present." if not is_description_missing else "Meta description is missing.")
    if not is_description_missing:
        desc_length_chars = len(description_content)
        desc_length_px = round(desc_length_chars * AVG_CHAR_WIDTH_PX)
        is_desc_length_optimal = DESC_MIN_LENGTH_PX <= desc_length_px <= DESC_MAX_LENGTH_PX
        description_category.add_content('', f'Description: "{description_content}"')
        description_category.add_content(is_desc_length_optimal,
            f"Description length is approx. {desc_length_px}px ({desc_length_chars} chars). Recommended pixel range is {DESC_MIN_LENGTH_PX}-{DESC_MAX_LENGTH_PX}px." if is_desc_length_optimal
            else f"Description length is approx. {desc_length_px}px ({desc_length_chars} chars). This is outside the recommended range ({DESC_MIN_LENGTH_PX}-{DESC_MAX_LENGTH_PX}px).")
        description_category.add_chart_content(
            chart_type='range', threshold1=DESC_MIN_LENGTH_PX, threshold2=DESC_MAX_LENGTH_PX,
            threshold_unit="px", value=desc_length_px,
        )
        if not is_desc_length_optimal:
             description_category.add_content("improvement", f"Adjust the description length. Aim for {DESC_MIN_LENGTH_PX}-{DESC_MAX_LENGTH_PX} pixels to ensure it's fully visible in search results.")
    else:
         description_category.add_content("improvement", "Add a unique and compelling meta description. It influences click-through rates from search results.")
    card.add_category(description_category)

    # --- Canonical URL ---
    canonical_category = Category('Canonical Tag')
    canonical_link = soup.find('link', attrs={'rel': 'canonical'})
    has_canonical = canonical_link is not None
    canonical_href = canonical_link['href'].strip() if has_canonical else 'Not found'
    canonical_category.add_content(has_canonical, f"Canonical link tag found: {canonical_href}" if has_canonical else "Canonical link tag is missing.")
    if not has_canonical:
         canonical_category.add_content("improvement", f"Add a canonical link tag (`<link rel=\"canonical\" href=\"{url}\">`) to prevent duplicate content issues.")
    elif has_canonical and canonical_href != url:
        norm_url = url.rstrip('/')
        norm_canon = canonical_href.rstrip('/')
        is_reasonable_diff = (
            norm_canon == norm_url or
            norm_canon == norm_url.replace("http://", "https://") or
            norm_canon == norm_url.replace("https://", "http://") or
            norm_canon.replace("://www.","://") == norm_url.replace("://www.","://")
         )
        if not is_reasonable_diff:
            canonical_category.add_content(False, f"Warning: Canonical tag ({canonical_href}) points to a significantly different URL than accessed ({url}). Ensure this is intentional.")
            canonical_category.add_content("improvement", "Verify the canonical tag. It should typically point to the preferred version of the current page URL.")
        else:
             canonical_category.add_content(True, f"Canonical tag points to a similar URL ({canonical_href}), likely handling variations correctly.")
    card.add_category(canonical_category)

    # --- Language & Location ---
    language_category = Category('Language & Location')
    html_lang = soup.html.get('lang', '').strip() if soup.html else ''
    declared_lang = html_lang or 'Not declared'
    language_category.add_content(declared_lang != 'Not declared', f'Declared HTML lang attribute: {declared_lang}')
    detected_lang = 'Error'
    page_text = soup.get_text()
    try:
        DetectorFactory.seed = 0
        if page_text.strip():
            detected_langs = detect_langs(page_text)
            if detected_langs:
                detected_lang = detected_langs[0].lang
                language_category.add_content(True, f'Detected language in text: {detected_lang} (Probability: {detected_langs[0].prob:.1%})')
            else: language_category.add_content(False, 'Could not detect language from page text.')
        else: language_category.add_content(False, 'No text content found for language detection.')
    except LangDetectException: language_category.add_content(False, 'Error during automatic language detection.')
    except Exception as e: language_category.add_content(False, f'Unexpected error during language detection: {e}')
    if declared_lang != 'Not declared' and detected_lang != 'Error':
        lang_match = detected_lang.split('-')[0].lower() == declared_lang.split('-')[0].lower()
        language_category.add_content(lang_match, "Declared and detected languages match." if lang_match else f"Declared language '{declared_lang}' might mismatch detected language '{detected_lang}'.")
        if not lang_match: language_category.add_content("improvement", "Ensure the `lang` attribute in `<html>` correctly reflects the main language of the page content.")
    elif declared_lang == 'Not declared': language_category.add_content("improvement", "Declare the page language using the `lang` attribute on the `<html>` tag (e.g., `<html lang=\"en\">`).")
    server_location = 'Unknown'
    try:
        domain = parsed_url.netloc.split(':')[0]
        ip = socket.gethostbyname(domain)
        ip_api_response = requests.get(IP_API_URL_TEMPLATE.format(ip=ip), timeout=5)
        ip_api_response.raise_for_status()
        location_data = ip_api_response.json()
        country = location_data.get('country', 'Unknown')
        city = location_data.get('city', '')
        server_location = f"{city}, {country}" if city and country != 'Unknown' else country
    except socket.gaierror: server_location = 'Domain not resolvable'
    except requests.exceptions.RequestException: server_location = 'Location API unreachable'
    except Exception: server_location = 'Error during location lookup'
    finally: language_category.add_content(server_location not in ['Unknown', 'Error during location lookup', 'Domain not resolvable', 'Location API unreachable'], f'Server Location (estimated): {server_location}')
    card.add_category(language_category)

    # --- Essential Meta Tags (Charset only now) ---
    meta_tags_category = Category('Essential Meta Tags')
    charset_meta = soup.find('meta', attrs={'charset': True})
    charset_http_equiv = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'content-type'})
    charset_content = charset_http_equiv.get('content') if charset_http_equiv else ''
    has_charset = charset_meta is not None or 'charset=' in charset_content.lower()
    charset_value = charset_meta['charset'] if charset_meta else (charset_content.split('charset=')[-1].strip() if 'charset=' in charset_content.lower() else 'Not found')
    meta_tags_category.add_content(has_charset, f"Character set declared: {charset_value}" if has_charset else "Character set meta tag missing.")
    if not has_charset: meta_tags_category.add_content("improvement", "Add a character set meta tag (e.g., `<meta charset=\"UTF-8\">`) to ensure correct text rendering.")
    card.add_category(meta_tags_category)

    # --- Favicon ---
    favicon_category = Category('Favicon')
    favicon_rels = ['icon', 'shortcut icon', 'apple-touch-icon', 'mask-icon']
    has_favicon = soup.find('link', attrs={'rel': lambda r: r and r.lower() in favicon_rels}) is not None
    favicon_category.add_content(has_favicon, "Favicon link tag found." if has_favicon else "No favicon link tag found.")
    if not has_favicon: favicon_category.add_content("improvement", "Add a favicon link tag in the `<head>`. It improves brand recognition in browser tabs and bookmarks.")
    card.add_category(favicon_category)

    # --- Social Media Tags ---
    social_category = Category('Social Media Tags (Open Graph & Twitter)')
    og_tags = {meta.get('property'): meta.get('content') for meta in soup.find_all('meta', property=re.compile(r'^og:'))}
    twitter_tags = {meta.get('name'): meta.get('content') for meta in soup.find_all('meta', attrs={'name': re.compile(r'^twitter:')})}
    has_og_tags = bool(og_tags)
    has_twitter_tags = bool(twitter_tags)
    social_category.add_content(has_og_tags, f"Found {len(og_tags)} Open Graph (og:) tags." if has_og_tags else "No Open Graph (og:) tags found.")
    if not has_og_tags: social_category.add_content("improvement", "Add Open Graph tags (og:title, og:description, og:image, og:url) to control how your page appears when shared on platforms like Facebook.")
    else:
        essential_og = ['og:title', 'og:description', 'og:image', 'og:url']
        missing_og = [tag for tag in essential_og if tag not in og_tags or not og_tags[tag]]
        if missing_og:
            social_category.add_content(False, f"Missing essential Open Graph tags: {', '.join(missing_og)}.")
            social_category.add_content("improvement", "Ensure essential Open Graph tags (og:title, og:description, og:image, og:url) are present and have content.")
    social_category.add_content(has_twitter_tags, f"Found {len(twitter_tags)} Twitter Card (twitter:) tags." if has_twitter_tags else "No Twitter Card (twitter:) tags found.")
    if not has_twitter_tags: social_category.add_content("improvement", "Add Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image) to control appearance when shared on Twitter.")
    else:
        essential_tw = ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']
        missing_tw = [tag for tag in essential_tw if tag not in twitter_tags or not twitter_tags[tag]]
        if missing_tw:
            social_category.add_content(False, f"Missing essential Twitter Card tags: {', '.join(missing_tw)}.")
            social_category.add_content("improvement", "Ensure essential Twitter Card tags (twitter:card, twitter:title, twitter:description, twitter:image) are present and have content.")
    card.add_category(social_category)
    return card

# --- Content Quality Card (No changes needed) ---
def build_content_quality_card(soup: BeautifulSoup) -> Card:
    # (This function remains the same as in the previous version)
    card = Card('Content Quality')
    content_category = Category('Text Content Analysis')
    page_text = soup.get_text()
    words = page_text.split()
    total_word_count = len(words)
    unique_words = set(w.lower() for w in words if len(w) > 1)
    is_length_sufficient = total_word_count >= MIN_CONTENT_WORD_COUNT
    content_category.add_content(is_length_sufficient,
        f"Content length is {total_word_count} words." if is_length_sufficient
        else f"Content length is {total_word_count} words, which is below the recommended minimum of {MIN_CONTENT_WORD_COUNT}.")
    if not is_length_sufficient: content_category.add_content("improvement", f"Consider expanding the content if the topic requires more detail. Aim for at least {MIN_CONTENT_WORD_COUNT} words.")
    else: content_category.add_content("", f"Unique words (basic filter): {len(unique_words)}")
    title_text = soup.title.string.strip().lower() if soup.title and soup.title.string else ""
    if title_text:
        title_keywords = set(word for word in title_text.split() if len(word) > 3)
        content_lower = page_text.lower()
        title_words_in_content = {kw for kw in title_keywords if kw in content_lower}
        relevance_check_passed = len(title_words_in_content) > 0 or not title_keywords
        content_category.add_content(relevance_check_passed, "Keywords from the title appear in the content." if relevance_check_passed else "Keywords from the title were not found in the page content.")
        if not relevance_check_passed: content_category.add_content("improvement", f"Ensure important keywords from your title ('{title_text}') are naturally integrated into the main content.")
    else: content_category.add_content(False, "Title tag missing, cannot perform title/content relevance check.")
    sentences = set()
    duplicates_found = False
    potential_duplicates_list = []
    for tag in soup.find_all(['p', 'li', 'div', 'span', 'article', 'section']):
        tag_text = tag.get_text(separator=' ', strip=True)
        potential_sentences = re.split(r'[.!?]\s+', tag_text)
        for sentence in potential_sentences:
            cleaned_sentence = sentence.strip().lower()
            if len(cleaned_sentence.split()) > 5:
                if cleaned_sentence in sentences:
                    duplicates_found = True
                    potential_duplicates_list.append(cleaned_sentence[:80] + "...")
                sentences.add(cleaned_sentence)
    if len(sentences) < 5 and not duplicates_found : content_category.add_content(True, "Not enough distinct sentences found to reliably check for duplicates.")
    else:
        content_category.add_content(not duplicates_found, "No significant duplicate sentences found." if not duplicates_found else "Potential duplicate sentences found.")
        if duplicates_found: content_category.add_content("improvement", f"Avoid repeating identical sentences or large text blocks. Example duplicate found: '{potential_duplicates_list[0]}'")
    card.add_category(content_category)
    return card

# --- Structured Data Card ---
def build_structured_data_card(soup: BeautifulSoup, url: str) -> Card:
    # (This function remains the same as in the previous version)
    card = Card('Structured Data (Schema.org)')
    structured_data_category = Category('Schema Markup Detection')
    schema_elements = soup.find_all(attrs={"itemscope": True, "itemtype": True})
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    has_microdata = len(schema_elements) > 0
    has_json_ld = len(json_ld_scripts) > 0
    has_rich_snippets = has_microdata or has_json_ld
    detected_types = set()
    if not has_rich_snippets:
        structured_data_category.add_content(False, "No Schema.org structured data (Microdata or JSON-LD) detected.")
        structured_data_category.add_content("improvement", f"Implement structured data using Schema.org (JSON-LD recommended) to help search engines understand your content.")
    else:
        structured_data_category.add_content(True, "Schema.org structured data detected.")
        if has_microdata:
            structured_data_category.add_content("", f"Found {len(schema_elements)} Microdata element(s).")
            for element in schema_elements: detected_types.add(element.get('itemtype', 'Unknown Type').split('/')[-1])
        if has_json_ld:
            structured_data_category.add_content("", f"Found {len(json_ld_scripts)} JSON-LD script tag(s).")
            for script in json_ld_scripts:
                try:
                    ld_json = json.loads(script.string)
                    items = ld_json if isinstance(ld_json, list) else [ld_json]
                    for item in items: detected_types.add(item.get('@type', 'Unknown Type'))
                except json.JSONDecodeError: structured_data_category.add_content(False, "Found JSON-LD script, but failed to parse its content.")
                except Exception: structured_data_category.add_content(False, "Error processing detected JSON-LD content.")
        if detected_types: structured_data_category.add_content(True, f"Detected Schema types: {', '.join(sorted(list(detected_types)))}")
        structured_data_category.add_content("improvement", "Verify your structured data using Google's Rich Results Test or Schema.org validator.")
    card.add_category(structured_data_category)
    return card

# --- Linking Card (No changes needed) ---
def build_linking_card(soup: BeautifulSoup, url: str) -> Card:
    # (This function remains the same as in the previous version)
    card = Card('Linking Analysis')
    links_category = Category('Internal & External Links')
    all_links = soup.find_all('a', href=True)
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc.replace("www.", "")
    internal_links = []
    external_links = []
    links_analyzed_count = 0
    for link in all_links:
        href = link.get('href', '').strip()
        try: absolute_href = urljoin(url, href)
        except ValueError: absolute_href = href
        parsed_href = urlparse(absolute_href)
        if not href or href.startswith(('#', 'mailto:', 'tel:', 'javascript:')): continue
        links_analyzed_count += 1
        link_text = link.get_text(strip=True)
        is_internal = False
        if not parsed_href.scheme and parsed_href.path and not parsed_href.netloc: is_internal = True
        elif parsed_href.netloc.replace("www.", "") == base_domain: is_internal = True
        link_data = {'href': href, 'absolute_href': absolute_href, 'text': link_text}
        if is_internal: internal_links.append(link_data)
        else: external_links.append(link_data)

    internal_link_count = len(internal_links)
    links_category.add_content(internal_link_count > 0, f"Found {internal_link_count} internal links (out of {links_analyzed_count} total analyzed).")
    if internal_link_count > 0:
        internal_empty_text = [l for l in internal_links if not l['text']]
        has_internal_empty = len(internal_empty_text) > 0
        links_category.add_content(not has_internal_empty, "All internal links have text." if not has_internal_empty else f"{len(internal_empty_text)} internal link(s) have empty text.")
        if has_internal_empty: links_category.add_content("improvement", f"Provide descriptive text for all internal links. Empty link example: {internal_empty_text[0]['href']}")
        internal_long_text = [l for l in internal_links if len(l['text']) > MAX_LINK_TEXT_LENGTH]
        has_internal_long = len(internal_long_text) > 0
        links_category.add_content(not has_internal_long, "Internal link texts are concise." if not has_internal_long else f"{len(internal_long_text)} internal link(s) have long text (> {MAX_LINK_TEXT_LENGTH} chars).")
        if has_internal_long: links_category.add_content("improvement", f"Keep internal link texts descriptive but concise. Long text example: '{internal_long_text[0]['text'][:50]}...'")
        internal_texts = [l['text'].lower() for l in internal_links if l['text']]
        if len(internal_texts) > 1:
            has_duplicate_internal_texts = len(internal_texts) != len(set(internal_texts))
            links_category.add_content(not has_duplicate_internal_texts, "Internal link texts appear varied." if not has_duplicate_internal_texts else "Some internal links use identical text.")
            if has_duplicate_internal_texts: links_category.add_content("improvement", "If links point to different destinations, use unique, descriptive text for each link.")

    external_link_count = len(external_links)
    links_category.add_content(True, f"Found {external_link_count} external links.")
    if external_link_count > 0:
        external_empty_text = [l for l in external_links if not l['text']]
        has_external_empty = len(external_empty_text) > 0
        links_category.add_content(not has_external_empty, "All external links have text." if not has_external_empty else f"{len(external_empty_text)} external link(s) have empty text.")
        if has_external_empty: links_category.add_content("improvement", f"Provide descriptive text for external links. Empty link example: {external_empty_text[0]['href']}")
        nofollow_links = 0
        for link_tag in soup.find_all('a', href=True):
             href = link_tag.get('href', '').strip()
             absolute_href = urljoin(url, href)
             parsed_href = urlparse(absolute_href)
             is_external_tag = parsed_href.netloc.replace("www.", "") != base_domain and parsed_href.netloc != ""
             if is_external_tag and 'nofollow' in link_tag.get('rel', []): nofollow_links += 1
        if nofollow_links > 0: links_category.add_content("", f"{nofollow_links} external link(s) have the 'nofollow' attribute.")
    card.add_category(links_category)
    return card

# --- Mobile & Accessibility Card (ADDED Lighthouse Checks) ---
def build_mobile_accessibility_card(soup: BeautifulSoup, lighthouse_metrics: dict | None) -> Card:
    """ Builds the Mobile & Accessibility card with added Lighthouse checks. """
    card = Card('Mobile & Accessibility')

    # --- Viewport ---
    viewport_category = Category('Mobile Viewport')
    # (Viewport logic remains the same)
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    has_viewport = viewport_meta is not None
    viewport_content = viewport_meta['content'] if has_viewport else 'Not found'
    viewport_category.add_content(has_viewport, f"Viewport meta tag present: {viewport_content}" if has_viewport else "Viewport meta tag missing.")
    if not has_viewport: viewport_category.add_content("improvement", "Add a viewport meta tag (`<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">`).")
    elif has_viewport and "user-scalable=no" in viewport_content.replace(" ", ""):
         viewport_category.add_content(False, "Warning: Viewport prevents zooming (`user-scalable=no`), harming accessibility.")
         viewport_category.add_content("improvement", "Remove `user-scalable=no` from the viewport tag.")
    elif has_viewport and "maximum-scale=1" in viewport_content.replace(" ", ""):
         viewport_category.add_content(False, "Warning: Viewport restricts maximum scale, potentially hindering zoom.")
         viewport_category.add_content("improvement", "Avoid setting `maximum-scale=1` in the viewport tag.")
    card.add_category(viewport_category)

    # --- Image Alt Text ---
    image_alt_category = Category('Image Accessibility (Alt Text)')
    # (Alt text logic remains the same)
    all_images = soup.find_all('img')
    images_missing_alt = [img for img in all_images if not img.get('alt', '').strip()]
    count_missing_alts = len(images_missing_alt)
    total_images = len(all_images)
    if total_images == 0: image_alt_category.add_content(True, "No `<img>` tags found.")
    else:
        image_alt_category.add_content(count_missing_alts == 0, f"All {total_images} image(s) have alt text." if count_missing_alts == 0 else f"{count_missing_alts} of {total_images} image(s) are missing alt text.")
        if count_missing_alts > 0:
            examples = [img.get('src', 'N/A')[:70] + ('...' if len(img.get('src','N/A')) > 70 else '') for img in images_missing_alt[:3]]
            image_alt_category.add_content('improvement', f"Add descriptive alt text to meaningful images. Missing examples: {', '.join(examples)}. Use `alt=\"\"` for decorative images.")
    card.add_category(image_alt_category)

    # --- ARIA Landmarks ---
    aria_category = Category('Structural Accessibility (ARIA Landmarks)')
    # (ARIA logic remains the same)
    found_landmarks = set()
    for element in soup.find_all(attrs={'role': True}):
        roles = element['role'].split()
        for role in roles:
            if role in ARIA_LANDMARKS: found_landmarks.add(role)
    tag_map = {'navigation': 'nav', 'main': 'main', 'complementary': 'aside', 'contentinfo': 'footer', 'banner': 'header'}
    for tag_name in ARIA_LANDMARKS:
        html5_tag = tag_map.get(tag_name)
        if html5_tag and soup.find(html5_tag): found_landmarks.add(tag_name)
        if tag_name == 'form' and soup.find('form'): found_landmarks.add(tag_name)
        if tag_name == 'search' and soup.find(attrs={'role': 'search'}): found_landmarks.add(tag_name)
    if not found_landmarks:
        aria_category.add_content(False, "No major ARIA landmarks or HTML5 elements (like <main>, <nav>) found.")
        aria_category.add_content("improvement", "Use HTML5 elements or ARIA landmarks to structure page content for screen reader navigation.")
    else:
        aria_category.add_content(True, f"Found landmarks: {', '.join(sorted(list(found_landmarks)))}.")
        main_elements = soup.find_all('main') + soup.find_all(attrs={'role': 'main'})
        if len(main_elements) == 0:
             aria_category.add_content(False, "No main landmark (<main> or role='main') found.")
             aria_category.add_content("improvement", "Wrap primary content in a <main> element.")
        elif len(main_elements) > 1:
             aria_category.add_content(False, f"Multiple ({len(main_elements)}) main landmarks found. Only one allowed per page.")
             aria_category.add_content("improvement", "Ensure only one <main> element or role='main'.")
    card.add_category(aria_category)

    # --- Form Labels ---
    form_label_category = Category('Form Accessibility (Labels)')
    # (Form label logic remains the same)
    form_elements = soup.find_all(FORM_ELEMENTS_NEEDING_LABEL)
    elements_without_label = 0
    total_form_elements = len(form_elements)
    if total_form_elements == 0: form_label_category.add_content(True, "No form elements found requiring labels.")
    else:
        for elem in form_elements:
            elem_id = elem.get('id')
            has_label_for = False
            if elem_id:
                if soup.find('label', attrs={'for': elem_id}): has_label_for = True
            is_wrapped = False
            parent = elem.parent
            if parent and isinstance(parent, Tag) and parent.name == 'label': is_wrapped = True
            has_aria_label = bool(elem.get('aria-label', '').strip())
            has_aria_labelledby = bool(elem.get('aria-labelledby', '').strip())
            input_type = elem.get('type', '').lower()
            is_self_labeling_type = input_type in ['hidden', 'submit', 'reset', 'button', 'image']
            if not has_label_for and not is_wrapped and not has_aria_label and not has_aria_labelledby and not is_self_labeling_type: elements_without_label += 1
        form_label_category.add_content(elements_without_label == 0, f"All {total_form_elements} form elements appear to have labels." if elements_without_label == 0 else f"{elements_without_label} of {total_form_elements} form elements seem to be missing labels.")
        if elements_without_label > 0: form_label_category.add_content("improvement", "Ensure every form input, select, textarea has a programmatically associated label (<label for>, wrapping label, or aria-label).")
    card.add_category(form_label_category)

    # --- NEW: Additional Accessibility Checks from Lighthouse ---
    lh_a11y_category = Category('Other Accessibility Checks (Lighthouse)')
    if not lighthouse_metrics:
        lh_a11y_category.add_content(False, "Detailed accessibility checks unavailable (Requires PageSpeed Data).")
    else:
        # Heading Order
        heading_audit = get_audit_details(lighthouse_metrics, 'heading-order')
        heading_score = get_audit_score(heading_audit)
        if heading_score is not None:
             lh_a11y_category.add_content(heading_score == 1.0, f"Heading levels ({', '.join(HEADING_TAGS)}) follow a logical order." if heading_score == 1.0 else "Heading levels may skip levels (e.g., H1 to H3), confusing structure.")
             if heading_score < 1.0: lh_a11y_category.add_content("improvement", "Ensure heading ranks increase by only one level at a time (e.g., H1 followed by H2).")

        # Button Name
        button_audit = get_audit_details(lighthouse_metrics, 'button-name')
        button_score = get_audit_score(button_audit)
        if button_score is not None:
            lh_a11y_category.add_content(button_score == 1.0, "All buttons have accessible names." if button_score == 1.0 else "Some buttons are missing accessible names.")
            if button_score < 1.0: lh_a11y_category.add_content("improvement", "Provide descriptive text content or use `aria-label`/`aria-labelledby` for all <button> elements.")

        # Link Name
        link_audit = get_audit_details(lighthouse_metrics, 'link-name')
        link_score = get_audit_score(link_audit)
        if link_score is not None:
             lh_a11y_category.add_content(link_score == 1.0, "All links have discernible text." if link_score == 1.0 else "Some links lack discernible text (empty, or generic like 'click here').")
             if link_score < 1.0: lh_a11y_category.add_content("improvement", "Ensure all links (<a> tags) have clear, descriptive text indicating their purpose or destination.")

        # Image Aspect Ratio (Moved from Performance/Best Practices)
        aspect_audit = get_audit_details(lighthouse_metrics, 'image-aspect-ratio')
        aspect_score = get_audit_score(aspect_audit)
        if aspect_score is not None:
            lh_a11y_category.add_content(aspect_score == 1.0, "Images display with correct aspect ratio." if aspect_score == 1.0 else "Some images may be distorted due to incorrect aspect ratio.")
            if aspect_score < 1.0: lh_a11y_category.add_content("improvement", "Ensure image display dimensions match the image's natural aspect ratio to prevent distortion.")

        # Font Size (Basic Check)
        font_audit = get_audit_details(lighthouse_metrics, 'font-size')
        font_score = get_audit_score(font_audit)
        if font_score is not None:
             lh_a11y_category.add_content(font_score == 1.0, "Font sizes appear generally legible." if font_score == 1.0 else "Some text may be too small to read easily, especially on mobile.")
             if font_score < 1.0:
                 failing_items = font_audit.get('details', {}).get('items', [])
                 fail_count = len(failing_items)
                 lh_a11y_category.add_content("improvement", f"Ensure base font size is adequate and text scales appropriately. ({fail_count} instances found below threshold).")


        # Note on Color Contrast
        contrast_audit = get_audit_details(lighthouse_metrics, 'color-contrast')
        contrast_score = get_audit_score(contrast_audit)
        if contrast_score is not None and contrast_score < 1.0:
            lh_a11y_category.add_content(False, "Potential color contrast issues found between text and background.")
            lh_a11y_category.add_content("improvement", "Verify text has sufficient contrast against its background (WCAG AA standard: 4.5:1 for normal text, 3:1 for large text). Requires manual verification or specialized tools.")

    card.add_category(lh_a11y_category)

    return card

def build_performance_card(url: str,
                           soup: BeautifulSoup,
                           response: requests.Response,
                           pagespeed_data: dict | None,
                           lighthouse_metrics: dict | None) -> Card:
    """ Builds the Performance card with detailed Core Web Vitals sections. """
    card = Card('Performance')

    # --- 1) Core Web Vitals Overview ---
    overview = Category('Core Web Vitals')
    overview.add_content(
        True,
        "Core Web Vitals are a set of user-centric metrics defined by Google to measure loading performance, interactivity, and visual stability."
    )
    card.add_category(overview)

    if not lighthouse_metrics:
        # Fallback if no CWV data
        no_data = Category('Core Web Vitals Data')
        no_data.add_content(False, "Core Web Vitals data unavailable (requires PageSpeed/Lighthouse data).")
        card.add_category(no_data)
    else:
        # helper to fetch audit details
        def audit(name):
            return get_audit_details(lighthouse_metrics, name)

        # --- 2) Largest Contentful Paint ---
        lcp_value_s = audit('largest-contentful-paint').get("numericValue", 0) / 1000
        lcp_cat = Category('Largest Contentful Paint')
        lcp_cat.add_content(
            lcp_value_s <= LCP_THRESHOLD_SECONDS,
            "Measures the time it takes for the largest visible content element to render."
        )
        lcp_cat.add_chart_content(
            chart_type='decline',
            threshold1=LCP_THRESHOLD_SECONDS,
            threshold2=LCP_THRESHOLD_SECONDS * 1.5,
            threshold_unit="s",
            value=round(lcp_value_s, 2)
        )
        card.add_category(lcp_cat)

        # --- 3) First Contentful Paint ---
        fcp_value_s = audit('first-contentful-paint').get("numericValue", 0) / 1000
        fcp_cat = Category('First Contentful Paint')
        fcp_cat.add_content(
            fcp_value_s <= FCP_THRESHOLD_SECONDS,
            "Measures the time from navigation to when the first text or image is painted."
        )
        fcp_cat.add_chart_content(
            chart_type='decline',
            threshold1=FCP_THRESHOLD_SECONDS,
            threshold2=FCP_THRESHOLD_SECONDS * 1.5,
            threshold_unit="s",
            value=round(fcp_value_s, 2)
        )
        card.add_category(fcp_cat)

        # --- 4) Cumulative Layout Shift ---
        cls_value = audit('cumulative-layout-shift').get("numericValue", 0)
        cls_cat = Category('Cumulative Layout Shift')
        cls_cat.add_content(
            cls_value <= CLS_THRESHOLD,
            "Measures the sum of all unexpected layout shifts that occur during the page’s lifespan."
        )
        cls_cat.add_chart_content(
            chart_type='decline',
            threshold1=CLS_THRESHOLD,
            threshold2=CLS_THRESHOLD * 1.5,
            threshold_unit="",
            value=round(cls_value, 3)
        )
        card.add_category(cls_cat)

        # --- 5) Total Blocking Time ---
        tbt_value_ms = audit('total-blocking-time').get("numericValue", 0)
        tbt_cat = Category('Total Blocking Time')
        tbt_cat.add_content(
            tbt_value_ms <= TBT_THRESHOLD_MS,
            "Measures the total amount of time that the main thread was blocked, preventing user input."
        )
        tbt_cat.add_chart_content(
            chart_type='decline',
            threshold1=TBT_THRESHOLD_MS,
            threshold2=TBT_THRESHOLD_MS * 1.5,
            threshold_unit="ms",
            value=round(tbt_value_ms, 0)
        )
        card.add_category(tbt_cat)

        # --- 6) Speed Index ---
        si_value_s = audit('speed-index').get("numericValue", 0) / 1000
        si_cat = Category('Speed Index')
        si_cat.add_content(
            si_value_s <= SPEED_INDEX_THRESHOLD_SECONDS,
            "Measures how quickly the contents of a page are visibly populated."
        )
        si_cat.add_chart_content(
            chart_type='decline',
            threshold1=SPEED_INDEX_THRESHOLD_SECONDS,
            threshold2=SPEED_INDEX_THRESHOLD_SECONDS * 1.5,
            threshold_unit="s",
            value=round(si_value_s, 2)
        )
        card.add_category(si_cat)

        # --- 7a) Time To First Byte (Root Document) ---
        if pagespeed_data and 'rootDocumentTTFB' in pagespeed_data:
            root_tt_ms = pagespeed_data['rootDocumentTTFB']
            root_cat = Category('Time To First Byte (Root Document)')
            root_cat.add_content(
                root_tt_ms <= TTFB_THRESHOLD_SECONDS * 1000,
                "Measures the time for the HTML root document to start loading."
            )
            root_cat.add_chart_content(
                chart_type='decline',
                threshold1=TTFB_THRESHOLD_SECONDS * 1000,
                threshold2=TTFB_THRESHOLD_SECONDS * 2 * 1000,
                threshold_unit="ms",
                value=round(root_tt_ms, 0)
            )
            card.add_category(root_cat)

        # --- 7b) Time To First Byte (Server Response) ---
        ttfb_value_ms = audit('server-response-time').get("numericValue", 0)
        server_cat = Category('Time To First Byte (Server Response)')
        server_cat.add_content(
            ttfb_value_ms <= TTFB_THRESHOLD_SECONDS * 1000,
            "Measures the time until the first byte is received from the server after the request is sent."
        )
        server_cat.add_chart_content(
            chart_type='decline',
            threshold1=TTFB_THRESHOLD_SECONDS * 1000,
            threshold2=TTFB_THRESHOLD_SECONDS * 2 * 1000,
            threshold_unit="ms",
            value=round(ttfb_value_ms, 0)
        )
        if ttfb_value_ms > TTFB_THRESHOLD_SECONDS * 1000:
            server_cat.add_content(
                "improvement",
                "Optimize server configuration, database queries, caching, or use a CDN to reduce TTFB."
            )
        card.add_category(server_cat)

    # --- 8) Performance Opportunities (unchanged) ---
    opp_category = Category('Performance Opportunities')
    if not lighthouse_metrics:
        opp_category.add_content(False, "Performance opportunities unavailable (requires PageSpeed/Lighthouse data).")
    else:
        # Render Blocking Resources
        rb = get_audit_details(lighthouse_metrics, 'render-blocking-resources')
        savings_ms = rb.get('details', {}).get('overallSavingsMs', 0)
        items = rb.get('details', {}).get('items', [])
        if items:
            opp_category.add_content(False, f"Eliminate render-blocking resources (Est. Savings: {format_ms(savings_ms)}).")
            for item in items[:3]:
                opp_category.add_content("", f"- {item.get('url', 'N/A')} ({format_bytes(item.get('totalBytes'))})")
            opp_category.add_content("improvement", "Inline critical resources, defer non-critical JS, and optimize CSS delivery.")
        else:
            opp_category.add_content(True, "No significant render-blocking resources identified.")

        # Unused CSS
        css = get_audit_details(lighthouse_metrics, 'unused-css-rules')
        css_bytes = css.get('details', {}).get('overallSavingsBytes', 0)
        if css_bytes > 1024:
            opp_category.add_content(False, f"Reduce unused CSS (Est. Savings: {format_bytes(css_bytes)}).")
            opp_category.add_content("improvement", "Remove unused CSS rules or split CSS into smaller files loaded only when needed.")

        # Unused JS
        js = get_audit_details(lighthouse_metrics, 'unused-javascript')
        js_bytes = js.get('details', {}).get('overallSavingsBytes', 0)
        if js_bytes > 1024:
            opp_category.add_content(False, f"Reduce unused JavaScript (Est. Savings: {format_bytes(js_bytes)}).")
            opp_category.add_content("improvement", "Remove unused JS code or use code splitting to load JS chunks on demand.")

        # Properly Sized Images
        img = get_audit_details(lighthouse_metrics, 'uses-responsive-images')
        img_bytes = img.get('details', {}).get('overallSavingsBytes', 0)
        if img_bytes > 10240:
            opp_category.add_content(False, f"Properly size images (Est. Savings: {format_bytes(img_bytes)}).")
            opp_category.add_content("improvement", "Serve images appropriately sized for their display dimensions to save bandwidth.")

    card.add_category(opp_category)

    # --- 9) Page Load Stats (Size & Requests) ---
    budget_category = Category('Page Load Stats (Size & Requests)')
    if not lighthouse_metrics:
        budget_category.add_content(False, "Page load stats unavailable.")
    else:
        try:
            total_size_bytes = lighthouse_metrics.get("total-byte-weight", {}).get("numericValue", 0)
            requests = lighthouse_metrics.get("network-requests", {}).get("details", {}).get("items", [])
            total_kb = total_size_bytes / 1024
            count = len(requests) if requests else 0

            budget_category.add_content(
                total_kb <= MAX_PAGE_SIZE_KB,
                f"Total Page Size: {total_kb:.0f} KB"
            )
            budget_category.add_content(
                count <= MAX_REQUESTS,
                f"Total Requests: {count}"
            )
            if total_kb > MAX_PAGE_SIZE_KB or count > MAX_REQUESTS:
                budget_category.add_content("improvement", "Reduce page size & requests (optimize images, minify & combine files, lazy load).")
        except Exception as e:
            budget_category.add_content(False, f"Error processing page load stats: {e}")
    card.add_category(budget_category)

    # --- 10) Server Compression ---
    compression_category = Category('Server Compression')
    encoding = response.headers.get('Content-Encoding')
    uses = encoding in {'br', 'gzip', 'deflate'}
    label = {'br': 'Brotli (br)', 'gzip': 'Gzip (gzip)', 'deflate': 'Deflate'}.get(encoding, 'None')
    compression_category.add_content(
        uses,
        f"Server compression enabled: {label}" if uses else "Server compression (Gzip/Brotli) not enabled."
    )
    if not uses:
        compression_category.add_content("improvement", "Enable Gzip or Brotli compression on your server.")
    card.add_category(compression_category)

    # --- 11) Modern Image Formats ---
    image_format_category = Category('Modern Image Formats')
    imgs = soup.find_all('img')
    legacy = any(img.get('src', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) for img in imgs)
    modern = any(img.get('src', '').lower().endswith(('.webp', '.avif', '.svg')) for img in imgs)
    if not imgs:
        image_format_category.add_content(True, "No `<img>` tags found.")
    elif modern and not legacy:
        image_format_category.add_content(True, "Modern image formats (WebP, AVIF, SVG) used.")
    elif modern and legacy:
        image_format_category.add_content(True, "Both modern and legacy image formats used.")
        image_format_category.add_content("improvement", "Consider converting remaining legacy images to WebP/AVIF.")
    elif legacy and not modern:
        image_format_category.add_content(False, "Only legacy image formats (JPG, PNG, GIF) found.")
        image_format_category.add_content("improvement", "Use modern image formats (WebP/AVIF) for better compression.")
    else:
        image_format_category.add_content(False, "Could not identify modern image formats.")
    card.add_category(image_format_category)

    return card


# --- Technical Configuration Card (ADDED Lighthouse Checks, StackPacks) ---
def build_technical_config_card(url: str, response: requests.Response, lighthouse_metrics: dict | None, stack_packs: list | None) -> Card:
    """ Builds the Technical Configuration card with added Lighthouse checks. """
    card = Card('Technical Configuration')
    parsed_url = urlparse(url)
    base_domain = parsed_url.netloc

    # --- HTTPS & Redirects ---
    # (This section remains the same)
    redirects_category = Category('HTTPS & Redirects')
    final_url = response.url
    is_final_https = final_url.startswith("https://")
    if not is_final_https:
         redirects_category.add_content(False, f"Final URL ({final_url}) does not use HTTPS.")
         redirects_category.add_content("improvement", "Migrate the entire site to HTTPS.")
    else: redirects_category.add_content(True, "Page is served over HTTPS.")
    if response.history:
        initial_url = response.history[0].url
        is_initial_http = initial_url.startswith("http://")
        if is_initial_http and is_final_https:
             initial_norm = urlparse(initial_url)._replace(scheme='').geturl()
             final_norm = urlparse(final_url)._replace(scheme='').geturl()
             if initial_norm == final_norm: redirects_category.add_content(True, f"Correct redirect from HTTP to HTTPS detected ({initial_url} -> {final_url}).")
             else: redirects_category.add_content(False, f"Redirect detected: {initial_url} -> ... -> {final_url}.")
        else:
             redirect_chain = ' -> '.join([r.url for r in response.history] + [final_url])
             redirects_category.add_content(False, f"Redirect chain detected: {redirect_chain}.")
             redirects_category.add_content("improvement", "Minimize redirects and ensure correct status codes (301).")
    # WWW vs Non-WWW Check
    if base_domain:
        opposite_url = None
        current_scheme = parsed_url.scheme
        path_query = parsed_url._replace(scheme='', netloc='').geturl()
        try:
            if base_domain.startswith("www."): opposite_domain = base_domain[4:]
            else: opposite_domain = f"www.{base_domain}"
            opposite_url = f"{current_scheme}://{opposite_domain}{path_query}"
            redirecting_www_correctly = False
            www_check_message = "Could not verify WWW/Non-WWW consistency."
            if opposite_url:
                try:
                    response_opposite = requests.get(opposite_url, timeout=10, allow_redirects=True)
                    if response_opposite.url == final_url:
                         redirecting_www_correctly = True
                         www_check_message = f"The {'non-WWW' if base_domain.startswith('www.') else 'WWW'} version correctly redirects."
                    else:
                         redirecting_www_correctly = False
                         www_check_message = f"WWW and non-WWW versions resolve inconsistently (Opposite: {response_opposite.url})."
                except requests.exceptions.RequestException as e: www_check_message = f"Error checking WWW/Non-WWW redirect: {e}"; redirecting_www_correctly = False
                redirects_category.add_content(redirecting_www_correctly, www_check_message)
                if not redirecting_www_correctly: redirects_category.add_content("improvement", "Ensure only one canonical version (www or non-www) is live, and the other 301 redirects.")
        except Exception as e: redirects_category.add_content(False, f"Error during WWW/Non-WWW check setup: {e}")
    card.add_category(redirects_category)

    # --- Robots.txt & Sitemap ---
    # (This section remains the same)
    robots_category = Category('Robots.txt & Sitemap')
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    robots_found = False
    sitemap_in_robots = None
    robots_status = "Not Checked"
    try:
        response_robots = requests.get(robots_url, timeout=10, allow_redirects=False)
        if response_robots.status_code == 200:
            robots_found = True; robots_status = "Found and accessible."
            robots_content = response_robots.text
            for line in robots_content.splitlines():
                if line.strip().lower().startswith("sitemap:"): sitemap_in_robots = line.split(":", 1)[1].strip(); break
        else: robots_status = f"Found but status {response_robots.status_code}."
    except requests.exceptions.RequestException: robots_status = "Not found or connection error."
    except Exception as e: robots_status = f"Error checking robots.txt: {e}"
    robots_category.add_content(robots_found, f"Robots.txt status: {robots_status}")
    if not robots_found: robots_category.add_content("improvement", "Create a `robots.txt` file in the root directory.")
    sitemap_found = False; sitemap_url_checked = "N/A"; sitemap_status = "Not Found"
    if sitemap_in_robots:
        sitemap_url_checked = sitemap_in_robots
        try:
            response_sitemap = requests.head(sitemap_url_checked, timeout=10, allow_redirects=True)
            if response_sitemap.status_code == 200: sitemap_found = True; sitemap_status = f"Declared in robots.txt and accessible."
            else: sitemap_status = f"Declared in robots.txt ({sitemap_url_checked}) but not reachable (Status: {response_sitemap.status_code})."
        except requests.exceptions.RequestException: sitemap_status = f"Declared in robots.txt ({sitemap_url_checked}) but connection error."
        except Exception as e: sitemap_status = f"Error checking declared sitemap: {e}"
        robots_category.add_content(sitemap_found, f"Sitemap status: {sitemap_status}")
        if not sitemap_found and "not reachable" in sitemap_status: robots_category.add_content("improvement", "Ensure the Sitemap URL in robots.txt is correct.")
    elif not sitemap_found and base_domain:
        common_sitemap_paths = ["/sitemap.xml", "/sitemap_index.xml"]
        for path in common_sitemap_paths:
            sitemap_url = f"{parsed_url.scheme}://{base_domain}{path}"
            try:
                response_sitemap = requests.head(sitemap_url, timeout=10, allow_redirects=True)
                if response_sitemap.status_code == 200: sitemap_found = True; sitemap_url_checked = sitemap_url; sitemap_status = f"Found at: {sitemap_url_checked}"; break
            except requests.exceptions.RequestException: continue
            except Exception as e: sitemap_status = f"Error checking {sitemap_url}: {e}"; break
        robots_category.add_content(sitemap_found, f"Sitemap status: {sitemap_status}")
        if not sitemap_found and sitemap_status == "Not Found": robots_category.add_content("improvement", "Create an XML sitemap (sitemap.xml) and submit it to search engines.")
    card.add_category(robots_category)

    # --- HTTP Security Headers ---
    # (This section remains the same)
    security_category = Category('HTTP Security Headers')
    headers = response.headers
    found_headers = []; missing_headers = []
    for header in SECURITY_HEADERS:
        if header in headers: found_headers.append(header)
        else: missing_headers.append(header)
    if not missing_headers: security_category.add_content(True, f"All checked security headers found: {', '.join(found_headers)}.")
    else:
        security_category.add_content(len(found_headers) > 0, f"Found headers: {', '.join(found_headers) if found_headers else 'None'}.")
        security_category.add_content(False, f"Missing headers: {', '.join(missing_headers)}.")
        security_category.add_content("improvement", f"Implement missing headers like {', '.join(missing_headers)} to enhance security.")
    card.add_category(security_category)

    # --- NEW: Best Practices & SEO Checks from Lighthouse ---
    lh_checks_category = Category('Other Technical Checks (Lighthouse)')
    if not lighthouse_metrics:
        lh_checks_category.add_content(False, "Detailed technical checks unavailable (Requires PageSpeed Data).")
    else:
        # Doctype
        doctype_audit = get_audit_details(lighthouse_metrics, 'doctype')
        doctype_score = get_audit_score(doctype_audit)
        if doctype_score is not None:
             lh_checks_category.add_content(doctype_score == 1.0, "HTML doctype is present." if doctype_score == 1.0 else "HTML doctype is missing.")
             if doctype_score < 1.0: lh_checks_category.add_content("improvement", "Add `<!DOCTYPE html>` at the beginning of your HTML.")

        # Console Errors
        errors_audit = get_audit_details(lighthouse_metrics, 'errors-in-console')
        error_items = errors_audit.get('details', {}).get('items', [])
        if not error_items:
            lh_checks_category.add_content(True, "No browser errors reported in the console during page load.")
        else:
            lh_checks_category.add_content(False, f"{len(error_items)} browser errors found in the console.")
            # List first few errors
            for item in error_items[:3]:
                source = item.get('source', {})
                if isinstance(source, dict):
                    source_url = source.get('url', 'N/A')
                    lh_checks_category.add_content("", f"- {item.get('description', 'N/A')} (Source: {source_url})")
                else:
                    lh_checks_category.add_content("", f"- {item.get('description', 'N/A')} (Source: {source})")
            lh_checks_category.add_content("improvement", "Fix JavaScript errors reported in the browser console to ensure proper page functionality.")

        # Deprecations
        deprecations_audit = get_audit_details(lighthouse_metrics, 'deprecations')
        deprecation_items = deprecations_audit.get('details', {}).get('items', [])
        if not deprecation_items:
            lh_checks_category.add_content(True, "No deprecated APIs reported in use.")
        else:
            lh_checks_category.add_content(False, f"{len(deprecation_items)} deprecated APIs found.")
            for item in deprecation_items[:3]:
                 lh_checks_category.add_content("", f"- {item.get('value', 'N/A')}")
            lh_checks_category.add_content("improvement", "Replace deprecated browser APIs with modern alternatives to prevent future breakage.")

        # HTTP Status Code (might be redundant with response.status_code, but explicit check)
        status_code_audit = get_audit_details(lighthouse_metrics, 'http-status-code')
        status_score = get_audit_score(status_code_audit)
        if status_score is not None and status_score < 1.0:
            lh_checks_category.add_content(False, "Page may not return a successful HTTP status code (2xx).")
            # Details might contain the actual code if available in the audit
        else:
              lh_checks_category.add_content(True, "Page returns a successful HTTP status code (2xx).")

        # Is Crawlable (might be redundant with robots.txt check)
        crawlable_audit = get_audit_details(lighthouse_metrics, 'is-crawlable')
        crawlable_score = get_audit_score(crawlable_audit)
        if crawlable_score is not None:
            lh_checks_category.add_content(crawlable_score == 1.0, "Page appears to be crawlable by search engines." if crawlable_score == 1.0 else "Page may be blocked from crawling (check robots.txt and meta tags).")


    card.add_category(lh_checks_category)

    # --- NEW: Stack Packs ---
    if stack_packs:
        stack_category = Category('Platform Specific Advice (Stack Packs)')
        stack_found = False
        for pack in stack_packs:
            pack_title = pack.get('title')
            pack_desc = pack.get('descriptions', {})
            if pack_title and pack_desc:
                 stack_found = True
                 stack_category.add_content(True, f"Detected Platform: {pack_title}")
                 # Display descriptions (often contains specific advice)
                 for key, desc in pack.get('descriptions', {}).items():
                     if desc: # Show non-empty descriptions
                         stack_category.add_content("", f"- {desc}")
        if not stack_found:
             stack_category.add_content(True, "No specific platform advice (Stack Packs) detected.")

        card.add_category(stack_category)


    return card

# --- AI Card (No changes needed) ---
def build_ai_card(soup: BeautifulSoup) -> Card:
    # (This function remains the same as in the previous version)
    card = Card('AI Analysis')
    title_text = soup.title.string.strip() if soup.title and soup.title.string else ""
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description_content = description_tag.get('content', '').strip() if description_tag else ""
    if not title_text and not description_content:
        error_category = Category("Missing Data"); error_category.add_content(False, "No title or description found for AI analysis."); card.add_category(error_category); return card
    try:
        try: loop = asyncio.get_running_loop()
        except RuntimeError: loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        ai_results = loop.run_until_complete(ai_analyzer(description_content, title_text))
        if description_content:
            ai_desc_category = Category('AI Analysis: Description')
            ai_desc_category.add_content("", f'Original Description: "{description_content}"')
            desc_rating = ai_results.get('description_rating', 0); desc_reason = ai_results.get('description_reason', 'N/A'); desc_improvement = ai_results.get('description_improvement', 'N/A')
            is_desc_good = desc_rating >= AI_RATING_THRESHOLD
            ai_desc_category.add_content(is_desc_good, f"AI Rating: {desc_rating}/100. Reasoning: {desc_reason}")
            if not is_desc_good or "No improvement suggestion" not in desc_improvement: ai_desc_category.add_content("improvement", f"AI Suggestion: {desc_improvement}")
            card.add_category(ai_desc_category)
        else: card.add_category(Category('AI Analysis: Description').add_content(False, "No description found."))
        if title_text:
            ai_title_category = Category('AI Analysis: Title')
            ai_title_category.add_content("", f'Original Title: "{title_text}"')
            title_rating = ai_results.get('title_rating', 0); title_reason = ai_results.get('title_reason', 'N/A'); title_improvement = ai_results.get('title_improvement', 'N/A')
            is_title_good = title_rating >= AI_RATING_THRESHOLD
            ai_title_category.add_content(is_title_good, f"AI Rating: {title_rating}/100. Reasoning: {title_reason}")
            if not is_title_good or "No improvement suggestion" not in title_improvement: ai_title_category.add_content("improvement", f"AI Suggestion: {title_improvement}")
            card.add_category(ai_title_category)
        else: card.add_category(Category('AI Analysis: Title').add_content(False, "No title found."))
    except Exception as e: error_category = Category("Error during AI Analysis"); error_category.add_content(False, f"AI analysis could not be performed: {e}"); card.add_category(error_category)
    return card


# ############################################################################ #
#                              HELPER FUNCTIONS                              #
# ############################################################################ #
# (build_not_available_card, build_serp_preview, get_overall_rating_text,
#  get_improvement_count_text, build_overall_results remain the same)
def build_not_available_card(title: str, category_title: str, message: str) -> Card:
    """ Creates a placeholder Card indicating a feature is not available. """
    card = Card(title)
    category = Category(category_title)
    category.add_content("improvement", message) # Using 'improvement' type for consistent display
    card.add_category(category)
    return card

def build_serp_preview(soup: BeautifulSoup, url: str, response: requests.Response) -> dict:
    """ Generates data for a Search Engine Results Page (SERP) preview. (Translated) """
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag.get('content', '').strip() if description_tag else "No description found."
    serp_points = 0; title_length = len(title); desc_length_chars = len(description); desc_length_px = round(desc_length_chars * SERP_DESC_AVG_CHAR_WIDTH_PX)
    if title != "No title found":
        serp_points += 5
        if SERP_TITLE_MIN_LENGTH <= title_length <= SERP_TITLE_MAX_LENGTH: serp_points += 45
        elif SERP_TITLE_ACCEPTABLE_MIN <= title_length < SERP_TITLE_MIN_LENGTH: serp_points += 20
        elif SERP_TITLE_MAX_LENGTH < title_length <= SERP_TITLE_ACCEPTABLE_MAX: serp_points += 20
    if description != "No description found.":
        serp_points += 5
        if SERP_DESC_MIN_LENGTH_PX <= desc_length_px <= SERP_DESC_MAX_LENGTH_PX: serp_points += 45
        elif SERP_DESC_ACCEPTABLE_MIN_PX <= desc_length_px < SERP_DESC_MIN_LENGTH_PX: serp_points += 20
        elif SERP_DESC_MAX_LENGTH_PX < desc_length_px <= SERP_DESC_ACCEPTABLE_MAX_PX: serp_points += 20
    serp_points = min(serp_points, 100)
    return {'isCard': False, 'serp_mobile': {'url': url, 'title': title, 'description': description}, 'serp_desktop': {'url': url, 'title': title, 'description': description}, "points": serp_points}

def get_overall_rating_text(rating: int) -> str:
    """ Generates text interpretation for the overall rating. (English) """
    if rating >= 90: return "Excellent! This page follows most best practices."
    if rating >= 75: return "Good. The page is well-optimized, but there's room for improvement."
    if rating >= 50: return "Fair. Several areas need attention for better optimization."
    return "Poor. Significant improvements are needed across multiple areas."

def get_improvement_count_text(count: int) -> str:
    """ Generates text for the number of improvements. (English) """
    if count == 0: return "No specific improvement suggestions found."
    if count == 1: return "1 improvement suggestion found."
    return f"{count} improvement suggestions found."

def build_overall_results(results: dict) -> dict:
    """ Calculates overall rating and improvement count. (Translated) """
    card_results = {k: v for k, v in results.items() if isinstance(v, dict) and v.get('isCard', True)}
    overall_rating = calculate_overall_points(card_results)
    improvement_count = calculate_improvement_count(card_results)
    return {'isCard': False, 'overall_rating': overall_rating, 'overall_rating_text': get_overall_rating_text(overall_rating), 'improvement_count': improvement_count, 'improvement_count_text': get_improvement_count_text(improvement_count)}

# ############################################################################ #
#                                END OF SCRIPT                                 #
# ############################################################################ #