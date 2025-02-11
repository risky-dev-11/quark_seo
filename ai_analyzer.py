import json
from dotenv import load_dotenv
import os
from openai import OpenAI 

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# Tool for AI-Feedback for the description
description = [{
        "type": "function",
        "function": {
            "name": "rate_website_description",
            "description": "Bewerte bitte die Beschreibung der Webseite. Bewerte, ob die Beschreibung eine gute Zusammenfassung ist, sie prägnant und klar ist, Schlüsselwörter verwendet werden, sie einen Unique Selling Point hervorheben, nicht die Länge von 155 Zeichen überschreitet und eine Handlungsaufforderung enthält.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "integer",
                        "description": "Bewertung der Beschreibung auf einer Skala von 1-100."
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
title = [{
        "type": "function",
        "function": {
            "name": "rate_website_title",
            "description": "Bitte bewerte den Titel der Webseite daraufhin, ob er die Länge von 55 Zeichen nicht überschreitet, das Haupt-Keyword an erster Stelle oder zumindest am Anfang steht, kein Keyword-Spamming enthält, einen Marken- oder Firmennamen nutzt, eine klare Handlungsaufforderung beinhaltet und Sonderzeichen passend zur Hervorhebung verwendet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rating": {
                        "type": "integer",
                        "description": "Bewertung des Titels auf einer Skala von 1-100."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Eine knappe Bewertung des Titels nach den Kriterien."
                    },
                    "improvement": {
                        "type": "string",
                        "description": "Vorschläge zur Verbesserung des Titels - falls die Kriterien nicht erfüllt sind!"
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





def ai_analyzer(website_description, website_title):
    
    client = OpenAI(api_key=openai_api_key, max_retries=1)

    # Bewertung der Beschreibung
    completion_description = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Bitte bewerte die Beschreibung einer Webseite - Verwende Formulierungen wie 'Die Beschreibung deiner Webseite' - ###Beginn der Beschreibung###{website_description}.###Ende der Beschreibung###"}],
        tools=description,
        tool_choice = {"type": "function", "function": {"name": "rate_website_description"}}
    )

    ai_output_description = json.loads(completion_description.choices[0].message.tool_calls[0].function.arguments)


    # Bewertung des Titels
    completion_title = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Bitte bewerte den Titel einer Webseite - Verwende Formulierungen wie 'Der Titel deiner Webseite' - ###Beginn des Titels###{website_title}.###Ende des  Titels###"}],
        tools=title,
        tool_choice = {"type": "function", "function": {"name": "rate_website_title"}}
    )

    ai_output_title = json.loads(completion_title.choices[0].message.tool_calls[0].function.arguments)

    return {
        "description_rating": ai_output_description['rating'],
        "description_reason": ai_output_description['reason'],
        "description_improvement": ai_output_description['improvement'],
        "title_rating": ai_output_title['rating'],
        "title_reason": ai_output_title['reason'],
        "title_improvement": ai_output_title['improvement']
    }