from app import db
from run import flask_app
from models import User, AnalyzedWebsite
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(flask_app)
def init_db():
    with flask_app.app_context():
        db.create_all()
        print("Database tables created.")
        
        # Create an example user
        hashed_password = bcrypt.generate_password_hash('Timer640').decode('utf-8')
        example_user = User(first_name='Niklas', last_name='Werthmann', email='n11werthmann@gmail.com', password=hashed_password, role='user')
        db.session.add(example_user)
        
        # Create an example analyzed website
        example_website = AnalyzedWebsite(url='example.com', results=
            {
            'overall_results': [{
                'overall_rating_value': "81",
                'overall_rating_text': "Die analysierte Webseite hat eine Gesamtbewertung von 81 von 100 Punkten. Das ist eine gute Bewertung, es bestehen jedoch noch einige Verbesserungsmöglichkeiten.",
                'improvement_count': "16",
                'improvement_count_text': "Es wurden 16 Verbesserungsmöglichkeiten für die Webseite gefunden.",
            }],
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
            'metadata_results': [{
                'title': [{
                    'missing_text': "Titel ist vorhanden", 
                    'missing_bool': False,
                    'text': "lichess.org • Kostenloses Online-Schach", 
                    'domain_in_title_text': "Die Domain steht im Seitentitel.", 
                    'domain_in_title_bool': True, 
                    'length': 39, 
                    'length_comment': "Die Länge deines Titels ist genau richtig", 
                    'length_comment_bool': True,
                    'word_repetitons_text': "Es gibt keine Wortwiederholungen im Titel.", 
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
            }],
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
            }],
            'pagestructure_results': [{
                'headings': [{
                    'h1_heading_bool': True, 
                    'h1_heading_text': "H1-Überschrift ist vorhanden",
                    'structure_bool': False, 
                    'structure_text': "Die Seitenstruktur ist nicht optimal. Die Hierachie der Überschriften (H1-H6) sollte eingehalten werden.",           
                }],
                "points": 79,
            }],
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
            }],
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
            }],
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
        })
        db.session.add(example_website)
        
        db.session.commit()
        print("Example user and analyzed website created.")

if __name__ == "__main__":
    init_db()

