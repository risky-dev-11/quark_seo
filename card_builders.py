# ############################################################################ #
#                                  IMPORTS                                     #
# ############################################################################ #

# Standard Library Imports
import asyncio
import socket
import os

# Third-Party Imports
import requests
from bs4 import BeautifulSoup # Assuming soup is BeautifulSoup object
from langdetect import detect_langs, DetectorFactory, LangDetectException
import dotenv

# Local Application/Library Specific Imports
from text_snippet_functions import (
    get_improvement_count_text, get_overall_rating_text, get_title_incorrect_length_text,
    get_title_missing_improvement_text, get_title_word_repetitions_improvement_text, get_title_missing_text,
    get_domain_in_title_text, get_title_length_text, get_title_word_repetitions_text, get_description_missing_text,
    get_description_length_text, get_language_comment, get_favicon_included_text, get_comparison_title_text,
    get_content_length_comment, get_duplicate_text, get_alt_attributes_missing_text,
    get_internal_length_linktext_text, get_internal_no_linktext_text, get_internal_linktext_repetitions_text,
    get_external_length_linktext_text, get_external_no_linktext_text, get_external_linktext_repetitions_text,
    get_redirecting_www_text, get_compression_text
)
from models import Card, Category, ChartContent, calculate_improvement_count, calculate_overall_points
from ai_analyzer import ai_analyzer # Assuming ai_analyzer is an async function

# ############################################################################ #
#                              ENVIRONMENT SETUP                               #
# ############################################################################ #

dotenv.load_dotenv()
GOOGLE_PAGESPEED_API_KEY = os.getenv("GOOGLE_PAGESPEED_API_KEY")

# ############################################################################ #
#                                 CONSTANTS                                    #
# ############################################################################ #

# --- Core Web Vitals Thresholds ---
LCP_THRESHOLD_SECONDS = 2.5
FCP_THRESHOLD_SECONDS = 1.8
TBT_THRESHOLD_MS = 200.0
CLS_THRESHOLD = 0.1
SPEED_INDEX_THRESHOLD_SECONDS = 4.3

# --- Metadata Thresholds ---
TITLE_MIN_LENGTH = 50
TITLE_MAX_LENGTH = 60
# Approximate pixel width per character for description length check
# Note: This is a simplification; actual pixel width varies by character.
AVG_CHAR_WIDTH_PX = 6.19
DESC_MIN_LENGTH_PX = 800
DESC_MAX_LENGTH_PX = 960

# --- Page Quality Thresholds ---
MIN_CONTENT_WORD_COUNT = 300
MAX_LINK_TEXT_LENGTH = 30 # Arbitrary threshold for link text length

# --- AI Analysis Thresholds ---
AI_RATING_THRESHOLD = 80 # Minimum rating (out of 100) to be considered "good"

# --- SERP Preview Approx Pixel Width ---
SERP_DESC_AVG_CHAR_WIDTH_PX = 6.11 # Different estimate for SERP preview?
SERP_DESC_MIN_LENGTH_PX = 500 # Optimal min length for SERP description
SERP_DESC_MAX_LENGTH_PX = 960 # Optimal max length for SERP description
SERP_DESC_ACCEPTABLE_MIN_PX = 200 # Acceptable min length range
SERP_DESC_ACCEPTABLE_MAX_PX = 1260 # Acceptable max length range (truncated but has content)
SERP_TITLE_MIN_LENGTH = 50
SERP_TITLE_MAX_LENGTH = 60
SERP_TITLE_ACCEPTABLE_MIN = 25
SERP_TITLE_ACCEPTABLE_MAX = 85 # Truncated but likely has keywords

# --- API Endpoints ---
GOOGLE_PAGESPEED_API_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
IP_API_URL_TEMPLATE = "http://ip-api.com/json/{ip}"

# ############################################################################ #
#                             MAIN ORCHESTRATOR                              #
# ############################################################################ #

def build_all_cards(results: dict, soup: BeautifulSoup, url: str, response: requests.Response, is_premium_user: bool):
    """
    Builds and adds all the SEO analysis card sections to the results dictionary.

    This function acts as a central coordinator, calling specific builder functions
    for each logical card (Metadata, Core Web Vitals, Technical SEO, etc.).
    It handles premium user checks for specific cards (Core Web Vitals, AI Analysis).

    The 'index' key is added to each card's dictionary before adding it to 'results'.
    This is used client-side to enforce a specific display order, working around
    potential JSON object key ordering issues.

    Args:
        results (dict): The dictionary where card results will be stored.
                        Expected to be modified in place.
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page.
        response (requests.Response): The response object from the initial request to the URL.
        is_premium_user (bool): Flag indicating if the user has premium access.
    """
    # --- Metadata Card ---
    metadata_card = build_metadata_card(soup, url)
    metadata_card.add_to_results(results, index=1)

    # --- Core Web Vitals Card ---
    if is_premium_user:
        core_web_vitals_card = build_core_web_vitals_card(url)
        core_web_vitals_card.add_to_results(results, index=2)
    else:
        core_web_vitals_card = build_not_available_card(
            title='Core Web Vitals',
            category_title='Core Web Vitals nicht verfügbar',
            message='Die Core Web Vitals sind nur für Premium-Nutzer verfügbar. Bitte aktualisieren Sie Ihr Abonnement, um diese Funktion zu nutzen.'
        )
        # Assign full points if not available to avoid penalizing non-premium users in overall score
        core_web_vitals_card.add_to_results(results, manual_points=100, index=2)

    # --- Technical SEO Card ---
    technical_seo_card = build_technical_seo_card(soup, url, response)
    technical_seo_card.add_to_results(results, index=3)

    # --- Page Quality & Links Card ---
    page_quality_and_links_card = build_page_quality_and_links_card(soup, url)
    page_quality_and_links_card.add_to_results(results, index=4)

    # --- AI Analysis Card ---
    if is_premium_user:
        ai_results_card = build_ai_card(soup)
        ai_results_card.add_to_results(results, index=5)
    else:
        ai_results_card = build_not_available_card(
            title='KI - Analyse',
            category_title='KI-Analyse nicht verfügbar',
            message='Die KI-Analyse ist nur für Premium-Nutzer verfügbar. Bitte aktualisieren Sie Ihr Abonnement, um diese Funktion zu nutzen.'
        )
        # Assign full points if not available
        ai_results_card.add_to_results(results, manual_points=100, index=5)

# ############################################################################ #
#                            CARD BUILDER FUNCTIONS                            #
# ############################################################################ #

