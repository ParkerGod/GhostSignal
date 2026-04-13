# -*- coding: utf-8 -*-
"""
幽灵信号 - Interactable 基类模块
所有可点击的设备（如旋钮、按钮、纸张）均继承此类
"""

import pygame
import math
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Callable, Any


class Interactable(ABC):
    """
    可交互对象基类
    所有可点击的场景物体都继承此类，并重写 on_click 和 on_hover 方法
    """
    
    def __init__(self, 
                 x: int, 
                 y: int, 
                 width: int, 
                 height: int,
                 name: str = "",
                 description: str = ""):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.description = description
        self.visible = True
        self.enabled = True
        self.is_hovered = False
        
        # 回调函数
        self.on_click_callback: Optional[Callable] = None
        self.on_hover_callback: Optional[Callable] = None
        self.on_leave_callback: Optional[Callable] = None
        
        # 视觉属性
        self.normal_color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.disabled_color = (50, 50, 50)
        self.border_color = (200, 200, 200)
        self.border_width = 2
        
    def set_callbacks(self,
                      on_click: Optional[Callable] = None,
                      on_hover: Optional[Callable] = None,
                      on_leave: Optional[Callable] = None):
        """设置回调函数"""
        self.on_click_callback = on_click
        self.on_hover_callback = on_hover
        self.on_leave_callback = on_leave
        
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool = False):
        """更新交互状态"""
        if not self.visible or not self.enabled:
            return
            
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # 鼠标进入
        if self.is_hovered and not was_hovered:
            self.on_hover()
            if self.on_hover_callback:
                self.on_hover_callback(self)
                
        # 鼠标离开
        if not self.is_hovered and was_hovered:
            if self.on_leave_callback:
                self.on_leave_callback(self)
                
        # 点击
        if self.is_hovered and mouse_clicked:
            self.on_click()
            if self.on_click_callback:
                self.on_click_callback(self)
                
    @abstractmethod
    def on_click(self):
        """点击事件 - 子类必须重写"""
        pass
        
    @abstractmethod
    def on_hover(self):
        """悬停事件 - 子类必须重写"""
        pass
        
    def draw(self, surface: pygame.Surface):
        """绘制基础形状"""
        if not self.visible:
            return
            
        color = self.disabled_color if not self.enabled else (
            self.hover_color if self.is_hovered else self.normal_color
        )
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width)
        
        # 绘制名称
        if self.name:
            font = pygame.font.SysFont("simhei", 16)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
            
    def get_position(self) -> Tuple[int, int]:
        """获取位置"""
        return (self.rect.x, self.rect.y)
        
    def set_position(self, x: int, y: int):
        """设置位置"""
        self.rect.x = x
        self.rect.y = y
        
    def contains_point(self, point: Tuple[int, int]) -> bool:
        """检查点是否在对象内"""
        return self.rect.collidepoint(point)


