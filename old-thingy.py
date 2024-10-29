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
    }