# -*- coding: utf-8 -*-
"""
Regicide Game - Card System
扑克牌系统实现
"""

from enum import Enum
import pygame

class Suit(Enum):
    """花色枚举"""
    HEARTS = "♥️"      # 红桃 - 治疗
    DIAMONDS = "♦️"    # 方块 - 抽牌
    SPADES = "♠️"      # 黑桃 - 攻击敌人手牌
    CLUBS = "♣️"       # 草花 - 防御

class Rank(Enum):
    """牌面枚举"""
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

class Card:
    """单张扑克牌类"""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        
    def __str__(self):
        """字符串表示"""
        rank_names = {
            Rank.ACE: "A", Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4",
            Rank.FIVE: "5", Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8",
            Rank.NINE: "9", Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K"
        }
        return f"{rank_names[self.rank]}{self.suit.value}"
    
    def __eq__(self, other):
        """相等比较"""
        return isinstance(other, Card) and self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self):
        """哈希值，用于集合操作"""
        return hash((self.suit, self.rank))
    
    @property
    def attack_value(self):
        """攻击力值"""
        return self.rank.value
    
    @property
    def is_face_card(self):
        """是否是人头牌（J、Q、K）"""
        return self.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]
    
    @property
    def is_number_card(self):
        """是否是数字牌（A-10）"""
        return not self.is_face_card
    
    @property
    def color(self):
        """牌的颜色"""
        return "red" if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else "black"
    
    def get_suit_ability_description(self):
        """获取花色特殊能力描述"""
        abilities = {
            Suit.HEARTS: "治疗：回复弃牌堆中的牌",
            Suit.DIAMONDS: "抽牌：从牌库抽取更多牌",
            Suit.SPADES: "攻击：让敌人丢弃手牌",
            Suit.CLUBS: "防御：减少敌人反击伤害"
        }
        return abilities[self.suit]

class Deck:
    """牌库类"""
    
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        """重置为完整牌库（52张牌）"""
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                self.cards.append(Card(suit, rank))
    
    def shuffle(self):
        """洗牌"""
        import random
        random.shuffle(self.cards)
    
    def draw(self):
        """抽一张牌"""
        if self.cards:
            return self.cards.pop()
        return None
    
    def draw_multiple(self, count):
        """抽多张牌"""
        drawn = []
        for _ in range(min(count, len(self.cards))):
            card = self.draw()
            if card:
                drawn.append(card)
        return drawn
    
    def add_card(self, card):
        """添加一张牌到牌库底部"""
        self.cards.insert(0, card)
    
    def add_cards(self, cards):
        """添加多张牌到牌库底部"""
        for card in cards:
            self.add_card(card)
    
    def is_empty(self):
        """检查牌库是否为空"""
        return len(self.cards) == 0
    
    def cards_left(self):
        """剩余牌数"""
        return len(self.cards)
    
    def get_enemies(self):
        """获取所有敌人牌（J、Q、K）"""
        enemies = []
        for card in self.cards[:]:
            if card.is_face_card:
                enemies.append(card)
                self.cards.remove(card)
        return enemies
    
    def get_number_cards(self):
        """获取所有数字牌（A-10）"""
        number_cards = []
        for card in self.cards[:]:
            if card.is_number_card:
                number_cards.append(card)
                self.cards.remove(card)
        return number_cards

class Hand:
    """手牌类"""
    
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        """添加一张牌"""
        self.cards.append(card)
        self.sort_cards()
    
    def add_cards(self, cards):
        """添加多张牌"""
        self.cards.extend(cards)
        self.sort_cards()
    
    def remove_card(self, card):
        """移除一张牌"""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def remove_cards(self, cards):
        """移除多张牌"""
        removed = []
        for card in cards:
            if self.remove_card(card):
                removed.append(card)
        return removed
    
    def sort_cards(self):
        """排序手牌：按花色和牌面大小排序"""
        suit_order = {Suit.HEARTS: 0, Suit.DIAMONDS: 1, Suit.CLUBS: 2, Suit.SPADES: 3}
        self.cards.sort(key=lambda card: (suit_order[card.suit], card.rank.value))
    
    def get_cards_by_rank(self, rank):
        """获取指定牌面的所有牌"""
        return [card for card in self.cards if card.rank == rank]
    
    def get_cards_by_suit(self, suit):
        """获取指定花色的所有牌"""
        return [card for card in self.cards if card.suit == suit]
    
    def can_play_combo(self, cards):
        """检查是否可以打出组合牌"""
        if not cards:
            return False
        
        # 检查是否都在手牌中
        for card in cards:
            if card not in self.cards:
                return False
        
        # 获取所有非A牌的牌面
        non_ace_ranks = [card.rank for card in cards if card.rank != Rank.ACE]
        ace_cards = [card for card in cards if card.rank == Rank.ACE]
        
        # 如果只有A牌，可以出牌
        if not non_ace_ranks:
            return True
        
        # 如果有非A牌，检查非A牌是否都是相同牌面
        # A牌可以和任意数量的相同牌面的非A牌一起出
        if len(set(non_ace_ranks)) > 1:
            return False
        
        return True
    
    def is_empty(self):
        """检查手牌是否为空"""
        return len(self.cards) == 0
    
    def size(self):
        """手牌数量"""
        return len(self.cards)
    
    def get_available_ranks(self):
        """获取手牌中所有可用的牌面"""
        ranks = set()
        for card in self.cards:
            ranks.add(card.rank)
        return sorted(ranks, key=lambda r: r.value)
    
    def __str__(self):
        """字符串表示"""
        if not self.cards:
            return "空手牌"
        return " ".join(str(card) for card in self.cards)