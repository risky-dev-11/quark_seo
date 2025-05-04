def get_website_response_time_text(website_response_time):
    """
    Generates a descriptive text evaluating the website response time.

    Args:
        website_response_time (float): The response time in seconds.

    Returns:
        str: A text describing the response time quality.
    """
    if website_response_time < 0.1:
        return "The website response time is excellent."
    elif 0.1 <= website_response_time < 0.3:
        return "The website response time is good."
    else:
        return "The website response time could be improved."

def get_file_size_text(file_size):
    """
    Generates a descriptive text evaluating the website's file size.

    Args:
        file_size (int): The file size in bytes.

    Returns:
        str: A text describing the file size quality.
    """
    # Optional: Convert bytes to KB for potentially clearer thresholds if desired
    # file_size_kb = file_size / 1024
    if file_size < 50000: # Thresholds kept in bytes as per original logic
        return "The website file size is very good."
    elif 50000 <= file_size < 100000:
        return "The website file size is good."
    else:
        return "The website file size could be improved."

def get_media_count_text(media_count):
    """
    Generates a descriptive text evaluating the number of media elements on the page.

    Args:
        media_count (int): The number of media elements (e.g., images, videos).

    Returns:
        str: A text describing the media count level.
    """
    if media_count < 5:
        return "The number of media elements on the page is low."
    elif 5 <= media_count < 15:
        return "The number of media elements on the page is reasonable."
    else:
        return "The number of media elements on the page is high."

def get_link_count_text(internal_link_count, external_link_count):
    """
    Generates a descriptive text evaluating the total number of internal and external links.

    Args:
        internal_link_count (int): The number of internal links.
        external_link_count (int): The number of external links.

    Returns:
        str: A text describing the total link count level.
    """
    total_links = internal_link_count + external_link_count
    if total_links < 10:
        return "The number of internal and external links is low."
    elif 10 <= total_links < 30:
        return "The number of internal and external links is good."
    else:
        return "The number of internal and external links is high."

def get_title_missing_text(title_missing_bool):
    """
    Indicates whether the page title tag is present or missing.

    Args:
        title_missing_bool (bool): True if the title tag is missing, False otherwise.

    Returns:
        str: A text stating the presence or absence of the title tag.
    """
    if title_missing_bool:
        return "The title tag is missing."
    else:
        return "The title tag is present."

def get_title_missing_improvement_text():
    """
    Provides a suggestion for improvement if the page title tag is missing.

    Returns:
        str: An improvement suggestion text for a missing title tag.
    """
    return "Definitely add a meaningful meta title with relevant keywords! It's essential for search engine optimization as it influences rankings and is the first thing users see in search results. Without it, visibility and click-through rates decrease significantly!"

def get_domain_in_title_text(domain_in_title_bool):
    """
    Indicates whether the domain name is included in the page title tag.

    Args:
        domain_in_title_bool (bool): True if the domain is included, False otherwise.

    Returns:
        str: A text stating if the domain is in the title tag.
    """
    if domain_in_title_bool:
        return "The domain is included in the page title."
    else:
        return "The domain is not included in the page title."

def get_title_length_text(title_length):
    """
    Evaluates the length of the page title tag.

    Args:
        title_length (int): The length of the title in characters.

    Returns:
        str: A text describing if the title length is short, optimal, or long.
    """
    if title_length < 50:
        return f"The title length of {title_length} characters is too short."
    elif 50 <= title_length <= 60:
        return f"The title length of {title_length} characters is optimal."
    else:
        return f"The title length of {title_length} characters is too long."

def get_title_incorrect_length_text(title_length):
    """
    Provides improvement suggestions for non-optimal title tag lengths.

    Args:
        title_length (int): The length of the title in characters.

    Returns:
        str: An improvement suggestion text if the length is not optimal, otherwise an empty string.
    """
    if title_length > 60:
        return f"The title length is {title_length} characters, which is too long. Google typically truncates title tags after 50-60 characters. Ensure the most important information and keywords are placed within this limit for optimal display in search results."
    elif title_length < 50:
        return f"The title length is only {title_length} characters and doesn't utilize the available potential. Google usually displays title tags up to 50-60 characters. It's recommended to use the available space as much as possible to include relevant information and keywords."
    return "" # Return empty string if the length is optimal

