from text_snippet_functions import (
    get_hierarchy_text, get_improvement_count_text, get_overall_rating_text, get_title_incorrect_length_text, get_title_missing_improvement_text, get_title_word_repetitions_improvement_text, get_title_missing_text,
    get_domain_in_title_text, get_title_length_text, get_title_word_repetitions_text, get_description_missing_text,
    get_description_length_text, get_language_comment, get_favicon_included_text, get_comparison_title_text,
    get_content_length_comment, get_duplicate_text, get_alt_attributes_missing_text, get_h1_heading_text, get_structure_text,
    get_internal_length_linktext_text, get_internal_no_linktext_text, get_internal_linktext_repetitions_text,
    get_external_length_linktext_text, get_external_no_linktext_text, get_external_linktext_repetitions_text, get_redirecting_www_text, get_compression_text
)
from models import Card, Category, calculate_improvement_count, calculate_overall_points
from ai_analyzer import ai_analyzer
import requests
import socket
from langdetect import detect_langs, DetectorFactory
import asyncio
import dotenv
import os

dotenv.load_dotenv() 

def build_all_cards(results, soup, url, response):
    """
    Builds and adds all the card sections to the results.
    This function delegates to smaller helper functions for each card.
    """

    # Core Web Vitals Card
    core_web_vitals_card = build_core_web_vitals_card(url)
    core_web_vitals_card.add_to_results(results)
    
    # Technical SEO Card
    technicalseo_card = build_technicalseo_card(soup, url, response)
    technicalseo_card.add_to_results(results)
    
    # Metadata Card
    metadata_card = build_metadata_card(soup, url)
    metadata_card.add_to_results(results)
    
    # AI Analysis Card
    ai_results_card = build_ai_card(soup)
    ai_results_card.add_to_results(results)

    # Page Quality Card
    pagequality_and_links_card = build_pagequality_and_links_card(soup, url)
    pagequality_and_links_card.add_to_results(results)
    
    
def build_core_web_vitals_card(url):
    
    card = Card('Core Web Vitals')

    api_key = os.getenv("GOOGLE_PAGESPEED_API_KEY")
    
    params = {
        "url": url,
        "key": api_key,
        "strategy": "desktop"
    }

    response = requests.get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed', params=params)
    
    if response.status_code == 200:
        data = response.json()
        lighthouse_metrics = data.get("lighthouseResult", {}).get("audits", {})
        lcp_category = Category('Largest Contentful Paint')
        fcp_category = Category('First Contentful Paint')
        tbt_category = Category('Total Blocking Time')
        cls_category = Category('Cumulative Layout Shift')
        speed_index_category = Category('Speed Index')

        lcp_category.add_content(float(lighthouse_metrics.get("largest-contentful-paint", {}).get("numericValue", float('inf'))) / 1000 <= 2.5, f"Die Ladezeit der größten sichtbaren Komponente auf der Seite beträgt {lighthouse_metrics.get('largest-contentful-paint', {}).get('displayValue', 'N/A')} Sekunden.")
        fcp_category.add_content(float(lighthouse_metrics.get("first-contentful-paint", {}).get("numericValue", float('inf'))) / 1000 <= 1.8, f"Die Ladezeit der ersten sichtbaren Komponente auf der Seite beträgt {lighthouse_metrics.get('first-contentful-paint', {}).get('displayValue', 'N/A')} Sekunden.")
        tbt_category.add_content(float(lighthouse_metrics.get("total-blocking-time", {}).get("numericValue", float('inf'))) <= 200, f"Die Zeit, die durch blockierende Ressourcen verloren geht, beträgt {lighthouse_metrics.get('total-blocking-time', {}).get('displayValue', 'N/A')} Millisekunden.")
        cls_category.add_content(float(lighthouse_metrics.get("cumulative-layout-shift", {}).get("numericValue", float('inf'))) <= 0.1, f"Die visuelle Stabilität der Seite während des Ladens beträgt {lighthouse_metrics.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')}.")
        speed_index_category.add_content(float(lighthouse_metrics.get("speed-index", {}).get("numericValue", float('inf'))) / 1000 <= 4.3, f"Die Geschwindigkeit, mit der der sichtbare Inhalt geladen wird, beträgt {lighthouse_metrics.get('speed-index', {}).get('displayValue', 'N/A')} Sekunden.")
        
        card.add_category(lcp_category)
        card.add_category(fcp_category)
        card.add_category(tbt_category)
        card.add_category(cls_category)
        card.add_category(speed_index_category)
    else:
        error_category = Category('Error')
        error_category.add_content(False, 'Es ist ein Fehler bei dem Abrufen der Core Web Vitals aufgetreten. Bitte entschuldigen Sie die Unannehmlichkeiten.')
    
    return card