def build_core_web_vitals_card(url: str) -> Card:
    """
    Builds the Core Web Vitals card by fetching data from Google PageSpeed Insights API.

    Args:
        url (str): The URL to analyze.

    Returns:
        Card: A Card object populated with Core Web Vitals categories and results.
              Returns a card with an error message if the API call fails.
    """
    card = Card('Core Web Vitals')

    try:
        params = {
            "url": url,
            "key": GOOGLE_PAGESPEED_API_KEY,
            "strategy": "desktop"  # Or potentially "mobile" or both
        }

        response = requests.get(GOOGLE_PAGESPEED_API_URL, params=params, timeout=30)  # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        data = response.json()
        lighthouse_metrics = data.get("lighthouseResult", {}).get("audits", {})

        # --- Define Chart Categories ---
        lcp_category = Category('Largest Contentful Paint')
        fcp_category = Category('First Contentful Paint')
        tbt_category = Category('Total Blocking Time')
        cls_category = Category('Cumulative Layout Shift')
        speed_index_category = Category('Speed Index')

        # --- Extract and Evaluate Metrics ---
        lcp_value_ms = lighthouse_metrics.get("largest-contentful-paint", {}).get("numericValue", float('inf'))
        # Largest Contentful Paint (LCP) measures the time it takes for the largest visible content (e.g., an image or text block) to load and become visible on the screen.
        lcp_category.add_content(
            lcp_value_ms / 1000 <= LCP_THRESHOLD_SECONDS,
            "Largest Contentful Paint (LCP) indicates how quickly the largest visible content on the page is fully loaded and visible."
        )
        lcp_category.add_chart_content(
            chart_type='decline',
            threshold1=round(LCP_THRESHOLD_SECONDS, 2),
            threshold2=round(LCP_THRESHOLD_SECONDS * 1.5, 2),  # Threshold2: 50% higher than optimal
            threshold_unit="s",
            value=round(lcp_value_ms / 1000, 2)
        )

        # First Contentful Paint (FCP) measures the time it takes for the first piece of content (e.g., text, image, or canvas) to appear on the screen.
        fcp_value_ms = lighthouse_metrics.get("first-contentful-paint", {}).get("numericValue", float('inf'))
        fcp_category.add_content(
            fcp_value_ms / 1000 <= FCP_THRESHOLD_SECONDS,
            "First Contentful Paint (FCP) measures how quickly the first visible content appears on the page."
        )
        fcp_category.add_chart_content(
            chart_type='decline',
            threshold1=round(FCP_THRESHOLD_SECONDS, 2),
            threshold2=round(FCP_THRESHOLD_SECONDS * 1.5, 2),  # Threshold2: 50% higher than optimal
            threshold_unit="s",
            value=round(fcp_value_ms / 1000, 2)
        )

        # Total Blocking Time (TBT) measures the total time during which the main thread is blocked, preventing user interaction.
        tbt_value_ms = lighthouse_metrics.get("total-blocking-time", {}).get("numericValue", float('inf'))
        tbt_category.add_content(
            tbt_value_ms <= TBT_THRESHOLD_MS,
            "Total Blocking Time (TBT) reflects how much time the page was unresponsive to user input."
        )
        tbt_category.add_chart_content(
            chart_type='decline',
            threshold1=round(TBT_THRESHOLD_MS, 2),
            threshold2=round(TBT_THRESHOLD_MS * 1.5, 2),  # Threshold2: 50% higher than optimal
            threshold_unit="ms",
            value=round(tbt_value_ms, 2)
        )

        # Cumulative Layout Shift (CLS) measures the visual stability of a page by tracking unexpected layout shifts during the page's lifecycle.
        cls_value = lighthouse_metrics.get("cumulative-layout-shift", {}).get("numericValue", float('inf'))
        cls_category.add_content(
            cls_value <= CLS_THRESHOLD,
            "Cumulative Layout Shift (CLS) evaluates the visual stability of the page by measuring unexpected layout shifts."
        )
        cls_category.add_chart_content(
            chart_type='decline',
            threshold1=round(CLS_THRESHOLD, 2),
            threshold2=round(CLS_THRESHOLD * 1.5, 2),  # Threshold2: 50% higher than optimal
            threshold_unit=" ",
            value=round(cls_value, 2)
        )

        # Speed Index measures how quickly the content of a page is visibly populated during loading.
        speed_index_value_ms = lighthouse_metrics.get("speed-index", {}).get("numericValue", float('inf'))
        speed_index_category.add_content(
            speed_index_value_ms / 1000 <= SPEED_INDEX_THRESHOLD_SECONDS,
            "Speed Index measures how quickly the visible parts of the page are populated during loading."
        )
        speed_index_category.add_chart_content(
            chart_type='decline',
            threshold1=round(SPEED_INDEX_THRESHOLD_SECONDS, 2),
            threshold2=round(SPEED_INDEX_THRESHOLD_SECONDS * 1.5, 2),  # Threshold2: 50% higher than optimal
            threshold_unit="s",
            value=round(speed_index_value_ms / 1000, 2)
        )

        # --- Add Chart Categories to Card ---
        card.add_category(lcp_category)
        card.add_category(fcp_category)
        card.add_category(tbt_category)
        card.add_category(cls_category)
        card.add_category(speed_index_category)
        return card

    except Exception as e:
        print(f"Error fetching Core Web Vitals: {e}")
        error_category = Category('Verarbeitungsfehler')
        error_category.add_content(
            False,
            'Ein unerwarteter Fehler ist bei der Verarbeitung der Core Web Vitals aufgetreten.'
        )
        card.add_category(error_category)

        return card

# ---------------------------------------------------------------------------- #