class RadioKnob(Interactable):
    """无线电旋钮 - 用于频率调节"""
    
    def __init__(self, x: int, y: int, radius: int = 40, name: str = "频率旋钮"):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, name)
        self.radius = radius
        self.angle = 0
        self.value = 100.0
        self.min_value = 80.0
        self.max_value = 200.0
        self.dragging = False
        
        self.normal_color = (139, 69, 19)
        self.hover_color = (160, 82, 45)
        
    def on_click(self):
        """点击开始拖动"""
        self.dragging = True
        
    def on_hover(self):
        """悬停提示"""
        pass
        
    def update_drag(self, mouse_pos: Tuple[int, int], mouse_down: bool):
        """更新拖动状态"""
        if not mouse_down:
            self.dragging = False
            return
            
        if self.dragging:
            center_x = self.rect.centerx
            center_y = self.rect.centery
            dx = mouse_pos[0] - center_x
            dy = mouse_pos[1] - center_y
            self.angle = math.atan2(dy, dx)
            # 将角度映射到频率值
            normalized_angle = (self.angle + math.pi) / (2 * math.pi)
            self.value = self.min_value + normalized_angle * (self.max_value - self.min_value)
            
    def draw(self, surface: pygame.Surface):
        """绘制旋钮"""
        if not self.visible:
            return
            
        center = (self.rect.centerx, self.rect.centery)
        color = self.hover_color if self.is_hovered else self.normal_color
        
        # 绘制外圈
        pygame.draw.circle(surface, color, center, self.radius)
        pygame.draw.circle(surface, self.border_color, center, self.radius, 3)
        
        # 绘制指示线
        end_x = center[0] + int(math.cos(self.angle) * (self.radius - 5))
        end_y = center[1] + int(math.sin(self.angle) * (self.radius - 5))
        pygame.draw.line(surface, (255, 255, 255), center, (end_x, end_y), 3)
        
        # 显示频率值
        font = pygame.font.SysFont("simhei", 14)
        text = font.render(f"{self.value:.2f}", True, (255, 255, 255))
        text_rect = text.get_rect(center=(center[0], center[1] + self.radius + 15))
        surface.blit(text, text_rect)