def get_title_word_repetitions_text(word_repetitions_bool):
    """
    Indicates if there are repeated words within the page title tag.

    Args:
        word_repetitions_bool (bool): True if repetitions exist, False otherwise.

    Returns:
        str: A text stating whether word repetitions were found in the title.
    """
    if word_repetitions_bool:
        return "There are word repetitions in the title."
    else:
        return "There are no word repetitions in the title."

def get_title_word_repetitions_improvement_text(repeated_words):
    """
    Provides an improvement suggestion regarding word repetitions in the title tag.

    Args:
        repeated_words (str): A string listing the repeated words.

    Returns:
        str: An improvement suggestion text concerning repeated words.
    """
    return f"The following words are repeated: {repeated_words}. Duplicate words in the meta title waste valuable space, reduce readability, and can be perceived as spam, potentially negatively impacting click-through rates and SEO ranking."

def get_description_missing_text(description_missing_bool):
    """
    Indicates whether the meta description tag is present or missing.

    Args:
        description_missing_bool (bool): True if the description is missing, False otherwise.

    Returns:
        str: A text stating the presence or absence of the meta description.
    """
    if description_missing_bool:
        return "The meta description is missing."
    else:
        return "The meta description is present."

def get_description_length_text(length_pixels):
    """
    Evaluates the length of the meta description tag in pixels.

    Args:
        length_pixels (int): The length of the description in pixels.

    Returns:
        str: A text describing if the description length is short, optimal, or long based on pixel width.
    """
    if length_pixels < 300: # Note: Pixel limits can vary and are estimates. Character counts (e.g., < 70, 70-160, > 160) are often used too.
        return f"The description length of {length_pixels} pixels is too short."
    elif 300 <= length_pixels <= 960: # These pixel values are common estimates for Google SERPs
        return f"The description length of {length_pixels} pixels is optimal."
    else:
        return f"The description length of {length_pixels} pixels is too long."

def get_language_comment(metatag_language, text_language):
    """
    Compares the language declared in the meta tag (e.g., `lang` attribute or `http-equiv`)
    with the detected language of the page's main content.

    Args:
        metatag_language (str | None): The language code from the metatag (e.g., 'en', 'en-US').
        text_language (str | None): The detected language code of the main content (e.g., 'en').

    Returns:
        str: A text describing whether the declared and detected languages match.
    """
    if metatag_language and text_language:
        # Normalize or simplify comparison (e.g., check if base languages match)
        meta_base = metatag_language.split('-')[0].lower()
        text_base = text_language.split('-')[0].lower()
        if text_base == meta_base:
            return "The text language matches the metatag language declaration."
        else:
            return f"The detected text language ('{text_language}') does not match the declared metatag language ('{metatag_language}')."
    elif metatag_language and not text_language:
        return f"Language '{metatag_language}' is declared, but the text language could not be detected."
    elif not metatag_language and text_language:
        return f"No language declared via metatag, but the text language was detected as '{text_language}'."
    else:
        return "Could not determine the language for either the text or the metatag."


def get_favicon_included_text(favicon_included_bool):
    """
    Indicates whether a favicon is present and correctly linked on the page.

    Args:
        favicon_included_bool (bool): True if the favicon is detected, False otherwise.

    Returns:
        str: A text stating the presence and correct linkage of the favicon.
    """
    if favicon_included_bool:
        return "Favicon is present and correctly linked."
    else:
        return "Favicon is missing or not correctly linked."

def get_comparison_title_text(comparison_title_with_content_bool):
    """
    Indicates if words from the page title are also found within the main content.

    Args:
        comparison_title_with_content_bool (bool): Interpretation adjusted: True if *all* title words are found in content, False if *some* are unused.

    Returns:
        str: A text describing the usage of title words in the content.
    """
    # Original logic seemed reversed based on comment. Assuming bool means "all_words_found":
    if comparison_title_with_content_bool:
         return "All words from the page title are used in the text/content of the page."
    else:
         return "Some words from the page title are not used in the text/content of the page."


def get_content_length_comment(word_count):
    """
    Provides a comment on the content length based on the word count.

    Args:
        word_count (int): The number of words in the main content.

    Returns:
        str: A comment evaluating the content length.
    """
    if word_count < 800:
        # Consider adding more nuance, e.g., < 300 is very short, 300-800 is short.
        return f"The content, with {word_count} words, is somewhat short. Depending on the website's design and purpose, this might be sufficient, but often more content is better for SEO."
    else: # >= 800
        return f"The content length, with {word_count} words, appears sufficient."