def build_metadata_card(soup: BeautifulSoup, url: str) -> Card:
    """
    Builds the Metadata card, analyzing title, description, rich snippets, language,
    essential meta tags, and favicon.

    Args:
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page.

    Returns:
        Card: A Card object populated with metadata-related categories and results.
    """
    card = Card('Metadaten')

    # --- Title Category ---
    title_category = Category('Titel')
    title_tag = soup.title
    title_text = title_tag.string.strip() if title_tag and title_tag.string else ""
    is_title_missing = not bool(title_text)

    title_category.add_content(not is_title_missing, get_title_missing_text(is_title_missing))

    if is_title_missing:
        title_category.add_content("improvement", get_title_missing_improvement_text())
    else:
        title_length = len(title_text)
        is_title_length_correct = TITLE_MIN_LENGTH <= title_length <= TITLE_MAX_LENGTH
        has_domain_in_title = url in title_text # Simple check, might need refinement based on desired domain format
        title_words = title_text.lower().split() # Lowercase for case-insensitive repetition check
        word_counts = {word: title_words.count(word) for word in set(title_words)}
        repeated_words = [word for word, count in word_counts.items() if count > 1]
        has_title_word_repetitions = len(repeated_words) > 0

        title_category.add_content('', f'Titel: "{title_text}"') # Display the actual title
        title_category.add_content(not has_domain_in_title, get_domain_in_title_text(has_domain_in_title))
        title_category.add_content(is_title_length_correct, get_title_length_text(title_length))
        if not is_title_length_correct:
            title_category.add_content("improvement", get_title_incorrect_length_text(title_length))

        title_category.add_content(not has_title_word_repetitions, get_title_word_repetitions_text(has_title_word_repetitions))
        if has_title_word_repetitions:
            title_category.add_content("improvement", get_title_word_repetitions_improvement_text(', '.join(repeated_words)))

    card.add_category(title_category)

    # --- Description Category ---
    description_category = Category('Beschreibung')
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description_content = description_tag.get('content', '').strip() if description_tag else ""
    is_description_missing = not bool(description_content)

    description_category.add_content(not is_description_missing, get_description_missing_text(is_description_missing))

    if not is_description_missing:
        desc_length_chars = len(description_content)
        # Approximate pixel length (highly dependent on font and characters)
        desc_length_px = round(desc_length_chars * AVG_CHAR_WIDTH_PX)
        is_desc_length_optimal = DESC_MIN_LENGTH_PX <= desc_length_px <= DESC_MAX_LENGTH_PX

        description_category.add_content('', f'Beschreibung: "{description_content}"') # Display actual description
        description_category.add_content(is_desc_length_optimal, get_description_length_text(desc_length_px))
        description_category.add_chart_content(
            chart_type='range',
            threshold1=DESC_MIN_LENGTH_PX,
            threshold2=DESC_MAX_LENGTH_PX,
            threshold_unit="px",
            value=desc_length_px,
        )
        # Potentially add improvement text if length is not optimal
        if not is_desc_length_optimal:
             description_category.add_content("improvement", f"Die Beschreibungslänge ({desc_length_px}px / {desc_length_chars} Zeichen) ist nicht optimal ({DESC_MIN_LENGTH_PX}-{DESC_MAX_LENGTH_PX}px empfohlen). Passen Sie sie an, um in Suchergebnissen vollständig angezeigt zu werden.")

    else:
         description_category.add_content("improvement", "Fügen Sie eine Meta-Beschreibung hinzu. Sie ist entscheidend für die Klickrate in Suchergebnissen.")

    card.add_category(description_category)

    # --- Rich Snippets Category ---
    rich_snippets_category = Category('Rich Snippets (Schema.org)')
    # Find elements with 'itemscope' and 'itemtype' which indicate microdata usage
    schema_elements = soup.find_all(attrs={"itemscope": True, "itemtype": True})
    # Also check for JSON-LD scripts
    json_ld_scripts = soup.find_all('script', type='application/ld+json')

    has_rich_snippets = len(schema_elements) > 0 or len(json_ld_scripts) > 0

    if has_rich_snippets:
         rich_snippets_category.add_content(True, "Die Webseite verwendet strukturierte Daten (Rich Snippets).")
         for snippet in schema_elements:
             item_type = snippet.get('itemtype', 'Unbekannt')
             itemprops = snippet.find_all(attrs={"itemprop": True})
             # Provide more context if possible (e.g., itemprop content)
             itemprops_details = [f"{prop.get('itemprop')}: {prop.get('content') or prop.get_text(strip=True)[:50]+'...'}" for prop in itemprops]
             rich_snippets_category.add_content('', f"Gefundenes Microdata Snippet: {item_type}, Eigenschaften: {', '.join(itemprops_details)}")
         for _ in json_ld_scripts:
              rich_snippets_category.add_content('', "Gefundenes JSON-LD Snippet.") # Could potentially parse JSON here for more detail
    else:
         rich_snippets_category.add_content(False, "Die Webseite verwendet keine erkannten strukturierten Daten (Rich Snippets).")
         rich_snippets_category.add_content("improvement", f"Es wurden keine Rich Snippets (Schema.org Microdata oder JSON-LD) auf der analysierten Seite ({url}) gefunden. Implementieren Sie strukturierte Daten, um Suchmaschinen detaillierte Informationen über Ihren Inhalt zu geben und Rich Results in SERPs zu ermöglichen. Beachten Sie, dass diese oft auf spezifischen Unterseiten (Produkte, Artikel etc.) vorhanden sind.")

    card.add_category(rich_snippets_category)

    # --- Language Category ---
    language_category = Category('Sprache & Standort')
    html_lang = soup.html.get('lang', '').strip() if soup.html else ''
    meta_lang_tag = soup.find('meta', attrs={'http-equiv': 'Content-Language'}) # Less common now
    meta_lang = meta_lang_tag.get('content', '').strip() if meta_lang_tag else ''
    declared_lang = html_lang or meta_lang or 'Nicht deklariert'

    language_category.add_content(declared_lang != 'Nicht deklariert', f'Deklarierte Sprache (HTML lang / Meta): {declared_lang}')

    detected_lang = 'Fehler'
    detected_lang_probability = 0.0
    page_text = soup.get_text()
    try:
        # langdetect needs seed for deterministic results if run multiple times on same text
        DetectorFactory.seed = 0
        if page_text.strip():
            detected_languages_with_probabilities = detect_langs(page_text)
            if detected_languages_with_probabilities:
                best_match = detected_languages_with_probabilities[0]
                detected_lang = best_match.lang
                detected_lang_probability = best_match.prob
                language_category.add_content(True, f'Im Text erkannte Sprache: {detected_lang} (mit {detected_lang_probability:.1%} Wahrscheinlichkeit)')
            else:
                language_category.add_content(False, 'Sprache konnte im Text nicht erkannt werden.')
        else:
            language_category.add_content(False, 'Kein ausreichender Textinhalt zur Spracherkennung gefunden.')

    except LangDetectException:
         language_category.add_content(False, 'Fehler bei der automatischen Spracherkennung.')
         detected_lang = 'Fehler' # Ensure it doesn't match declared_lang
    except Exception as e: # Catch other potential errors during detection
         language_category.add_content(False, f'Unerwarteter Fehler bei der Spracherkennung: {e}')
         detected_lang = 'Fehler'

    # Compare declared vs. detected (basic check)
    # Note: Language codes might differ (e.g., 'de' vs 'de-DE'). This is a simple check.
    lang_match = detected_lang != 'Fehler' and detected_lang in declared_lang.lower()
    language_category.add_content(lang_match, get_language_comment(declared_lang, detected_lang))
    if declared_lang != 'Nicht deklariert' and not lang_match:
        language_category.add_content("improvement", "Die deklarierte Sprache stimmt möglicherweise nicht mit der erkannten Sprache des Inhalts überein. Stellen Sie sicher, dass das `lang`-Attribut im `<html>`-Tag korrekt gesetzt ist. (Hinweis: Unsere Spracherkennung ist nicht perfekt).")
    elif declared_lang == 'Nicht deklariert':
         language_category.add_content("improvement", "Es wurde keine Sprache deklariert. Fügen Sie das `lang`-Attribut zum `<html>`-Tag hinzu (z.B. `<html lang=\"de\">`).")


    # Server Location (Best Effort)
    server_location = 'Unbekannt'
    try:
        # Extract domain, handling potential schemes and paths
        domain_parts = url.split('//')
        domain = (domain_parts[1] if len(domain_parts) > 1 else domain_parts[0]).split('/')[0].split(':')[0] # Handle potential port number
        ip = socket.gethostbyname(domain)
        # Use template for IP API URL
        ip_api_response = requests.get(IP_API_URL_TEMPLATE.format(ip=ip), timeout=5)
        ip_api_response.raise_for_status()
        server_location = ip_api_response.json().get('country', 'Unbekannt')
    except socket.gaierror:
        server_location = 'Domain nicht auflösbar'
    except requests.exceptions.RequestException:
        server_location = 'Standort-API nicht erreichbar'
    except Exception: # Catch-all for other unexpected errors during IP lookup
        server_location = 'Fehler bei Standortabfrage'
    finally:
        language_category.add_content(server_location not in ['Unbekannt', 'Fehler bei Standortabfrage', 'Domain nicht auflösbar', 'Standort-API nicht erreichbar'], f'Serverstandort (geschätzt): {server_location}')

    card.add_category(language_category)

    # --- Essential Meta Tags Category ---
    meta_tags_category = Category('Wichtige Meta-Tags')

    # Charset
    charset_meta = soup.find('meta', attrs={'charset': True})
    charset_http_equiv = soup.find('meta', attrs={'http-equiv': lambda x: x and x.lower() == 'content-type'})
    charset_content = charset_http_equiv.get('content') if charset_http_equiv else ''
    # Prefer <meta charset="UTF-8">
    has_charset = charset_meta is not None or 'charset=' in charset_content.lower()
    charset_value = charset_meta['charset'] if charset_meta else (charset_content.split('charset=')[-1].strip() if 'charset=' in charset_content.lower() else 'Nicht gefunden')
    meta_tags_category.add_content(has_charset, f"Zeichensatz (Charset) deklariert: {charset_value}" if has_charset else "Zeichensatz (Charset) Meta-Tag fehlt.")
    if not has_charset:
         meta_tags_category.add_content("improvement", "Fügen Sie ein Charset Meta-Tag hinzu (z.B. `<meta charset=\"UTF-8\">`), um sicherzustellen, dass Sonderzeichen korrekt dargestellt werden.")

    # Viewport (Crucial for Mobile)
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    has_viewport = viewport_meta is not None
    viewport_content = viewport_meta['content'] if has_viewport else 'Nicht gefunden'
    meta_tags_category.add_content(has_viewport, f"Viewport Meta-Tag vorhanden: {viewport_content}" if has_viewport else "Viewport Meta-Tag fehlt.")
    if not has_viewport:
        meta_tags_category.add_content("improvement", "Fügen Sie ein Viewport Meta-Tag hinzu (z.B. `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">`), um die mobile Darstellung zu optimieren.")
    elif has_viewport and "user-scalable=no" in viewport_content:
         meta_tags_category.add_content(False, "Warnung: Das Viewport-Tag verhindert das Zoomen (`user-scalable=no`), was die Barrierefreiheit beeinträchtigt.")
         meta_tags_category.add_content("improvement", "Entfernen Sie `user-scalable=no` aus dem Viewport-Tag, um Nutzern das Zoomen auf Mobilgeräten zu ermöglichen.")


    # Canonical URL
    canonical_link = soup.find('link', attrs={'rel': 'canonical'})
    has_canonical = canonical_link is not None
    canonical_href = canonical_link['href'] if has_canonical else 'Nicht gefunden'
    meta_tags_category.add_content(has_canonical, f"Canonical Link-Tag vorhanden: {canonical_href}" if has_canonical else "Canonical Link-Tag fehlt.")
    if not has_canonical:
         meta_tags_category.add_content("improvement", f"Fügen Sie ein Canonical Link-Tag (`<link rel=\"canonical\" href=\"{url}\">`) hinzu, um Duplicate Content Probleme zu vermeiden, besonders wenn die Seite über mehrere URLs erreichbar ist.")
    elif has_canonical and canonical_href != url:
        # Check if it's a reasonable difference (e.g., HTTP vs HTTPS, www vs non-www, trailing slash)
        is_reasonable_diff = (
            canonical_href == url.replace("http://", "https://") or
            canonical_href == url.replace("https://", "http://") or
            canonical_href == url.rstrip('/') or
            canonical_href == url + '/' or
            canonical_href.replace("://www.","://") == url.replace("://www.","://") # handles www mismatch
         )
        if not is_reasonable_diff:
            meta_tags_category.add_content(False, f"Warnung: Das Canonical-Tag ({canonical_href}) verweist auf eine andere URL als die aufgerufene ({url}). Stellen Sie sicher, dass dies beabsichtigt ist.")
            meta_tags_category.add_content("improvement", "Überprüfen Sie das Canonical-Tag. Es sollte normalerweise auf die bevorzugte Version der aktuellen Seite zeigen.")
        else:
             meta_tags_category.add_content(True, f"Canonical Link-Tag verweist auf eine ähnliche URL ({canonical_href}), was wahrscheinlich korrekt ist (z.B. HTTP/HTTPS, www/non-www, Trailing Slash).")


    card.add_category(meta_tags_category)

    # --- Favicon Category ---
    favicon_category = Category('Favicon')
    # Common rel values for favicons
    favicon_rels = ['icon', 'shortcut icon', 'apple-touch-icon', 'mask-icon']
    has_favicon = soup.find('link', attrs={'rel': lambda r: r and r.lower() in favicon_rels}) is not None
    favicon_category.add_content(has_favicon, get_favicon_included_text(has_favicon))
    if not has_favicon:
        favicon_category.add_content("improvement", "Fügen Sie ein Favicon hinzu. Es verbessert das Branding und die Wiedererkennung in Browser-Tabs und Lesezeichen.")

    card.add_category(favicon_category)

    return card