def build_metadata_card(soup, url):
    card = Card('Metadaten')
    
    # Titel Category
    title_category = Category('Titel')
    title_missing = (soup.title is None or not soup.title.string.strip())
    title_category.add_content(not title_missing, get_title_missing_text(title_missing))
    if title_missing:
        title_category.add_content("improvement", get_title_missing_improvement_text())
    else:
        title_text = soup.title.string
        title_category.add_content('', title_text)
        title_category.add_content(url not in title_text, get_domain_in_title_text(url in title_text))
        title_correct_length_bool = 50 <= len(title_text) <= 60
        title_category.add_content(title_correct_length_bool, get_title_length_text(len(title_text)))
        if not title_correct_length_bool:
            title_category.add_content("improvement", get_title_incorrect_length_text(len(title_text)))
        title_words = title_text.split()
        repeated_words = [word for word in set(title_words) if title_words.count(word) > 1]
        title_word_repetition_bool = len(repeated_words) > 0
        title_category.add_content(not title_word_repetition_bool, get_title_word_repetitions_text(title_word_repetition_bool))
        if title_word_repetition_bool:
            title_category.add_content("improvement", get_title_word_repetitions_improvement_text(', '.join(repeated_words)))
    card.add_category(title_category)
    
    # Beschreibung Category
    description_category = Category('Beschreibung')
    description_content = next((meta.get('content', '').strip() for meta in soup.find_all('meta', attrs={'name': 'description'}) if meta.get('content', '').strip()), "")
    description_missing = not bool(description_content)
    description_category.add_content(not description_missing, get_description_missing_text(description_missing))
    if description_content:
        description_category.add_content('', description_content)
        desc_length_px = round(len(description_content) * 6.19)
        description_category.add_content(300 <= desc_length_px <= 960, get_description_length_text(desc_length_px))
    card.add_category(description_category)

    # Rich Snippets & Rich Results
    rich_snippets_category = Category('Rich Snippets')
    rich_snippets = soup.find_all(attrs={"itemtype": True})
    rich_snippets_used = len(rich_snippets) > 0
    rich_snippets_category.add_content(rich_snippets_used, "Die Webseite verwendet Rich Snippets." if rich_snippets_used else "Die Webseite verwendet keine Rich Snippets.")
    if rich_snippets_used:
        for snippet in rich_snippets:
            itemprops = snippet.find_all(attrs={"itemprop": True})
            itemprops_text = ', '.join([itemprop.get('itemprop') for itemprop in itemprops])
            rich_snippets_category.add_content('', f"Gefundenes Snippet: {snippet.get('itemtype')}, mit itemprops: {itemprops_text}")
    else:
        rich_snippets_category.add_content("improvement", f"Es wurden keine Rich Snippets oder Rich Results gefunden. Möglicherweise sind diese nur auf spezifischen Produktseiten o. Ä. vorhanden, in dieser Analyse wurde lediglich die Seite {url} analysiert.")
    card.add_category(rich_snippets_category)

    # Sprache Category
    language_category = Category('Sprache')
    meta_lang = soup.find('meta', attrs={'name': 'language'}) or soup.html.get('lang') or 'Unbekannt'
    language_category.add_content('', 'Meta/HTML-Sprache: ' + meta_lang)
    
    # langdetect is not deterministic by default, so we set a seed to make it deterministic
    DetectorFactory.seed = 0
    detected_languages_with_probabilities = detect_langs(soup.get_text())
    detected_languages_with_probability = detected_languages_with_probabilities[0]
    detected_lang = detected_languages_with_probability.lang
    detected_lang_probability = detected_languages_with_probability.prob
    language_category.add_content('', 'Im Text erkannte Sprache: ' + detected_lang + f' (mit {detected_lang_probability:.2%} Wahrscheinlichkeit)')

    try:
        domain = url.split('/')[2] if '//' in url else url.split('/')[0]
        ip = socket.gethostbyname(domain)
        server_location = requests.get(f"http://ip-api.com/json/{ip}").json().get('country', 'Unbekannt')
    except Exception:
        server_location = 'Unbekannt'
    language_category.add_content('', 'Serverstandort: ' + server_location)
    language_category.add_content(detected_lang in meta_lang, get_language_comment(meta_lang, detected_lang))
    if detected_lang not in meta_lang:
        language_category.add_content("improvement", "Hinweis: Unser Spracherkennungssystem kann auch falsch liegen. Bitte stellen Sie sicher, dass die im Meta-Tag angegebene Sprache auch der tatsächlichen Sprache des Inhalts entspricht.")
    card.add_category(language_category)

    # Check miscellaneous meta tags charset, content-type, canonical, viewport
    meta_tags_category = Category('Meta-Tags')

    # Charset
    charset_meta = soup.find('meta', attrs={'charset': True})
    charset_present = charset_meta is not None
    meta_tags_category.add_content(charset_present, f"Charset Meta-Tag vorhanden: {charset_meta['charset']}" if charset_present else "Charset Meta-Tag fehlt.")

    # Content-Type
    content_type_meta = soup.find('meta', attrs={'http-equiv': 'Content-Type'})
    content_type_present = content_type_meta is not None
    meta_tags_category.add_content(content_type_present, f"Content-Type Meta-Tag vorhanden: {content_type_meta['content']}" if content_type_present else "Content-Type Meta-Tag fehlt.")

    # Canonical
    canonical_meta = soup.find('link', attrs={'rel': 'canonical'})
    canonical_present = canonical_meta is not None
    meta_tags_category.add_content(canonical_present, f"Canonical Meta-Tag vorhanden: {canonical_meta['href']}" if canonical_present else "Canonical Meta-Tag fehlt.")

    # Viewport
    viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
    viewport_present = viewport_meta is not None
    meta_tags_category.add_content(viewport_present, f"Viewport Meta-Tag vorhanden: {viewport_meta['content']}" if viewport_present else "Viewport Meta-Tag fehlt.")

    card.add_category(meta_tags_category)
    # Favicon Category
    favicon_category = Category('Favicon')
    has_favicon = soup.find('link', attrs={'rel': 'icon'}) is not None
    favicon_category.add_content(has_favicon, get_favicon_included_text(has_favicon))
    card.add_category(favicon_category)
    
    return card

