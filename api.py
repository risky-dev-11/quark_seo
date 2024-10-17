from flask import Blueprint, jsonify
from tinydb import TinyDB, Query
import time

db = TinyDB('data/database.json')
query = Query()

api = Blueprint('api_blueprint', __name__)

@api.route('/api/count_of_analyzed_websites', methods=['GET'])
def count_of_analyzed_websites():
    return jsonify({"count": len(db.tables())}), 200

@api.route('/api/analyze/<path:url>', methods=['GET'])
def analyze_url(url):
    table = db.table(url)

    table.upsert({
        'overall_results': [{
            'overall_rating_value': "81",
            'overall_rating_text': "Die analysierte Webseite hat eine Gesamtbewertung von 81 von 100 Punkten. Das ist eine gute Bewertung, es bestehen jedoch noch einige Verbesserungsmöglichkeiten.",
            'improvement_count': "16",
            'improvement_count_text': "Es wurden 16 Verbesserungsmöglichkeiten für die Webseite gefunden.",
        }],
    }, Query().overall_results.exists())

    table.upsert({
        'general_results': [{
            'website_response_time': "0.07s",
            'website_response_time_text': "Die Antwortzeit der Website ist ausgezeichnet.",
            'file_size': "67kB",
            'file_size_text': "Die Dateigröße der Website ist sehr gut.",
            'word_count': "364", 
            'word_count_text': "Die Wortanzahl ist etwas gering. Eine gute Seite sollte etwa 800 Wörter enthalten.",
            'media_count': "23",
            'media_count_text': "Die Anzahl der Medien auf der Seite ist angemessen.",
            'link_count': "99 Intern / 12 Extern",
            'link_count_text': "Die Anzahl der internen und externen Links ist gut.",
        }],
    }, Query().general_results.exists())

    table.upsert({
        'metadata_results': [{
            'title': [{
                'missing_text': "Titel ist vorhanden", 
                'missing_bool': False,
                'text': "lichess.org • Kostenloses Online-Schach", 
                'domain_in_title_text': "Die Domain steht im Seitentitel.", 
                'domain_in_title_bool': True, 
                'length': 39, 
                'length_comment': "Die Länge deines Titels ist genau richtig", 
                'length_comment_bool': True, 'word_repetitons_text': "Es gibt keine Wortwiederholungen im Titel.", 
                'word_repetitons_bool': False, 
                }],
            'description': [{
                'missing_text': "Beschreibung ist vorhanden", 
                'missing_bool': False,
                'text': "Kostenloser Online-Schach-Server. Spiele jetzt auf einer übersichtlichen Benutzeroberfläche Schach! Keine Registrierung und keine Plugins erforderlich, komplett ohne Werbung. Spiele gegen den Computer, Freunde oder zufällige Gegner!", 
                'length_pixels': 1472, 
                'length_comment': "Deine Beschreibung ist zu lang! Maximale Länge sind 1000 Pixel (etwa 160 Zeichen).", 
                'length_comment_bool': True,
                }],
            'language': [{
                'metatag_language': "de-de", 
                'text_language': "de", 
                'server_location': "Deutschland",
                'language_comment': "Die Sprache des Texts entspricht der Sprache des Metatags.",
                }],
            'favicon': [{
                'included_bool': True, 
                'included_text': "Favicon ist vorhanden und korrekt eingebunden.",
                }],
            "points": 70,
        }]
    }, Query().metadata_results.exists())

    table.upsert({
        'pagequality_results': [{
            'content': [{
                'comparison_title_text': "Einige Wörter aus dem Seitentitel werden nicht im Text bzw. Inhalt der Seite verwendet", 
                'comparison_title_bool': False, 
                'length': 386,
                'length_comment': "Der Inhalt ist mit 386 Wörtern etwas kurz. Eine gute Seite zu einem Thema sollte Text mit etwa 800 Wörtern enthalten.", 
                'length_comment_bool': False,
                'duplicate_text': "Es gibt keine doppelten Inhalte auf der Seite.",
                'duplicate_bool': True,
                }],
            'pictures': [{
                'alt_attributes_missing': 16, 
                'alt_attributes_missing_text': "Bei 16 Bildern fehlt das Alt-Attribut. Der Inhalt von Alt-Attributen wird von Suchmaschinen auch als Text gewertet und ist wichtig für die Bildersuche.", 
                'alt_attributes_missing_bool': False,
                }],
            "points": 44,
        }]
    }, Query().pagequality_results.exists())

    table.upsert({
        'pagestructure_results': [{
            'headings': [{
                'h1_heading_bool': True, 
                'h1_heading_text': "H1-Überschrift ist vorhanden",
                'structure_bool': False, 
                'structure_text': "Die Seitenstruktur ist nicht optimal. Die Hierachie der Überschriften (H1-H6) sollte eingehalten werden.",           
                }],
        "points": 79,
        }]
    }, Query().pagestructure_results.exists())

    table.upsert({
        'links_results': [{
            'links_internal': [{
                'count': 99,
                'length_linktext_text': "Keiner der Linktexte ist zu lang.", 
                'length_linktext_bool': True, 
                'no_linktext': 8, 
                'no_linktext_text': "8 Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen.", 
                'no_linktext_bool': False, 
                'linktext_repetitions_text': "Einige der Linktexte wiederholen sich.",
                'linktext_repetitions_bool': False,         
                }],
            'links_external': [{
                'count': 4,
                'length_linktext_text': "Keiner der Linktexte ist zu lang.", 
                'length_linktext_bool': True, 
                'no_linktext': 2, 
                'no_linktext_text': "2 Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen.", 
                'no_linktext_bool': False, 
                'linktext_repetitions_text': "Keine der Linktexte wiederholen sich.",
                'linktext_repetitions_bool': True,             
                }],
            "points": 79,
        }]
    }, Query().links_results.exists())

    table.upsert({
        'server_results': [{
            'http_redirect': [{
                'site_redirects_text': "Die Seite leitet nicht auf eine andere Seite um.", 
                'site_redirects_bool': True, 
                'redirecting_www_text': "Die Weiterleitung von Adressen mit und ohne www. ist korrekt konfiguriert.",
                'redirecting_www_bool': "True",   
            }],
            'http_header': [{
                'compression_text': "Der Webserver nutzt GZip zur komprimierten Übertragung der Webseite.", 
                'compression_bool': True, 
            }],
            'performance': [{
                'website_response_time_text': "Die Antwortzeit der Website ist mit 0,7s ausgezeichnet.",
                'file_size_text': "Die Dateigröße der Website ist mit 65kb sehr gut.",
            }],                        
            "points": 100,
        }]
    }, Query().server_results.exists())

    table.upsert({
        'externalfactors_results': [{
            'blacklists': [{
                'is_blacklist_text': 'Die Seite wird nicht als "nur für Erwachsene" eingestuft.', 
                'is_blacklist_bool': True, 
            }],
            'backlinks': [{
                'text': "Es wurden keine Backlinks gefunden.",
            }],                        
            "points": 100,
        }]
    }, Query().externalfactors_results.exists())

    time.sleep(5)
    return jsonify({"message": "URL analysis started successfully"}), 200

