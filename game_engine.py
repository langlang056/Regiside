# -*- coding: utf-8 -*-
"""
Regicide Game - Game Engine
游戏引擎和战斗系统
"""

from enum import Enum
from card import *
from enemy import *
import random

class GameState(Enum):
    """游戏状态"""
    MENU = "MENU"
    PLAYING = "PLAYING"
    PLAYER_TURN = "PLAYER_TURN"
    ENEMY_TURN = "ENEMY_TURN"
    DISCARD_SELECTION = "DISCARD_SELECTION"
    VICTORY = "VICTORY"
    DEFEAT = "DEFEAT"

class RegicideGame:
    """Regicide游戏主引擎"""

    # 手牌上限
    MAX_HAND_SIZE = 10

    def __init__(self, player_count=1):
        self.player_count = player_count
        self.game_state = GameState.MENU
        
        # 初始化游戏组件
        self.deck = Deck()
        self.discard_pile = []
        self.enemy_queue = EnemyQueue()
        
        # 玩家手牌（支持多人游戏扩展）
        self.player_hands = [Hand() for _ in range(player_count)]
        self.current_player = 0
        
        # 游戏状态
        self.turn_count = 0
        self.game_over = False
        self.victory = False
        
        # 战斗状态
        self.last_battle_result = None
        
        # 弃牌选择状态
        self.required_discard_value = 0  # 需要弃牌的总点数
        self.selected_for_discard = []   # 选中要弃牌的牌
        
    def start_new_game(self):
        """开始新游戏"""
        # 重置所有状态
        self.deck.reset()
        self.deck.shuffle()
        self.discard_pile.clear()
        self.enemy_queue.restart()
        
        # 移除敌人牌，只保留数字牌
        enemy_cards = self.deck.get_enemies()
        self.deck = Deck()
        number_cards = self.deck.get_number_cards()
        self.deck.cards = number_cards
        self.deck.shuffle()
        
        # 给每个玩家发初始手牌（8张）
        for hand in self.player_hands:
            hand.cards.clear()
            initial_cards = self.deck.draw_multiple(8)
            hand.add_cards(initial_cards)
        
        # 设置游戏状态
        self.game_state = GameState.PLAYING
        self.current_player = 0
        self.turn_count = 0
        self.game_over = False
        self.victory = False
        
        return True
    
    def get_current_player_hand(self):
        """获取当前玩家手牌"""
        return self.player_hands[self.current_player]
    
    def can_play_cards(self, cards):
        """检查是否可以打出指定牌组"""
        current_hand = self.get_current_player_hand()
        return current_hand.can_play_combo(cards)
    
    def play_cards(self, cards):
        """玩家打牌"""
        if not self.can_play_cards(cards):
            return False
        
        current_hand = self.get_current_player_hand()
        current_enemy = self.enemy_queue.get_current_enemy()
        
        if not current_enemy or current_enemy.is_defeated:
            return False
        
        # 执行战斗
        battle_result = self._execute_battle(cards, current_enemy)
        self.last_battle_result = battle_result
        
        # 先应用花色特殊效果（在将打出的牌加入弃牌堆之前）
        self._apply_suit_effects(cards, battle_result)
        
        # 从手牌移除打出的牌
        removed_cards = current_hand.remove_cards(cards)
        self.discard_pile.extend(removed_cards)
        
        # 处理敌人被击败
        if current_enemy.is_defeated:
            self.enemy_queue.defeat_current_enemy()
            battle_result.enemy_defeated = True
            
            # 检查是否获胜
            if self.enemy_queue.is_all_defeated():
                self.victory = True
                self.game_state = GameState.VICTORY
                return battle_result
        
        # 处理反击伤害
        if battle_result.counter_damage > 0:
            self._handle_counter_damage(battle_result.counter_damage)
        
        # 检查失败条件
        if self._check_defeat_conditions():
            self.game_over = True
            self.game_state = GameState.DEFEAT
        
        self.turn_count += 1
        return battle_result
    
    def _execute_battle(self, cards, enemy):
        """执行战斗逻辑"""
        result = BattleResult()

        # 先应用黑桃效果（降低敌人攻击力）
        spades_cards = [card for card in cards if card.suit == Suit.SPADES]
        if spades_cards:
            spades_power = sum(card.attack_value for card in spades_cards)
            attack_reduction = spades_power
            if not enemy.is_defeated:
                total_reduction = enemy.reduce_attack_power(attack_reduction)
                result.add_special_effect(f"Spades: Reduced enemy attack by {attack_reduction} (total -{total_reduction})")

        # 计算总攻击力
        total_attack = sum(card.attack_value for card in cards)

        # 计算组合牌加成
        if len(cards) > 1:
            combo_bonus = len(cards) * (len(cards) - 1)
            total_attack += combo_bonus
            result.add_special_effect(f"Combo bonus: +{combo_bonus}")

        # 梅花翻倍效果
        clubs_cards = [card for card in cards if card.suit == Suit.CLUBS]
        if clubs_cards:
            clubs_power = sum(card.attack_value for card in clubs_cards)
            # 根据梅花牌力值决定翻倍效果
            if clubs_power > 0:
                total_attack *= 2
                result.add_special_effect(f"Clubs: Double damage (Clubs power {clubs_power})")

        # 对敌人造成伤害
        damage_dealt = enemy.take_damage(total_attack)
        result.damage_dealt = damage_dealt

        # 计算反击伤害（如果敌人未被击败）
        if not enemy.is_defeated:
            counter_damage = enemy.get_counter_attack_damage(0)  # 移除梅花防御，现在没有防御值
            result.counter_damage = counter_damage

        return result
    
    def _apply_suit_effects(self, cards, result):
        """应用花色特殊效果"""
        suits_played = set(card.suit for card in cards)

        for suit in suits_played:
            suit_cards = [card for card in cards if card.suit == suit]
            suit_power = sum(card.attack_value for card in suit_cards)

            # A牌（动物伙伴）可以与任何其他牌组合，并提供各自花色的效果

            if suit == Suit.HEARTS:
                # 红桃：治疗 - 从弃牌堆回复牌到手牌（考虑手牌上限）
                current_hand = self.get_current_player_hand()
                # 计算打出牌后的实际手牌数量
                current_hand_size = len(current_hand.cards) - len(cards)

                if current_hand_size >= self.MAX_HAND_SIZE:
                    result.add_special_effect(f"Hearts: Hand full ({self.MAX_HAND_SIZE} cards), cannot heal")
                elif not self.discard_pile:
                    result.add_special_effect("Hearts: Discard pile empty, cannot heal")
                else:
                    healed_cards = self._heal_cards(suit_power, len(cards))
                    result.cards_healed = len(healed_cards)
                    if healed_cards:
                        if len(healed_cards) < suit_power:
                            available_space = self.MAX_HAND_SIZE - current_hand_size
                            if available_space < suit_power:
                                result.add_special_effect(f"Hearts: Healed {len(healed_cards)} cards (limited by hand size)")
                            else:
                                result.add_special_effect(f"Hearts: Healed {len(healed_cards)} cards (limited by discard pile)")
                        else:
                            result.add_special_effect(f"Hearts: Healed {len(healed_cards)} cards")

            elif suit == Suit.DIAMONDS:
                # 方块：抽牌（考虑手牌上限）
                current_hand = self.get_current_player_hand()
                # 计算打出牌后的实际手牌数量
                current_hand_size = len(current_hand.cards) - len(cards)

                if current_hand_size >= self.MAX_HAND_SIZE:
                    # 手牌已满，无法抽牌
                    result.add_special_effect(f"Diamonds: Hand full ({self.MAX_HAND_SIZE} cards), cannot draw")
                else:
                    # 计算最多可抽多少张牌
                    max_draw = min(suit_power, self.MAX_HAND_SIZE - current_hand_size)
                    drawn_cards = self.deck.draw_multiple(max_draw)

                    if drawn_cards:
                        current_hand.add_cards(drawn_cards)
                        result.cards_drawn = len(drawn_cards)
                        if len(drawn_cards) < suit_power:
                            result.add_special_effect(f"Diamonds: Drew {len(drawn_cards)} cards (limited by hand size)")
                        else:
                            result.add_special_effect(f"Diamonds: Drew {len(drawn_cards)} cards")
                    
            elif suit == Suit.SPADES:
                # 黑桃效果已在 _execute_battle 中处理，这里不需要重复处理
                pass
            
            # 梅花的翻倍效果已在 _execute_battle 中处理
    
    def _heal_cards(self, heal_amount, cards_being_played=0):
        """从弃牌堆治疗牌回手牌（考虑手牌上限）"""
        if not self.discard_pile:
            return []

        current_hand = self.get_current_player_hand()
        # 计算打出牌后的实际手牌数量
        current_hand_size = len(current_hand.cards) - cards_being_played

        # 检查手牌上限
        if current_hand_size >= self.MAX_HAND_SIZE:
            return []

        # 计算最多可治疗多少张牌
        max_heal = min(heal_amount, len(self.discard_pile), self.MAX_HAND_SIZE - current_hand_size)
        if max_heal <= 0:
            return []

        # 随机选择治疗的牌
        healed_cards = random.sample(self.discard_pile, max_heal)

        # 从弃牌堆移除，加入当前玩家手牌
        for card in healed_cards:
            self.discard_pile.remove(card)
            current_hand.add_card(card)
        
        return healed_cards
    
    def _handle_counter_damage(self, damage):
        """处理反击伤害 - 现在需要手动选择弃牌"""
        current_hand = self.get_current_player_hand()
        
        if current_hand.size() == 0 or damage <= 0:
            return
        
        # 设置需要弃牌的点数要求
        self.required_discard_value = damage
        self.selected_for_discard = []
        
        # 改变游戏状态为弃牌选择
        self.game_state = GameState.DISCARD_SELECTION
    
    def _check_defeat_conditions(self):
        """检查失败条件"""
        # 条件1：牌库为空且没有手牌
        if self.deck.is_empty():
            for hand in self.player_hands:
                if not hand.is_empty():
                    return False
            return True
        
        # 条件2：所有玩家手牌都为空且牌库为空
        all_hands_empty = all(hand.is_empty() for hand in self.player_hands)
        if all_hands_empty and self.deck.is_empty():
            return True
            
        return False
    
    def get_game_state_info(self):
        """获取游戏状态信息"""
        info = {
            'current_enemy': self.enemy_queue.get_current_enemy(),
            'next_enemy': self.enemy_queue.get_next_enemy(),
            'remaining_enemies': self.enemy_queue.get_remaining_enemies(),
            'defeated_enemies': self.enemy_queue.get_defeated_enemies(),
            'current_phase': self.enemy_queue.get_current_phase(),
            'phase_progress': self.enemy_queue.get_phase_progress(),
            'deck_size': self.deck.cards_left(),
            'discard_pile_size': len(self.discard_pile),
            'turn_count': self.turn_count,
            'game_state': self.game_state,
            'victory': self.victory,
            'game_over': self.game_over
        }
        return info
    
    def get_hand_info(self, player_index=0):
        """获取指定玩家的手牌信息"""
        if 0 <= player_index < len(self.player_hands):
            hand = self.player_hands[player_index]
            return {
                'cards': hand.cards,
                'size': hand.size(),
                'available_ranks': hand.get_available_ranks(),
                'is_empty': hand.is_empty()
            }
        return None
    
    def get_possible_plays(self):
        """获取所有可能的出牌组合"""
        current_hand = self.get_current_player_hand()
        possible_plays = []
        
        # 单张牌
        for card in current_hand.cards:
            possible_plays.append([card])
        
        # 组合牌（相同牌面）
        for rank in current_hand.get_available_ranks():
            cards_of_rank = current_hand.get_cards_by_rank(rank)
            if len(cards_of_rank) > 1:
                # 2张相同牌面
                for i in range(len(cards_of_rank)):
                    for j in range(i + 1, len(cards_of_rank)):
                        possible_plays.append([cards_of_rank[i], cards_of_rank[j]])
                
                # 3张相同牌面
                if len(cards_of_rank) >= 3:
                    for i in range(len(cards_of_rank)):
                        for j in range(i + 1, len(cards_of_rank)):
                            for k in range(j + 1, len(cards_of_rank)):
                                possible_plays.append([cards_of_rank[i], cards_of_rank[j], cards_of_rank[k]])
                
                # 4张相同牌面
                if len(cards_of_rank) == 4:
                    possible_plays.append(cards_of_rank)
        
        return possible_plays
    
    def calculate_play_effectiveness(self, cards):
        """计算出牌的效果预览"""
        if not cards:
            return None
        
        current_enemy = self.enemy_queue.get_current_enemy()
        if not current_enemy:
            return None
        
        # 计算总攻击力
        total_attack = sum(card.attack_value for card in cards)
        
        # 计算组合牌加成
        if len(cards) > 1:
            combo_bonus = len(cards) * (len(cards) - 1)
            total_attack += combo_bonus
        
        # 梅花翻倍效果
        clubs_cards = [card for card in cards if card.suit == Suit.CLUBS]
        if clubs_cards:
            clubs_power = sum(card.attack_value for card in clubs_cards)
            if clubs_power > 0:
                total_attack *= 2
        
        # 计算反击伤害（现在没有防御）
        counter_damage = 0
        damage_to_enemy = min(total_attack, current_enemy.current_health)
        if damage_to_enemy < current_enemy.current_health:
            counter_damage = current_enemy.attack_power  # 移除防御计算
        
        return {
            'total_attack': total_attack,
            'damage_to_enemy': damage_to_enemy,
            'will_defeat_enemy': damage_to_enemy >= current_enemy.current_health,
            'counter_damage': counter_damage,
            'combo_bonus': combo_bonus if len(cards) > 1 else 0
        }
    
    def reset_game(self):
        """重置游戏"""
        self.game_state = GameState.MENU
        self.turn_count = 0
        self.game_over = False
        self.victory = False
        self.last_battle_result = None
        self.required_discard_value = 0
        self.selected_for_discard = []
    
    def toggle_discard_selection(self, card):
        """切换弃牌选择状态"""
        if self.game_state != GameState.DISCARD_SELECTION:
            return False
            
        if card in self.selected_for_discard:
            self.selected_for_discard.remove(card)
        else:
            self.selected_for_discard.append(card)
        return True
    
    def can_confirm_discard(self):
        """检查是否可以确认弃牌"""
        if self.game_state != GameState.DISCARD_SELECTION:
            return False
        
        total_value = sum(card.attack_value for card in self.selected_for_discard)
        return total_value >= self.required_discard_value
    
    def confirm_discard(self):
        """确认弃牌选择"""
        if not self.can_confirm_discard():
            return False
        
        current_hand = self.get_current_player_hand()
        
        # 从手牌中移除选中的牌
        for card in self.selected_for_discard:
            if card in current_hand.cards:
                current_hand.cards.remove(card)
                self.discard_pile.append(card)
        
        # 重置弃牌状态
        self.selected_for_discard = []
        self.required_discard_value = 0
        self.game_state = GameState.PLAYING
        
        return True