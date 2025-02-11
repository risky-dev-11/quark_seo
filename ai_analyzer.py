from dotenv import load_dotenv
import os
from openai import OpenAI 

load_dotenv()

def ai_analyzer(website_description, website_title):
    openai_api_key = os.getenv('OPENAI_API_KEY')

    client = OpenAI(api_key=openai_api_key, max_retries=1)



    # Bewertung der Beschreibung

    description = [{
        "type": "function",
        "function": {
            "name": "rate_website_description",
            "description": "Bewerte bitte die Beschreibung der Webseite. Bewerte, ob die Beschreibung eine gute Zusammenfassung ist, sie prägnant und klar ist, Schlüsselwörter verwendet werden, sie einen Unique Selling Point hervorheben, nicht die Länge von 155 Zeichen überschreitet und eine Handlungsaufforderung enthält.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "string",
                        "description": "Bewertung der Beschreibung von einer Skala von 1-100."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Eine knappe Bewertung der Beschreibung nach den Kriterien."
                    },
                    "improvement": {
                        "type": "string",
                        "description": "Vorschläge zur Verbesserung der Beschreibung - falls die Kriterien nicht erfüllt sind!"
                    },
                },
                "required": [
                    "rating",
                    "reason",
                    "improvement"
                ],
                "additionalProperties": False
            },
            "strict": True
        }
    }]

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Bitte bewerte die Beschreibung einer Webseite - Verwende Formulierungen wie 'Die Beschreibung deiner Webseite' - ###Beginn der Beschreibung###{website_description}.###Ende der Beschreibung###"}],
        tools=description,
        tool_choice = {"type": "function", "function": {"name": "rate_website_description"}}
    )

    print(completion.choices[0].message.tool_calls)


    # Bewertung des Titels

ai_analyzer("Kostenloser Online-Schach-Server. Spiele jetzt auf einer übersichtlichen Benutzeroberfläche Schach! Keine Registrierung und keine Plugins erforderlich, komplett ohne Werbung. Spiele gegen den Computer, Freunde oder zufällige Gegner!", "lichess.org • Kostenloses Online-Schach")
