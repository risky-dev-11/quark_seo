def get_website_response_time_text(website_response_time):
    if website_response_time < 0.1:
        return "Die Antwortzeit der Website ist ausgezeichnet."
    elif 0.1 <= website_response_time < 0.3:
        return "Die Antwortzeit der Website ist gut."
    else:
        return "Die Antwortzeit der Website könnte verbessert werden."

def get_file_size_text(file_size):
    if file_size < 50000:
        return "Die Dateigröße der Website ist sehr gut."
    elif 50000 <= file_size < 100000:
        return "Die Dateigröße der Website ist gut."
    else:
        return "Die Dateigröße der Website könnte verbessert werden."

def get_media_count_text(media_count):
    if media_count < 5:
        return "Die Anzahl der Medien auf der Seite ist gering."
    elif 5 <= media_count < 15:
        return "Die Anzahl der Medien auf der Seite ist angemessen."
    else:
        return "Die Anzahl der Medien auf der Seite ist hoch."

def get_link_count_text(internal_link_count, external_link_count):
    total_links = internal_link_count + external_link_count
    if total_links < 10:
        return "Die Anzahl der internen und externen Links ist gering."
    elif 10 <= total_links < 30:
        return "Die Anzahl der internen und externen Links ist gut."
    else:
        return "Die Anzahl der internen und externen Links ist hoch."
    
def get_title_missing_text(title_missing_bool):
    return "Der Titel fehlt." if title_missing_bool else "Der Titel ist vorhanden."

def get_domain_in_title_text(domain_in_title_bool):
    return "Die Domain steht im Seitentitel." if domain_in_title_bool else "Die Domain steht nicht im Seitentitel."


def get_title_length_text(title_length):
    if title_length < 35:
        return f"Die Länge des Titels ist mit {title_length} Zeichen zu kurz."
    elif 35 <= title_length <= 60:
        return f"Die Länge des Titels ist mit {title_length} Zeichen optimal."
    else:
        return f"Die Länge des Titels ist mit {title_length} Zeichen zu lang."

def get_title_word_repetitions_text(word_repetitions_bool):
    if not word_repetitions_bool:
        return "Es gibt keine Wortwiederholungen im Titel."
    else:
        return "Es gibt Wortwiederholungen im Titel."

def get_description_missing_text(description_missing_bool):
    return "Die Beschreibung fehlt." if description_missing_bool else "Die Beschreibung ist vorhanden."

def get_description_length_text(length_pixels):
    if length_pixels < 300:
        return f"Die Beschreibung ist mit {length_pixels} Pixeln zu kurz! Eine gute Beschreibung sollte mindestens 300 Pixel (etwa 50 Zeichen) lang sein."
    elif 300 <= length_pixels <= 960:
        return f"Die Länge der Beschreibung ist mit {length_pixels} Pixeln in Ordnung."
    else:
        return f"Die Beschreibung ist mit {length_pixels} Pixeln zu lang! Maximale Länge sind 960 Pixel (etwa 160 Zeichen)."

def get_language_comment(metatag_language, text_language):
    if metatag_language and text_language:
        if text_language in metatag_language:
            return "Die Sprache des Texts entspricht der Sprache des Metatags."
        else:
            return "Die Sprache des Texts entspricht nicht der Sprache des Metatags."
    return "Es konnte keine Sprache für den Text oder den Metatag ermittelt werden."

def get_favicon_included_text(favicon_included_bool):
    return "Favicon ist vorhanden und korrekt eingebunden." if favicon_included_bool else "Favicon fehlt oder ist nicht korrekt eingebunden."

def get_comparison_title_text(comparison_title_with_content_bool):
    if comparison_title_with_content_bool:
        return "Einige Wörter aus dem Seitentitel werden nicht im Text bzw. Inhalt der Seite verwendet."
    else:
        return "Alle Wörter aus dem Seitentitel werden im Text bzw. Inhalt der Seite verwendet."

def get_content_length_comment(word_count):
    if word_count < 800:
        return f"Der Inhalt ist mit {word_count} Wörtern etwas kurz. Eine gute Seite zu einem Thema sollte Text mit etwa 800 Wörtern enthalten."
    else:
        return f"Der Inhalt ist mit {word_count} Wörtern ausreichend."

def get_duplicate_text(duplicate_bool):
    return "Es gibt keine doppelten Inhalte auf der Seite." if duplicate_bool else "Es gibt doppelte Inhalte auf der Seite."

def get_alt_attributes_missing_text(alt_attributes_missing_count):
    if alt_attributes_missing_count == 0:
        return "Alle Bilder haben ein Alt-Attribut."
    elif alt_attributes_missing_count == 1:
        return "Bei einem Bild fehlt das Alt-Attribut. Der Inhalt von Alt-Attributen wird von Suchmaschinen auch als Text gewertet und ist wichtig für die Bildersuche."
    return f"Bei {alt_attributes_missing_count} Bildern fehlt das Alt-Attribut. Der Inhalt von Alt-Attributen wird von Suchmaschinen auch als Text gewertet und ist wichtig für die Bildersuche."

def get_h1_heading_text(h1_heading_bool):
    return "H1-Überschrift ist vorhanden." if h1_heading_bool else "H1-Überschrift fehlt."

def get_structure_text(structure_bool):
    return "Die Hierachie der Überschriften wurde eingehalten." if structure_bool else "Die Seitenstruktur ist nicht optimal. Die Hierachie der Überschriften (H1-H6) sollte eingehalten werden."

def get_internal_length_linktext_text(length_linktext_internal_bool):
    return "Keiner der internen Linktexte ist zu lang." if length_linktext_internal_bool else "Einige der internen Linktexte sind zu lang."

def get_internal_no_linktext_text(no_linktext_count_internal):
    if no_linktext_count_internal == 0:
        return "Alle internen Links haben einen Linktext."
    elif no_linktext_count_internal == 1:
        return "Ein interner Link hat keinen Linktext oder nur Inhalt in Alt- und Titelattributen."
    else:
        return f"{no_linktext_count_internal} interne Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen."

def get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool):
    return "Einige der internen Linktexte wiederholen sich." if linktext_repetitions_internal_bool else "Es gibt keine Wiederholungen bei den internen Linktexten."

def get_external_length_linktext_text(length_linktext_external_bool):
    return "Keiner der externen Linktexte ist zu lang." if length_linktext_external_bool else "Einige der externen Linktexte sind zu lang."

def get_external_no_linktext_text(no_linktext_count_external):
    if no_linktext_count_external == 0:
        return "Alle externen Links haben einen Linktext."
    elif no_linktext_count_external == 1:
        return "Ein externer Link hat keinen Linktext oder nur Inhalt in Alt- und Titelattributen."
    else:
        return f"{no_linktext_count_external} externe Links haben keinen Linktext oder nur Inhalt in Alt- und Titelattributen."

def get_external_linktext_repetitions_text(linktext_repetitions_external_bool):
    return "Einige der externen Linktexte wiederholen sich." if linktext_repetitions_external_bool else "Es gibt keine Wiederholungen bei den externen Linktexten."

