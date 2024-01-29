from copy import deepcopy
from collections import Counter
from itertools import combinations
from .rank import Rank
from .handrank.ranks import (
    HighCard,
    OnePair,
    TwoPair,
    ThreeOfAKind,
    StraightFlush,
    Straight,
    Flush,
    FourOfAKind,
    FullHouse,
    RoyalFlush,
    NotRankableHandRank,
)


class Hand:
    def __init__(self, cards):
        cards = sorted(cards, key=lambda card: card.rank) if cards is not None else []
        self.cards = deepcopy(cards) if len(cards) > 0 is not None else cards

    def number_of_cards(self):
        return len(self.cards)

    def describe_hand_rank(self):
        if self.number_of_cards() != 5:
            return NotRankableHandRank(self.cards).describe_hand()

        rank_counts = Counter(card.rank for card in self.cards)

        # Check for specific hand rankings
        if self.is_royal_flush():
            return RoyalFlush(self.cards[0].suit).describe_hand()

        elif self.is_straight_flush():
            high_card_rank = max(self.cards, key=lambda card: card.rank).rank
            return StraightFlush(high_card_rank).describe_hand()

        elif self.is_four_of_a_kind():
            card_rank = rank_counts.most_common()[0][0]
            return FourOfAKind(card_rank).describe_hand()

        elif self.is_full_house():
            trips = rank_counts.most_common()[0][0]
            pairs = rank_counts.most_common()[-1][0]
            return FullHouse(trips, pairs).describe_hand()

        elif self.is_flush():
            return Flush(self.cards).describe_hand()

        elif self.is_straight():
            card_rank = self.cards[-1].rank
            return Straight(card_rank).describe_hand()

        elif self.is_three_of_a_kind():
            card_rank = rank_counts.most_common()[0][0]
            return ThreeOfAKind(card_rank).describe_hand()

        elif self.is_two_pair():
            low_pair = rank_counts.most_common()[0][0]
            high_pair = rank_counts.most_common()[1][0]
            kicker = rank_counts.most_common()[-1][0]
            return TwoPair(high_pair, low_pair, kicker).describe_hand()

        elif self.is_one_pair():
            pair = rank_counts.most_common()[0][0]
            rest = [card for card in self.cards if card.rank != pair]
            return OnePair(pair, rest).describe_hand()
        else:
            return HighCard(self.cards).describe_hand()

    def _contains_five_cards_in_sequence(self):
        return all(
            self.cards[i].rank.value == self.cards[i - 1].rank.value + 1
            for i in range(1, len(self.cards))
        )

    def is_straight_flush(self) -> bool:
        # The hand contains five cards of the same suit
        if len(set(card.suit for card in self.cards)) != 1:
            return False

        # Also the hand contains five cards of sequential rank and the highest card is ACE
        return (
            self._contains_five_cards_in_sequence()
            and not max(self.cards, key=lambda card: card.rank).rank == Rank.ACE
        )

    def is_royal_flush(self) -> bool:
        # The hand contains five cards of the same suit
        if len(set(card.suit for card in self.cards)) != 1:
            return False

        # Also the hand contains five cards of sequential rank
        if not self._contains_five_cards_in_sequence():
            return False

        # The highest card is ACE
        return max(self.cards, key=lambda card: card.rank).rank == Rank.ACE

    def is_four_of_a_kind(self) -> bool:
        # The hand contains four cards of one rank
        # and any other unmatched card
        rank_counts = Counter(card.rank for card in self.cards)
        return sorted([4, 1]) == sorted(rank_counts.values())

    def is_full_house(self) -> bool:
        # The hand contains three matching cards of one rank
        # and two matching cards of another rank
        rank_counts = Counter(card.rank for card in self.cards)
        return sorted([3, 2]) == sorted(rank_counts.values())

    def is_flush(self) -> bool:
        # The hand contains five cards of the same suit
        if len(set(card.suit for card in self.cards)) != 1:
            return False
        # also the hand contains five cards not in sequence
        return not self._contains_five_cards_in_sequence()

    def is_straight(self) -> bool:
        # The hand contains at least two different suits
        if len(set(card.suit for card in self.cards)) < 2:
            return False
        # also the hand contains five cards of sequential rank
        return self._contains_five_cards_in_sequence()

    def is_three_of_a_kind(self) -> bool:
        # The hand contains three cards of one rank
        # with two cards not of this rank nor the same as each other
        rank_counts = Counter(card.rank for card in self.cards)
        return sorted([3, 1, 1]) == sorted(rank_counts.values())

    def is_two_pair(self) -> bool:
        # The hand contains three cards of one rank
        # with two cards of another rank
        rank_counts = Counter(card.rank for card in self.cards)
        return sorted([2, 2, 1]) == sorted(rank_counts.values())

    def is_one_pair(self) -> bool:
        # The hand contains two cards of one rank
        # with three cards not of this rank nor the same as each other
        rank_counts = Counter(card.rank for card in self.cards)
        return sorted([2, 1, 1, 1]) == sorted(rank_counts.values())

    def compare_to(self, other):
        if len(self.cards) != 5 or len(other.cards) != 5:
            return 0

        # Compare hand ranks based on poker hand hierarchy
        self_rank = self.get_hand_rank()
        other_rank = other.get_hand_rank()

        if self_rank < other_rank:
            return -1
        elif self_rank > other_rank:
            return 1
        else:
            # If the hand ranks are the same, compare high cards
            self_high_card = max(self.cards, key=lambda card: card.rank).rank
            other_high_card = max(other.cards, key=lambda card: card.rank).rank

            if self_high_card < other_high_card:
                return -1
            elif self_high_card > other_high_card:
                return 1
            else:
                return 0

    def get_hand_rank(self) -> int:
        if self.is_royal_flush():
            return 10
        elif self.is_straight_flush():
            return 9
        elif self.is_four_of_a_kind():
            return 8
        elif self.is_full_house():
            return 7
        elif self.is_flush():
            return 6
        elif self.is_straight():
            return 5
        elif self.is_three_of_a_kind():
            return 4
        elif self.is_two_pair():
            return 3
        elif self.is_one_pair():
            return 2
        else:
            # High Card
            return 1

    def find_best_hand(self):
        # Ensure the input has at least 5 cards
        if len(self.cards) < 5:
            raise ValueError("Not enough cards to form a hand")

        # Generate all combinations of 5 cards
        all_combinations = list(combinations(self.cards, 5))

        # Initialize variables to store the best hand and its rank
        best_hand = None
        best_rank = float("-inf")

        # Iterate through all combinations and find the best hand
        for combo in all_combinations:
            current_hand = Hand(list(combo))
            current_rank = current_hand.get_hand_rank()

            # Update if the current hand has a higher rank
            if current_rank > best_rank:
                best_rank = current_rank
                best_hand = current_hand

        return best_hand
