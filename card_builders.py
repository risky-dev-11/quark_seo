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

def build_all_cards(results, soup, url, response):
    """
    Builds and adds all the card sections to the results.
    This function delegates to smaller helper functions for each card.
    """
    # Metadata Card
    metadata_card = build_metadata_card(soup, url)
    metadata_card.add_to_results(results)
    
    # Page Quality Card
    pagequality_card = build_pagequality_card(soup)
    pagequality_card.add_to_results(results)
    
    # Page Structure Card
    pagestructure_card = build_pagestructure_card(soup)
    pagestructure_card.add_to_results(results)
    
    # Links Card
    links_card = build_links_card(soup, url)
    links_card.add_to_results(results)
    
    # Server Card
    server_card = build_server_card(soup, url, response)
    server_card.add_to_results(results)
    
    # AI Analysis Card
    ai_results_card = build_ai_card(soup)
    ai_results_card.add_to_results(results)

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
        desc_length_px = round(len(description_content) * 6.11)
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
    
    # Favicon Category
    favicon_category = Category('Favicon')
    has_favicon = soup.find('link', attrs={'rel': 'icon'}) is not None
    favicon_category.add_content(has_favicon, get_favicon_included_text(has_favicon))
    card.add_category(favicon_category)
    
    return card

def build_pagequality_card(soup):
    card = Card('Seitenqualität')
    
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
    
    # Bilder Category
    images_category = Category('Bilder')
    missing_alts = sum(1 for img in soup.find_all('img') if not img.get('alt') or not img.get('alt').strip())
    images_category.add_content(missing_alts == 0, get_alt_attributes_missing_text(missing_alts))
    if missing_alts > 0:
        images_category.add_content('improvement', "Fügen Sie Alt-Attribute zu allen Bildern hinzu! Sie verbessern damit die Barrierefreiheit Ihrer Website und helfen Suchmaschinen, den Bildinhalt zu verstehen. Das steigert sowohl die Nutzerfreundlichkeit als auch Ihr Ranking.")
    card.add_category(images_category)
    
    return card

def build_pagestructure_card(soup):
    card = Card('Seitenstruktur')
    
    headings_category = Category('Überschriften')
    headings = [tag.name for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    structure_ok = all(int(headings[i][1]) >= int(headings[i + 1][1]) - 1 for i in range(len(headings) - 1))
    hierarchy_ok = all(f'h{i}' in headings for i in range(1, 7) if any(f'h{j}' in headings for j in range(i, 7)))
    headings_category.add_content(soup.find('h1') is not None, get_h1_heading_text(soup.find('h1') is not None))
    headings_category.add_content(structure_ok, get_structure_text(structure_ok))
    headings_category.add_content(hierarchy_ok, get_hierarchy_text(hierarchy_ok))
    card.add_category(headings_category)
    
    return card

def build_links_card(soup, url):
    card = Card('Links')
    
    # Internal links
    internal_links = [link for link in soup.find_all('a', href=True) if url in link['href']]
    internal_category = Category('Interne Links')
    internal_category.add_content(all(len(link.text) < 30 for link in internal_links), get_internal_length_linktext_text(all(len(link.text) < 30 for link in internal_links)))
    no_text_internal = sum(1 for link in internal_links if not link.text.strip()) > 0
    internal_category.add_content(not no_text_internal, get_internal_no_linktext_text(no_text_internal))
    duplicate_internal = len([link.text for link in internal_links]) != len(set([link.text for link in internal_links]))
    internal_category.add_content(not duplicate_internal, get_internal_linktext_repetitions_text(duplicate_internal))
    card.add_category(internal_category)
    
    # External links
    external_links = [link for link in soup.find_all('a', href=True) if url not in link['href']]
    external_category = Category('Externe Links')
    external_category.add_content(all(len(link.text) < 30 for link in external_links), get_external_length_linktext_text(all(len(link.text) < 30 for link in external_links)))
    no_text_external = sum(1 for link in external_links if not link.text.strip()) > 0
    external_category.add_content(not no_text_external, get_external_no_linktext_text(no_text_external))
    duplicate_external = len([link.text for link in external_links]) != len(set([link.text for link in external_links]))
    external_category.add_content(not duplicate_external, get_external_linktext_repetitions_text(duplicate_external))
    card.add_category(external_category)
    
    return card

def build_server_card(soup, url, response):
    card = Card('Technische SEO')
    
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
    if 110 <= len(description) <= 165:
        serp_points += 25
    if 100 <= len(description) <= 120:
        serp_points += 25
    if 30 <= len(title_text) <= 60:
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