class ClickableButton(Interactable):
    """可点击按钮"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 name: str = "按钮", text: str = ""):
        super().__init__(x, y, width, height, name)
        self.text = text if text else name
        self.clicked = False
        
    def on_click(self):
        """按钮点击"""
        self.clicked = True
        
    def on_hover(self):
        """悬停效果"""
        pass
        
    def draw(self, surface: pygame.Surface):
        """绘制按钮"""
        if not self.visible:
            return
            
        color = self.disabled_color if not self.enabled else (
            (180, 180, 180) if self.clicked else (
                self.hover_color if self.is_hovered else self.normal_color
            )
        )
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=5)
        
        # 绘制文字
        font = pygame.font.SysFont("simhei", 18)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        self.clicked = False


class CollectablePaper(Interactable):
    """可收集的纸张/线索"""
    
    def __init__(self, x: int, y: int, width: int = 60, height: int = 80,
                 name: str = "纸张", item_id: str = ""):
        super().__init__(x, y, width, height, name)
        self.item_id = item_id
        self.collected = False
        
        self.normal_color = (245, 222, 179)
        self.hover_color = (255, 235, 205)
        
    def on_click(self):
        """收集纸张"""
        if not self.collected:
            self.collected = True
            self.visible = False
            
    def on_hover(self):
        """悬停提示"""
        pass
        
    def draw(self, surface: pygame.Surface):
        """绘制纸张"""
        if not self.visible or self.collected:
            return
            
        color = self.hover_color if self.is_hovered else self.normal_color
        
        # 绘制纸张背景
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (139, 119, 101), self.rect, 2)
        
        # 绘制纸张上的线条（模拟文字）
        line_color = (100, 100, 100)
        for i in range(3):
            y = self.rect.y + 15 + i * 15
            pygame.draw.line(surface, line_color, 
                           (self.rect.x + 5, y), 
                           (self.rect.x + self.rect.width - 5, y), 2)


class FrequencyTuner(Interactable):
    """频率微调器 - 支持鼠标滚轮"""
    
    def __init__(self, x: int, y: int, width: int = 200, height: int = 40,
                 name: str = "频率调节器"):
        super().__init__(x, y, width, height, name)
        self.frequency = 100.0
        self.min_freq = 80.0
        self.max_freq = 200.0
        self.step = 0.1
        self.target_range = (142.0, 143.0)
        self.in_target_range = False
        
        self.normal_color = (50, 50, 80)
        self.hover_color = (70, 70, 110)
        
    def on_click(self):
        """点击选中"""
        pass
        
    def on_hover(self):
        """悬停"""
        pass
        
    def adjust_frequency(self, delta: float):
        """调整频率值"""
        self.frequency += delta * self.step
        self.frequency = max(self.min_freq, min(self.max_freq, self.frequency))
        self._check_target_range()
        
    def _check_target_range(self):
        """检查是否在目标范围内"""
        self.in_target_range = self.target_range[0] <= self.frequency <= self.target_range[1]
        
    def draw(self, surface: pygame.Surface):
        """绘制频率调节器"""
        if not self.visible:
            return
            
        # 背景
        color = self.hover_color if self.is_hovered else self.normal_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # 频率显示
        font = pygame.font.SysFont("simhei", 20)
        freq_text = f"{self.frequency:.2f} MHz"
        text_color = (0, 255, 0) if self.in_target_range else (255, 255, 255)
        text_surface = font.render(freq_text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
        # 目标范围指示
        indicator_y = self.rect.bottom + 10
        pygame.draw.line(surface, (100, 100, 100), 
                        (self.rect.x, indicator_y), 
                        (self.rect.right, indicator_y), 3)
        
        # 当前位置指示
        freq_percent = (self.frequency - self.min_freq) / (self.max_freq - self.min_freq)
        indicator_x = self.rect.x + int(freq_percent * self.rect.width)
        indicator_color = (0, 255, 0) if self.in_target_range else (255, 0, 0)
        pygame.draw.circle(surface, indicator_color, (indicator_x, indicator_y), 6)


class InteractiveDesk(Interactable):
    """交互式书桌"""
    
    def __init__(self, x: int, y: int, width: int = 300, height: int = 150,
                 name: str = "书桌"):
        super().__init__(x, y, width, height, name)
        self.items_on_desk = []
        
        self.normal_color = (101, 67, 33)
        self.hover_color = (139, 90, 43)
        
    def on_click(self):
        """点击书桌"""
        pass
        
    def on_hover(self):
        """悬停"""
        pass
        
    def add_item(self, item: Interactable):
        """在书桌上添加物品"""
        self.items_on_desk.append(item)
        
    def draw(self, surface: pygame.Surface):
        """绘制书桌"""
        if not self.visible:
            return
            
        color = self.hover_color if self.is_hovered else self.normal_color
        
        # 桌面
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (60, 40, 20), self.rect, 3)
        
        # 桌腿
        leg_width = 20
        leg_color = (80, 50, 25)
        pygame.draw.rect(surface, leg_color, 
                        (self.rect.x + 10, self.rect.bottom, leg_width, 100))
        pygame.draw.rect(surface, leg_color, 
                        (self.rect.right - 30, self.rect.bottom, leg_width, 100))


class LockedBox(Interactable):
    """带锁的盒子"""
    
    def __init__(self, x: int, y: int, width: int = 80, height: int = 60,
                 name: str = "锁盒", required_item: str = ""):
        super().__init__(x, y, width, height, name)
        self.required_item = required_item
        self.locked = True
        self.opened = False
        
        self.normal_color = (105, 105, 105)
        self.hover_color = (128, 128, 128)
        
    def on_click(self):
        """尝试打开盒子"""
        pass
        
    def on_hover(self):
        """悬停"""
        pass
        
    def try_unlock(self, item_id: str) -> bool:
        """尝试用物品解锁"""
        if item_id == self.required_item:
            self.locked = False
            self.opened = True
            return True
        return False
        
    def draw(self, surface: pygame.Surface):
        """绘制盒子"""
        if not self.visible:
            return
            
        color = self.hover_color if self.is_hovered else self.normal_color
        
        # 盒子主体
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        
        # 锁
        if self.locked:
            lock_x = self.rect.centerx
            lock_y = self.rect.centery
            pygame.draw.circle(surface, (218, 165, 32), (lock_x, lock_y - 5), 8)
            pygame.draw.rect(surface, (218, 165, 32), 
                           (lock_x - 4, lock_y - 5, 8, 12))
        else:
            # 打开状态
            pygame.draw.line(surface, (255, 255, 255),
                           (self.rect.x + 5, self.rect.centery),
                           (self.rect.right - 5, self.rect.centery), 2)