# ---------------------------------------------------------------------------- #

def build_page_quality_and_links_card(soup: BeautifulSoup, url: str) -> Card:
    """
    Builds the Page Quality and Links card, analyzing images (alt text), content
    (length, uniqueness, title relevance), and internal/external links.

    Args:
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page (used for link classification).

    Returns:
        Card: A Card object populated with content and link-related categories.
    """
    card = Card('Inhalt und Verlinkung')

    # --- Images Category ---
    images_category = Category('Bilder')
    all_images = soup.find_all('img')
    images_missing_alt = [img for img in all_images if not img.get('alt', '').strip()]
    count_missing_alts = len(images_missing_alt)

    images_category.add_content(count_missing_alts == 0, get_alt_attributes_missing_text(count_missing_alts))
    if count_missing_alts > 0:
        # List first few images without alt text as examples
        examples = [img.get('src', 'N/A')[:70] + ('...' if len(img.get('src','N/A')) > 70 else '') for img in images_missing_alt[:3]]
        images_category.add_content('improvement', f"Fügen Sie beschreibende Alt-Attribute zu allen Bildern hinzu (z.B. für: {', '.join(examples)}). Dies verbessert Barrierefreiheit und SEO.")
    card.add_category(images_category)

    # --- Content Category ---
    content_category = Category('Inhalt')
    page_text = soup.get_text()
    page_text_words = set(page_text.lower().split())
    word_count = len(page_text_words) # Count unique words? Or total words? Original used split() -> total words
    total_word_count = len(page_text.split())

    # Title comparison
    title_text = soup.title.string.strip().lower() if soup.title and soup.title.string else ""
    title_words = set(title_text.split())
    # Check if *any* title word is present, not all (original check was issubset)
    title_words_in_content = any(word in page_text_words for word in title_words if word) # Check if any non-empty title word exists in content
    content_category.add_content(title_words_in_content, get_comparison_title_text(not title_words_in_content)) # Function expects inverse boolean? Check text_snippet_functions
    if not title_words_in_content and title_words:
         content_category.add_content("improvement", "Wichtige Schlüsselwörter aus dem Titel sollten auch im Hauptinhalt der Seite vorkommen.")


    # Content length
    content_category.add_content(total_word_count >= MIN_CONTENT_WORD_COUNT, get_content_length_comment(total_word_count))
    if total_word_count < MIN_CONTENT_WORD_COUNT:
        content_category.add_content("improvement", f"Der Textumfang ({total_word_count} Wörter) ist relativ gering. Für ausführliche Themen sind oft mehr als {MIN_CONTENT_WORD_COUNT} Wörter sinnvoll, um Relevanz zu signalisieren.")

    # Duplicate content (simple sentence check)
    # Improved sentence splitting and filtering
    sentences = []
    for tag in soup.find_all(['p', 'div', 'span', 'li', 'article', 'section']):
        # Split by common sentence terminators, filter empty strings
        potential_sentences = [s.strip() for s in tag.get_text().replace('!','.').replace('?','.').split('.') if s.strip()]
        sentences.extend(potential_sentences)

    has_duplicate_sentences = False
    if len(sentences) > 5: # Only check if there are enough sentences to make duplicates meaningful
        has_duplicate_sentences = len(sentences) != len(set(sentences))
        content_category.add_content(not has_duplicate_sentences, get_duplicate_text(has_duplicate_sentences))
        if has_duplicate_sentences:
            content_category.add_content("improvement", "Es wurden doppelte Sätze im Text gefunden. Vermeiden Sie wiederholte Textblöcke, um die Lesbarkeit und Einzigartigkeit des Inhalts zu gewährleisten.")
    else:
        # Not enough sentences to reliably check for duplicates
         content_category.add_content(True, "Nicht genügend Sätze für eine zuverlässige Duplikatsprüfung gefunden.")


    card.add_category(content_category)

    # --- Links Category ---
    links_category = Category('Verlinkung (Intern & Extern)')
    all_links = soup.find_all('a', href=True)
    # Ensure URL has scheme for proper comparison; use base domain check for internal links
    base_url = url.split('//')[-1].split('/')[0]
    formatted_url_no_scheme = base_url.replace("www.", "") # Normalize www

    internal_links = []
    external_links = []

    for link in all_links:
        href = link['href'].strip()
        if not href or href.startswith(('#', 'mailto:', 'tel:')):
            continue # Skip anchor links, mailto, tel

        # Check if internal: starts with /, ., or contains own domain (more robust check)
        is_internal = False
        if href.startswith(('/', '.')):
             is_internal = True
        elif '://' in href:
            link_domain = href.split('//')[-1].split('/')[0].replace("www.", "") # Normalize www for comparison
            if link_domain == formatted_url_no_scheme:
                is_internal = True
        # Consider URLs without scheme as internal if they don't look like external domains
        elif not (href.startswith('http:') or href.startswith('https:')) and '.' not in href.split('/')[0]:
             is_internal = True


        if is_internal:
            internal_links.append(link)
        else: # Assume external if it has a scheme and different domain, or just looks like an external domain
            external_links.append(link)


    # --- Internal Links Analysis ---
    internal_link_count = len(internal_links)
    links_category.add_content(internal_link_count > 0, f"Anzahl interner Links: {internal_link_count}")

    if internal_link_count > 0:
        long_internal_link_texts = [link.text for link in internal_links if len(link.text.strip()) > MAX_LINK_TEXT_LENGTH]
        has_long_internal_link_texts = len(long_internal_link_texts) > 0
        links_category.add_content(not has_long_internal_link_texts, get_internal_length_linktext_text(has_long_internal_link_texts))
        if has_long_internal_link_texts:
             links_category.add_content("improvement", f"Einige interne Linktexte sind sehr lang (>{MAX_LINK_TEXT_LENGTH} Zeichen). Halten Sie Linktexte prägnant und aussagekräftig.")

        internal_links_without_text = [link for link in internal_links if not link.text.strip()]
        has_internal_links_without_text = len(internal_links_without_text) > 0
        links_category.add_content(not has_internal_links_without_text, get_internal_no_linktext_text(has_internal_links_without_text))
        if has_internal_links_without_text:
             links_category.add_content("improvement", "Einige interne Links haben keinen Text oder nur Leerraum. Stellen Sie sicher, dass alle Links sichtbaren, beschreibenden Text haben.")

        internal_link_texts = [link.text.strip().lower() for link in internal_links if link.text.strip()]
        has_duplicate_internal_link_texts = False
        if len(internal_link_texts) > 0:
            has_duplicate_internal_link_texts = len(internal_link_texts) != len(set(internal_link_texts))
        links_category.add_content(not has_duplicate_internal_link_texts, get_internal_linktext_repetitions_text(has_duplicate_internal_link_texts))
        if has_duplicate_internal_link_texts:
            links_category.add_content("improvement", "Es gibt interne Links mit identischem Linktext, die auf unterschiedliche Ziele zeigen könnten. Variieren Sie Linktexte, um den Kontext besser zu beschreiben.")


    # --- External Links Analysis ---
    external_link_count = len(external_links)
    links_category.add_content(True, f"Anzahl externer Links: {external_link_count}") # Always add count info

    if external_link_count > 0:
        long_external_link_texts = [link.text for link in external_links if len(link.text.strip()) > MAX_LINK_TEXT_LENGTH]
        has_long_external_link_texts = len(long_external_link_texts) > 0
        links_category.add_content(not has_long_external_link_texts, get_external_length_linktext_text(has_long_external_link_texts))
        # Improvement suggestion might depend on context for external links length

        external_links_without_text = [link for link in external_links if not link.text.strip()]
        has_external_links_without_text = len(external_links_without_text) > 0
        links_category.add_content(not has_external_links_without_text, get_external_no_linktext_text(has_external_links_without_text))
        if has_external_links_without_text:
            links_category.add_content("improvement", "Einige externe Links haben keinen Text. Geben Sie allen Links beschreibenden Text.")


        external_link_texts = [link.text.strip().lower() for link in external_links if link.text.strip()]
        has_duplicate_external_link_texts = False
        if len(external_link_texts) > 0:
            has_duplicate_external_link_texts = len(external_link_texts) != len(set(external_link_texts))
        links_category.add_content(not has_duplicate_external_link_texts, get_external_linktext_repetitions_text(has_duplicate_external_link_texts))
        # Improvement suggestion might depend on context for duplicate external links


    card.add_category(links_category)

    return card

