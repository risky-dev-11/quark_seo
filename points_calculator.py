def calculate_metadata_points(title_missing_bool, domain_in_title_bool, title_length, word_repetitions_bool, description_missing_bool, length_pixels, metatag_language, points_language, favicon_included_bool):
    max_points = 29
    points = 0
    points += get_title_missing_points(title_missing_bool)
    points += get_domain_in_title_points(domain_in_title_bool)
    points += get_title_length_points(title_length)
    points += get_title_word_repetitions_points(word_repetitions_bool)
    points += get_description_missing_points(description_missing_bool)
    points += get_description_length_points(length_pixels)
    points += get_language_comment(metatag_language, points_language)
    points += get_favicon_included_points(favicon_included_bool)
    return round((points / max_points) * 100)

def get_title_missing_points(title_missing_bool):
    return 0 if title_missing_bool else 5

def get_domain_in_title_points(domain_in_title_bool):
    return 0 if domain_in_title_bool else 2

def get_title_length_points(title_length):
    if title_length < 35:
        return 0
    elif 35 <= title_length <= 60:
        return 3
    else:
        return 0

def get_title_word_repetitions_points(word_repetitions_bool):
    if not word_repetitions_bool:
        return 3
    else:
        return 0

def get_description_missing_points(description_missing_bool):
    return 0 if description_missing_bool else 5

def get_description_length_points(length_pixels):
    if length_pixels < 300:
        return 0
    elif 300 <= length_pixels <= 960:
        return 3
    else:
        return 0

def get_language_comment(metatag_language, points_language):
    if metatag_language and points_language:
        if points_language in metatag_language:
            return 3
        else:
            return 0
    return 0

def get_favicon_included_points(favicon_included_bool):
    return 4 if favicon_included_bool else 0

#####################################################################################################

def calculate_pagequality_points(comparison_title_with_content_bool, word_count, duplicate_bool, alt_attributes_missing_count):
    max_points = 12
    points = 0
    points += get_comparison_title_points(comparison_title_with_content_bool)
    points += get_content_length_comment(word_count)
    points += get_duplicate_points(duplicate_bool)
    points += get_alt_attributes_missing_points(alt_attributes_missing_count)
    return round((points / max_points) * 100)

def get_comparison_title_points(comparison_title_with_content_bool):
    if comparison_title_with_content_bool:
        return 0
    else:
        return 3

def get_content_length_comment(word_count):
    if word_count < 800:
        return 0
    else:
        return 1

def get_duplicate_points(duplicate_bool):
    return 4 if duplicate_bool else 0

def get_alt_attributes_missing_points(alt_attributes_missing_count):
    if alt_attributes_missing_count == 0:
        return 4
    elif alt_attributes_missing_count == 1:
        return 3
    return 0

#####################################################################################################

def calculate_pagestructure_points(h1_heading_bool, structure_bool):
    max_points = 5
    points = 0
    points += get_h1_heading_points(h1_heading_bool)
    points += get_structure_points(structure_bool)
    return round((points / max_points) * 100)

def get_h1_heading_points(h1_heading_bool):
    return 3 if h1_heading_bool else 0

def get_structure_points(structure_bool):
    return 2 if structure_bool else 0

#####################################################################################################

def calculate_links_points(length_linkpoints_internal_bool, no_linkpoints_count_internal, linkpoints_repetitions_internal_bool, length_linkpoints_external_bool, no_linkpoints_count_external, linkpoints_repetitions_external_bool):
    max_points = 14
    points = 0
    points += get_internal_length_linkpoints_points(length_linkpoints_internal_bool)
    points += get_internal_no_linkpoints_points(no_linkpoints_count_internal)
    points += get_internal_linkpoints_repetitions_points(linkpoints_repetitions_internal_bool)
    points += get_external_length_linkpoints_points(length_linkpoints_external_bool)
    points += get_external_no_linkpoints_points(no_linkpoints_count_external)
    points += get_external_linkpoints_repetitions_points(linkpoints_repetitions_external_bool)
    return round((points / max_points) * 100)

def get_internal_length_linkpoints_points(length_linkpoints_internal_bool):
    return 2 if length_linkpoints_internal_bool else 0

def get_internal_no_linkpoints_points(no_linkpoints_count_internal):
    if no_linkpoints_count_internal == 0:
        return 3
    elif no_linkpoints_count_internal == 1:
        return 2
    else:
        return 0

def get_internal_linkpoints_repetitions_points(linkpoints_repetitions_internal_bool):
    return 0 if linkpoints_repetitions_internal_bool else 2

def get_external_length_linkpoints_points(length_linkpoints_external_bool):
    return 2 if length_linkpoints_external_bool else 0

def get_external_no_linkpoints_points(no_linkpoints_count_external):
    if no_linkpoints_count_external == 0:
        return 3
    elif no_linkpoints_count_external == 1:
        return 2
    else:
        return 0
def get_external_linkpoints_repetitions_points(linkpoints_repetitions_external_bool):
    return 0 if linkpoints_repetitions_external_bool else 2

#####################################################################################################

def calculate_server_points(site_redirects_bool, redirecting_www_bool, compression_bool):
    max_points = 9
    points = 0
    points += get_site_redirects_points(site_redirects_bool)
    points += get_redirecting_www_points(redirecting_www_bool)
    points += get_compression_points(compression_bool)
    return round((points / max_points) * 100)

def get_site_redirects_points(site_redirects_bool):
    return 0 if site_redirects_bool else 3

def get_redirecting_www_points(redirecting_www_bool):
    return 3 if redirecting_www_bool else 0

def get_compression_points(compression_bool):
    return 3 if compression_bool else 0