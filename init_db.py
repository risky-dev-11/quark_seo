from app import db
from run import flask_app
from models import User, AnalyzedWebsite
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(flask_app)

def init_db():
    with flask_app.app_context():
        db.drop_all()  # Drop all tables
        db.create_all()  # Create all tables
        print("Database tables created.")
        
        # Create an example user
        hashed_password = bcrypt.generate_password_hash('1234').decode('utf-8')
        example_user = User(first_name='Niklas', last_name='Werthmann', email='n11werthmann@gmail.com', password=hashed_password, role='user')
        db.session.add(example_user)
        
        # Create an example analyzed website
        example_website = AnalyzedWebsite(user_uuid=1, url='example.com', results={
            "general_results": {
            "isCard": False,
            "website_response_time": 0.749074,
            "website_response_time_text": "Die Antwortzeit der Website könnte verbessert werden.",
            "file_size": "39.872 kB",
            "file_size_text": "Die Dateigröße der Website ist sehr gut.",
            "word_count": 508,
            "word_count_text": "Hier gibt grundsätzlich es kein richtig oder falsch.",
            "media_count": 17,
            "media_count_text": "Die Anzahl der Medien auf der Seite ist hoch.",
            "link_count": "23 Intern / 101 Extern",
            "link_count_text": "Die Anzahl der internen und externen Links ist hoch."
            },
            "metadaten": {
            "isCard": True,
            "card_name": "Metadaten",
            "points": 62.5,
            "titel": {
                "category_name": "Titel",
                "content": [
                {"bool": True, "text": "Der Titel ist vorhanden."},
                {"bool": "", "text": "lichess.org • Free Online Chess"},
                {"bool": False, "text": "Die Domain steht im Seitentitel."},
                {"bool": False, "text": "Die Länge des Titels ist mit 31 Zeichen zu kurz."},
                {"bool": True, "text": "Es gibt keine Wortwiederholungen im Titel."}
                ]
            },
            "beschreibung": {
                "category_name": "Beschreibung",
                "content": [
                {"bool": True, "text": "Die Beschreibung ist vorhanden."},
                {"bool": "", "text": "Free online chess server. Play chess in a clean interface. No registration, no ads, no plugin required. Play chess with the computer, friends or random opponents."},
                {"bool": False, "text": "Die Beschreibung ist mit 990 Pixeln zu lang."}
                ]
            },
            "sprache": {
                "category_name": "Sprache",
                "content": [
                {"bool": "", "text": "Meta/HTML-Sprache: en-GB"},
                {"bool": "", "text": "Im Text erkannte Sprache: en"},
                {"bool": "", "text": "Serverstandort: France"},
                {"bool": True, "text": "Die Sprache des Texts entspricht der Sprache des Metatags."}
                ]
            },
            "favicon": {
                "category_name": "Favicon",
                "content": [
                {"bool": True, "text": "Favicon ist vorhanden und korrekt eingebunden."}
                ]
            }
            },
            "seitenqualität": {
            "isCard": True,
            "card_name": "Seitenqualität",
            "points": 50.0,
            "inhalt": {
                "category_name": "Inhalt",
                "content": [
                {"bool": True, "text": "Einige Wörter aus dem Seitentitel werden nicht im Text bzw. Inhalt der Seite verwendet."},
                {"bool": True, "text": "Der Inhalt ist mit 508 Wörtern etwas kurz."},
                {"bool": False, "text": "Es gibt keine doppelten Inhalte auf der Seite."}
                ]
            },
            "bilder": {
                "category_name": "Bilder",
                "content": [
                {"bool": False, "text": "Bei 15 Bildern fehlt das Alt-Attribut."}
                ]
            }
            },
            "seitenstruktur": {
            "isCard": True,
            "card_name": "Seitenstruktur",
            "points": 50.0,
            "überschriften": {
                "category_name": "Überschriften",
                "content": [
                {"bool": False, "text": "H1-Überschrift fehlt."},
                {"bool": True, "text": "Die Hierachie der Überschriften wurde eingehalten."}
                ]
            }
            },
            "links": {
            "isCard": True,
            "card_name": "Links",
            "points": 50.0,
            "interne links": {
                "category_name": "Interne Links",
                "content": [
                {"bool": True, "text": "Keiner der internen Linktexte ist zu lang."},
                {"bool": False, "text": "Einige der internen Linktexte sind zu lang."},
                {"bool": False, "text": "Alle internen Links haben einen Linktext."},
                {"bool": False, "text": "Es gibt keine Wiederholungen bei den internen Linktexten."}
                ]
            },
            "externe links": {
                "category_name": "Externe Links",
                "content": [
                {"bool": True, "text": "Keiner der externen Linktexte ist zu lang."},
                {"bool": False, "text": "Einige der externen Linktexte sind zu lang."},
                {"bool": True, "text": "Ein externer Link hat keinen Linktext oder nur Inhalt in Alt- und Titelattributen."},
                {"bool": True, "text": "Einige der externen Linktexte wiederholen sich."}
                ]
            }
            },
            "server": {
            "isCard": True,
            "card_name": "Server",
            "points": 100.0,
            "weiterleitungen": {
                "category_name": "Weiterleitungen",
                "content": [
                {"bool": True, "text": "Die Seite leitet auf eine andere Seite um."},
                {"bool": True, "text": "Die Weiterleitung von Adressen mit und ohne www. ist korrekt konfiguriert."}
                ]
            },
            "komprimierung": {
                "category_name": "Komprimierung",
                "content": [
                {"bool": True, "text": "Der Webserver nutzt br zur komprimierten Übertragung der Webseite."}
                ]
            }
            },
            "serp_preview": {
            "isCard": False,
            "serp_mobile": {
                "url": "http://lichess.org",
                "title": "lichess.org • Free Online Chess",
                "description": "Free online chess server. Play chess in a clean interface. No registration, no ads, no plugin required. Play chess with the computer, friends or random opponents."
            },
            "serp_desktop": {
                "url": "http://lichess.org",
                "title": "lichess.org • Free Online Chess",
                "description": "Free online chess server. Play chess in a clean interface. No registration, no ads, no plugin required. Play chess with the computer, friends or random opponents."
            },
            "points": 50
            },
            "overall_results": {
            "isCard": False,
            "overall_rating": 60,
            "overall_rating_text": "Die analysierte Webseite hat eine Gesamtbewertung von 60 von 100 Punkten. Die Webseite ist teilweise optimiert. Es bestehen noch einige Verbesserungsmöglichkeiten.",
            "improvement_count": 10,
            "improvement_count_text": "Es wurden 10 Verbesserungsmöglichkeiten gefunden."
            }
        })
        db.session.add(example_website)
        
        db.session.commit()
        print("Example user and analyzed website created.")

if __name__ == "__main__":
    init_db()

