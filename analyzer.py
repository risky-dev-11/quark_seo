from text_snippet_functions import *
from models import AnalyzedWebsite
import requests
from bs4 import BeautifulSoup
import langdetect
import socket

def analyze_website(url, db):

    response = requests.get(url if url.startswith(('http://', 'https://')) else 'http://' + url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # General results
    website_response_time = response.elapsed.total_seconds()
    file_size = len(response.content)
    word_count = len(soup.get_text().split())
    media_count = len(soup.find_all('img')) + len(soup.find_all('video')) + len(soup.find_all('audio'))
    internal_link_count = len([link for link in soup.find_all('a', href=True) if url in link['href']])
    external_link_count = len([link for link in soup.find_all('a', href=True) if url not in link['href']])

    # Metadata results - title
    title_missing_bool = soup.title is None or not soup.title.string.strip()
    if (not title_missing_bool):
        title_text = soup.title.string
        domain_in_title_bool = url in soup.title.string
        title_length = len(soup.title.string)
        title_length_bool = title_length < 30 or title_length > 60 
        title_word_repetitions_bool = len(set(soup.title.string.split())) != len(soup.title.string.split())

    # Metadata results - description
    description_missing_bool = soup.find('meta', attrs={'name': 'description'}) is None
    if (not description_missing_bool):
        description_of_the_website = soup.find('meta', attrs={'name': 'description'})['content']
        length_pixels = round(len(description_of_the_website) * 6.11) # 1 character is about 6 pixels
        description_length_bool = length_pixels > 960

    # Metadata results - language
    metatag_language = soup.find('meta', attrs={'name': 'language'}) or soup.html.get('lang')
    text_language = langdetect.detect(soup.get_text())

    # Get the IP address of the URL
    ip_address = socket.gethostbyname(url)'
    # Get the server location using the IP address
    server_location = requests.get(f'http://ip-api.com/json/{ip_address}').json().get('country', 'Unknown')
    
    language_matching_bool = metatag_language and text_language and text_language in metatag_language

    # Metadata results - favicon
    favicon_included_bool = soup.find('link', attrs={'rel': 'icon'}) is not None

    # pagequality results - content
    comparison_title_with_content_bool = set(soup.title.string.split()).issubset(set(soup.get_text().split()))
    # Split text into sentences considering different tags
    duplicate_bool = len(sentences := [sentence.strip() for tag in ['p', 'div', 'span', 'li'] for element in soup.find_all(tag) for sentence in element.get_text().split('.') if sentence.strip()]) != len(set(sentences))

    # pagequality results - pictures
    alt_attributes_missing_count = sum(1 for img in soup.find_all('img') if not img.get('alt') or not img.get('alt').strip())
    alt_attributes_missing_bool = alt_attributes_missing_count > 0

    ######
    
    # pagestructure results - headings
    h1_heading_bool = soup.find('h1') is not None
    headings = [tag.name for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    structure_bool = all(int(headings[i][1]) >= int(headings[i + 1][1]) - 1 for i in range(len(headings) - 1))

    # links results - internal
    internal_link_list = [link for link in soup.find_all('a', href=True) if url in link['href']]
    link_results_internal_link_count = internal_link_count # use the same value as in general results
    length_linktext_internal_bool = all(len(link.text) < 30 for link in internal_link_list)
    link_texts_internal = [link.text for link in internal_link_list]
    no_linktext_count_internal = sum(1 for text in link_texts_internal if not text.strip())
    no_linktext_count_internal_bool = no_linktext_count_internal > 0
    linktext_repetitions_internal_bool = len(link_texts_internal) != len(set(link_texts_internal))
    
    # links results - external
    external_link_list = [link for link in soup.find_all('a', href=True) if url not in link['href']]
    link_results_external_link_count = external_link_count # use the same value as in general results
    length_linktext_external_bool = all(len(link.text) < 30 for link in external_link_list)
    link_texts_external = [link.text for link in external_link_list]
    no_linktext_count_external = sum(1 for text in link_texts_external if not text.strip())
    no_linktext_count_external_bool = no_linktext_count_external > 0
    linktext_repetitions_external_bool = len(link_texts_external) != len(set(link_texts_external))

    # server results - http redirect
    site_redirects_bool = response.history == []
    redirecting_www_bool = response.history == []

    # server results - http header
    compression = response.headers.get('Content-Encoding')

    # server results - performance
    performance_website_response_time = website_response_time # use the same value as in general results

    # externalfactors results - blacklists
    is_blacklist_bool = False
    backlinks_bool = False

    


    analysis_results = AnalyzedWebsite(url=url, results=
        {
        'overall_results': [{
            'overall_rating_value': "81",
            'overall_rating_text': "Die analysierte Webseite hat eine Gesamtbewertung von 81 von 100 Punkten. Das ist eine gute Bewertung, es bestehen jedoch noch einige Verbesserungsmöglichkeiten.",
            'improvement_count': "16",
            'improvement_count_text': "Es wurden 16 Verbesserungsmöglichkeiten für die Webseite gefunden.",
        }],
        'general_results': [{
            'website_response_time': website_response_time,
            'website_response_time_text': get_website_response_time_text(website_response_time),
            'file_size': f"{file_size / 1000} kB",
            'file_size_text': get_file_size_text(file_size),
            'word_count': word_count, 
            'word_count_text': "Hier gibt es kein richtig oder falsch.",
            'media_count': media_count,
            'media_count_text': get_media_count_text(media_count),
            'link_count': f"{internal_link_count} Intern / {external_link_count} Extern",
            'link_count_text': get_link_count_text(internal_link_count, external_link_count),
        }],
        'metadata_results': [{
            'title': [{                
                'missing_bool': title_missing_bool, 
                'missing_text': get_title_missing_text(title_missing_bool),
                'text': title_text,
                'domain_in_title_bool': not domain_in_title_bool, 
                'domain_in_title_text': get_domain_in_title_text(domain_in_title_bool),
                'length_comment_bool': not title_length_bool,  
                'length_comment': get_title_length_text(title_length), 
                'word_repetitons_bool': not title_word_repetitions_bool,
                'word_repetitons_text': get_title_word_repetitions_text(title_word_repetitions_bool),
       
            }],
            'description': [{
                'missing_bool': description_missing_bool,
                'missing_text': get_description_missing_text(description_missing_bool), 
                'text': description_of_the_website,
                'length_comment_bool': description_length_bool,
                'length_comment': get_description_length_text(length_pixels), 
            }],
            'language': [{
                'metatag_language': metatag_language, 
                'text_language': text_language, 
                'server_location': server_location,
                'language_comment_bool': language_matching_bool,
                'language_comment': get_language_comment(metatag_language, text_language),
            }],
            'favicon': [{
                'included_bool': favicon_included_bool, 
                'included_text': get_favicon_included_text(favicon_included_bool),
            }],
            "points": 70,
        }],
        'pagequality_results': [{
            'content': [{
                'comparison_title_bool': not comparison_title_with_content_bool, 
                'comparison_title_text': get_comparison_title_text(comparison_title_with_content_bool),                 
                'length_comment_bool': word_count < 800,
                'length_comment': get_content_length_comment(word_count),                
                'duplicate_bool': duplicate_bool,
                'duplicate_text': get_duplicate_text(duplicate_bool),
            }],
            'pictures': [{ 
                'alt_attributes_missing_bool': alt_attributes_missing_bool,
                'alt_attributes_missing_text': get_alt_attributes_missing_text(alt_attributes_missing_count),    
            }],
            "points": 44,
        }],
        'pagestructure_results': [{
            'headings': [{
                'h1_heading_bool': h1_heading_bool, 
                'h1_heading_text': get_h1_heading_text(h1_heading_bool),
                'structure_bool': structure_bool, 
                'structure_text': get_structure_text(structure_bool),           
            }],
            "points": 79,
        }],
        'links_results': [{
            'links_internal': [{
                'count': link_results_internal_link_count,                
                'length_linktext_bool': not length_linktext_internal_bool, 
                'length_linktext_text': get_internal_length_linktext_text(length_linktext_internal_bool), 
                'no_linktext_bool': no_linktext_count_internal_bool, 
                'no_linktext_text': get_internal_no_linktext_text(no_linktext_count_internal_bool), 
                'linktext_repetitions_bool': not linktext_repetitions_internal_bool,  
                'linktext_repetitions_text': get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool),                       
            }],
            'links_external': [{
                'count': link_results_external_link_count,
                'length_linktext_bool': not length_linktext_external_bool, 
                'length_linktext_text': get_external_length_linktext_text(length_linktext_external_bool), 
                'no_linktext_bool': no_linktext_count_external_bool, 
                'no_linktext_text': get_external_no_linktext_text(no_linktext_count_external_bool), 
                'linktext_repetitions_bool': not linktext_repetitions_external_bool,  
                'linktext_repetitions_text': get_external_linktext_repetitions_text(linktext_repetitions_external_bool),              
            }],
            "points": 79,
        }],
        'server_results': [{
            'http_redirect': [{
                'site_redirects_bool': True, 
                'site_redirects_text': "Die Seite leitet nicht auf eine andere Seite um.",
                'redirecting_www_bool': "True",  
                'redirecting_www_text': "Die Weiterleitung von Adressen mit und ohne www. ist korrekt konfiguriert.",
            }],
            'http_header': [{
                'compression_bool': True, 
                'compression_text': "Der Webserver nutzt GZip zur komprimierten Übertragung der Webseite.", 
            }],
            'performance': [{
                'website_response_time_text': "Die Antwortzeit der Website ist mit 0,7s ausgezeichnet.",
                'file_size_text': "Die Dateigröße der Website ist mit 65kb sehr gut.",
            }],                        
            "points": 100,
        }],
        'externalfactors_results': [{
            'blacklists': [{
                'is_blacklist_bool': True, 
                'is_blacklist_text': 'Die Seite wird nicht als "nur für Erwachsene" eingestuft.', 
            }],
            'backlinks': [{
                'text': "Es wurden keine Backlinks gefunden.",
            }],                        
            "points": 100,
        }],
        'serp_preview': [{
            'serp_mobile': [{
                'url': url if url.startswith(('http://', 'https://')) else 'http://' + url,
                'title': title_text, 
                'description': description_of_the_website, 
            }],
            'serp_desktop': [{
                'url': url if url.startswith(('http://', 'https://')) else 'http://' + url,
                'title': title_text, 
                'description': description_of_the_website, 
            }],                        
        }]
    })
    db.session.add(analysis_results)
    db.session.commit()