# ---------------------------------------------------------------------------- #

def build_technical_seo_card(soup: BeautifulSoup, url: str, response: requests.Response) -> Card:
    """
    Builds the Technical SEO card, analyzing image formats, robots.txt, sitemap,
    redirects (HTTP->HTTPS, www), and compression.

    Args:
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page.
        response (requests.Response): The response object from the initial request to the URL.

    Returns:
        Card: A Card object populated with technical SEO categories and results.
    """
    card = Card('Technische SEO')

    # --- Image Formats Category ---
    image_format_category = Category('Moderne Bildformate')
    images = soup.find_all('img')
    uses_legacy_formats = any(
        img.get('src', '').lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        for img in images if img.get('src') # Ensure src exists
    )
    uses_modern_formats = any(
         img.get('src', '').lower().endswith(('.webp', '.avif', '.svg')) # Added SVG
         for img in images if img.get('src')
    )

    if uses_modern_formats and not uses_legacy_formats:
         image_format_category.add_content(True, "Moderne Bildformate (WebP, AVIF, SVG) werden verwendet.")
    elif uses_modern_formats and uses_legacy_formats:
         image_format_category.add_content(True, "Es werden sowohl moderne als auch ältere Bildformate (JPG, PNG) genutzt.")
         image_format_category.add_content("improvement", "Erwägen Sie, alle Bilder in moderne Formate (WebP, AVIF) zu konvertieren, um Ladezeiten weiter zu optimieren.")
    elif not uses_modern_formats and uses_legacy_formats:
        image_format_category.add_content(False, "Es wurden Bilder in älteren Formaten (JPG, PNG, GIF) gefunden.")
        image_format_category.add_content("improvement", "Verwenden Sie moderne Bildformate wie WebP oder AVIF. Sie bieten bessere Kompression bei hoher Qualität und beschleunigen das Laden der Seite erheblich.")
    else:
         image_format_category.add_content(True, "Keine gängigen Bildformate (JPG, PNG, GIF, WebP, AVIF, SVG) in `<img>`-Tags gefunden oder keine Bilder vorhanden.")

    card.add_category(image_format_category)


    # --- Robots.txt and Sitemap Category ---
    robots_category = Category('Robots.txt & Sitemap')
    # Extract base domain robustly
    try:
        domain_parts = url.split('//')
        base_domain = (domain_parts[1] if len(domain_parts) > 1 else domain_parts[0]).split('/')[0].split(':')[0]
    except IndexError:
        base_domain = None # Handle cases where URL parsing fails unexpectedly

    robots_found = False
    robots_url_checked = "N/A"
    sitemap_in_robots = None # Store URL found in robots.txt
    robots_content = ""

    if base_domain:
        # Check both http and https, prefer https if original url is https
        schemes_to_check = ['https', 'http'] if url.startswith('https') else ['http', 'https']
        for scheme in schemes_to_check:
            robots_url = f"{scheme}://{base_domain}/robots.txt"
            robots_url_checked = robots_url
            try:
                # Use HEAD request first? Maybe not, need content for sitemap.
                response_robots = requests.get(robots_url, timeout=10, allow_redirects=False) # Don't follow redirects for robots.txt
                if response_robots.status_code == 200:
                    robots_found = True
                    robots_content = response_robots.text
                    # Look for Sitemap directive (case-insensitive)
                    for line in robots_content.splitlines():
                        if line.strip().lower().startswith("sitemap:"):
                            sitemap_in_robots = line.split(":", 1)[1].strip()
                            break # Found first sitemap directive
                    break # Stop checking schemes once found
            except requests.exceptions.RequestException:
                continue # Try next scheme or fail silently

    robots_category.add_content(robots_found, f"Robots.txt gefunden unter {robots_url_checked}" if robots_found else f"Keine Robots.txt unter http(s)://{base_domain}/robots.txt gefunden.")
    if not robots_found and base_domain:
        robots_category.add_content("improvement", "Erstellen Sie eine `robots.txt`-Datei im Hauptverzeichnis Ihrer Domain, um Suchmaschinen-Crawlern Anweisungen zu geben.")

    # Sitemap Check
    sitemap_found = False
    sitemap_url_checked = "N/A"

    if sitemap_in_robots:
        sitemap_found = True
        sitemap_url_checked = sitemap_in_robots
        robots_category.add_content(True, f"Sitemap in Robots.txt deklariert: {sitemap_url_checked}")
        # Optional: Add a check if this sitemap URL is actually reachable
        try:
            response_sitemap = requests.head(sitemap_url_checked, timeout=10)
            if response_sitemap.status_code != 200:
                 robots_category.add_content(False, f"Warnung: Die in robots.txt deklarierte Sitemap ({sitemap_url_checked}) ist nicht erreichbar (Status: {response_sitemap.status_code}).")
                 robots_category.add_content("improvement", "Stellen Sie sicher, dass die in robots.txt angegebene Sitemap-URL korrekt und erreichbar ist.")

        except requests.exceptions.RequestException:
             robots_category.add_content(False, f"Warnung: Fehler beim Prüfen der Erreichbarkeit der Sitemap ({sitemap_url_checked}) aus robots.txt.")


    elif base_domain: # Only check common locations if not found in robots.txt
        common_sitemap_paths = ["/sitemap.xml", "/sitemap_index.xml"]
        schemes_to_check = ['https', 'http'] if url.startswith('https') else ['http', 'https']
        for path in common_sitemap_paths:
            for scheme in schemes_to_check:
                sitemap_url = f"{scheme}://{base_domain}{path}"
                sitemap_url_checked = sitemap_url
                try:
                    # Use HEAD request for faster check
                    response_sitemap = requests.head(sitemap_url, timeout=10, allow_redirects=True) # Allow redirects for sitemap
                    if response_sitemap.status_code == 200:
                        sitemap_found = True
                        break # Stop checking schemes/paths
                except requests.exceptions.RequestException:
                    continue # Try next scheme/path or fail silently
            if sitemap_found: break # Stop checking paths

        robots_category.add_content(sitemap_found, f"Sitemap an Standardorten gefunden ({sitemap_url_checked})" if sitemap_found else "Keine Sitemap an Standardorten (sitemap.xml, sitemap_index.xml) gefunden.")
        if not sitemap_found:
             robots_category.add_content("improvement", "Erstellen Sie eine Sitemap (z.B. sitemap.xml) und reichen Sie diese bei Suchmaschinen ein. Deklarieren Sie den Pfad idealerweise auch in Ihrer robots.txt.")
    else:
         robots_category.add_content(False, "Sitemap-Prüfung übersprungen, da Basis-Domain nicht ermittelt werden konnte.")


    card.add_category(robots_category)


    # --- Redirects Category ---
    redirects_category = Category('Weiterleitungen & HTTPS')
    has_redirects = bool(response.history) # response is the final response after following redirects

    if has_redirects:
        first_redirect = response.history[0]
        initial_url = first_redirect.url
        final_url = response.url # The URL after all redirects

        # Check for HTTP -> HTTPS redirect
        is_http_request = initial_url.startswith("http://")
        is_final_url_https = final_url.startswith("https://")
        # Check if the domain/path stayed roughly the same
        initial_url_no_scheme = initial_url.split("://", 1)[-1]
        final_url_no_scheme = final_url.split("://", 1)[-1]
        is_domain_path_same = initial_url_no_scheme == final_url_no_scheme

        if is_http_request and is_final_url_https and is_domain_path_same:
            redirects_category.add_content(True, f"Korrekte Weiterleitung von HTTP zu HTTPS ({initial_url} -> {final_url}) erkannt.")
        else:
            # Describe the redirect chain simply
            redirect_chain = ' -> '.join([r.url for r in response.history] + [response.url])
            redirects_category.add_content(False, f"Weiterleitung erkannt: {redirect_chain}.")
            redirects_category.add_content("improvement", "Es finden Weiterleitungen statt. Stellen Sie sicher, dass diese notwendig sind und korrekt (Status 301 für permanente) implementiert wurden. Zu viele oder unnötige Weiterleitungen können die Ladezeit erhöhen.")

    else: # No redirects followed by the requests library
         redirects_category.add_content(True, "Keine Weiterleitungen beim Abruf der URL festgestellt.")


    # HTTPS Usage Check (based on final URL)
    if not response.url.startswith("https://"):
         redirects_category.add_content(False, "Die finale URL verwendet kein HTTPS.")
         redirects_category.add_content("improvement", "Stellen Sie Ihre gesamte Website auf HTTPS um. Es ist ein wichtiger Rankingfaktor und schafft Vertrauen bei Nutzern.")
    else:
        # If original request was HTTP but final is HTTPS, it was handled above.
        # If original was HTTPS and final is HTTPS, it's good.
        if url.startswith("https://"):
             redirects_category.add_content(True, "Die Seite wird korrekt über HTTPS ausgeliefert.")

    https_or_https = url.split('://')[0] if '://' in url else 'http' # Default to http if no scheme
    # Check www vs non-www consistency (simple check: request opposite)
    if base_domain:
        opposite_url = None
        if base_domain.startswith("www."):
            opposite_domain = base_domain[4:]
            opposite_url = f"{https_or_https}://{opposite_domain}{url.split(base_domain)[-1]}" # Reconstruct path/query
        else:
            opposite_domain = f"www.{base_domain}"
            opposite_url = f"{https_or_https}://{opposite_domain}{url.split(base_domain)[-1]}"

        redirecting_www_correctly = False
        www_check_message = "WWW/Non-WWW Konsistenz konnte nicht geprüft werden."
        if opposite_url:
            try:
                response_opposite = requests.get(opposite_url, timeout=10, allow_redirects=True) # Allow redirects here
                # Check if final URL after potential redirect matches the *original* request's final URL
                if response_opposite.url == response.url:
                     redirecting_www_correctly = True
                     www_check_message = get_redirecting_www_text(False) # Text function expects boolean indicating if *both* are accessible
                else:
                     # Both versions might be live without redirecting to a canonical one
                     redirecting_www_correctly = False
                     www_check_message = get_redirecting_www_text(True) # True means both accessible without redirect to one

            except requests.exceptions.RequestException:
                 www_check_message = "Fehler beim Prüfen der WWW/Non-WWW-Weiterleitung."
                 redirecting_www_correctly = False # Treat error as non-compliant

            redirects_category.add_content(redirecting_www_correctly, www_check_message)
            if not redirecting_www_correctly:
                 redirects_category.add_content("improvement", "Stellen Sie sicher, dass nur eine Version (entweder mit www oder ohne www) erreichbar ist und die andere Version per 301-Redirect darauf weiterleitet, um Duplicate Content zu vermeiden.")

    card.add_category(redirects_category)

    # --- Compression Category ---
    compression_category = Category('Compression')
    content_encoding = response.headers.get('Content-Encoding')

    # Mapping of encodings to readable names
    encoding_names = {
        'br': 'Brotli (br)',
        'gzip': 'Gzip (gzip)',
        'deflate': 'Deflate (deflate)'
    }

    # Check if compression is used
    uses_compression = content_encoding in encoding_names
    compression_type = encoding_names.get(content_encoding, f"Unknown ({content_encoding})" if content_encoding else 'None')

    # Add content to the category
    compression_category.add_content(uses_compression, get_compression_text(compression_type, uses_compression))

    # Suggest improvement if no compression is used
    if not uses_compression:
        compression_category.add_content(
            "improvement",
            "Enable server-side compression (e.g., Gzip or Brotli). "
            "This significantly reduces the file size of HTML, CSS, and JavaScript, speeding up load times."
        )

    card.add_category(compression_category)

    return card

