# -*- coding: utf-8 -*-
"""
幽灵信号 - 怀疑度系统模块
业务逻辑包含一个"怀疑度"计数器
若玩家多次在交互中选择错误的频率或回复，将导致游戏进入"信号中断"的失败结局
"""

import pygame
import random
from typing import Optional, Callable, List
from game_data import SUSPICION_CONFIG, STORY_TEXTS


class SuspicionSystem:
    """
    怀疑度系统
    跟踪玩家的错误操作，当怀疑度达到阈值时触发失败结局
    """
    
    def __init__(self):
        self.value = SUSPICION_CONFIG["initial_value"]
        self.max_value = SUSPICION_CONFIG["max_value"]
        self.failure_threshold = SUSPICION_CONFIG["failure_threshold"]
        
        # 惩罚值配置
        self.wrong_frequency_penalty = SUSPICION_CONFIG["wrong_frequency_penalty"]
        self.wrong_combination_penalty = SUSPICION_CONFIG["wrong_combination_penalty"]
        self.hint_usage_penalty = SUSPICION_CONFIG["hint_usage_penalty"]
        self.correct_action_reduction = SUSPICION_CONFIG["correct_action_reduction"]
        
        # 状态
        self.is_failure = False
        self.warning_shown = False
        
        # 回调函数
        self.on_failure: Optional[Callable] = None
        self.on_warning: Optional[Callable] = None
        self.on_value_changed: Optional[Callable[[int], None]] = None
        
        # 历史记录
        self.history: List[dict] = []
        
    def add_suspicion(self, amount: int, reason: str = ""):
        """
        增加怀疑度
        
        Args:
            amount: 增加的值
            reason: 原因
        """
        if self.is_failure:
            return
            
        old_value = self.value
        self.value = min(self.max_value, self.value + amount)
        
        # 记录历史
        self.history.append({
            "type": "increase",
            "amount": amount,
            "reason": reason,
            "new_value": self.value
        })
        
        # 触发值变化回调
        if self.on_value_changed:
            self.on_value_changed(self.value)
            
        # 检查警告阈值
        if not self.warning_shown and self.value >= self.max_value * 0.7:
            self.warning_shown = True
            if self.on_warning:
                self.on_warning()
                
        # 检查是否达到失败阈值
        if self.value >= self.failure_threshold:
            self._trigger_failure()
            
    def reduce_suspicion(self, amount: int, reason: str = ""):
        """
        减少怀疑度（正确操作奖励）
        
        Args:
            amount: 减少的值
            reason: 原因
        """
        if self.is_failure:
            return
            
        old_value = self.value
        self.value = max(0, self.value - amount)
        
        # 记录历史
        self.history.append({
            "type": "decrease",
            "amount": amount,
            "reason": reason,
            "new_value": self.value
        })
        
        # 触发值变化回调
        if self.on_value_changed:
            self.on_value_changed(self.value)
            
    def on_wrong_frequency(self):
        """错误的频率操作"""
        self.add_suspicion(self.wrong_frequency_penalty, "错误的频率")
        
    def on_wrong_combination(self):
        """错误的物品组合"""
        self.add_suspicion(self.wrong_combination_penalty, "错误的物品组合")
        
    def on_hint_used(self):
        """使用提示"""
        self.add_suspicion(self.hint_usage_penalty, "使用提示")
        
    def on_correct_action(self):
        """正确的操作"""
        self.reduce_suspicion(self.correct_action_reduction, "正确操作")
        
    def _trigger_failure(self):
        """触发失败结局"""
        self.is_failure = True
        if self.on_failure:
            self.on_failure()
            
    def get_percentage(self) -> float:
        """获取怀疑度百分比"""
        return self.value / self.max_value
        
    def get_status_text(self) -> str:
        """获取当前状态文本"""
        percentage = self.get_percentage()
        
        if percentage < 0.3:
            return "信任"
        elif percentage < 0.5:
            return "怀疑"
        elif percentage < 0.7:
            return "警惕"
        elif percentage < 0.9:
            return "危险"
        else:
            return "临界"
            
    def get_status_color(self) -> tuple:
        """获取状态颜色"""
        percentage = self.get_percentage()
        
        if percentage < 0.3:
            return (0, 255, 0)  # 绿色
        elif percentage < 0.5:
            return (255, 255, 0)  # 黄色
        elif percentage < 0.7:
            return (255, 165, 0)  # 橙色
        else:
            return (255, 0, 0)  # 红色
            
    def reset(self):
        """重置系统"""
        self.value = SUSPICION_CONFIG["initial_value"]
        self.is_failure = False
        self.warning_shown = False
        self.history.clear()
        
    def set_callbacks(self,
                     on_failure: Optional[Callable] = None,
                     on_warning: Optional[Callable] = None,
                     on_value_changed: Optional[Callable[[int], None]] = None):
        """设置回调函数"""
        self.on_failure = on_failure
        self.on_warning = on_warning
        self.on_value_changed = on_value_changed


