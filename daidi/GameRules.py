from Card import Card, Deck
from collections import Counter
from itertools import combinations


class Game:

    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.players = [Player(self.deck.cards[i*13:(i+1)*13]) for i in range(4)]
        self.current_turn = self.find_diamond_three()
        self.current_pile = []
        self.last_player = None
        self.pass_count = 0
        self.first_play = True
        self.game_over = False

    def process_move(self, player, move):
        self.current_pile = move
        self.last_player = self.current_turn
        self.pass_count = 0
        if self.first_play and move:
            self.first_play = False

    def find_diamond_three(self):
        diamond_three = Card(1, 1)
        for index, player in enumerate(self.players):
            if diamond_three in player.hand:
                return index
        return 0  # Default to player 0 if not found

    def next_player(self):
        self.current_turn = (self.current_turn + 1) % 4

    def handle_pass(self):
        self.pass_count += 1
        if self.pass_count >= 3:  # All other players passed
            self.reset_control()
        else:
            self.next_player()

    def reset_control(self):
        if self.last_player is not None:
            self.current_turn = self.last_player
            self.current_pile = []
            self.pass_count = 0
        else:
            self.next_player()
            self.pass_count = 0

    def is_game_over(self):
        return any(len(player.hand) == 0 for player in self.players)

    def get_winner(self):
        for i, player in enumerate(self.players):
            if len(player.hand) == 0:
                return i
        return None

    def play_turn(self):
        current_player = self.players[self.current_turn]
        
        # Get valid moves for current player
        if self.first_play:
            # First play must include diamond 3
            valid_moves = self.get_first_play_moves(current_player)
        else:
            valid_moves = current_player.valid_moves(self.current_pile)
        
        # For now, just play the first valid move (AI-like behavior)
        if valid_moves:
            # Prefer playing a move over passing
            move = None
            for potential_move in valid_moves:
                if potential_move:  # Not a pass
                    move = potential_move
                    break
            
            if move is None:  # Only passes available
                move = valid_moves[0]  # Take the pass
            
            if move:  # Not a pass
                current_player.play_move(self.current_pile, move)
                self.process_move(current_player, move)
                print(f"Player {self.current_turn} plays: {move}")
                # Move to next player after playing
                self.next_player()
            else:  # Pass
                self.handle_pass()
                print(f"Player {self.current_turn} passes")
        else:
            # No valid moves, must pass
            self.handle_pass()
            print(f"Player {self.current_turn} has no valid moves, passes")

    def get_first_play_moves(self, player):
        """Get valid moves for the first play (must include diamond 3)"""
        diamond_three = Card(1, 1)
        
        if diamond_three not in player.hand:
            return [[]]  # Can only pass
        
        moves = [[]]  # Can always pass
        
        # Singles
        moves.append([diamond_three])
        
        # Doubles (if player has another 3)
        threes = [card for card in player.hand if card.value == 1]
        if len(threes) >= 2:
            for pair in combinations(threes, 2):
                moves.append(list(pair))
        
        # Triples (if player has three 3s)
        if len(threes) >= 3:
            for triple in combinations(threes, 3):
                moves.append(list(triple))
        
        # 5-card hands (if player has 5 cards including diamond 3)
        if len(player.hand) >= 5:
            for combo in combinations(player.hand, 5):
                if diamond_three in combo:
                    moves.append(list(combo))
        
        return moves

    def game(self):
        while not self.is_game_over():
            print(f"\nPlayer {self.current_turn}'s turn")
            print(f"Current pile: {self.current_pile}")
            print(f"Player {self.current_turn} hand: {self.players[self.current_turn].hand}")
            
            self.play_turn()
            
            # Check if game is over
            if self.is_game_over():
                winner = self.get_winner()
                print(f"\nGame Over! Player {winner} wins!")
                break


