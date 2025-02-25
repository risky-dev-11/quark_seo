from models import TextProvider

file_path = "./static/text-snippets/german.json"
text_provider = TextProvider(file_path)

def get_website_response_time_text(website_response_time):
    if website_response_time < 0.1:
        return text_provider.get_text("website_response_time", "excellent")
    elif 0.1 <= website_response_time < 0.3:
        return text_provider.get_text("website_response_time", "good")
    else:
        return text_provider.get_text("website_response_time", "improveable")

def get_file_size_text(file_size):
    if file_size < 50000:
        return text_provider.get_text("file_size", "excellent")
    elif 50000 <= file_size < 100000:
        return text_provider.get_text("file_size", "good")
    else:
        return text_provider.get_text("file_size", "improveable")

def get_media_count_text(media_count):
    if media_count < 5:
        return text_provider.get_text("media_count", "low")
    elif 5 <= media_count < 15:
        return text_provider.get_text("media_count", "medium")
    else:
        return text_provider.get_text("media_count", "high")

def get_link_count_text(internal_link_count, external_link_count):
    total_links = internal_link_count + external_link_count
    if total_links < 10:
        return text_provider.get_text("link_count", "low")
    elif 10 <= total_links < 30:
        return text_provider.get_text("link_count", "medium")
    else:
        return text_provider.get_text("link_count", "high")

def get_title_missing_text(title_missing_bool):
    key = "missing" if title_missing_bool else "present"
    return text_provider.get_text("title_missing", key)

def get_title_missing_improvement_text():
    return text_provider.get_text("title_missing_improvement", "text")

def get_domain_in_title_text(domain_in_title_bool):
    key = "included" if domain_in_title_bool else "not_included"
    return text_provider.get_text("domain_in_title", key)

def get_title_length_text(title_length):
    if title_length < 50:
        return text_provider.get_text("title_length", "short", length=title_length)
    elif 50 <= title_length <= 60:
        return text_provider.get_text("title_length", "optimal", length=title_length)
    else:
        return text_provider.get_text("title_length", "long", length=title_length)
    
def get_title_incorrect_length_text(title_length):
    key = "too_long" if title_length > 60 else "too_short"
    return text_provider.get_text("incorrect_title_length", key, length=title_length)
   

def get_title_word_repetitions_text(word_repetitions_bool):
    key = "repetitions" if word_repetitions_bool else "no_repetitions"
    return text_provider.get_text("title_word_repetitions", key)

def get_title_word_repetitions_improvement_text(repeated_words):
    return text_provider.get_text("title_word_repetitions_improvement", "text", repeated_words=repeated_words)

def get_description_missing_text(description_missing_bool):
    key = "missing" if description_missing_bool else "present"
    return text_provider.get_text("description_missing", key)

def get_description_length_text(length_pixels):
    if length_pixels < 300:
        return text_provider.get_text("description_length", "short", length=length_pixels)
    elif 300 <= length_pixels <= 960:
        return text_provider.get_text("description_length", "optimal", length=length_pixels)
    else:
        return text_provider.get_text("description_length", "long", length=length_pixels)

def get_language_comment(metatag_language, text_language):
    if metatag_language and text_language:
        if text_language in metatag_language:
            return text_provider.get_text("language", "matching")
        else:
            return text_provider.get_text("language", "not_matching")
    return text_provider.get_text("language", "undetected")

def get_favicon_included_text(favicon_included_bool):
    key = "true" if favicon_included_bool else "false"
    return text_provider.get_text("favicon", key)

def get_comparison_title_text(comparison_title_with_content_bool):
    key = "some_unused" if comparison_title_with_content_bool else "all_used"
    return text_provider.get_text("comparison_title", key)

def get_content_length_comment(word_count):
    if word_count < 800:
        return text_provider.get_text("content_length", "short", word_count=word_count)
    else:
        return text_provider.get_text("content_length", "sufficient", word_count=word_count)

def get_duplicate_text(duplicate_bool):
    key = "true" if duplicate_bool else "false"
    return text_provider.get_text("duplicate_content", key)