def get_duplicate_text(duplicate_bool):
    """
    Indicates if duplicate content was detected on the page.

    Args:
        duplicate_bool (bool): True if duplicate content is suspected, False otherwise.

    Returns:
        str: A text stating whether duplicate content was found.
    """
    if duplicate_bool:
        return "Duplicate content was detected on the page."
    else:
        return "No duplicate content was detected on the page."

def get_alt_attributes_missing_text(alt_attributes_missing_count):
    """
    Describes how many images are missing their alt attributes.

    Args:
        alt_attributes_missing_count (int): The number of images lacking alt text.

    Returns:
        str: A text stating the count of images missing alt attributes.
    """
    if alt_attributes_missing_count == 0:
        return "All images have an alt attribute."
    elif alt_attributes_missing_count == 1:
        return "One image is missing its alt attribute."
    else:
        return f"{alt_attributes_missing_count} images are missing their alt attributes."

def get_h1_heading_text(h1_heading_bool):
    """
    Indicates whether an H1 heading tag is present on the page.

    Args:
        h1_heading_bool (bool): True if at least one H1 tag is present, False otherwise.

    Returns:
        str: A text stating the presence or absence of an H1 heading.
    """
    if h1_heading_bool:
        return "An H1 heading is present."
    else:
        return "The H1 heading is missing."

def get_structure_text(structure_bool):
    """
    Indicates if the heading structure (H1-H6) follows a logical order (e.g., no H3 before H2).
    Note: This often implies hierarchy as well. Clarify if distinct checks.

    Args:
        structure_bool (bool): True if the structure is considered correct, False otherwise.

    Returns:
        str: A text evaluating the heading structure.
    """
    if structure_bool:
        return "The heading structure is correct."
    else:
        return "The heading structure is incorrect (e.g., out of order)."

def get_hierarchy_text(hierarchy_bool):
    """
    Indicates if the heading hierarchy is correct (e.g., no skipped levels like H1 then H3).

    Args:
        hierarchy_bool (bool): True if the hierarchy is correct, False otherwise.

    Returns:
        str: A text evaluating the heading hierarchy.
    """
    if hierarchy_bool:
        return "The heading hierarchy is correct."
    else:
        return "The heading hierarchy is incorrect (e.g., levels skipped)."

def get_internal_length_linktext_text(length_linktext_internal_bool):
    """
    Indicates if any internal link texts exceed a recommended length.

    Args:
        length_linktext_internal_bool (bool): True if at least one internal link text is too long, False otherwise.

    Returns:
        str: A text stating whether any internal link texts are too long.
    """
    if length_linktext_internal_bool:
        return "Some internal link texts are too long."
    else:
        return "No internal link texts are too long."


def get_external_length_linktext_text(length_linktext_external_bool):
    """
    Indicates if any external link texts exceed a recommended length.

    Args:
        length_linktext_external_bool (bool): True if at least one external link text is too long, False otherwise.

    Returns:
        str: A text stating whether any external link texts are too long.
    """
    if length_linktext_external_bool:
        return "Some external link texts are too long."
    else:
        return "No external link texts are too long."


def get_internal_no_linktext_text(no_linktext_count_internal):
    """
    Describes how many internal links lack visible link text (relying only on alt/title or empty).

    Args:
        no_linktext_count_internal (int): The count of internal links without proper text content.

    Returns:
        str: A descriptive text about internal links missing text.
    """
    if no_linktext_count_internal == 0:
        return "All internal links have link text."
    elif no_linktext_count_internal == 1:
        return "One internal link has no link text or only content in alt/title attributes."
    else:
        return f"{no_linktext_count_internal} internal links have no link text or only content in alt/title attributes."

def get_external_no_linktext_text(no_linktext_count_external):
    """
    Describes how many external links lack visible link text (relying only on alt/title or empty).

    Args:
        no_linktext_count_external (int): The count of external links without proper text content.

    Returns:
        str: A descriptive text about external links missing text.
    """
    if no_linktext_count_external == 0:
        return "All external links have link text."
    elif no_linktext_count_external == 1:
        return "One external link has no link text or only content in alt/title attributes."
    else:
        return f"{no_linktext_count_external} external links have no link text or only content in alt/title attributes."

def get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool):
    """
    Indicates if there are identical link texts used for different internal link destinations.

    Args:
        linktext_repetitions_internal_bool (bool): True if repetitions targeting different URLs exist, False otherwise.

    Returns:
        str: A text stating whether internal link text repetitions were found.
    """
    if linktext_repetitions_internal_bool:
        return "Some internal link texts are repeated (used for different target URLs)."
    else:
        return "There are no repetitions among internal link texts pointing to different URLs."

