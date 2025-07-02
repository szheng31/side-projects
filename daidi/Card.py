import random
class Card:

    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __lt__(self, other):
        return (self.value == other.value
                and self.suit < other.suit) or self.value < other.value

    def __gt__(self, other):
        return (self.value == other.value
                and self.suit > other.suit) or self.value > other.value

    def __str__(self):
        unicode_suits = {1: "♢", 2: "♧", 3: "♡", 4: "♤"}
        values_mapping = {
            1: "3",
            2: "4",
            3: "5",
            4: "6",
            5: "7",
            6: "8",
            7: "9",
            8: "10",
            9: "J",
            10: "Q",
            11: "K",
            12: "A",
            13: "2"
        }

        return f"({values_mapping[self.value]},{unicode_suits[self.suit]})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

class Deck:
    def __init__(self):
        self.cards = self.generateCards()

    def generateCards(self):
        vals = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        ]  # to reduce overhead and for simplicities sake, i will represent each card as a number
        suits = [1, 2, 3, 4]  #
        deck = []
        for c in vals:
            for s in suits:
                deck.append(Card(c, s))
        return deck

    def shuffle(self):
        random.shuffle(self.cards)

    def __str__(self):
        return str(self.cards)