# ---------------------------------------------------------------------------- #

def build_ai_card(soup: BeautifulSoup) -> Card:
    """
    Builds the AI Analysis card by sending title and description to an AI analyzer.

    Args:
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.

    Returns:
        Card: A Card object populated with AI analysis results for title and description.
              Returns a card with error messages if AI analysis fails.
    """
    card = Card('KI - Analyse')

    # Extract Title and Description safely
    title_text = soup.title.string.strip() if soup.title and soup.title.string else ""
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description_content = description_tag.get('content', '').strip() if description_tag else ""

    # Check if sufficient data is available for AI analysis
    if not title_text and not description_content:
        error_category = Category("Fehlende Daten")
        error_category.add_content(False, "Kein Titel oder Beschreibung für die KI-Analyse gefunden.")
        card.add_category(error_category)
        return card
    elif not title_text:
         ai_title_category = Category('Titel (Fehlend)')
         ai_title_category.add_content(False, "Kein Titel für die KI-Analyse gefunden.")
         card.add_category(ai_title_category)
    elif not description_content:
         ai_description_category = Category('Beschreibung (Fehlend)')
         ai_description_category.add_content(False, "Keine Beschreibung für die KI-Analyse gefunden.")
         card.add_category(ai_description_category)


    try:
        # Run the asynchronous AI analyzer function
        # Ensure event loop management if running within a sync context
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError: # 'RuntimeError: There is no current event loop...'
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        ai_results = loop.run_until_complete(ai_analyzer(description_content, title_text))

        # --- AI Description Category ---
        # Only add if description was present
        if description_content:
            ai_description_category = Category('KI-Analyse: Beschreibung')
            ai_description_category.add_content("", f'Original: "{description_content}"') # Show original
            # Check if keys exist in results before accessing
            desc_rating = ai_results.get('description_rating', 0)
            desc_reason = ai_results.get('description_reason', 'Keine Begründung erhalten.')
            desc_improvement = ai_results.get('description_improvement', 'Kein Verbesserungsvorschlag erhalten.')

            is_desc_good = desc_rating >= AI_RATING_THRESHOLD
            ai_description_category.add_content(is_desc_good, f"Bewertung: {desc_rating}/100. {desc_reason}")
            if not is_desc_good or "Kein Verbesserungsvorschlag" not in desc_improvement : # Show improvement if score is low OR if suggestion exists
                ai_description_category.add_content("improvement", f"Vorschlag: {desc_improvement}")
            card.add_category(ai_description_category)

        # --- AI Title Category ---
        # Only add if title was present
        if title_text:
            ai_title_category = Category('KI-Analyse: Titel')
            ai_title_category.add_content("", f'Original: "{title_text}"') # Show original
            # Check if keys exist in results before accessing
            title_rating = ai_results.get('title_rating', 0)
            title_reason = ai_results.get('title_reason', 'Keine Begründung erhalten.')
            title_improvement = ai_results.get('title_improvement', 'Kein Verbesserungsvorschlag erhalten.')

            is_title_good = title_rating >= AI_RATING_THRESHOLD
            ai_title_category.add_content(is_title_good, f"Bewertung: {title_rating}/100. {title_reason}")
            if not is_title_good or "Kein Verbesserungsvorschlag" not in title_improvement: # Show improvement if score is low OR if suggestion exists
                ai_title_category.add_content("improvement", f"Vorschlag: {title_improvement}")
            card.add_category(ai_title_category)

    except Exception as e:
        # Catch potential errors during the async call or processing
        error_category = Category("Fehler bei KI-Analyse")
        error_category.add_content(False, f"Die KI-Analyse konnte nicht durchgeführt werden: {e}")
        card.add_category(error_category)

    return card

