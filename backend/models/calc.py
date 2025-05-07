class Calc:
    def __init__(self, results):
        self.results = results

    def calculate_overall_points(self):
        overall_points = 0
        achieved_points = 0
        for card in self.results.values():
            if 'points' in card:
                overall_points += 100
                achieved_points += int(card.get('points', 0) or 0)
        return round((achieved_points / overall_points) * 100) if overall_points != 0 else 0

    def calculate_improvement_count(self):
        false_count = 0
        for _, card in self.results.items():
            if card.get('isCard', False):
                false_count += self.count_false_in_card(card)
        return false_count

    def count_false_in_card(self, card):
        false_count = 0
        for category in card.values():
            if isinstance(category, dict) and 'content' in category: 
                false_count += self.count_false_in_category(category)
        return false_count

    def count_false_in_category(self, category):
        return sum(1 for content in category['content'] if content['bool'] is False)