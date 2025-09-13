# -*- coding: utf-8 -*-
"""
Regicide Game - Complete implementation with image-based cards
"""

import pygame
import sys
import os
from game_engine import RegicideGame, GameState
from card import Card, Suit, Rank
from enemy import Enemy
from image_card_renderer import ImageCardRenderer
import math

# 设置环境变量
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

class Colors:
    """颜色常量"""
    # 背景色
    DARK_BLUE = (25, 25, 60)
    NAVY = (20, 30, 48)
    ROYAL_BLUE = (30, 45, 80)
    
    # 卡牌颜色
    WHITE = (255, 255, 255)
    BLACK = (20, 20, 20)
    RED = (220, 20, 20)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    
    # 游戏元素颜色
    GREEN = (34, 139, 34)
    LIGHT_GREEN = (144, 238, 144)
    ORANGE = (255, 140, 0)
    PURPLE = (138, 43, 226)
    
    # UI颜色
    BUTTON_NORMAL = (60, 80, 120)
    BUTTON_HOVER = (80, 100, 140)
    BUTTON_SELECTED = (100, 120, 160)
    TEXT_LIGHT = (240, 240, 240)
    TEXT_DARK = (60, 60, 60)

class FixedCardRenderer:
    """修复版卡牌渲染器 - 使用英文和符号"""
    
    def __init__(self):
        self.card_width = 80
        self.card_height = 120
        self.small_card_width = 60
        self.small_card_height = 90
        
        # 花色符号映射（使用ASCII字符）
        self.suit_symbols = {
            Suit.HEARTS: "H",      # Hearts
            Suit.DIAMONDS: "D",    # Diamonds
            Suit.SPADES: "S",      # Spades
            Suit.CLUBS: "C"        # Clubs
        }
        
        # 花色颜色
        self.suit_colors = {
            Suit.HEARTS: Colors.RED,
            Suit.DIAMONDS: Colors.RED,
            Suit.SPADES: Colors.BLACK,
            Suit.CLUBS: Colors.BLACK
        }
        
    def draw_card(self, surface, card, x, y, selected=False, small=False):
        """绘制单张卡牌"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height
        
        # 卡牌背景
        card_rect = pygame.Rect(x, y, width, height)
        border_color = Colors.GOLD if selected else Colors.WHITE
        background_color = Colors.WHITE
        
        # 绘制边框和背景
        pygame.draw.rect(surface, border_color, card_rect, 3 if selected else 1)
        inner_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
        pygame.draw.rect(surface, background_color, inner_rect)
        
        # 确定卡牌颜色
        text_color = self.suit_colors[card.suit]
        
        # 绘制牌面
        font_size = 14 if small else 18
        font = pygame.font.Font(None, font_size)
        
        # 牌面文字
        rank_text = self._get_rank_display(card.rank)
        rank_surface = font.render(rank_text, True, text_color)
        
        # 花色符号
        suit_text = self.suit_symbols[card.suit]
        suit_surface = font.render(suit_text, True, text_color)
        
        # 位置计算
        rank_x = x + 5
        rank_y = y + 5
        suit_x = x + width - suit_surface.get_width() - 5
        suit_y = y + height - suit_surface.get_height() - 5
        
        surface.blit(rank_surface, (rank_x, rank_y))
        surface.blit(suit_surface, (suit_x, suit_y))
        
        # 中央大花色符号
        if not small:
            center_font = pygame.font.Font(None, 32)
            center_suit = center_font.render(suit_text, True, text_color)
            center_x = x + width // 2 - center_suit.get_width() // 2
            center_y = y + height // 2 - center_suit.get_height() // 2
            surface.blit(center_suit, (center_x, center_y))
        
        # A牌宠物标识
        if card.rank == Rank.ACE:
            pet_font = pygame.font.Font(None, 16)
            pet_text = pet_font.render("PET", True, Colors.GOLD)
            pet_x = x + width // 2 - pet_text.get_width() // 2
            pet_y = y + height - 20
            surface.blit(pet_text, (pet_x, pet_y))
        
        return card_rect
    
    def draw_card_back(self, surface, x, y, small=False):
        """绘制卡背"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height
        
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, Colors.NAVY, card_rect)
        pygame.draw.rect(surface, Colors.WHITE, card_rect, 2)
        
        # 装饰图案
        center_x = x + width // 2
        center_y = y + height // 2
        pygame.draw.circle(surface, Colors.GOLD, (center_x, center_y), width // 4, 2)
        
        return card_rect
    
    def draw_enemy_card(self, surface, enemy, x, y):
        """绘制敌人卡牌"""
        width = self.card_width * 1.5
        height = self.card_height * 1.5
        
        # 敌人卡牌背景
        card_rect = pygame.Rect(x, y, width, height)
        
        # 根据敌人类型选择背景色
        if enemy.rank == Rank.JACK:
            bg_color = Colors.GREEN
            enemy_name = "JACK"
        elif enemy.rank == Rank.QUEEN:
            bg_color = Colors.PURPLE
            enemy_name = "QUEEN"
        else:  # KING
            bg_color = Colors.ORANGE
            enemy_name = "KING"
        
        pygame.draw.rect(surface, bg_color, card_rect)
        pygame.draw.rect(surface, Colors.GOLD, card_rect, 4)
        
        # 绘制敌人信息
        font_large = pygame.font.Font(None, 28)
        font_medium = pygame.font.Font(None, 22)
        font_small = pygame.font.Font(None, 18)
        
        # 敌人名称
        suit_name = self.suit_symbols[enemy.suit]
        name_text = f"{suit_name} {enemy_name}"
        name_surface = font_medium.render(name_text, True, Colors.WHITE)
        name_x = x + width // 2 - name_surface.get_width() // 2
        name_y = y + 10
        surface.blit(name_surface, (name_x, name_y))
        
        # 生命值
        health_text = f"{enemy.current_health}/{enemy.max_health}"
        health_surface = font_large.render(health_text, True, Colors.WHITE)
        health_x = x + width // 2 - health_surface.get_width() // 2
        health_y = y + height // 2 - 20
        surface.blit(health_surface, (health_x, health_y))
        
        # 攻击力
        attack_text = f"ATK: {enemy.attack_power}"
        attack_surface = font_small.render(attack_text, True, Colors.WHITE)
        attack_x = x + width // 2 - attack_surface.get_width() // 2
        attack_y = y + height - 30
        surface.blit(attack_surface, (attack_x, attack_y))
        
        # 生命值条
        health_bar_width = width - 20
        health_bar_height = 8
        health_bar_x = x + 10
        health_bar_y = y + height // 2 + 10
        
        # 背景
        health_bg_rect = pygame.Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height)
        pygame.draw.rect(surface, Colors.BLACK, health_bg_rect)
        
        # 当前生命值
        health_ratio = enemy.get_health_percentage()
        current_health_width = int(health_bar_width * health_ratio)
        if current_health_width > 0:
            health_rect = pygame.Rect(health_bar_x, health_bar_y, current_health_width, health_bar_height)
            health_color = Colors.GREEN if health_ratio > 0.5 else (Colors.ORANGE if health_ratio > 0.25 else Colors.RED)
            pygame.draw.rect(surface, health_color, health_rect)
        
        return card_rect
    
    def _get_rank_display(self, rank):
        """获取牌面显示文字"""
        rank_names = {
            Rank.ACE: "A", Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4",
            Rank.FIVE: "5", Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8",
            Rank.NINE: "9", Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K"
        }
        return rank_names[rank]

