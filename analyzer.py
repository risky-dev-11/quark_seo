from text_snippet_functions import *
from points_calculator import calculate_metadata_points, calculate_pagequality_points, calculate_pagestructure_points, calculate_links_points, calculate_server_points
from models import AnalyzedWebsite
import requests
from bs4 import BeautifulSoup
import langdetect
import socket

def analyze_website(url, db):

    try:
        response = requests.get(url if url.startswith(('http://', 'https://')) else 'http://' + url)
    except Exception:
        raise requests.exceptions.RequestException('Unser Server konnte die Webseite nicht erreichen. Bitte überprüfen Sie die URL und versuchen Sie es erneut.')
    
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
    
    domain = url.split('/')[2] if '//' in url else url.split('/')[0]
    ip_address = socket.gethostbyname(domain)
    # Get the server location using the IP address
    try:
        server_location = requests.get(f'http://ip-api.com/json/{ip_address}').json().get('country', 'Unknown')
    except Exception:
        server_location = 'Unbekannt'
    
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
    link_results_internal_link_count = internal_link_count # use the same bool as in general results
    length_linktext_internal_bool = all(len(link.text) < 30 for link in internal_link_list)
    link_texts_internal = [link.text for link in internal_link_list]
    no_linktext_count_internal = sum(1 for text in link_texts_internal if not text.strip())
    no_linktext_count_internal_bool = no_linktext_count_internal > 0
    linktext_repetitions_internal_bool = len(link_texts_internal) != len(set(link_texts_internal))
    
    # links results - external
    external_link_list = [link for link in soup.find_all('a', href=True) if url not in link['href']]
    link_results_external_link_count = external_link_count # use the same bool as in general results
    length_linktext_external_bool = all(len(link.text) < 30 for link in external_link_list)
    link_texts_external = [link.text for link in external_link_list]
    no_linktext_count_external = sum(1 for text in link_texts_external if not text.strip())
    no_linktext_count_external_bool = no_linktext_count_external > 0
    linktext_repetitions_external_bool = len(link_texts_external) != len(set(link_texts_external))

    # server results - http redirect
    site_redirects_bool = response.url != 'http://' + url and response.url != 'https://' + url   
    www_url = (url if url.startswith(('http://', 'https://')) else 'http://' + url).replace('http://', 'http://www.').replace('https://', 'https://www.')
    try:
        response_with_www = requests.get(www_url)
        redirecting_www_bool = response.status_code == 200 and response_with_www.status_code == 200
    except Exception:
        redirecting_www_bool = False
    

    # server results - http header
    compression = response.headers.get('Content-Encoding')
    compression_bool = compression is not None

    metadata_points = calculate_metadata_points(title_missing_bool, domain_in_title_bool, title_length, title_word_repetitions_bool, description_missing_bool, length_pixels, metatag_language, text_language, favicon_included_bool)
    pagequality_points = calculate_pagequality_points(comparison_title_with_content_bool, word_count, duplicate_bool, alt_attributes_missing_count)
    pagestructure_points = calculate_pagestructure_points(h1_heading_bool, structure_bool)
    links_points = calculate_links_points(length_linktext_internal_bool, no_linktext_count_internal, linktext_repetitions_internal_bool, length_linktext_external_bool, no_linktext_count_external, linktext_repetitions_external_bool)
    server_points = calculate_server_points(site_redirects_bool, redirecting_www_bool, compression_bool)

    max_points_of_all_categories = 69
    overall_points = metadata_points + pagequality_points + pagestructure_points + links_points + server_points
    overall_rating_bool = round((overall_points / max_points_of_all_categories) * 100)

    analysis_results = AnalyzedWebsite(url=url, results=
        {
        'overall_results': [{
            'isCard': False,
            'overall_rating_bool': overall_rating_bool,
            'overall_rating_text': "Die analysierte Webseite hat eine Gesamtbewertung von 81 von 100 Punkten. Das ist eine gute Bewertung, es bestehen jedoch noch einige Verbesserungsmöglichkeiten.",
            'improvement_count': "16",
            'improvement_count_text': "Es wurden 16 Verbesserungsmöglichkeiten für die Webseite gefunden.",
        }],
        'general_results': [{
            'isCard': False,
            '1': {
                'value': website_response_time,
                'text': get_website_response_time_text(website_response_time)
            },
            '2': {
                'value': f"{file_size / 1000} kB",
                'text': get_file_size_text(file_size)
            },
            '3': {
                'value': word_count,
                'text': "Hier gibt es kein richtig oder falsch."
            },
            '4': {
                'value': media_count,
                'text': get_media_count_text(media_count)
            },
            '5': {
                'value': f"{internal_link_count} Intern / {external_link_count} Extern",
                'text': get_link_count_text(internal_link_count, external_link_count)
            },
        }],
        'metadata_results': [{
            'isCard': True,
            'card_name': 'Metadaten',
            'title': [{
                'category_name': 'Titel',
                'content': [{
                    '0': {
                        'bool': title_missing_bool,
                        'text': get_title_missing_text(title_missing_bool)
                    },
                    '1': {
                        'bool': '',
                        'text': title_text,
                    },
                    '2': {
                        'bool': not domain_in_title_bool,
                        'text': get_domain_in_title_text(domain_in_title_bool)
                    },
                    '3': {
                        'bool': not title_length_bool,
                        'text': get_title_length_text(title_length)
                    },
                    '4': {
                        'bool': not title_word_repetitions_bool,
                        'text': get_title_word_repetitions_text(title_word_repetitions_bool)
                    },
                }],
            }],
            
            'description': [{
                'category_name': 'Beschreibung',
                'content': [{
                    '0': {
                        'bool': description_missing_bool,
                        'text': get_description_missing_text(description_missing_bool)
                    },
                    '1': {
                        'bool': description_length_bool,
                        'text': description_of_the_website,
                    },
                    '2': {
                        'bool': description_length_bool,
                        'text': get_description_length_text(length_pixels)
                    },
                }],
            }],

            'language': [{
                'category_name': 'Sprache',
                'content': [{
                    '0': {
                        'bool': language_matching_bool,
                        'text': get_language_comment(metatag_language, text_language)
                    },
                    '1': {
                        'bool': '',
                        'text': f'Meta-Tag Sprache: {metatag_language}'
                    },
                    '2': {
                        'bool': '',
                        'text': f'Textsprache: {text_language}'
                    },
                    '3': {
                        'bool': '',
                        'text': f'Server: {server_location}'
                    },
                }],
            }],

            'favicon': [{
                'category_name': 'Favicon',
                'content': [{
                    '0': {
                        'bool': favicon_included_bool,
                        'text': get_favicon_included_text(favicon_included_bool)
                    }
                }],
            }],

            "points": metadata_points,
        }],

        'pagequality_results': [{
            'isCard': True,
            'card_name': 'Seitenqualität',
            'content': [{
                'category_name': 'Inhalt',
                'content': [{
                    '0': {
                        'bool': not comparison_title_with_content_bool,
                        'text': get_comparison_title_text(comparison_title_with_content_bool)
                    },
                    '1': {
                        'bool': word_count < 800,
                        'text': get_content_length_comment(word_count)
                    },
                    '2': {
                        'bool': duplicate_bool,
                        'text': get_duplicate_text(duplicate_bool)
                    },
                }],
            }],
            
            'pictures': [{
                'category_name': 'Bilder',
                'content': [{
                    '0': {
                        'bool': alt_attributes_missing_bool,
                        'text': get_alt_attributes_missing_text(alt_attributes_missing_count)
                    }
                }],
            }],
            
            "points": pagequality_points,
        }],

        'pagestructure_results': [{
            'isCard': True,
            'card_name': 'Seitenstruktur',
            'headings': [{
                'category_name': 'Überschriften',
                'content': [{
                    '0': {
                        'bool': h1_heading_bool,
                        'text': get_h1_heading_text(h1_heading_bool)
                    },
                    '1': {
                        'bool': structure_bool,
                        'text': get_structure_text(structure_bool)
                    },
                }],
            }],
            
            "points": pagestructure_points,
        }],

        'links_results': [{
            'isCard': True,
            'card_name': 'Links',
            'links_internal': [{
                'category_name': 'Interne Links',
                'content': [{
                    '0': {
                        'bool': length_linktext_internal_bool,
                        'text': get_internal_length_linktext_text(length_linktext_internal_bool)
                    },
                    '1': {
                        'bool': no_linktext_count_internal_bool,
                        'text': get_internal_no_linktext_text(no_linktext_count_internal_bool)
                    },
                    '2': {
                        'bool': not linktext_repetitions_internal_bool,
                        'text': get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool)
                    },
                }],
            }],

            'links_external': [{
                'category_name': 'Externe Links',
                'content': [{
                    '0': {
                        'bool': length_linktext_external_bool,
                        'text': get_external_length_linktext_text(length_linktext_external_bool)
                    },
                    '1': {
                        'bool': no_linktext_count_external_bool,
                        'text': get_external_no_linktext_text(no_linktext_count_external_bool)
                    },
                    '2': {
                        'bool': not linktext_repetitions_external_bool,
                        'text': get_external_linktext_repetitions_text(linktext_repetitions_external_bool)
                    },
                }],
            }],
            
            "points": links_points,
        }],

        'server_results': [{
            'isCard': True,
            'card_name': 'Server',
            'http_redirect': [{
                'category_name': 'HTTP Redirect',
                'content': [{
                    '0': {
                        'bool': not site_redirects_bool,
                        'text': get_site_redirects_text(site_redirects_bool)
                    },
                    '1': {
                        'bool': redirecting_www_bool,
                        'text': get_redirecting_www_text(redirecting_www_bool)
                    }
                }],
            }],
            
            'http_header': [{
                'category_name': 'HTTP Header',
                'content': [{
                    '0': {
                        'bool': compression_bool,
                        'text': get_compression_text(compression, compression_bool)
                    },
                }],
            }],
            
            'performance': [{
                'category_name': 'Performance',
                'content': [{
                    '0': {
                        'bool': website_response_time,
                        'text': get_website_response_time_text(website_response_time)
                    },
                    '1': {
                        'bool': f"{file_size / 1000} kB",
                        'text': get_file_size_text(file_size)
                    }
                }],
            }],
            
            "points": server_points,
        }],

        'serp_preview': [{
            'isCard': False,
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
            "points": 50,
        }]
    })
    db.session.add(analysis_results)
    db.session.commit()