def get_external_linktext_repetitions_text(linktext_repetitions_external_bool):
    """
    Indicates if there are identical link texts used for different external link destinations.

    Args:
        linktext_repetitions_external_bool (bool): True if repetitions targeting different URLs exist, False otherwise.

    Returns:
        str: A text stating whether external link text repetitions were found.
    """
    if linktext_repetitions_external_bool:
        return "Some external link texts are repeated (used for different target URLs)."
    else:
        return "There are no repetitions among external link texts pointing to different URLs."

def get_site_redirects_text(site_redirects_bool):
    """
    Indicates if the originally analyzed URL resulted in a redirect.

    Args:
        site_redirects_bool (bool): True if the initial URL redirected, False otherwise.

    Returns:
        str: A text stating whether the analyzed URL itself redirected.
    """
    if site_redirects_bool:
        return "The analyzed page redirects to another URL."
    else:
        return "The analyzed page does not redirect."

def get_redirecting_www_text(redirecting_www_bool):
    """
    Indicates if redirection between www and non-www versions of the domain is correctly configured
    (i.e., one version consistently redirects to the other).

    Args:
        redirecting_www_bool (bool): True if www/non-www redirection is consistent, False otherwise.

    Returns:
        str: A text evaluating the www/non-www redirection setup.
    """
    if redirecting_www_bool:
        return "Redirection between www and non-www addresses is configured correctly."
    else:
        return "Redirection between www and non-www addresses is not configured correctly (or consistently)."

def get_redirecting_history_text(url):
    """
    Describes a redirection that occurred during the analysis, showing the target URL.

    Args:
        url (str): The URL the page redirected to.

    Returns:
        str: A text stating the redirection target.
    """
    return f"A redirection occurred to the page: {url}."

def get_compression_text(compression: str | None, compression_bool: bool) -> str:
    """
    Indicates if web server compression (like gzip or brotli) is enabled for transferring the webpage.

    Args:
        compression (str | None): The formatted compression method (e.g., 'Brotli (br)', 'Unknown (xyz)'), or 'None'.
        compression_bool (bool): True if compression is enabled, False otherwise.

    Returns:
        str: A text stating whether compression is used and, if so, which type.
    """
    if compression_bool and compression and compression.lower() != 'None':
        return f"The web server uses {compression} for compressed transmission of the webpage."
    elif compression_bool:
        return "The web server uses compression for the transmission of the webpage."
    else:
        return "The web server does not use compression for the transmission of the webpage."


def get_overall_rating_text(overall_rating):
    """
    Provides a summary text based on the overall SEO rating score.

    Args:
        overall_rating (int): The overall rating score (expected range 0-100).

    Returns:
        str: A summary text evaluating the overall optimization level.
    """
    if 0 <= overall_rating < 40:
        return f"The analyzed webpage has an overall rating of {overall_rating} out of 100 points. The webpage is not optimized. There are many opportunities for improvement."
    elif 40 <= overall_rating < 55:
        return f"The analyzed webpage has an overall rating of {overall_rating} out of 100 points. The webpage is poorly optimized. There are several opportunities for improvement."
    elif 55 <= overall_rating < 70:
        return f"The analyzed webpage has an overall rating of {overall_rating} out of 100 points. The webpage is partially optimized. There are still some opportunities for improvement."
    elif 70 <= overall_rating < 90:
        return f"The analyzed webpage has an overall rating of {overall_rating} out of 100 points. The webpage is well optimized. There are few opportunities for improvement."
    elif 90 <= overall_rating <= 100:
        return f"The analyzed webpage has an overall rating of {overall_rating} out of 100 points. The website is excellently optimized. There are hardly any opportunities for improvement."
    else:
        # Handle unexpected rating values
        return f"An error occurred during rating calculation (Score: {overall_rating}). Please try again."

def get_improvement_count_text(improvement_count):
    """
    States the number of improvement suggestions identified during the analysis.

    Args:
        improvement_count (int): The number of identified improvement points.

    Returns:
        str: A text summarizing the count of improvement opportunities.
    """
    if improvement_count < 0: # Handle potential negative counts if errors occur upstream
        return "An error occurred calculating improvement opportunities."
    elif improvement_count == 0:
        return "No opportunities for improvement were found."
    elif improvement_count == 1:
        return "One opportunity for improvement was found."
    else:
        return f"{improvement_count} opportunities for improvement were found."