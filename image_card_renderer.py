# -*- coding: utf-8 -*-
"""
Image-based Card Renderer for Regicide Game
基于图像的卡牌渲染器
"""

import pygame
import os
from card import Card, Suit, Rank
from enemy import Enemy

class ImageCardRenderer:
    """基于图像的卡牌渲染器"""

    def __init__(self):
        # 卡牌尺寸（增大手牌尺寸以便更好地看清花色）
        self.card_width = 100
        self.card_height = 150
        self.small_card_width = 80
        self.small_card_height = 120

        # 敌人卡牌尺寸
        self.enemy_card_width = int(self.card_width * 1.5)
        self.enemy_card_height = int(self.card_height * 1.5)

        # 图像缓存
        self.card_images = {}
        self.enemy_images = {}
        self.card_back_image = None

        # 加载所有图像
        self._load_all_images()

        # 颜色定义
        self.colors = {
            'gold': (255, 215, 0),
            'white': (255, 255, 255),
            'green': (144, 238, 144)
        }

    def _load_all_images(self):
        """加载所有卡牌图像"""
        print("Loading card images...")

        # 加载普通卡牌
        for suit in Suit:
            for rank in Rank:
                # 跳过敌人卡牌
                if rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
                    continue

                filename = f"assets/images/cards/{suit.name.lower()}_{rank.name.lower()}.png"
                if os.path.exists(filename):
                    image = pygame.image.load(filename)
                    self.card_images[(suit, rank)] = image
                else:
                    print(f"Warning: Image not found: {filename}")

        # 加载敌人卡牌
        for suit in Suit:
            for rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
                filename = f"assets/images/enemies/{suit.name.lower()}_{rank.name.lower()}.png"
                if os.path.exists(filename):
                    image = pygame.image.load(filename)
                    self.enemy_images[(suit, rank)] = image
                else:
                    print(f"Warning: Enemy image not found: {filename}")

        # 加载卡背
        back_filename = "assets/images/backs/card_back.png"
        if os.path.exists(back_filename):
            self.card_back_image = pygame.image.load(back_filename)
        else:
            print(f"Warning: Card back image not found: {back_filename}")

        print(f"Loaded {len(self.card_images)} card images and {len(self.enemy_images)} enemy images")

    def draw_card(self, surface, card, x, y, selected=False, small=False):
        """绘制单张卡牌"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height

        # 获取卡牌图像
        card_key = (card.suit, card.rank)
        if card_key in self.card_images:
            # 缩放图像到合适大小
            original_image = self.card_images[card_key]
            scaled_image = pygame.transform.scale(original_image, (width, height))

            # 绘制卡牌
            card_rect = pygame.Rect(x, y, width, height)
            surface.blit(scaled_image, (x, y))

            # 如果被选中，绘制金色边框
            if selected:
                pygame.draw.rect(surface, self.colors['gold'], card_rect, 3)

        else:
            # 如果没有图像，回退到文本渲染
            card_rect = self._draw_fallback_card(surface, card, x, y, selected, small)

        return pygame.Rect(x, y, width, height)

    def draw_card_back(self, surface, x, y, small=False):
        """绘制卡背"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height

        if self.card_back_image:
            # 缩放卡背图像
            scaled_back = pygame.transform.scale(self.card_back_image, (width, height))
            surface.blit(scaled_back, (x, y))
        else:
            # 回退到简单的卡背绘制
            self._draw_fallback_card_back(surface, x, y, small)

        return pygame.Rect(x, y, width, height)

    def draw_enemy_card(self, surface, enemy, x, y):
        """绘制敌人卡牌"""
        width = self.enemy_card_width
        height = self.enemy_card_height

        # 获取敌人图像
        enemy_key = (enemy.suit, enemy.rank)
        if enemy_key in self.enemy_images:
            # 缩放敌人图像
            original_image = self.enemy_images[enemy_key]
            scaled_image = pygame.transform.scale(original_image, (width, height))

            # 绘制敌人卡牌
            surface.blit(scaled_image, (x, y))

            # 在图像上绘制当前生命值和攻击力信息
            self._draw_enemy_stats(surface, enemy, x, y, width, height)

        else:
            # 回退到文本渲染
            self._draw_fallback_enemy(surface, enemy, x, y)

        return pygame.Rect(x, y, width, height)

    def _draw_enemy_stats(self, surface, enemy, x, y, width, height):
        """在敌人卡牌上绘制状态信息"""
        font_large = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)

        # 半透明背景
        stats_bg = pygame.Surface((width, 60))
        stats_bg.set_alpha(180)
        stats_bg.fill((0, 0, 0))
        surface.blit(stats_bg, (x, y + height - 60))

        # 生命值
        health_text = f"HP: {enemy.current_health}/{enemy.max_health}"
        health_surface = font_large.render(health_text, True, self.colors['white'])
        health_x = x + width // 2 - health_surface.get_width() // 2
        health_y = y + height - 50
        surface.blit(health_surface, (health_x, health_y))

        # 攻击力
        attack_text = f"ATK: {enemy.attack_power}"
        attack_surface = font_small.render(attack_text, True, self.colors['white'])
        attack_x = x + width // 2 - attack_surface.get_width() // 2
        attack_y = y + height - 25
        surface.blit(attack_surface, (attack_x, attack_y))

        # 生命值条
        health_bar_width = width - 20
        health_bar_height = 6
        health_bar_x = x + 10
        health_bar_y = y + height - 15

        # 背景
        health_bg_rect = pygame.Rect(health_bar_x, health_bar_y, health_bar_width, health_bar_height)
        pygame.draw.rect(surface, (100, 100, 100), health_bg_rect)

        # 当前生命值
        if enemy.max_health > 0:
            health_ratio = enemy.current_health / enemy.max_health
            current_width = int(health_bar_width * health_ratio)

            # 根据生命值选择颜色
            if health_ratio > 0.6:
                bar_color = self.colors['green']
            elif health_ratio > 0.3:
                bar_color = (255, 255, 0)  # 黄色
            else:
                bar_color = (255, 0, 0)    # 红色

            if current_width > 0:
                current_rect = pygame.Rect(health_bar_x, health_bar_y, current_width, health_bar_height)
                pygame.draw.rect(surface, bar_color, current_rect)

    def _draw_fallback_card(self, surface, card, x, y, selected=False, small=False):
        """回退的文本卡牌绘制"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height

        # 基本卡牌背景
        card_rect = pygame.Rect(x, y, width, height)
        border_color = self.colors['gold'] if selected else self.colors['white']
        background_color = self.colors['white']

        pygame.draw.rect(surface, border_color, card_rect, 3 if selected else 1)
        inner_rect = pygame.Rect(x + 2, y + 2, width - 4, height - 4)
        pygame.draw.rect(surface, background_color, inner_rect)

        # 简单的文本显示
        font = pygame.font.Font(None, 16 if small else 20)

        # 花色符号映射
        suit_symbols = {
            Suit.HEARTS: "♥",
            Suit.DIAMONDS: "♦",
            Suit.SPADES: "♠",
            Suit.CLUBS: "♣"
        }

        # 牌面值
        rank_names = {
            Rank.ACE: "A", Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4",
            Rank.FIVE: "5", Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8",
            Rank.NINE: "9", Rank.TEN: "10"
        }

        suit_color = (220, 20, 20) if card.suit in [Suit.HEARTS, Suit.DIAMONDS] else (20, 20, 20)

        rank_text = rank_names.get(card.rank, card.rank.name[0])
        suit_text = suit_symbols[card.suit]

        # 绘制文本
        rank_surface = font.render(rank_text, True, suit_color)
        suit_surface = font.render(suit_text, True, suit_color)

        surface.blit(rank_surface, (x + 5, y + 5))
        surface.blit(suit_surface, (x + 5, y + 25))

        return card_rect

    def _draw_fallback_card_back(self, surface, x, y, small=False):
        """回退的卡背绘制"""
        width = self.small_card_width if small else self.card_width
        height = self.small_card_height if small else self.card_height

        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (20, 30, 48), card_rect)
        pygame.draw.rect(surface, self.colors['white'], card_rect, 2)

        # 简单装饰
        center_x = x + width // 2
        center_y = y + height // 2
        pygame.draw.circle(surface, self.colors['gold'], (center_x, center_y), width // 4, 2)

    def _draw_fallback_enemy(self, surface, enemy, x, y):
        """回退的敌人卡牌绘制"""
        width = self.enemy_card_width
        height = self.enemy_card_height

        # 根据敌人类型选择颜色
        if enemy.rank == Rank.JACK:
            bg_color = (34, 139, 34)  # 绿色
        elif enemy.rank == Rank.QUEEN:
            bg_color = (138, 43, 226)  # 紫色
        else:  # KING
            bg_color = (255, 140, 0)   # 橙色

        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, card_rect)
        pygame.draw.rect(surface, self.colors['gold'], card_rect, 4)

        # 简单的敌人信息显示
        font = pygame.font.Font(None, 24)
        name_text = f"{enemy.rank.name}"
        name_surface = font.render(name_text, True, self.colors['white'])
        name_x = x + width // 2 - name_surface.get_width() // 2
        name_y = y + 10
        surface.blit(name_surface, (name_x, name_y))