def build_pagequality_and_links_card(soup, url):
    card = Card('Inhalt und Verlinkung')
    
    # Bilder Category
    images_category = Category('Bilder')
    missing_alts = sum(1 for img in soup.find_all('img') if not img.get('alt') or not img.get('alt').strip())
    images_category.add_content(missing_alts == 0, get_alt_attributes_missing_text(missing_alts))
    if missing_alts > 0:
        images_category.add_content('improvement', "Fügen Sie Alt-Attribute zu allen Bildern hinzu! Sie verbessern damit die Barrierefreiheit Ihrer Website und helfen Suchmaschinen, den Bildinhalt zu verstehen. Das steigert sowohl die Nutzerfreundlichkeit als auch Ihr Ranking.")
    card.add_category(images_category)

    # Inhalt Category
    content_category = Category('Inhalt')
    title_text = soup.title.string if soup.title and soup.title.string.strip() else ""
    title_words = set(title_text.split())
    page_text_words = set(soup.get_text().split())
    content_category.add_content(not title_words.issubset(page_text_words), get_comparison_title_text(title_words.issubset(page_text_words)))
    word_count = len(soup.get_text().split())
    content_category.add_content(word_count >= 300, get_content_length_comment(word_count))
    
    sentences = [sentence.strip() for tag in ['p', 'div', 'span', 'li'] 
                    for element in soup.find_all(tag) 
                    for sentence in element.get_text().split('.') if sentence.strip()]
    duplicates = len(sentences) != len(set(sentences))
    content_category.add_content(duplicates, get_duplicate_text(duplicates))
    card.add_category(content_category)
    
    # Links Category
    links_category = Category('Verlinkung')
    
    # Internal links
    internal_links = [link for link in soup.find_all('a', href=True) if url in link['href']]
    links_category.add_content(all(len(link.text) < 30 for link in internal_links), get_internal_length_linktext_text(all(len(link.text) < 30 for link in internal_links)))
    no_text_internal = sum(1 for link in internal_links if not link.text.strip()) > 0
    links_category.add_content(not no_text_internal, get_internal_no_linktext_text(no_text_internal))
    duplicate_internal = len([link.text for link in internal_links]) != len(set([link.text for link in internal_links]))
    links_category.add_content(not duplicate_internal, get_internal_linktext_repetitions_text(duplicate_internal))
    
    # External links
    external_links = [link for link in soup.find_all('a', href=True) if url not in link['href']]
    links_category.add_content(all(len(link.text) < 30 for link in external_links), get_external_length_linktext_text(all(len(link.text) < 30 for link in external_links)))
    no_text_external = sum(1 for link in external_links if not link.text.strip()) > 0
    links_category.add_content(not no_text_external, get_external_no_linktext_text(no_text_external))
    duplicate_external = len([link.text for link in external_links]) != len(set([link.text for link in external_links]))
    links_category.add_content(not duplicate_external, get_external_linktext_repetitions_text(duplicate_external))
    
    card.add_category(links_category)
    
    return card

