# -*- coding: utf-8 -*-
"""
幽灵信号 - 分层渲染系统模块
界面渲染分为背景层、物品层和 UI 提示层
使用 pygame.Surface.blit 的先后顺序管理遮盖关系
"""

import pygame
from typing import List, Optional, Tuple
from interactable import Interactable


class Layer:
    """渲染层基类"""
    
    def __init__(self, width: int, height: int, name: str = ""):
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.name = name
        self.visible = True
        self.dirty = True  # 是否需要重绘
        
    def clear(self):
        """清空层"""
        self.surface.fill((0, 0, 0, 0))
        
    def mark_dirty(self):
        """标记需要重绘"""
        self.dirty = True
        
    def render(self, target_surface: pygame.Surface, pos: Tuple[int, int] = (0, 0)):
        """渲染到目标表面"""
        if self.visible:
            target_surface.blit(self.surface, pos)


class BackgroundLayer(Layer):
    """背景层 - 渲染场景背景"""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height, "background")
        self.bg_color = (20, 20, 40)
        self.background_image: Optional[pygame.Surface] = None
        
    def set_background_color(self, color: Tuple[int, int, int]):
        """设置背景颜色"""
        self.bg_color = color
        self.mark_dirty()
        
    def set_background_image(self, image: Optional[pygame.Surface]):
        """设置背景图片"""
        self.background_image = image
        self.mark_dirty()
        
    def draw(self):
        """绘制背景层"""
        if not self.dirty:
            return
            
        self.clear()
        
        # 绘制背景色
        self.surface.fill(self.bg_color)
        
        # 如果有背景图，绘制背景图
        if self.background_image:
            # 缩放背景图以适应屏幕
            scaled = pygame.transform.scale(self.background_image, 
                                          (self.surface.get_width(), 
                                           self.surface.get_height()))
            self.surface.blit(scaled, (0, 0))
        else:
            # 绘制简单的背景装饰
            self._draw_decorations()
            
        self.dirty = False
        
    def _draw_decorations(self):
        """绘制背景装饰"""
        width = self.surface.get_width()
        height = self.surface.get_height()
        
        # 绘制窗户/夜空效果
        window_rect = pygame.Rect(50, 50, 200, 150)
        pygame.draw.rect(self.surface, (10, 10, 30), window_rect)
        pygame.draw.rect(self.surface, (60, 60, 80), window_rect, 3)
        
        # 绘制月亮
        pygame.draw.circle(self.surface, (255, 255, 200), 
                          (window_rect.centerx, window_rect.centery), 30)
        
        # 绘制星星
        import random
        random.seed(42)  # 固定随机种子
        for _ in range(20):
            x = random.randint(window_rect.x + 10, window_rect.right - 10)
            y = random.randint(window_rect.y + 10, window_rect.bottom - 10)
            pygame.draw.circle(self.surface, (255, 255, 255), (x, y), 2)


class ObjectLayer(Layer):
    """物品层 - 渲染场景中的可交互对象"""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height, "objects")
        self.objects: List[Interactable] = []
        
    def add_object(self, obj: Interactable):
        """添加可交互对象"""
        self.objects.append(obj)
        self.mark_dirty()
        
    def remove_object(self, obj: Interactable):
        """移除可交互对象"""
        if obj in self.objects:
            self.objects.remove(obj)
            self.mark_dirty()
            
    def clear_objects(self):
        """清空所有对象"""
        self.objects.clear()
        self.mark_dirty()
        
    def update_objects(self, mouse_pos: Tuple[int, int], mouse_clicked: bool = False):
        """更新所有对象的状态"""
        for obj in self.objects:
            obj.update(mouse_pos, mouse_clicked)
            
    def draw(self):
        """绘制所有对象"""
        self.clear()
        
        # 按Y坐标排序，实现简单的深度效果
        sorted_objects = sorted(self.objects, key=lambda o: o.rect.y)
        
        for obj in sorted_objects:
            obj.draw(self.surface)
            
    def get_object_at(self, pos: Tuple[int, int]) -> Optional[Interactable]:
        """获取指定位置的对象"""
        # 从后往前检查（上面的对象优先）
        for obj in reversed(self.objects):
            if obj.visible and obj.contains_point(pos):
                return obj
        return None


