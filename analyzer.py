from text_snippet_functions import get_hierarchy_text, get_improvement_count_text, get_overall_rating_text, get_redirecting_history_text, get_website_response_time_text, get_file_size_text, get_media_count_text, get_link_count_text, get_title_missing_text, get_domain_in_title_text, get_title_length_text, get_title_word_repetitions_text, get_description_missing_text, get_description_length_text, get_language_comment, get_favicon_included_text, get_comparison_title_text, get_content_length_comment, get_duplicate_text, get_alt_attributes_missing_text, get_h1_heading_text, get_structure_text, get_internal_length_linktext_text, get_internal_no_linktext_text, get_internal_linktext_repetitions_text, get_external_length_linktext_text, get_external_no_linktext_text, get_external_linktext_repetitions_text, get_site_redirects_text, get_redirecting_www_text, get_compression_text
from models import AnalyzedWebsite, Category, Card, calculate_improvement_count, calculate_overall_points
import requests
from bs4 import BeautifulSoup
import langdetect
import socket

def analyze_website(user_uuid, url, db):

    results = {}

    http_const = 'http://'
    https_const = 'https://'

    try:
        session = requests.Session()
        session.max_redirects = 5
        response = session.get(url if url.startswith((http_const, https_const)) else http_const + url, allow_redirects=True)
        
    except Exception:
        print('Unser Server konnte die Webseite nicht erreichen. Bitte überprüfen Sie die URL und versuchen Sie es erneut.')
        raise requests.exceptions.RequestException('Unser Server konnte die Webseite nicht erreichen. Bitte überprüfen Sie die URL und versuchen Sie es erneut.')
    
    soup = BeautifulSoup(response.text, 'html.parser')

    
    # General results
    website_response_time = response.elapsed.total_seconds()
    file_size = len(response.content)
    word_count = len(soup.get_text().split())
    media_count = len(soup.find_all('img')) + len(soup.find_all('video')) + len(soup.find_all('audio'))
    internal_link_count = len([link for link in soup.find_all('a', href=True) if url in link['href']])
    external_link_count = len([link for link in soup.find_all('a', href=True) if url not in link['href']])
    
    general_results = {
            'isCard': False,
            'website_response_time': website_response_time,
            'website_response_time_text': get_website_response_time_text(website_response_time),
            'file_size': f"{file_size / 1000} kB",
            'file_size_text': get_file_size_text(file_size), 
            'word_count': word_count,
            'word_count_text': "Hier gibt grundsätzlich es kein richtig oder falsch.",
            'media_count': media_count,
            'media_count_text': get_media_count_text(media_count),
            'link_count': f"{internal_link_count} Intern / {external_link_count} Extern",
            'link_count_text': get_link_count_text(internal_link_count, external_link_count),
        }   
    results['general_results'] = general_results

    ########################################

    # Create the metadata card
    metadata_card = Card('Metadaten')

    ##########

    # Create the title category
    title_category = Category('Titel')

    # Add the content of the title category
    title_missing_bool = soup.title is None or not soup.title.string.strip()
    title_category.add_content(not title_missing_bool, get_title_missing_text(title_missing_bool))
    # if the title is not missing, add more details about it
    if (not title_missing_bool):
        title_category.add_content('', soup.title.string)
        title_category.add_content(url not in soup.title.string, get_domain_in_title_text(url in soup.title.string))
        title_category.add_content(len(soup.title.string) < 30 or len(soup.title.string) > 60, get_title_length_text(len(soup.title.string)))
        title_category.add_content(len(set(soup.title.string.split())) == len(soup.title.string.split()), get_title_word_repetitions_text(len(set(soup.title.string.split())) != len(soup.title.string.split())))
    
    # Add the title category to the card
    metadata_card.add_category(title_category)

    ####################

    # Create the description category
    description_category = Category('Beschreibung')

     # Add the content of the description category
    description_missing_bool = soup.find('meta', attrs={'name': 'description'}) is None or not soup.find('meta', attrs={'name': 'description'})['content'].strip()
    description_category.add_content(not description_missing_bool, get_description_missing_text(description_missing_bool))
    # if the description is not missing, add more details about it
    if (not description_missing_bool):
        description_category.add_content('', soup.find('meta', attrs={'name': 'description'})['content'])
        # Calculate the approximate length of the description in pixels
        description_length_in_pixels = round(len(soup.find('meta', attrs={'name': 'description'})['content']) * 6.11) # 1 character is about 6 pixels
        description_category.add_content(description_length_in_pixels >= 300 and description_length_in_pixels <= 960, get_description_length_text(description_length_in_pixels))

    # Add the description category to the card
    metadata_card.add_category(description_category)

    ####################

     # Create the language category
    language_category = Category('Sprache')

    # Add the content of the language category
    metatag_language = soup.find('meta', attrs={'name': 'language'}) or soup.html.get('lang') or 'Unbekannt'
    text_language = langdetect.detect(soup.get_text())
    language_category.add_content('', 'Meta/HTML-Sprache: ' + metatag_language)
    language_category.add_content('', 'Im Text erkannte Sprache: ' + text_language)
    # Get the server location using the IP address derived thoruugh the socket.gethostname(domain)
    try:
        server_location = requests.get(f"http://ip-api.com/json/{socket.gethostbyname(url.split('/')[2] if '//' in url else url.split('/')[0])}").json().get('country', 'Unbekannt')
    except Exception:
        server_location = 'Unbekannt'
    language_category.add_content('', 'Serverstandort: ' + server_location)
    language_category.add_content(text_language in metatag_language, get_language_comment(metatag_language, text_language))

    # Add the language category to the card
    metadata_card.add_category(language_category)

    ####################

     # Create the favicon category
    favicon_category = Category('Favicon')

    # Add the content of the favicon category
    favicon_category.add_content(soup.find('link', attrs={'rel': 'icon'}) is not None, get_favicon_included_text(soup.find('link', attrs={'rel': 'icon'}) is not None))

    # Add the favicon category to the card
    metadata_card.add_category(favicon_category)

    ####################

    metadata_card.add_to_results(results)

    ########################################
    
    # Create the pagequality card
    pagequality_card = Card('Seitenqualität')
    
    ##########

    # Create the content category
    title_category = Category('Inhalt')

    # Add the content of the content category
    title_category.add_content(not set(soup.title.string.split()).issubset(set(soup.get_text().split())), get_comparison_title_text(set(soup.title.string.split()).issubset(set(soup.get_text().split()))))
    title_category.add_content(word_count >= 300, get_content_length_comment(word_count))
    title_category.add_content(len(sentences := [sentence.strip() for tag in ['p', 'div', 'span', 'li'] for element in soup.find_all(tag) for sentence in element.get_text().split('.') if sentence.strip()]) != len(set(sentences)), get_duplicate_text(len(sentences) != len(set(sentences))))

    # Add the content category to the card
    pagequality_card.add_category(title_category)

    ####################

    # Create the alt attributes category
    alt_attributes_category = Category('Bilder')

    # Add the content of the alt attributes category
    alt_attributes_missing_count = sum(1 for img in soup.find_all('img') if not img.get('alt') or not img.get('alt').strip())
    alt_attributes_category.add_content(alt_attributes_missing_count == 0, get_alt_attributes_missing_text(alt_attributes_missing_count))

    # Add the alt attributes category to the card
    pagequality_card.add_category(alt_attributes_category)

    ####################

    pagequality_card.add_to_results(results)

    ########################################

    # Create the pagestructure card
    pagestructure_card = Card('Seitenstruktur')

    ##########
    
    # Create the headings category
    headings_category = Category('Überschriften')

    # Add the content of the headings category
    headings = [tag.name for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

    # structure_bool: Ensures that the second element of each consecutive pair in 
    # headings is in a non-increasing order, allowing a difference of at most 1.
    # hierarchy_bool: Ensures that if any heading from h{i} to h6 is present,
    # then all preceding headings h1 to h{i-1} must also be present.
    structure_bool = all(int(headings[i][1]) >= int(headings[i + 1][1]) - 1 for i in range(len(headings) - 1))
    hierarchy_bool = all(f'h{i}' in headings for i in range(1, 7) if any(f'h{j}' in headings for j in range(i, 7)))
    headings_category.add_content(soup.find('h1') is not None, get_h1_heading_text(soup.find('h1') is not None))
    headings_category.add_content(structure_bool, get_structure_text(structure_bool))
    headings_category.add_content(hierarchy_bool, get_hierarchy_text(hierarchy_bool))
    
    # Add the headings category to the card
    pagestructure_card.add_category(headings_category)

    ####################

    pagestructure_card.add_to_results(results)

    ########################################

    # Create the links card
    links_card = Card('Links')

    ##########

    # Create the internal links category
    internal_links_category = Category('Interne Links')

    # Add the content of the internal links category
    internal_link_list = [link for link in soup.find_all('a', href=True) if url in link['href']]
    internal_link_count = len(internal_link_list)
    internal_links_category.add_content(all(len(link.text) < 30 for link in internal_link_list), get_internal_length_linktext_text(all(len(link.text) < 30 for link in internal_link_list)))
    internal_links_category.add_content(sum(1 for text in [link.text for link in internal_link_list] if not text.strip()) <= 0, get_internal_no_linktext_text(sum(1 for text in [link.text for link in internal_link_list] if not text.strip()) > 0))
    internal_links_category.add_content(len([link.text for link in internal_link_list]) == len(set([link.text for link in internal_link_list])), get_internal_linktext_repetitions_text(len([link.text for link in internal_link_list]) != len(set([link.text for link in internal_link_list]))))

    # Add the internal links category to the card
    links_card.add_category(internal_links_category)

    ####################

    # Create the external links category
    external_links_category = Category('Externe Links')

    # Add the content of the external links category
    external_link_list = [link for link in soup.find_all('a', href=True) if url not in link['href']]
    external_link_count = len(external_link_list)
    external_links_category.add_content(all(len(link.text) < 30 for link in external_link_list), get_external_length_linktext_text(all(len(link.text) < 30 for link in external_link_list)))
    external_links_category.add_content(sum(1 for text in [link.text for link in external_link_list] if not text.strip()) <= 0, get_external_no_linktext_text(sum(1 for text in [link.text for link in external_link_list] if not text.strip()) > 0))
    external_links_category.add_content(len([link.text for link in external_link_list]) == len(set([link.text for link in external_link_list])), get_external_linktext_repetitions_text(len([link.text for link in external_link_list]) != len(set([link.text for link in external_link_list]))))

    # Add the external links category to the card
    links_card.add_category(external_links_category)

    ####################

    links_card.add_to_results(results)

    ########################################

    # Create the server card
    server_card = Card('Server')

    ##########

    # Create the redirects category
    redirects_category = Category('Weiterleitungen')

    # Add the content of the redirects category
    site_redirects_bool = bool(response.history)
    www_url = (url if url.startswith((http_const, https_const)) else http_const + url).replace(http_const, 'http://www.').replace(https_const, 'https://www.')
    try:
        response_with_www = requests.get(www_url)
        redirecting_www_bool = response.status_code == 200 and response_with_www.status_code == 200
    except Exception:
        redirecting_www_bool = False

    redirects_category.add_content(not site_redirects_bool, get_site_redirects_text(site_redirects_bool))
    if site_redirects_bool:
        redirects_category.add_content('', get_redirecting_history_text(response.history[-1].headers['Location']))
    redirects_category.add_content(redirecting_www_bool, get_redirecting_www_text(redirecting_www_bool))

    # Add the redirects category to the card
    server_card.add_category(redirects_category)

    ####################

    # Create the compression category
    compression_category = Category('Komprimierung')

    # Add the content of the compression category
    compression = response.headers.get('Content-Encoding')
    compression_category.add_content(compression is not None, get_compression_text(compression, compression is not None))

    # Add the compression category to the card
    server_card.add_category(compression_category)

    ####################

    server_card.add_to_results(results)

    ########################################

    title_text = soup.title.string if soup.title and soup.title.string.strip() else ""
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description_of_the_website = description_tag['content'] if description_tag else ""

    # Calculate the SERP preview points
    try:
        serp_points = 0
        description_length_in_pixels = round(len(description_of_the_website) * 6.11)  # Ensure this variable is defined
        if 110 <= len(description_of_the_website) <= 165:
            serp_points += 25
        if 100 <= len(description_of_the_website) <= 120:
            serp_points += 25
        if 30 <= len(title_text) <= 60:
            serp_points += 50
    except Exception:
        serp_points = 0

    serp_preview = {
            'isCard': False,
            'serp_mobile': {
                'url': url if url.startswith((http_const, https_const)) else http_const + url,
                'title': title_text,
                'description': description_of_the_website,
            },
            'serp_desktop': {
                'url': url if url.startswith((http_const, https_const)) else http_const + url,
                'title': title_text,
                'description': description_of_the_website,
            },
            "points": serp_points,
        }
    results['serp_preview'] = serp_preview

    # calculate the overall rating

    overall_rating = calculate_overall_points(results)
    improvement_count = calculate_improvement_count(results)

    overall_results = {
        'isCard': False,
        'overall_rating': overall_rating,
        'overall_rating_text': get_overall_rating_text(overall_rating),
        'improvement_count': improvement_count,
        'improvement_count_text': get_improvement_count_text(improvement_count),
    }
    results['overall_results'] = overall_results

    analysis_results = AnalyzedWebsite(user_uuid=user_uuid, url=url, results=results)
            
    db.session.add(analysis_results)
    db.session.commit()

    return analysis_results.uuid