class Player:

    def __init__(self, hand):
        self.hand = hand

    def valid_moves(self, played_card):
        moves = [[]]  # empty array is pass
        
        # If pile is empty, any valid move is allowed
        if not played_card:
            # Singles
            for card in self.hand:
                moves.append([card])
            
            # Doubles
            counter = Counter(card.value for card in self.hand)
            for value, count in counter.items():
                if count >= 2:
                    same_value_cards = [card for card in self.hand if card.value == value]
                    for pair in combinations(same_value_cards, 2):
                        moves.append(list(pair))
            
            # Triples
            for value, count in counter.items():
                if count >= 3:
                    same_value_cards = [card for card in self.hand if card.value == value]
                    for triple in combinations(same_value_cards, 3):
                        moves.append(list(triple))
            
            # 5-card hands
            if len(self.hand) >= 5:
                for combo in combinations(self.hand, 5):
                    moves.append(list(combo))
            
            return moves
        
        # if played card is a single
        if len(played_card) == 1:
            for card in self.hand:
                if card > played_card[0]:
                    moves.append([card])

        # if played card is a double
        elif len(played_card) == 2:
            counter = Counter(card.value for card in self.hand)
            for value, count in counter.items():
                if count >= 2:
                    same_value_cards = [card for card in self.hand if card.value == value]
                    for pair in combinations(same_value_cards, 2):
                        pair = list(pair)

                        if pair[0].value == played_card[0].value:
                            pair_max_suit = max(card.suit for card in pair)
                            played_max_suit = max(card.suit for card in played_card)
                            if pair_max_suit > played_max_suit:
                                moves.append(pair)
                        else:
                            if pair[0].value > played_card[0].value:
                                moves.append(pair)

        elif len(played_card) == 3:
            counter = Counter(card.value for card in self.hand)
            for value, count in counter.items():
                if count >= 3:
                    same_value_cards = [card for card in self.hand if card.value == value]
                    for triple in combinations(same_value_cards, 3):
                        triple = list(triple)
                        triple_higher = max(triple)
                        played_higher = max(played_card)
                        if triple_higher > played_higher:
                            moves.append(triple)

        elif len(played_card) == 5:
            played_type, played_rank = self._get_hand_type(played_card)
            
            for combo in combinations(self.hand, 5):
                combo = list(combo)
                combo_type, combo_rank = self._get_hand_type(combo)
                
                # Define hand rankings (higher index = higher rank)
                hand_rankings = ["straight", "flush", "full_house", "four_kind", "straight_flush"]
                
                # Check if combo can beat played_card
                if combo_type == played_type:
                    # Same type, compare ranks
                    if combo_type in ["flush", "four_kind", "full_house"]:
                        if combo_rank > played_rank:
                            moves.append(combo)
                    else:
                        if combo_rank > played_rank:
                            moves.append(combo)
                elif hand_rankings.index(combo_type) > hand_rankings.index(played_type):
                    # Higher ranked hand type can beat lower ranked hand type
                    moves.append(combo)

        return moves

    def play_move(self, played_card,move):
        moves = self.valid_moves(played_card)
        if move in moves:
            for card in move:
                self.hand.remove(card)
                
        else:
            return "Not Valid Move"    
        
    def _get_hand_type(self, cards):
        """Determine the type and ranking of a 5-card hand"""
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        value_counts = Counter(values)
        suit_counts = Counter(suits)
        
        # Check for straight flush first
        if self._is_straight(values) and len(suit_counts) == 1:
            return "straight_flush", max(values)
        
        # Check for four of a kind
        if 4 in value_counts.values():
            four_value = [v for v, c in value_counts.items() if c == 4][0]
            kicker = [v for v, c in value_counts.items() if c == 1][0]
            return "four_kind", (four_value, kicker)
        
        # Check for full house
        if 3 in value_counts.values() and 2 in value_counts.values():
            three_value = [v for v, c in value_counts.items() if c == 3][0]
            pair_value = [v for v, c in value_counts.items() if c == 2][0]
            return "full_house", (three_value, pair_value)
        
        # Check for flush
        if len(suit_counts) == 1:
            # For flush, rank by highest card, then suit if tied
            highest_card = max(cards)
            return "flush", (highest_card.value, highest_card.suit)
        
        # Check for straight
        if self._is_straight(values):
            return "straight", max(values)
        
        # High card
        return "high_card", max(values)
    
    def _is_straight(self, values):
        """Check if values form a straight (consecutive)"""
        sorted_values = sorted(values)
        for i in range(len(sorted_values) - 1):
            if sorted_values[i + 1] - sorted_values[i] != 1:
                return False
        return True
        