class UILayer(Layer):
    """UI 提示层 - 渲染用户界面和提示"""
    
    def __init__(self, width: int, height: int):
        super().__init__(width, height, "ui")
        self.hint_text = ""
        self.hint_timer = 0
        self.hint_duration = 3000  # 提示显示时间（毫秒）
        self.dialog_text = ""
        self.dialog_visible = False
        self.suspicion_bar_visible = True
        self.suspicion_value = 0
        self.suspicion_max = 100
        
        # 日志区域
        self.log_messages: List[str] = []
        self.max_log_messages = 5
        
    def show_hint(self, text: str, duration: int = 3000):
        """显示提示文本"""
        self.hint_text = text
        self.hint_timer = duration
        self.mark_dirty()
        
    def show_dialog(self, text: str):
        """显示对话文本"""
        self.dialog_text = text
        self.dialog_visible = True
        self.mark_dirty()
        
    def hide_dialog(self):
        """隐藏对话"""
        self.dialog_visible = False
        self.mark_dirty()
        
    def update_suspicion(self, value: int):
        """更新怀疑度显示"""
        self.suspicion_value = max(0, min(self.suspicion_max, value))
        self.mark_dirty()
        
    def add_log_message(self, message: str):
        """添加日志消息"""
        self.log_messages.append(message)
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages.pop(0)
        self.mark_dirty()
        
    def update(self, dt: int):
        """更新UI状态"""
        if self.hint_timer > 0:
            self.hint_timer -= dt
            if self.hint_timer <= 0:
                self.hint_text = ""
                self.mark_dirty()
                
    def draw(self):
        """绘制UI层"""
        self.clear()
        
        # 绘制怀疑度条
        if self.suspicion_bar_visible:
            self._draw_suspicion_bar()
            
        # 绘制提示文本
        if self.hint_text:
            self._draw_hint()
            
        # 绘制对话
        if self.dialog_visible:
            self._draw_dialog()
            
        # 绘制日志
        self._draw_log()
        
    def _draw_suspicion_bar(self):
        """绘制怀疑度条"""
        bar_x = 20
        bar_y = 20
        bar_width = 200
        bar_height = 20
        
        # 背景
        pygame.draw.rect(self.surface, (50, 50, 50), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 进度
        progress = self.suspicion_value / self.suspicion_max
        progress_width = int(bar_width * progress)
        
        # 颜色根据怀疑度变化
        if progress < 0.5:
            color = (0, 255, 0)
        elif progress < 0.8:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
            
        pygame.draw.rect(self.surface, color, 
                        (bar_x, bar_y, progress_width, bar_height))
        
        # 边框
        pygame.draw.rect(self.surface, (200, 200, 200), 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 标签
        font = pygame.font.SysFont("simhei", 14)
        label = font.render(f"怀疑度: {int(self.suspicion_value)}/{self.suspicion_max}", 
                           True, (255, 255, 255))
        self.surface.blit(label, (bar_x, bar_y - 18))
        
    def _draw_hint(self):
        """绘制提示文本"""
        font = pygame.font.SysFont("simhei", 16)
        
        # 计算文本尺寸
        text_surface = font.render(self.hint_text, True, (255, 255, 200))
        text_rect = text_surface.get_rect()
        
        # 提示框位置（屏幕底部中央）
        box_width = text_rect.width + 40
        box_height = text_rect.height + 20
        box_x = (self.surface.get_width() - box_width) // 2
        box_y = self.surface.get_height() - 100
        
        # 绘制提示框背景
        pygame.draw.rect(self.surface, (0, 0, 0, 200), 
                        (box_x, box_y, box_width, box_height))
        pygame.draw.rect(self.surface, (255, 255, 200), 
                        (box_x, box_y, box_width, box_height), 2)
        
        # 绘制文本
        text_x = box_x + (box_width - text_rect.width) // 2
        text_y = box_y + (box_height - text_rect.height) // 2
        self.surface.blit(text_surface, (text_x, text_y))
        
    def _draw_dialog(self):
        """绘制对话文本"""
        # 对话框位置
        dialog_x = 50
        dialog_y = self.surface.get_height() - 200
        dialog_width = self.surface.get_width() - 200
        dialog_height = 120
        
        # 绘制对话框背景
        pygame.draw.rect(self.surface, (20, 20, 40, 230), 
                        (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.surface, (150, 150, 200), 
                        (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # 绘制文本
        font = pygame.font.SysFont("simhei", 16)
        
        # 自动换行
        words = self.dialog_text
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            if font.size(test_line)[0] < dialog_width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
            
        # 绘制每一行
        line_height = 22
        start_y = dialog_y + 20
        for i, line in enumerate(lines[:4]):  # 最多显示4行
            text_surface = font.render(line, True, (255, 255, 255))
            self.surface.blit(text_surface, (dialog_x + 20, start_y + i * line_height))
            
    def _draw_log(self):
        """绘制日志消息"""
        if not self.log_messages:
            return
            
        log_x = 20
        log_y = 60
        log_width = 250
        line_height = 18
        
        font = pygame.font.SysFont("simhei", 12)
        
        for i, message in enumerate(self.log_messages):
            # 背景
            bg_rect = pygame.Rect(log_x, log_y + i * line_height, log_width, line_height - 2)
            pygame.draw.rect(self.surface, (0, 0, 0, 150), bg_rect)
            
            # 文本
            text_surface = font.render(message, True, (200, 200, 200))
            self.surface.blit(text_surface, (log_x + 5, log_y + i * line_height))


class LayeredRenderer:
    """
    分层渲染器
    管理所有渲染层，按顺序渲染
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 创建各层
        self.background_layer = BackgroundLayer(screen_width, screen_height)
        self.object_layer = ObjectLayer(screen_width, screen_height)
        self.ui_layer = UILayer(screen_width, screen_height)
        
        # 层列表（按渲染顺序）
        self.layers: List[Layer] = [
            self.background_layer,
            self.object_layer,
            self.ui_layer
        ]
        
    def render(self, screen: pygame.Surface):
        """
        渲染所有层到屏幕
        使用 pygame.Surface.blit 的先后顺序管理遮盖关系
        """
        # 更新并绘制每一层
        for layer in self.layers:
            if isinstance(layer, BackgroundLayer):
                layer.draw()
            elif isinstance(layer, ObjectLayer):
                layer.draw()
            elif isinstance(layer, UILayer):
                layer.draw()
                
            # 将层渲染到屏幕
            layer.render(screen)
            
    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool, dt: int):
        """更新所有层"""
        self.object_layer.update_objects(mouse_pos, mouse_clicked)
        self.ui_layer.update(dt)
        
    def set_background_color(self, color: Tuple[int, int, int]):
        """设置背景颜色"""
        self.background_layer.set_background_color(color)
        
    def add_object(self, obj: Interactable):
        """添加场景对象"""
        self.object_layer.add_object(obj)
        
    def remove_object(self, obj: Interactable):
        """移除场景对象"""
        self.object_layer.remove_object(obj)
        
    def clear_objects(self):
        """清空所有场景对象"""
        self.object_layer.clear_objects()
        
    def show_hint(self, text: str, duration: int = 3000):
        """显示提示"""
        self.ui_layer.show_hint(text, duration)
        
    def show_dialog(self, text: str):
        """显示对话"""
        self.ui_layer.show_dialog(text)
        
    def hide_dialog(self):
        """隐藏对话"""
        self.ui_layer.hide_dialog()
        
    def update_suspicion(self, value: int):
        """更新怀疑度显示"""
        self.ui_layer.update_suspicion(value)
        
    def add_log(self, message: str):
        """添加日志"""
        self.ui_layer.add_log_message(message)
        
    def get_object_at(self, pos: Tuple[int, int]) -> Optional[Interactable]:
        """获取指定位置的对象"""
        return self.object_layer.get_object_at(pos)