class Button:
    """按钮类"""
    
    def __init__(self, x, y, width, height, text, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.clicked = False
        
    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        return False
    
    def draw(self, surface):
        """绘制按钮"""
        if self.hovered:
            color = Colors.BUTTON_HOVER
        else:
            color = Colors.BUTTON_NORMAL
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Colors.WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, Colors.TEXT_LIGHT)
        text_x = self.rect.centerx - text_surface.get_width() // 2
        text_y = self.rect.centery - text_surface.get_height() // 2
        surface.blit(text_surface, (text_x, text_y))

class RegicideFixedGUI:
    """Regicide修复版GUI - 纯英文界面"""
    
    def __init__(self, width=1200, height=800):
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Regicide - Card Battle Game")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 游戏引擎
        self.game = RegicideGame()
        
        # 渲染器 - 使用图像渲染器
        self.card_renderer = ImageCardRenderer()
        
        # 字体（使用默认字体避免问题）
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # UI状态
        self.selected_cards = []
        self.card_rects = {}
        
        # 按钮
        self.buttons = {
            'new_game': Button(50, 50, 100, 35, "New Game"),
            'play_cards': Button(width - 150, height - 60, 100, 35, "Play Cards"),
            'confirm_discard': Button(width - 150, height - 100, 120, 35, "Confirm Discard"),
            'quit': Button(50, 20, 50, 25, "Quit", 16)  # 移到左上角
        }
        
        # 消息显示
        self.messages = []
        self.message_timer = 0
        
        # 花色能力说明
        self.suit_abilities = {
            "H": "Hearts: Heal cards from discard",
            "D": "Diamonds: Draw more cards",
            "S": "Spades: Deal extra damage", 
            "C": "Clubs: Double damage"
        }
        
        # 手牌滚动相关变量
        self.hand_scroll_offset = 0  # 手牌滚动偏移量
        self.max_visible_cards = 12  # 屏幕最多显示的手牌数量
        self.card_spacing = 105      # 卡牌间距（适应更大的卡牌）
    
    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 鼠标滚轮事件 - 滚动手牌
            elif event.type == pygame.MOUSEWHEEL:
                if self.game.game_state == GameState.PLAYING:
                    self.handle_hand_scroll(event.y)
            
            # 按钮事件
            for button_name, button in self.buttons.items():
                if button.handle_event(event):
                    self.handle_button_click(button_name)
            
            # 卡牌点击事件
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_card_click(event.pos)
    
    def handle_button_click(self, button_name):
        """处理按钮点击"""
        if button_name == 'new_game':
            self.game.start_new_game()
            self.selected_cards.clear()
            self.hand_scroll_offset = 0  # 重置滚动偏移
            self.add_message("New game started!")
            
        elif button_name == 'play_cards':
            if self.selected_cards and self.game.game_state == GameState.PLAYING:
                result = self.game.play_cards(self.selected_cards)
                if result:
                    self.show_battle_result(result)
                    self.selected_cards.clear()
                    # 调整滚动位置以防止超出范围
                    self.adjust_scroll_position()
                else:
                    self.add_message("Cannot play these cards!")
        
        elif button_name == 'confirm_discard':
            if self.game.game_state == GameState.DISCARD_SELECTION:
                if self.game.can_confirm_discard():
                    self.game.confirm_discard()
                    self.add_message("Discard confirmed!")
                else:
                    current_value = sum(card.attack_value for card in self.game.selected_for_discard)
                    required = self.game.required_discard_value
                    self.add_message(f"Need {required} points, selected {current_value}")
                    
        elif button_name == 'quit':
            self.running = False
    
    def handle_hand_scroll(self, scroll_y):
        """处理手牌滚动"""
        hand = self.game.get_current_player_hand()
        if not hand or hand.size() <= self.max_visible_cards:
            return  # 如果手牌不多，不需要滚动
        
        # 滚动方向：向上滚动（scroll_y > 0）向左移动，向下滚动（scroll_y < 0）向右移动
        scroll_speed = 2  # 每次滚动移动的卡牌数量
        
        if scroll_y > 0:  # 向上滚轮，左滚动
            self.hand_scroll_offset = max(0, self.hand_scroll_offset - scroll_speed)
        elif scroll_y < 0:  # 向下滚轮，右滚动  
            max_offset = max(0, hand.size() - self.max_visible_cards)
            self.hand_scroll_offset = min(max_offset, self.hand_scroll_offset + scroll_speed)
    
    def adjust_scroll_position(self):
        """调整滚动位置以防超出范围"""
        hand = self.game.get_current_player_hand()
        if not hand:
            self.hand_scroll_offset = 0
            return
        
        max_offset = max(0, hand.size() - self.max_visible_cards)
        self.hand_scroll_offset = min(self.hand_scroll_offset, max_offset)
    
    def handle_card_click(self, pos):
        """处理卡牌点击"""
        # 检查点击的是哪张手牌
        for card, rect in self.card_rects.items():
            if rect.collidepoint(pos):
                
                # 弃牌选择模式
                if self.game.game_state == GameState.DISCARD_SELECTION:
                    self.game.toggle_discard_selection(card)
                    break
                
                # 正常出牌模式
                elif self.game.game_state == GameState.PLAYING:
                    if card in self.selected_cards:
                        self.selected_cards.remove(card)
                    else:
                        # 检查是否可以组合
                        if not self.selected_cards:
                            self.selected_cards.append(card)
                        else:
                            # 检查是否可以组合（支持A牌宠物机制）
                            can_combine = False
                            
                            # 如果新卡是A，总是可以添加
                            if card.rank == Rank.ACE:
                                can_combine = True
                            # 如果已选的卡片中有A，且新卡与非A卡同牌面
                            elif any(c.rank == Rank.ACE for c in self.selected_cards):
                                non_ace_ranks = [c.rank for c in self.selected_cards if c.rank != Rank.ACE]
                                if not non_ace_ranks or card.rank == non_ace_ranks[0]:
                                    can_combine = True
                            # 如果都不是A，检查是否同牌面
                            elif card.rank == self.selected_cards[0].rank:
                                can_combine = True
                                
                            if can_combine:
                                self.selected_cards.append(card)
                            else:
                                # 重新选择
                                self.selected_cards = [card]
                break
    
    def add_message(self, text):
        """添加消息"""
        self.messages.append(text)
        self.message_timer = 180  # 3秒显示时间
        
        # 只保留最近5条消息
        if len(self.messages) > 5:
            self.messages.pop(0)
    
    def show_battle_result(self, result):
        """显示战斗结果"""
        summary = result.get_summary()
        for line in summary:
            # 转换中文消息为英文
            english_line = self._translate_message(line)
            self.add_message(english_line)
    
    def _translate_message(self, message):
        """转换消息为英文"""
        translations = {
            "对敌人造成": "Dealt",
            "点伤害": " damage to enemy",
            "受到": "Took", 
            "点反击伤害": " counter damage",
            "敌人被击败": "Enemy defeated!",
            "抽取了": "Drew",
            "张牌": " cards",
            "回复了": "Healed",
            "组合牌加成": "Combo bonus",
            "红桃治疗": "Hearts heal",
            "方块抽牌": "Diamonds draw", 
            "黑桃攻击": "Spades attack",
            "梅花翻倍": "Clubs double damage"
        }
        
        # 简单的消息转换
        if "造成" in message and "伤害" in message:
            return f"Dealt {message.split()[1]} damage"
        elif "反击伤害" in message:
            return f"Took {message.split()[1]} counter damage"
        elif "敌人被击败" in message:
            return "Enemy defeated!"
        elif "抽取了" in message:
            return f"Drew {message.split()[1]} cards"
        elif "回复了" in message:
            return f"Healed {message.split()[1]} cards"
        else:
            return message
    
    def update(self):
        """更新游戏状态"""
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer <= 0:
                self.messages.clear()
    
    def draw(self):
        """绘制游戏画面"""
        # 渐变背景
        self.draw_gradient_background()
        
        if self.game.game_state == GameState.MENU:
            self.draw_menu()
        elif self.game.game_state in [GameState.PLAYING, GameState.PLAYER_TURN]:
            self.draw_game()
        elif self.game.game_state == GameState.DISCARD_SELECTION:
            self.draw_discard_selection()
        elif self.game.game_state == GameState.VICTORY:
            self.draw_victory()
        elif self.game.game_state == GameState.DEFEAT:
            self.draw_defeat()
        
        # 根据游戏状态绘制相应按钮
        self.draw_buttons()
        
        # 绘制消息
        self.draw_messages()
        
        # 绘制花色说明
        self.draw_suit_guide()
        
        pygame.display.flip()
    
    def draw_gradient_background(self):
        """绘制渐变背景"""
        for y in range(self.height):
            ratio = y / self.height
            r = int(Colors.DARK_BLUE[0] + (Colors.NAVY[0] - Colors.DARK_BLUE[0]) * ratio)
            g = int(Colors.DARK_BLUE[1] + (Colors.NAVY[1] - Colors.DARK_BLUE[1]) * ratio)
            b = int(Colors.DARK_BLUE[2] + (Colors.NAVY[2] - Colors.DARK_BLUE[2]) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
    
    def draw_menu(self):
        """绘制菜单界面"""
        # 标题
        title_text = self.font_large.render("REGICIDE", True, Colors.GOLD)
        title_x = self.width // 2 - title_text.get_width() // 2
        title_y = self.height // 2 - 100
        self.screen.blit(title_text, (title_x, title_y))
        
        # 副标题
        subtitle_text = self.font_medium.render("Card Battle Game", True, Colors.WHITE)
        subtitle_x = self.width // 2 - subtitle_text.get_width() // 2
        subtitle_y = title_y + 60
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
        
        # 规则说明
        rules = [
            "Goal: Defeat all 12 enemies (4 Jacks, 4 Queens, 4 Kings)",
            "H=Heal  D=Draw  S=Attack  C=Double",
            "Same rank cards can combo for extra damage",
            "Click cards to select, then click Play Cards"
        ]
        
        for i, rule in enumerate(rules):
            rule_text = self.font_small.render(rule, True, Colors.TEXT_LIGHT)
            rule_x = self.width // 2 - rule_text.get_width() // 2
            rule_y = subtitle_y + 80 + i * 25
            self.screen.blit(rule_text, (rule_x, rule_y))
    
    def draw_game(self):
        """绘制游戏界面"""
        game_info = self.game.get_game_state_info()
        hand_info = self.game.get_hand_info()
        
        # 绘制当前敌人
        if game_info['current_enemy']:
            enemy_x = self.width // 2 - 60
            enemy_y = 100
            self.card_renderer.draw_enemy_card(self.screen, game_info['current_enemy'], enemy_x, enemy_y)
        
        # 绘制手牌
        self.draw_hand(hand_info['cards'])
        
        # 绘制游戏信息
        self.draw_game_info(game_info, hand_info)
        
        # 绘制牌堆
        self.draw_deck_display()
        
        # 绘制选中卡牌的效果预览
        if self.selected_cards:
            self.draw_play_preview()
    
    def draw_hand(self, cards):
        """绘制手牌 - 支持滚动"""
        if not cards:
            return

        self.card_rects.clear()

        # 计算可见手牌范围
        total_cards = len(cards)
        start_index = self.hand_scroll_offset
        end_index = min(start_index + self.max_visible_cards, total_cards)
        visible_cards = cards[start_index:end_index]

        # 手牌区域定位
        hand_area_margin = 60
        hand_area_y = self.height - 190
        hand_area_height = 170
        hand_area_rect = pygame.Rect(hand_area_margin, hand_area_y, self.width - 2 * hand_area_margin, hand_area_height)

        # 绘制手牌区域背景
        pygame.draw.rect(self.screen, (40, 40, 80, 100), hand_area_rect)
        pygame.draw.rect(self.screen, Colors.WHITE, hand_area_rect, 2)

        # 计算可见手牌布局
        if visible_cards:
            # 手牌垂直居中位置
            hand_y = hand_area_y + (hand_area_height - self.card_renderer.card_height) // 2

            # 计算水平居中布局
            visible_width = len(visible_cards) * self.card_spacing - (self.card_spacing - self.card_renderer.card_width)
            available_width = hand_area_rect.width - 20  # 留出边距

            if visible_width <= available_width:
                # 卡牌可以完全居中
                start_x = hand_area_rect.x + (available_width - visible_width) // 2 + 10
            else:
                # 卡牌太多，从左边开始排列
                start_x = hand_area_rect.x + 10

            # 绘制可见手牌
            for i, card in enumerate(visible_cards):
                x = start_x + i * self.card_spacing

                # 确保卡牌不超出手牌区域
                if x + self.card_renderer.card_width > hand_area_rect.right - 10:
                    break

                # 根据游戏状态确定选择状态
                if self.game.game_state == GameState.DISCARD_SELECTION:
                    selected = card in self.game.selected_for_discard
                else:
                    selected = card in self.selected_cards

                card_rect = self.card_renderer.draw_card(self.screen, card, x, hand_y, selected)
                self.card_rects[card] = card_rect

        # 绘制滚动指示器
        self.draw_scroll_indicators(total_cards)
    
    def draw_scroll_indicators(self, total_cards):
        """绘制滚动指示器"""
        if total_cards <= self.max_visible_cards:
            return  # 无需滚动指示器

        # 手牌区域相关参数（与draw_hand保持一致）
        hand_area_margin = 60
        hand_area_y = self.height - 190
        hand_area_height = 170

        # 滚动指示器位置（在手牌区域底部）
        indicator_y = hand_area_y + hand_area_height + 10

        # 左滚动箭头
        if self.hand_scroll_offset > 0:
            left_arrow_pos = (hand_area_margin + 20, indicator_y)
            pygame.draw.polygon(self.screen, Colors.WHITE, [
                (left_arrow_pos[0], left_arrow_pos[1]),
                (left_arrow_pos[0] + 15, left_arrow_pos[1] - 8),
                (left_arrow_pos[0] + 15, left_arrow_pos[1] + 8)
            ])
            # 显示左侧隐藏的牌数
            left_text = self.font_small.render(f"<{self.hand_scroll_offset}", True, Colors.WHITE)
            self.screen.blit(left_text, (left_arrow_pos[0] + 20, left_arrow_pos[1] - 8))

        # 右滚动箭头
        max_offset = max(0, total_cards - self.max_visible_cards)
        if self.hand_scroll_offset < max_offset:
            right_arrow_pos = (self.width - hand_area_margin - 35, indicator_y)
            pygame.draw.polygon(self.screen, Colors.WHITE, [
                (right_arrow_pos[0], right_arrow_pos[1]),
                (right_arrow_pos[0] - 15, right_arrow_pos[1] - 8),
                (right_arrow_pos[0] - 15, right_arrow_pos[1] + 8)
            ])
            # 显示右侧隐藏的牌数
            hidden_right = total_cards - (self.hand_scroll_offset + self.max_visible_cards)
            right_text = self.font_small.render(f"{hidden_right}>", True, Colors.WHITE)
            text_rect = right_text.get_rect()
            self.screen.blit(right_text, (right_arrow_pos[0] - text_rect.width - 20, right_arrow_pos[1] - 8))

        # 滚动状态文字
        status_text = f"Cards {self.hand_scroll_offset + 1}-{min(self.hand_scroll_offset + self.max_visible_cards, total_cards)} of {total_cards}"
        status_surface = self.font_small.render(status_text, True, Colors.TEXT_LIGHT)
        status_rect = status_surface.get_rect()
        status_x = (self.width - status_rect.width) // 2
        self.screen.blit(status_surface, (status_x, indicator_y - 20))

        # 滚动说明文字
        scroll_help = "Use mouse wheel to scroll through hand cards"
        help_surface = self.font_small.render(scroll_help, True, Colors.TEXT_LIGHT)
        help_rect = help_surface.get_rect()
        help_x = (self.width - help_rect.width) // 2
        self.screen.blit(help_surface, (help_x, indicator_y + 15))
    
    def draw_game_info(self, game_info, hand_info):
        """绘制游戏信息"""
        info_x = 50
        info_y = 150
        
        # 转换阶段信息
        phase = self._translate_phase(game_info['current_phase'])
        
        infos = [
            f"Phase: {phase}",
            f"Progress: {game_info['phase_progress']}",
            f"Enemies Left: {game_info['remaining_enemies']}",
            f"Deck: {game_info['deck_size']} cards",
            f"Discard: {game_info['discard_pile_size']} cards",
            f"Hand: {hand_info['size']} cards",
            f"Turn: {game_info['turn_count']}"
        ]
        
        for i, info in enumerate(infos):
            info_text = self.font_small.render(info, True, Colors.TEXT_LIGHT)
            self.screen.blit(info_text, (info_x, info_y + i * 25))
    
    def _translate_phase(self, phase):
        """转换阶段名称"""
        if "杰克" in phase:
            return "Jacks"
        elif "皇后" in phase:
            return "Queens"
        elif "国王" in phase:
            return "Kings"
        elif "胜利" in phase:
            return "Victory!"
        return phase
    
    def draw_play_preview(self):
        """绘制出牌效果预览"""
        effectiveness = self.game.calculate_play_effectiveness(self.selected_cards)
        if not effectiveness:
            return
        
        preview_x = self.width - 300
        preview_y = 340  # 调整到花色说明下方，增加更多间距
        
        # 背景
        preview_bg = pygame.Rect(preview_x - 10, preview_y - 10, 280, 150)
        pygame.draw.rect(self.screen, Colors.NAVY, preview_bg)
        pygame.draw.rect(self.screen, Colors.WHITE, preview_bg, 1)
        
        # 预览信息
        preview_info = [
            "Play Preview:",
            f"Total Attack: {effectiveness['total_attack']}",
            f"Damage to Enemy: {effectiveness['damage_to_enemy']}",
            f"Counter Damage: {effectiveness['counter_damage']}"
        ]
        
        if effectiveness['combo_bonus'] > 0:
            preview_info.append(f"Combo Bonus: +{effectiveness['combo_bonus']}")
        
        if effectiveness['will_defeat_enemy']:
            preview_info.append("Will defeat enemy!")
        
        for i, info in enumerate(preview_info):
            color = Colors.GOLD if i == 0 else Colors.WHITE
            if "Will defeat" in info:
                color = Colors.LIGHT_GREEN
                
            info_text = self.font_small.render(info, True, color)
            self.screen.blit(info_text, (preview_x, preview_y + i * 20))
    
    def draw_victory(self):
        """绘制胜利界面"""
        victory_text = self.font_large.render("VICTORY!", True, Colors.GOLD)
        victory_x = self.width // 2 - victory_text.get_width() // 2
        victory_y = self.height // 2 - 50
        self.screen.blit(victory_text, (victory_x, victory_y))
        
        subtitle_text = self.font_medium.render("All enemies defeated!", True, Colors.WHITE)
        subtitle_x = self.width // 2 - subtitle_text.get_width() // 2
        subtitle_y = victory_y + 60
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    def draw_defeat(self):
        """绘制失败界面"""
        defeat_text = self.font_large.render("DEFEAT", True, Colors.RED)
        defeat_x = self.width // 2 - defeat_text.get_width() // 2
        defeat_y = self.height // 2 - 50
        self.screen.blit(defeat_text, (defeat_x, defeat_y))
        
        subtitle_text = self.font_medium.render("Not enough cards to continue...", True, Colors.WHITE)
        subtitle_x = self.width // 2 - subtitle_text.get_width() // 2
        subtitle_y = defeat_y + 60
        self.screen.blit(subtitle_text, (subtitle_x, subtitle_y))
    
    def draw_messages(self):
        """绘制消息"""
        if not self.messages:
            return
        
        message_x = 50
        message_y = self.height - 300
        
        for i, message in enumerate(self.messages):
            alpha = min(255, self.message_timer * 2)  # 淡出效果
            message_text = self.font_small.render(message, True, Colors.WHITE)
            self.screen.blit(message_text, (message_x, message_y + i * 20))
    
    def draw_suit_guide(self):
        """绘制花色说明"""
        guide_x = self.width - 350
        guide_y = 180
        
        # 背景
        guide_bg = pygame.Rect(guide_x - 10, guide_y - 10, 330, 120)
        pygame.draw.rect(self.screen, Colors.NAVY, guide_bg)
        pygame.draw.rect(self.screen, Colors.WHITE, guide_bg, 1)
        
        # 标题
        title_text = self.font_small.render("Suit Abilities:", True, Colors.GOLD)
        self.screen.blit(title_text, (guide_x, guide_y))
        
        # 花色说明
        abilities = [
            "H (Hearts): Heal cards from discard",
            "D (Diamonds): Draw more cards",
            "S (Spades): Weaken enemy attack",
            "C (Clubs): Double damage"
        ]
        
        for i, ability in enumerate(abilities):
            ability_text = self.font_small.render(ability, True, Colors.WHITE)
            self.screen.blit(ability_text, (guide_x, guide_y + 20 + i * 18))
    
    def draw_buttons(self):
        """根据游戏状态绘制相应按钮"""
        if self.game.game_state == GameState.DISCARD_SELECTION:
            # 弃牌选择模式只显示确认按钮和退出按钮
            self.buttons['confirm_discard'].draw(self.screen)
            self.buttons['quit'].draw(self.screen)
        else:
            # 其他状态显示所有按钮（除了弃牌确认按钮）
            for name, button in self.buttons.items():
                if name != 'confirm_discard':
                    button.draw(self.screen)
    
    def draw_discard_selection(self):
        """绘制弃牌选择界面"""
        # 绘制基本游戏界面
        self.draw_game()
        
        # 半透明覆盖层
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 弃牌选择提示
        title_text = self.font_large.render("Select Cards to Discard", True, Colors.WHITE)
        title_x = self.width // 2 - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, 150))
        
        # 显示需求信息
        current_value = sum(card.attack_value for card in self.game.selected_for_discard)
        required = self.game.required_discard_value
        info_text = f"Required: {required} points | Selected: {current_value} points"
        
        info_surface = self.font_medium.render(info_text, True, Colors.WHITE)
        info_x = self.width // 2 - info_surface.get_width() // 2
        self.screen.blit(info_surface, (info_x, 190))
        
        # 提示文字
        hint_text = "Click cards to select/deselect them for discard"
        hint_surface = self.font_small.render(hint_text, True, Colors.SILVER)
        hint_x = self.width // 2 - hint_surface.get_width() // 2
        self.screen.blit(hint_surface, (hint_x, 220))
    
    def draw_deck_display(self):
        """绘制牌堆显示区域"""
        # 牌堆显示位置（右侧更高，更紧凑）
        deck_x = self.width - 140
        deck_y = 30
        
        # 绘制牌堆背景区域（更小）
        deck_area = pygame.Rect(deck_x - 10, deck_y - 10, 120, 150)
        pygame.draw.rect(self.screen, (30, 30, 60), deck_area)
        pygame.draw.rect(self.screen, Colors.WHITE, deck_area, 2)
        
        # 标题
        title_text = self.font_small.render("Deck", True, Colors.WHITE)
        title_x = deck_x + 50 - title_text.get_width() // 2
        self.screen.blit(title_text, (title_x, deck_y))
        
        # 获取牌堆信息
        remaining_cards = len(self.game.deck.cards)
        discard_pile_count = len(self.game.discard_pile)
        
        # 绘制牌堆卡背（如果有牌）- 更小的卡牌
        if remaining_cards > 0:
            card_back_x = deck_x + 50 - 15  # 30x40 小卡牌
            card_back_y = deck_y + 20
            card_rect = pygame.Rect(card_back_x, card_back_y, 30, 40)
            pygame.draw.rect(self.screen, Colors.NAVY, card_rect)
            pygame.draw.rect(self.screen, Colors.WHITE, card_rect, 1)
        
        # 显示剩余牌数
        remaining_text = f"Deck: {remaining_cards}"
        remaining_surface = self.font_small.render(remaining_text, True, Colors.WHITE)
        remaining_x = deck_x + 50 - remaining_surface.get_width() // 2
        self.screen.blit(remaining_surface, (remaining_x, deck_y + 70))
        
        # 显示弃牌堆数量
        discard_text = f"Discard: {discard_pile_count}"
        discard_surface = self.font_small.render(discard_text, True, Colors.SILVER)
        discard_x = deck_x + 50 - discard_surface.get_width() // 2
        self.screen.blit(discard_surface, (discard_x, deck_y + 90))
        
        # 如果牌堆为空，显示警告
        if remaining_cards == 0:
            warning_text = "EMPTY!"
            warning_surface = self.font_small.render(warning_text, True, Colors.RED)
            warning_x = deck_x + 50 - warning_surface.get_width() // 2
            self.screen.blit(warning_surface, (warning_x, deck_y + 45))

if __name__ == "__main__":
    game = RegicideFixedGUI()
    game.run()