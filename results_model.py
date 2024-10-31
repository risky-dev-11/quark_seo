def calculate_overall_points(results):
    overall_points = 0
    achieved_points = 0
    for card in results.values():
        if 'points' in card:
            overall_points += 100
            achieved_points += card.get('points', 0)
    return round((achieved_points / overall_points) * 100) if overall_points != 0 else 0

def calculate_improvement_count(results):
    false_count = 0
    for _, card in results.items():
        if card.get('isCard', False):
            for category in card.values():
                if isinstance(category, dict) and 'content' in category:
                    for content in category['content']:
                        if content['bool'] is False:
                            false_count += 1
    return false_count

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
    def __init__(self, card_name):
        self.card_name = card_name
        self.points = 0
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
        self.calculate_points()
        results[self.card_name.lower()] = self.to_dict()
    
    def update_points(self, points):
        self.points = points
        
    def calculate_points(self):
        true_count = 0
        false_count = 0
        for category in self.categories.values():
            for content in category['content']:
                if content['bool'] is True:
                    true_count += 1
                elif content['bool'] is False:
                    false_count += 1
        total_points = true_count + false_count

        points_percentage = (true_count / total_points) * 100 if total_points != 0 else 0
        self.update_points(points_percentage)

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