def build_technicalseo_card(soup, url, response):
    card = Card('Technische SEO')
    
    # Check for image formats
    images = soup.find_all('img')
    has_jpg_or_png = any(img.get('src', '').lower().endswith(('.jpg', '.jpeg', '.png')) for img in images)
    image_format_category = Category('Bildformate')
    image_format_category.add_content(not has_jpg_or_png, "Es wurden Bilder im JPG- oder PNG-Format gefunden." if has_jpg_or_png else "Es wurden keine Bilder im JPG- oder PNG-Format gefunden.")
    if has_jpg_or_png:
        image_format_category.add_content("improvement", "Es wird empfohlen, moderne Bildformate wie WebP oder AVIF zu verwenden, um die Ladezeiten zu optimieren.")
    card.add_category(image_format_category)


    # Extract the base domain
    base_domain = url.split('//')[-1].split('/')[0]
    print(base_domain)

    # Check for robots.txt
    robots_category = Category('Robots.txt')
    possible_robots_urls = [
        f"http://{base_domain}/robots.txt",
        f"https://{base_domain}/robots.txt"
    ]
    robots_found = False
    sitemap_found_in_robots = False
    sitemap_url_from_robots = ""
    for robots_url in possible_robots_urls:
        try:
            response_robots = requests.get(robots_url)
            if response_robots.status_code == 200:
                robots_found = True
                robots_content = response_robots.text
                if "Sitemap:" in robots_content:
                    sitemap_url_from_robots = robots_content.split("Sitemap:")[1].strip().split()[0]
                    sitemap_found_in_robots = True
                break
        except Exception:
            continue
    robots_category.add_content(robots_found, f"Robots.txt gefunden unter {robots_url}" if robots_found else "Keine Robots.txt gefunden.")
    card.add_category(robots_category)

    # Check for sitemap
    sitemap_category = Category('Sitemap')
    if sitemap_found_in_robots:
        sitemap_found = True
        sitemap_url = sitemap_url_from_robots
    else:
        possible_sitemap_urls = [
            f"http://{base_domain}/sitemap.xml",
            f"https://{base_domain}/sitemap.xml",
            f"http://{base_domain}/sitemap_index.xml",
            f"https://{base_domain}/sitemap_index.xml"
        ]
        sitemap_found = False
        for sitemap_url in possible_sitemap_urls:
            try:
                response_sitemap = requests.get(sitemap_url)
                if response_sitemap.status_code == 200:
                    sitemap_found = True
                    break
            except Exception:
                continue
    sitemap_category.add_content(sitemap_found, f"Sitemap gefunden unter {sitemap_url}" if sitemap_found else "Keine Sitemap gefunden.")
    card.add_category(sitemap_category)
    card.add_category(robots_category)

    redirects_category = Category('Weiterleitungen')
    has_redirects = bool(response.history)
    if has_redirects:
        last_redirect_url = response.history[-1].headers.get('Location', '')
        https_url = url.replace("http://", "https://")
        redirects_to_https = last_redirect_url == https_url
        if redirects_to_https:
            redirects_category.add_content(True, "Es erfolgt eine Weiterleitung von HTTP zu HTTPS. Dies ist eine empfohlene Best Practice, da verschlüsselte Verbindungen die Sicherheit und Vertrauenswürdigkeit der Website verbessern.")
        else:
            redirects_category.add_content(False, f"Die Seite leitet zu {last_redirect_url} weiter. Eine automatische Weiterleitung auf eine andere Seite hat negative Auswirkungen auf das SEO-Ranking, da Suchmaschinen Weiterleitungen als irreführend betrachten.")
    else:
        redirects_category.add_content(True, "Es erfolgt keine Weiterleitung auf eine andere Webseite.")

    # Check www-redirect (simplified check)
    www_url = url.replace("http://", "http://www.")
    try:
        response_www = requests.get(www_url)
        redirecting_www = response.status_code == 200 and response_www.status_code == 200
    except Exception:
        redirecting_www = False
    redirects_category.add_content(redirecting_www, get_redirecting_www_text(redirecting_www))
    card.add_category(redirects_category)
    
    compression_category = Category('Komprimierung')
    compression = response.headers.get('Content-Encoding')
    compression_category.add_content(compression is not None, get_compression_text(compression, compression is not None))
    card.add_category(compression_category)
    
    return card