class FailureEnding:
    """
    失败结局管理器
    处理"信号中断"结局的显示和流程
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_showing = False
        self.ending_texts = STORY_TEXTS["failure_ending"]
        self.current_text_index = 0
        self.text_timer = 0
        self.text_delay = 2000  # 每段文本显示时间
        self.ending_complete = False
        
        # 视觉特效
        self.static_noise = []
        self._generate_noise()
        
    def _generate_noise(self):
        """生成静态噪点"""
        import random
        self.static_noise = []
        for _ in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(1, 3)
            self.static_noise.append((x, y, size))
            
    def start(self):
        """开始显示失败结局"""
        self.is_showing = True
        self.current_text_index = 0
        self.text_timer = 0
        self.ending_complete = False
        
    def update(self, dt: int):
        """更新结局动画"""
        if not self.is_showing or self.ending_complete:
            return
            
        self.text_timer += dt
        
        if self.text_timer >= self.text_delay:
            self.text_timer = 0
            self.current_text_index += 1
            
            if self.current_text_index >= len(self.ending_texts):
                self.ending_complete = True
                
        # 更新噪点
        self._generate_noise()
        
    def draw(self, surface: pygame.Surface):
        """绘制失败结局"""
        if not self.is_showing:
            return
            
        # 黑色背景
        surface.fill((0, 0, 0))
        
        # 绘制静态噪点（信号中断效果）
        for x, y, size in self.static_noise:
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            pygame.draw.circle(surface, color, (x, y), size)
            
        # 绘制红色警告边框
        warning_intensity = abs((pygame.time.get_ticks() % 1000) - 500) / 500
        border_color = (int(255 * warning_intensity), 0, 0)
        pygame.draw.rect(surface, border_color, 
                        (0, 0, self.screen_width, self.screen_height), 10)
        
        # 绘制文本
        if self.current_text_index < len(self.ending_texts):
            font = pygame.font.SysFont("simhei", 28)
            text = self.ending_texts[self.current_text_index]
            
            # 文本阴影效果
            shadow_surface = font.render(text, True, (100, 0, 0))
            text_surface = font.render(text, True, (255, 0, 0))
            
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 
                                                       self.screen_height // 2))
            shadow_rect = shadow_surface.get_rect(center=(self.screen_width // 2 + 2, 
                                                           self.screen_height // 2 + 2))
            
            surface.blit(shadow_surface, shadow_rect)
            surface.blit(text_surface, text_rect)
            
        # 如果结束，显示重新开始提示
        if self.ending_complete:
            hint_font = pygame.font.SysFont("simhei", 20)
            hint_text = "按 R 键重新开始"
            hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, 
                                                       self.screen_height - 100))
            surface.blit(hint_surface, hint_rect)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件
        返回: 是否重新开始游戏
        """
        if not self.is_showing or not self.ending_complete:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset()
                return True
                
        return False
        
    def reset(self):
        """重置结局状态"""
        self.is_showing = False
        self.current_text_index = 0
        self.text_timer = 0
        self.ending_complete = False
        
    def is_complete(self) -> bool:
        """检查结局是否显示完毕"""
        return self.ending_complete


class SuccessEnding:
    """
    成功结局管理器
    处理游戏成功通关的结局
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_showing = False
        self.ending_texts = STORY_TEXTS["success_ending"]
        self.current_text_index = 0
        self.text_timer = 0
        self.text_delay = 2500
        self.ending_complete = False
        
        # 星星动画
        self.stars = []
        self._generate_stars()
        
    def _generate_stars(self):
        """生成星星"""
        import random
        self.stars = []
        for _ in range(50):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height)
            size = random.randint(2, 5)
            twinkle_speed = random.uniform(0.5, 2.0)
            self.stars.append({
                "x": x, "y": y, "size": size, 
                "twinkle_speed": twinkle_speed,
                "phase": random.random() * 3.14159 * 2
            })
            
    def start(self):
        """开始显示成功结局"""
        self.is_showing = True
        self.current_text_index = 0
        self.text_timer = 0
        self.ending_complete = False
        
    def update(self, dt: int):
        """更新结局动画"""
        if not self.is_showing or self.ending_complete:
            return
            
        self.text_timer += dt
        
        if self.text_timer >= self.text_delay:
            self.text_timer = 0
            self.current_text_index += 1
            
            if self.current_text_index >= len(self.ending_texts):
                self.ending_complete = True
                
        # 更新星星闪烁
        import math
        current_time = pygame.time.get_ticks() / 1000
        for star in self.stars:
            star["brightness"] = 0.5 + 0.5 * math.sin(
                current_time * star["twinkle_speed"] + star["phase"]
            )
            
    def draw(self, surface: pygame.Surface):
        """绘制成功结局"""
        if not self.is_showing:
            return
            
        # 深蓝色背景（夜空）
        surface.fill((10, 10, 40))
        
        # 绘制星星
        for star in self.stars:
            brightness = int(255 * star.get("brightness", 1))
            color = (brightness, brightness, int(brightness * 0.9))
            pygame.draw.circle(surface, color, 
                             (star["x"], star["y"]), star["size"])
            
        # 绘制文本
        if self.current_text_index < len(self.ending_texts):
            font = pygame.font.SysFont("simhei", 28)
            text = self.ending_texts[self.current_text_index]
            
            # 金色文本
            text_surface = font.render(text, True, (255, 215, 0))
            text_rect = text_surface.get_rect(center=(self.screen_width // 2, 
                                                       self.screen_height // 2))
            surface.blit(text_surface, text_rect)
            
        # 如果结束，显示提示
        if self.ending_complete:
            hint_font = pygame.font.SysFont("simhei", 20)
            hint_text = "按 R 键重新开始"
            hint_surface = hint_font.render(hint_text, True, (200, 200, 200))
            hint_rect = hint_surface.get_rect(center=(self.screen_width // 2, 
                                                       self.screen_height - 100))
            surface.blit(hint_surface, hint_rect)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件
        返回: 是否重新开始游戏
        """
        if not self.is_showing or not self.ending_complete:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.reset()
                return True
                
        return False
        
    def reset(self):
        """重置结局状态"""
        self.is_showing = False
        self.current_text_index = 0
        self.text_timer = 0
        self.ending_complete = False
        
    def is_complete(self) -> bool:
        """检查结局是否显示完毕"""
        return self.ending_complete