def get_alt_attributes_missing_text(alt_attributes_missing_count):
    if alt_attributes_missing_count == 0:
        return text_provider.get_text("alt_attributes", "none")
    elif alt_attributes_missing_count == 1:
        return text_provider.get_text("alt_attributes", "one")
    return text_provider.get_text("alt_attributes", "multiple", count=alt_attributes_missing_count)

def get_h1_heading_text(h1_heading_bool):
    key = "present" if h1_heading_bool else "missing"
    return text_provider.get_text("h1_heading", key)

def get_structure_text(structure_bool):
    key = "correct" if structure_bool else "incorrect"
    return text_provider.get_text("structure", key)

def get_hierarchy_text(hierachy_bool):
    key = "correct" if hierachy_bool else "incorrect"
    return text_provider.get_text("hierarchy", key)

def get_internal_length_linktext_text(length_linktext_internal_bool):
    key = "none" if length_linktext_internal_bool else "some"
    return text_provider.get_text("internal_length_linktext", key)

def get_external_length_linktext_text(length_linktext_external_bool):
    key = "none" if length_linktext_external_bool else "some"
    return text_provider.get_text("external_length_linktext", key)

def get_internal_no_linktext_text(no_linktext_count_internal):
    if no_linktext_count_internal == 0:
        return text_provider.get_text("internal_no_linktext", "none")
    elif no_linktext_count_internal == 1:
        return text_provider.get_text("internal_no_linktext", "one")
    return text_provider.get_text("internal_no_linktext", "multiple", count=no_linktext_count_internal)

def get_external_no_linktext_text(no_linktext_count_external):
    if no_linktext_count_external == 0:
        return text_provider.get_text("external_no_linktext", "none")
    elif no_linktext_count_external == 1:
        return text_provider.get_text("external_no_linktext", "one")
    else:
        return text_provider.get_text("external_no_linktext", "multiple", count=no_linktext_count_external)

def get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool):
    if linktext_repetitions_internal_bool:
        return text_provider.get_text("internal_linktext_repetitions", "true")
    else:
        return text_provider.get_text("internal_linktext_repetitions", "false")
    
def get_external_linktext_repetitions_text(linktext_repetitions_external_bool):
    if linktext_repetitions_external_bool:
        return text_provider.get_text("external_linktext_repetitions", "true")
    else:
        return text_provider.get_text("external_linktext_repetitions", "false")

def get_site_redirects_text(site_redirects_bool):
    if site_redirects_bool:
        return text_provider.get_text("site_redirects", "true")
    else:
        return text_provider.get_text("site_redirects", "false")

def get_redirecting_www_text(redirecting_www_bool):
    if redirecting_www_bool:
        return text_provider.get_text("redirecting_www", "true")
    else:
        return text_provider.get_text("redirecting_www", "false")
    
def get_redirecting_history_text(url):
    return text_provider.get_text("redirecting_history", "text", redirected_url=url)

def get_compression_text(compression, compression_bool):
    if compression_bool:
        return text_provider.get_text("compression", "true", method=compression)
    else:
        return text_provider.get_text("compression", "false")

def get_overall_rating_text(overall_rating):
    if overall_rating < 40:
        return text_provider.get_text("overall_rating", "loe", rating=overall_rating)
    elif 40 <= overall_rating < 55:
        return text_provider.get_text("overall_rating", "medium_low", rating=overall_rating)
    elif 55 <= overall_rating < 70:
        return text_provider.get_text("overall_rating", "medium_high", rating=overall_rating)
    elif 70 <= overall_rating < 90:
        return text_provider.get_text("overall_rating", "high", rating=overall_rating)
    elif 90 <= overall_rating <= 100:
        return text_provider.get_text("overall_rating", "very_high", rating=overall_rating)
    else:
        return text_provider.get_text("overall_rating", "error")

def get_improvement_count_text(improvement_count):
    if improvement_count == 0:
        return text_provider.get_text("improvement_count", "none")
    elif improvement_count == 1:
        return text_provider.get_text("improvement_count", "one")
    else:
        return text_provider.get_text("improvement_count", "multiple", count=improvement_count)