def build_ai_card(soup):
    card = Card('KI - Analyse')
    description = next((meta.get('content', '').strip() for meta in soup.find_all('meta', attrs={'name': 'description'}) if meta.get('content', '').strip()), "")
    title_text = soup.title.string if soup.title and soup.title.string.strip() else ""
    ai_results = asyncio.run(ai_analyzer(description, title_text))
    
    # AI Description Category
    ai_description_category = Category('Beschreibung')
    ai_description_category.add_content("", description)
    ai_description_category.add_content(ai_results['description_rating'] >= 80, ai_results['description_reason'])
    ai_description_category.add_content("improvement", ai_results['description_improvement'])
    card.add_category(ai_description_category)
    
    # AI Title Category
    ai_title_category = Category('Titel')
    ai_title_category.add_content("", title_text)
    ai_title_category.add_content(ai_results['title_rating'] >= 80, ai_results['title_reason'])
    ai_title_category.add_content("improvement", ai_results['title_improvement'])
    card.add_category(ai_title_category)
    
    return card

def build_serp_preview(soup, url, response):
    # Simplified SERP preview builder – adjust as needed.
    title_text = soup.title.string if soup.title and soup.title.string.strip() else ""
    description = next((meta.get('content', '').strip() for meta in soup.find_all('meta', attrs={'name': 'description'}) if meta.get('content', '').strip()), "")
    
    serp_points = 0

    desc_length_px = round(len(description) * 6.11)
    if 110 <= desc_length_px <= 165:
        serp_points += 25
    if 100 <= desc_length_px <= 120:
        serp_points += 25
    if 30 <= desc_length_px <= 60:
        serp_points += 50
    
    serp_preview = {
        'isCard': False,
        'serp_mobile': {'url': url, 'title': title_text, 'description': description},
        'serp_desktop': {'url': url, 'title': title_text, 'description': description},
        "points": serp_points,
    }
    return serp_preview

def build_overall_results(results):
    overall_rating = calculate_overall_points(results)
    improvement_count = calculate_improvement_count(results)
    return {
        'isCard': False,
        'overall_rating': overall_rating,
        'overall_rating_text': get_overall_rating_text(overall_rating),
        'improvement_count': improvement_count,
        'improvement_count_text': get_improvement_count_text(improvement_count),
    }
