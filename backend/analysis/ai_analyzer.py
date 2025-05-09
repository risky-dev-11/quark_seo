import asyncio
import json
from openai import OpenAI

from backend.config.env import OPENAI_API_KEY

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

async def ai_analyzer(website_description, website_title):
    client = OpenAI(api_key=OPENAI_API_KEY)

    description_message = [{
        "role": "user",
        "content": (
            f"Bitte bewerte die Beschreibung einer Webseite - Verwende Formulierungen wie 'Die Beschreibung deiner Webseite' - "
            f"###Beginn der Beschreibung###{website_description}.###Ende der Beschreibung###"
        )
    }]
    title_message = [{
        "role": "user",
        "content": (
            f"Bitte bewerte den Titel einer Webseite - Verwende Formulierungen wie 'Der Titel deiner Webseite' - "
            f"###Beginn des Titels###{website_title}.###Ende des Titels###"
        )
    }]

    # Use asyncio.to_thread to run the synchronous create() calls concurrently.
    task_description = asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o",
        messages=description_message,
        tools=description,
        tool_choice={"type": "function", "function": {"name": "rate_website_description"}}
    )
    task_title = asyncio.to_thread(
        client.chat.completions.create,
        model="gpt-4o",
        messages=title_message,
        tools=title,
        tool_choice={"type": "function", "function": {"name": "rate_website_title"}}
    )

    completion_description, completion_title = await asyncio.gather(task_description, task_title)

    ai_output_description = json.loads(completion_description.choices[0].message.tool_calls[0].function.arguments)
    ai_output_title = json.loads(completion_title.choices[0].message.tool_calls[0].function.arguments)

    return {
        "description_rating": ai_output_description['rating'],
        "description_reason": ai_output_description['reason'],
        "description_improvement": ai_output_description['improvement'],
        "title_rating": ai_output_title['rating'],
        "title_reason": ai_output_title['reason'],
        "title_improvement": ai_output_title['improvement']
    }