# Endpoint for retrieving the overall results
@api.route('/overall_results/<path:url>', methods=['GET'])
def get_overall_results(url): 
    table = db.table(url)
    results = table.search(query.overall_results.exists())
    if results:
        return jsonify(results[0]['overall_results']), 200
    print(results)
    return jsonify({"error": "No general results found"}), 404


# Endpoint for retrieving the general results
@api.route('/general_results/<path:url>', methods=['GET'])
def get_general_results(url):
    table = db.table(url)
    results = table.search(query.general_results.exists())
    if results:
        return jsonify(results[0]['general_results']), 200
    print(results)
    return jsonify({"error": "No general results found"}), 404

# Endpoint for retrieving the metadata results
@api.route('/metadata_results/<path:url>', methods=['GET'])
def get_metadata_results(url):  
    table = db.table(url)
    results = table.search(query.metadata_results.exists())
    if results:
        return jsonify(results[0]['metadata_results']), 200
    return jsonify({"error": "No metadata results found"}), 404

# Endpoint for retrieving the page quality results
@api.route('/pagequality_results/<path:url>', methods=['GET'])
def get_pagequality_results(url): 
    table = db.table(url)
    results = table.search(query.pagequality_results.exists())
    if results:
        return jsonify(results[0]['pagequality_results']), 200
    return jsonify({"error": "No page quality results found"}), 404

# Endpoint for retrieving the page structure results
@api.route('/pagestructure_results/<path:url>', methods=['GET'])
def get_pagestructure_results(url):  
    table = db.table(url)
    results = table.search(query.pagestructure_results.exists())
    if results:
        return jsonify(results[0]['pagestructure_results']), 200
    return jsonify({"error": "No page structure results found"}), 404

# Endpoint for retrieving the link results
@api.route('/links_results/<path:url>', methods=['GET'])
def get_links_results(url):  
    table = db.table(url)
    results = table.search(query.links_results.exists())
    if results:
        return jsonify(results[0]['links_results']), 200
    return jsonify({"error": "No links results found"}), 404

# Endpoint for retrieving the server results
@api.route('/server_results/<path:url>', methods=['GET'])
def get_server_results(url):
    table = db.table(url)
    results = table.search(query.server_results.exists())
    if results:
        return jsonify(results[0]['server_results']), 200
    return jsonify({"error": "No server results found"}), 404

# Endpoint for retrieving the external factors results
@api.route('/externalfactors_results/<path:url>', methods=['GET'])
def get_externalfactors_results(url):  
    table = db.table(url)
    results = table.search(query.externalfactors_results.exists())
    if results:
        return jsonify(results[0]['externalfactors_results']), 200
    return jsonify({"error": "No external factors results found"}), 404
