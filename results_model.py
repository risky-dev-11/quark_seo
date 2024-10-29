class Content:
    def __init__(self, bool, text):
        self.bool = bool
        self.text = text

    def to_dict(self):
        return {
            'bool': self.bool,
            'text': self.text
        }

class Category:
    def __init__(self, category_name):
        self.category_name = category_name
        self.content = []

    def add_content(self, bool, text):
        self.content.append(Content(bool, text).to_dict())

    def to_dict(self):
        return {
            'category_name': self.category_name,
            'content': self.content
        }

class Card:
    def __init__(self, card_name, points):
        self.card_name = card_name
        self.points = points
        self.is_card = True
        self.categories = {}

    def add_category(self, category):
        self.categories[category.category_name.lower()] = category.to_dict()

    def to_dict(self):
        return {
            'isCard': self.is_card,
            'card_name': self.card_name,
            'points': self.points,
            **self.categories
        }

    def add_to_results(self, results):
        results[self.card_name.lower()] = self.to_dict()

# EXAMPLE USAGE
#
#
# results = {}
#
# # Metadata results
# card = Card('Metadaten', metadata_points)
# category = Category('Titel')
#
# category.add_content(title_missing_bool, get_title_missing_text(title_missing_bool))
# category.add_content('', title_text if not title_missing_bool else '')
# category.add_content(not domain_in_title_bool, get_domain_in_title_text(domain_in_title_bool))
# category.add_content(not title_length_bool, get_title_length_text(title_length))
# category.add_content(not title_word_repetitions_bool, get_title_word_repetitions_text(title_word_repetitions_bool))
#
# card.add_category(category)
#
# category = Category('Beschreibung')
#
# category.add_content(description_missing_bool, get_description_missing_text(description_missing_bool))
# category.add_content('', description_of_the_website if not description_missing_bool else '')
# category.add_content(not description_length_bool, get_description_length_text(length_pixels))
#
# card.add_category(category)
#
# card.add_to_results(results)
#
# # Links results
# card = Card('Links', links_points)
#
# category = Category('Interne Links')
# category.add_content(length_linktext_internal_bool, get_internal_length_linktext_text(length_linktext_internal_bool))
# category.add_content(no_linktext_count_internal_bool, get_internal_no_linktext_text(no_linktext_count_internal_bool))
# category.add_content(not linktext_repetitions_internal_bool, get_internal_linktext_repetitions_text(linktext_repetitions_internal_bool))
# card.add_category(category)
#
# category = Category('Externe Links')
# category.add_content(length_linktext_external_bool, get_external_length_linktext_text(length_linktext_external_bool))
# category.add_content(no_linktext_count_external_bool, get_external_no_linktext_text(no_linktext_count_external_bool))
# category.add_content(not linktext_repetitions_external_bool, get_external_linktext_repetitions_text(linktext_repetitions_external_bool))
# card.add_category(category)
#
# card.add_to_results(results)
#
# print(results)