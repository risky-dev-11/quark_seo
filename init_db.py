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
                'isCard': False,
                'overall_rating_bool': True,
                'overall_rating_text': "Die analysierte Webseite hat eine Gesamtbewertung von 81 von 100 Punkten. Das ist eine gute Bewertung, es bestehen jedoch noch einige Verbesserungsmöglichkeiten.",
                'improvement_count': "16",
                'improvement_count_text': "Es wurden 16 Verbesserungsmöglichkeiten für die Webseite gefunden.",
            }],
            'general_results': [{
                'isCard': False,
                '1': {
                    'value': "0.07s",
                    'text': "Die Antwortzeit der Website ist ausgezeichnet."
                },
                '2': {
                    'value': "67 kB",
                    'text': "Die Dateigröße der Website ist sehr gut."
                },
                '3': {
                    'value': "364",
                    'text': "Hier gibt es kein richtig oder falsch."
                },
                '4': {
                    'value': "23",
                    'text': "Die Anzahl der Medien auf der Seite ist angemessen."
                },
                '5': {
                    'value': "99 Intern / 12 Extern",
                    'text': "Die Anzahl der internen und externen Links ist gut."
                },
            }],
            'metadata_results': [{
            'isCard': True,
            'card_name': 'Metadaten',
            'title': [{
                'category_name': 'Titel',
                'content': [{
                    '0': {
                        'bool': False,
                        'text': "Titel ist vorhanden"
                    },
                    '1': {
                        'bool': '',
                        'text': "lichess.org • Kostenloses Online-Schach",
                    },
                    '2': {
                        'bool': False,
                        'text': "Die Domain steht im Seitentitel."
                    },
                    '3': {
                        'bool': False,
                        'text': "Die Länge deines Titels ist genau richtig"
                    },
                    '4': {
                        'bool': False,
                        'text': "Es gibt keine Wortwiederholungen im Titel."
                    },
                }],
            }],
            
            'description': [{
                'category_name': 'Beschreibung',
                'content': [{
                '0': {
                    'bool': False,
                    'text': "Beschreibung ist vorhanden"
                },
                '1': {
                    'bool': True,
                    'text': "Kostenloser Online-Schach-Server. Spiele jetzt auf einer übersichtlichen Benutzeroberfläche Schach! Keine Registrierung und keine Plugins erforderlich, komplett ohne Werbung. Spiele gegen den Computer, Freunde oder zufällige Gegner!",
                },
                '2': {
                    'bool': True,
                    'text': "Deine Beschreibung ist zu lang! Maximale Länge sind 1000 Pixel (etwa 160 Zeichen)."
                },
                }],
            }],

            'language': [{
                'category_name': 'Sprache',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Die Sprache des Texts entspricht der Sprache des Metatags."
                },
                '1': {
                    'bool': '',
                    'text': 'Meta-Tag Sprache: de-de'
                },
                '2': {
                    'bool': '',
                    'text': 'Textsprache: de'
                },
                '3': {
                    'bool': '',
                    'text': 'Server: Deutschland'
                },
                }],
            }],

            'favicon': [{
                'category_name': 'Favicon',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Favicon ist vorhanden und korrekt eingebunden."
                }
                }],
            }],

            "points": 70,
            }],

            'pagequality_results': [{
            'isCard': True,
            'card_name': 'Seitenqualität',
            'content': [{
                'category_name': 'Inhalt',
                'content': [{
                '0': {
                    'bool': False,
                    'text': "Einige Wörter aus dem Seitentitel werden nicht im Text bzw. Inhalt der Seite verwendet"
                },
                '1': {
                    'bool': True,
                    'text': "Der Inhalt ist mit 386 Wörtern etwas kurz. Eine gute Seite zu einem Thema sollte Text mit etwa 800 Wörtern enthalten."
                },
                '2': {
                    'bool': True,
                    'text': "Es gibt keine doppelten Inhalte auf der Seite."
                },
                }],
            }],
            
            'pictures': [{
                'category_name': 'Bilder',
                'content': [{
                '0': {
                    'bool': False,
                    'text': "Bei 16 Bildern fehlt das Alt-Attribut. Der Inhalt von Alt-Attributen wird von Suchmaschinen auch als Text gewertet und ist wichtig für die Bildersuche."
                }
                }],
            }],
            
            "points": 44,
            }],

            'pagestructure_results': [{
            'isCard': True,
            'card_name': 'Seitenstruktur',
            'headings': [{
                'category_name': 'Überschriften',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "H1-Überschrift ist vorhanden"
                },
                '1': {
                    'bool': False,
                    'text': "Die Seitenstruktur ist nicht optimal. Die Hierachie der Überschriften (H1-H6) sollte eingehalten werden."
                },
                }],
            }],
            
            "points": 79,
            }],

            'links_results': [{
            'isCard': True,
            'card_name': 'Links',
            'links_internal': [{
                'category_name': 'Interne Links',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Keiner der Linktexte ist zu lang."
                },
                '1': {
                    'bool': False,
                    'text': "8 Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen."
                },
                '2': {
                    'bool': False,
                    'text': "Einige der Linktexte wiederholen sich."
                },
                }],
            }],

            'links_external': [{
                'category_name': 'Externe Links',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Keiner der Linktexte ist zu lang."
                },
                '1': {
                    'bool': False,
                    'text': "2 Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen."
                },
                '2': {
                    'bool': True,
                    'text': "Keine der Linktexte wiederholen sich."
                },
                }],
            }],
            
            "points": 79,
            }],

            'server_results': [{
            'isCard': True,
            'card_name': 'Server',
            'http_redirect': [{
                'category_name': 'HTTP Redirect',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Die Seite leitet nicht auf eine andere Seite um."
                },
                '1': {
                    'bool': True,
                    'text': "Die Weiterleitung von Adressen mit und ohne www. ist korrekt konfiguriert."
                }
                }],
            }],
            
            'http_header': [{
                'category_name': 'HTTP Header',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Der Webserver nutzt GZip zur komprimierten Übertragung der Webseite."
                },
                }],
            }],
            
            'performance': [{
                'category_name': 'Performance',
                'content': [{
                '0': {
                    'bool': True,
                    'text': "Die Antwortzeit der Website ist mit 0,7s ausgezeichnet."
                },
                '1': {
                    'bool': True,
                    'text': "Die Dateigröße der Website ist mit 65kb sehr gut."
                }
                }],
            }],
            
            "points": 100,
            }],

            'serp_preview': [{
            'isCard': False,
            'serp_mobile': [{
                'url': 'http://lichess.org',
                'title': "lichess.org • Kostenloses Online-Schach",
                'description': "Kostenloser Online-Schach-Server. Spiele jetzt auf einer übersichtlichen Benutzeroberfläche Schach! Keine Registrierung und keine Plugins erforderlich, komplett ohne Werbung. Spiele gegen den Computer, Freunde oder zufällige Gegner!",
            }],
            'serp_desktop': [{
                'url': 'http://lichess.org',
                'title': "lichess.org • Kostenloses Online-Schach",
                'description': "Kostenloser Online-Schach-Server. Spiele jetzt auf einer übersichtlichen Benutzeroberfläche Schach! Keine Registrierung und keine Plugins erforderlich, komplett ohne Werbung. Spiele gegen den Computer, Freunde oder zufällige Gegner!",
            }],
            "points": 50,
            }]
        })
        db.session.add(example_website)
        
        db.session.commit()
        print("Example user and analyzed website created.")

if __name__ == "__main__":
    init_db()