# ############################################################################ #
#                              HELPER FUNCTIONS                              #
# ############################################################################ #

def build_not_available_card(title: str, category_title: str, message: str) -> Card:
    """
    Creates a placeholder Card indicating a feature is not available.

    Used for premium features when accessed by non-premium users.

    Args:
        title (str): The main title for the Card.
        category_title (str): The title for the single Category within the card.
        message (str): The message to display within the category, explaining
                       why the feature is not available.

    Returns:
        Card: A Card object configured with the provided unavailable message.
    """
    card = Card(title)
    category = Category(category_title)
    # Using "improvement" type might not be semantically correct here,
    # but aligns with how Card might display messages marked as "improvement".
    # Consider adding a dedicated message type if needed in Card model.
    category.add_content("improvement", message)
    card.add_category(category)
    return card

# ---------------------------------------------------------------------------- #

def build_serp_preview(soup: BeautifulSoup, url: str, response: requests.Response) -> dict:
    """
    Generates data for a Search Engine Results Page (SERP) preview.

    Extracts title and description and calculates a simple points score based on
    their presence and length.

    Note: Pixel length calculations for SERP are approximate.

    Args:
        soup (BeautifulSoup): The parsed HTML content of the analyzed page.
        url (str): The URL of the analyzed page.
        response (requests.Response): The response object (currently unused here,
                                      but kept for signature consistency if needed later).

    Returns:
        dict: A dictionary containing SERP preview data (title, description, url)
              for mobile/desktop and a calculated points score. Structure includes:
              {'isCard': False, 'serp_mobile': {...}, 'serp_desktop': {...}, 'points': int}
    """
    # Extract Title and Description safely
    title = soup.title.string.strip() if soup.title and soup.title.string else "Kein Titel gefunden"
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag.get('content', '').strip() if description_tag else "Keine Beschreibung gefunden."

    serp_points = 0
    title_length = len(title)
    desc_length_chars = len(description)
    # Use different pixel width constant for SERP preview if needed
    desc_length_px = round(desc_length_chars * SERP_DESC_AVG_CHAR_WIDTH_PX)

    # Points for Title
    if title != "Kein Titel gefunden":
        serp_points += 5 # Base points for having a title
        if SERP_TITLE_MIN_LENGTH <= title_length <= SERP_TITLE_MAX_LENGTH:
            serp_points += 45 # Optimal length
        elif SERP_TITLE_ACCEPTABLE_MIN <= title_length < SERP_TITLE_MIN_LENGTH:
            serp_points += 20 # A bit short but acceptable
        elif SERP_TITLE_MAX_LENGTH < title_length < SERP_TITLE_ACCEPTABLE_MAX:
             serp_points += 20 # A bit long (truncated) but acceptable

    # Points for Description
    if description != "Keine Beschreibung gefunden.":
        serp_points += 5 # Base points for having a description
        if SERP_DESC_MIN_LENGTH_PX <= desc_length_px <= SERP_DESC_MAX_LENGTH_PX:
             serp_points += 45 # Optimal length
        elif SERP_DESC_ACCEPTABLE_MIN_PX <= desc_length_px < SERP_DESC_MIN_LENGTH_PX:
             serp_points += 20 # Short but acceptable
        elif SERP_DESC_MAX_LENGTH_PX < desc_length_px < SERP_DESC_ACCEPTABLE_MAX_PX:
             serp_points += 20 # Long (truncated) but acceptable


    # Ensure points don't exceed 100 if logic changes
    serp_points = min(serp_points, 100)

    serp_preview_data = {
        'isCard': False, # Indicates this is not a standard Card object for frontend
        'serp_mobile': {'url': url, 'title': title, 'description': description},
        'serp_desktop': {'url': url, 'title': title, 'description': description},
        "points": serp_points,
    }
    return serp_preview_data

# ---------------------------------------------------------------------------- #

def build_overall_results(results: dict) -> dict:
    """
    Calculates the overall rating and improvement count based on the generated cards.

    Args:
        results (dict): The dictionary containing all the generated card results.
                        It expects card data produced by `Card.add_to_results`.

    Returns:
        dict: A dictionary containing the overall score, score text,
              improvement count, and improvement text. Structure includes:
              {'isCard': False, 'overall_rating': int, 'overall_rating_text': str,
               'improvement_count': int, 'improvement_count_text': str}
    """
    # Filter out non-card entries like SERP preview before calculation
    card_results = {k: v for k, v in results.items() if isinstance(v, dict) and v.get('isCard', True)}

    overall_rating = calculate_overall_points(card_results)
    improvement_count = calculate_improvement_count(card_results)

    return {
        'isCard': False, # Indicates this is not a standard Card object for frontend
        'overall_rating': overall_rating,
        'overall_rating_text': get_overall_rating_text(overall_rating),
        'improvement_count': improvement_count,
        'improvement_count_text': get_improvement_count_text(improvement_count),
    }

# ############################################################################ #
#                                END OF SCRIPT                                 #
# ############################################################################ #