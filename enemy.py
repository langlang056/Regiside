# -*- coding: utf-8 -*-
"""
Regicide Game - Enemy System
敌人系统实现
"""

from enum import Enum
from card import Card, Suit, Rank
import random

class EnemyType(Enum):
    """敌人类型"""
    JACK = "杰克"
    QUEEN = "皇后"  
    KING = "国王"

class Enemy:
    """敌人类"""
    
    def __init__(self, card: Card):
        if not card.is_face_card:
            raise ValueError("敌人必须是人头牌（J、Q、K）")
        
        self.card = card
        self.suit = card.suit
        self.rank = card.rank
        
        # 设置敌人属性
        self.max_health = self._get_max_health()
        self.current_health = self.max_health
        self.base_attack_power = self._get_attack_power()
        self.attack_reduction = 0  # 黑桃造成的攻击力减少
        
        # 敌人状态
        self.is_defeated = False
        
    def _get_max_health(self):
        """根据牌面获取最大生命值"""
        health_values = {
            Rank.JACK: 20,
            Rank.QUEEN: 30,
            Rank.KING: 40
        }
        return health_values[self.rank]
    
    def _get_attack_power(self):
        """根据牌面获取攻击力"""
        attack_values = {
            Rank.JACK: 10,
            Rank.QUEEN: 15,
            Rank.KING: 20
        }
        return attack_values[self.rank]
    
    def take_damage(self, damage):
        """受到伤害"""
        if self.is_defeated:
            return 0
        
        actual_damage = min(damage, self.current_health)
        self.current_health -= actual_damage
        
        if self.current_health <= 0:
            self.is_defeated = True
            self.current_health = 0
            
        return actual_damage
    
    @property
    def attack_power(self):
        """获取当前实际攻击力（兼容性属性）"""
        return max(0, self.base_attack_power - self.attack_reduction)
    
    def get_current_attack_power(self):
        """获取当前实际攻击力（扣除黑桃减益）"""
        return self.attack_power
    
    def reduce_attack_power(self, reduction):
        """黑桃效果：永久降低攻击力"""
        self.attack_reduction += reduction
        return self.attack_reduction
    
    def get_counter_attack_damage(self, defense=0):
        """获取反击伤害（扣除防御）"""
        if self.is_defeated:
            return 0
        current_attack = self.get_current_attack_power()
        return max(0, current_attack - defense)
    
    def get_health_percentage(self):
        """获取血量百分比"""
        return self.current_health / self.max_health
    
    def get_enemy_type(self):
        """获取敌人类型"""
        type_map = {
            Rank.JACK: EnemyType.JACK,
            Rank.QUEEN: EnemyType.QUEEN,
            Rank.KING: EnemyType.KING
        }
        return type_map[self.rank]
    
    def get_suit_name(self):
        """获取花色中文名"""
        suit_names = {
            Suit.HEARTS: "红桃",
            Suit.DIAMONDS: "方块",
            Suit.SPADES: "黑桃",
            Suit.CLUBS: "草花"
        }
        return suit_names[self.suit]
    
    def get_display_name(self):
        """获取显示名称"""
        return f"{self.get_suit_name()}{self.get_enemy_type().value}"
    
    def get_description(self):
        """获取敌人描述"""
        return (f"{self.get_display_name()}\n"
                f"生命值: {self.current_health}/{self.max_health}\n"
                f"攻击力: {self.attack_power}")
    
    def __str__(self):
        return self.get_display_name()

class EnemyQueue:
    """敌人队列类 - 管理12个敌人的出场顺序"""
    
    def __init__(self):
        self.enemies = []
        self.current_enemy_index = 0
        self.setup_enemies()
    
    def setup_enemies(self):
        """设置敌人队列（按难度递增）"""
        # 创建所有12个敌人
        all_enemies = []
        
        # 4个杰克
        for suit in Suit:
            jack_card = Card(suit, Rank.JACK)
            all_enemies.append(Enemy(jack_card))
        
        # 4个皇后
        for suit in Suit:
            queen_card = Card(suit, Rank.QUEEN)
            all_enemies.append(Enemy(queen_card))
            
        # 4个国王
        for suit in Suit:
            king_card = Card(suit, Rank.KING)
            all_enemies.append(Enemy(king_card))
        
        # 按难度排序：先杰克，再皇后，最后国王
        jacks = [e for e in all_enemies if e.rank == Rank.JACK]
        queens = [e for e in all_enemies if e.rank == Rank.QUEEN]
        kings = [e for e in all_enemies if e.rank == Rank.KING]
        
        # 每个难度级别内部随机排序
        random.shuffle(jacks)
        random.shuffle(queens)
        random.shuffle(kings)
        
        # 组成最终队列
        self.enemies = jacks + queens + kings
        self.current_enemy_index = 0
    
    def get_current_enemy(self):
        """获取当前敌人"""
        if self.is_all_defeated():
            return None
        return self.enemies[self.current_enemy_index]
    
    def defeat_current_enemy(self):
        """击败当前敌人，移动到下一个"""
        if not self.is_all_defeated():
            current_enemy = self.enemies[self.current_enemy_index]
            current_enemy.is_defeated = True
            self.current_enemy_index += 1
    
    def get_next_enemy(self):
        """获取下一个敌人（预览）"""
        if self.current_enemy_index + 1 < len(self.enemies):
            return self.enemies[self.current_enemy_index + 1]
        return None
    
    def get_remaining_enemies(self):
        """获取剩余敌人数量"""
        return len(self.enemies) - self.current_enemy_index
    
    def get_defeated_enemies(self):
        """获取已击败的敌人数量"""
        return self.current_enemy_index
    
    def is_all_defeated(self):
        """检查是否所有敌人都被击败"""
        return self.current_enemy_index >= len(self.enemies)
    
    def get_progress_info(self):
        """获取进度信息"""
        total = len(self.enemies)
        defeated = self.get_defeated_enemies()
        return f"{defeated}/{total} 敌人已击败"
    
    def get_current_phase(self):
        """获取当前阶段"""
        if self.is_all_defeated():
            return "胜利！"
        
        current = self.get_current_enemy()
        if current.rank == Rank.JACK:
            return "第一阶段：杰克"
        elif current.rank == Rank.QUEEN:
            return "第二阶段：皇后"
        else:
            return "第三阶段：国王"
    
    def get_phase_progress(self):
        """获取当前阶段进度"""
        if self.is_all_defeated():
            return "完成"
        
        current = self.get_current_enemy()
        phase_enemies = [e for e in self.enemies if e.rank == current.rank]
        phase_defeated = sum(1 for e in phase_enemies if e.is_defeated)
        
        return f"{phase_defeated}/4"
    
    def restart(self):
        """重新开始游戏"""
        self.setup_enemies()

class BattleResult:
    """战斗结果类"""
    
    def __init__(self):
        self.damage_dealt = 0
        self.counter_damage = 0
        self.enemy_defeated = False
        self.special_effects = []
        self.cards_drawn = 0
        self.cards_healed = 0
        self.enemy_cards_discarded = 0
    
    def add_special_effect(self, effect):
        """添加特殊效果描述"""
        self.special_effects.append(effect)
    
    def get_summary(self):
        """获取战斗总结"""
        summary = []
        
        if self.damage_dealt > 0:
            summary.append(f"对敌人造成 {self.damage_dealt} 点伤害")
        
        if self.counter_damage > 0:
            summary.append(f"受到 {self.counter_damage} 点反击伤害")
        
        if self.enemy_defeated:
            summary.append("敌人被击败！")
        
        if self.cards_drawn > 0:
            summary.append(f"抽取了 {self.cards_drawn} 张牌")
            
        if self.cards_healed > 0:
            summary.append(f"回复了 {self.cards_healed} 张牌")
            
        if self.enemy_cards_discarded > 0:
            summary.append(f"敌人丢弃了 {self.enemy_cards_discarded} 张牌")
        
        summary.extend(self.special_effects)
        
        return summary