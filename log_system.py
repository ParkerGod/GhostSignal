# -*- coding: utf-8 -*-
"""
幽灵信号 - 日志系统模块
将玩家过去五分钟内触发的所有关键交互文本记录在一个可滚动查看的文字区域内
方便玩家回顾线索
"""

import pygame
import time
from typing import List, Dict, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
from game_data import LOG_CONFIG


class LogEntryType(Enum):
    """日志条目类型"""
    STORY = "story"           # 剧情相关
    INTERACTION = "interaction"  # 交互相关
    PUZZLE = "puzzle"         # 谜题相关
    ITEM = "item"             # 物品相关
    WARNING = "warning"       # 警告信息
    SYSTEM = "system"         # 系统信息
    
    def get_type_color(self) -> Tuple[int, int, int]:
        """获取类型对应的颜色"""
        colors = {
            LogEntryType.STORY: (255, 215, 0),      # 金色
            LogEntryType.INTERACTION: (100, 200, 255),  # 浅蓝
            LogEntryType.PUZZLE: (0, 255, 127),     # 春绿
            LogEntryType.ITEM: (255, 165, 0),       # 橙色
            LogEntryType.WARNING: (255, 69, 0),     # 红橙
            LogEntryType.SYSTEM: (200, 200, 200),   # 灰色
        }
        return colors.get(self, (255, 255, 255))


@dataclass
class LogEntry:
    """日志条目"""
    timestamp: float
    entry_type: LogEntryType
    message: str
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
            
    def get_formatted_time(self) -> str:
        """获取格式化的时间字符串"""
        local_time = time.localtime(self.timestamp)
        return time.strftime("%H:%M:%S", local_time)
        
    def get_type_color(self) -> Tuple[int, int, int]:
        """获取类型对应的颜色"""
        colors = {
            LogEntryType.STORY: (255, 215, 0),      # 金色
            LogEntryType.INTERACTION: (100, 200, 255),  # 浅蓝
            LogEntryType.PUZZLE: (0, 255, 127),     # 春绿
            LogEntryType.ITEM: (255, 165, 0),       # 橙色
            LogEntryType.WARNING: (255, 69, 0),     # 红橙
            LogEntryType.SYSTEM: (200, 200, 200),   # 灰色
        }
        return colors.get(self.entry_type, (255, 255, 255))


class LogSystem:
    """
    日志系统
    记录和管理游戏中的所有关键交互
    """
    
    def __init__(self):
        self.entries: List[LogEntry] = []
        self.max_entries = LOG_CONFIG["max_entries"]
        self.time_window_seconds = LOG_CONFIG["time_window_minutes"] * 60
        
        # 类型过滤
        self.enabled_types = set(LogEntryType)
        
        # 回调函数
        self.on_new_entry: Optional[Callable[[LogEntry], None]] = None
        
    def add_entry(self, message: str, entry_type: LogEntryType = LogEntryType.SYSTEM, 
                  metadata: Dict = None):
        """
        添加日志条目
        
        Args:
            message: 日志消息
            entry_type: 条目类型
            metadata: 额外元数据
        """
        entry = LogEntry(
            timestamp=time.time(),
            entry_type=entry_type,
            message=message,
            metadata=metadata or {}
        )
        
        self.entries.append(entry)
        
        # 限制条目数量
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
            
        # 触发回调
        if self.on_new_entry:
            self.on_new_entry(entry)
            
    def add_story_log(self, message: str):
        """添加剧情日志"""
        self.add_entry(message, LogEntryType.STORY)
        
    def add_interaction_log(self, message: str, object_name: str = ""):
        """添加交互日志"""
        self.add_entry(message, LogEntryType.INTERACTION, 
                      {"object": object_name})
        
    def add_puzzle_log(self, message: str, puzzle_id: str = ""):
        """添加谜题日志"""
        self.add_entry(message, LogEntryType.PUZZLE,
                      {"puzzle_id": puzzle_id})
        
    def add_item_log(self, message: str, item_id: str = ""):
        """添加物品日志"""
        self.add_entry(message, LogEntryType.ITEM,
                      {"item_id": item_id})
        
    def add_warning_log(self, message: str):
        """添加警告日志"""
        self.add_entry(message, LogEntryType.WARNING)

    def add_system_log(self, message: str):
        """添加系统日志"""
        self.add_entry(message, LogEntryType.SYSTEM)
        
    def get_recent_entries(self, count: int = None) -> List[LogEntry]:
        """获取最近的日志条目"""
        if count is None:
            return self.entries.copy()
        return self.entries[-count:]
        
    def get_entries_in_time_window(self) -> List[LogEntry]:
        """获取时间窗口内的日志条目（默认5分钟）"""
        current_time = time.time()
        cutoff_time = current_time - self.time_window_seconds
        
        return [entry for entry in self.entries 
                if entry.timestamp >= cutoff_time]
        
    def get_filtered_entries(self, entry_types: List[LogEntryType] = None) -> List[LogEntry]:
        """获取过滤后的日志条目"""
        if entry_types is None:
            entry_types = list(self.enabled_types)
            
        return [entry for entry in self.entries 
                if entry.entry_type in entry_types]
        
    def clear(self):
        """清空所有日志"""
        self.entries.clear()
        
    def clear_old_entries(self):
        """清理过期的日志条目"""
        current_time = time.time()
        cutoff_time = current_time - self.time_window_seconds
        
        self.entries = [entry for entry in self.entries 
                       if entry.timestamp >= cutoff_time]
        
    def set_type_enabled(self, entry_type: LogEntryType, enabled: bool):
        """设置某类型日志是否启用"""
        if enabled:
            self.enabled_types.add(entry_type)
        else:
            self.enabled_types.discard(entry_type)
            
    def get_statistics(self) -> Dict:
        """获取日志统计信息"""
        stats = {entry_type: 0 for entry_type in LogEntryType}
        
        for entry in self.entries:
            stats[entry.entry_type] += 1
            
        return {
            "total_entries": len(self.entries),
            "type_counts": stats,
            "time_range": {
                "oldest": self.entries[0].timestamp if self.entries else None,
                "newest": self.entries[-1].timestamp if self.entries else None
            }
        }


class LogViewer:
    """
    日志查看器
    提供可滚动查看的日志界面
    """
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.log_system: Optional[LogSystem] = None
        
        # 滚动状态
        self.scroll_offset = 0
        self.line_height = 20
        self.max_visible_lines = height // self.line_height - 2
        
        # 视觉属性
        self.bg_color = (20, 20, 30, 230)
        self.border_color = (100, 100, 120)
        self.text_color = (255, 255, 255)
        self.scrollbar_color = (80, 80, 100)
        self.scrollbar_thumb_color = (120, 120, 150)
        
        # 是否可见
        self.visible = False
        
        # 滚动条
        self.scrollbar_width = 10
        self.scrollbar_rect = pygame.Rect(
            x + width - self.scrollbar_width - 2,
            y + 2,
            self.scrollbar_width,
            height - 4
        )
        self.dragging_scrollbar = False
        
    def set_log_system(self, log_system: LogSystem):
        """设置日志系统"""
        self.log_system = log_system
        
    def toggle_visibility(self):
        """切换可见性"""
        self.visible = not self.visible
        
    def show(self):
        """显示查看器"""
        self.visible = True
        # 滚动到最新
        self.scroll_to_bottom()
        
    def hide(self):
        """隐藏查看器"""
        self.visible = False
        
    def scroll_up(self, lines: int = 3):
        """向上滚动"""
        self.scroll_offset = max(0, self.scroll_offset - lines)
        
    def scroll_down(self, lines: int = 3):
        """向下滚动"""
        if self.log_system:
            max_offset = max(0, len(self.log_system.entries) - self.max_visible_lines)
            self.scroll_offset = min(max_offset, self.scroll_offset + lines)
            
    def scroll_to_bottom(self):
        """滚动到底部"""
        if self.log_system:
            self.scroll_offset = max(0, len(self.log_system.entries) - self.max_visible_lines)
            
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        处理事件
        返回: 是否处理了事件
        """
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # 鼠标滚轮上
                self.scroll_up(2)
                return True
            elif event.button == 5:  # 鼠标滚轮下
                self.scroll_down(2)
                return True
            elif event.button == 1:  # 左键
                if self.scrollbar_rect.collidepoint(event.pos):
                    self.dragging_scrollbar = True
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging_scrollbar = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_scrollbar:
                # 根据鼠标位置计算滚动偏移
                rel_y = event.pos[1] - self.scrollbar_rect.y
                ratio = rel_y / self.scrollbar_rect.height
                
                if self.log_system:
                    max_offset = max(0, len(self.log_system.entries) - self.max_visible_lines)
                    self.scroll_offset = int(ratio * max_offset)
                    self.scroll_offset = max(0, min(max_offset, self.scroll_offset))
                    
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.scroll_up(self.max_visible_lines)
                return True
            elif event.key == pygame.K_PAGEDOWN:
                self.scroll_down(self.max_visible_lines)
                return True
            elif event.key == pygame.K_HOME:
                self.scroll_offset = 0
                return True
            elif event.key == pygame.K_END:
                self.scroll_to_bottom()
                return True
                
        return False
        
    def draw(self, surface: pygame.Surface):
        """绘制日志查看器"""
        if not self.visible or not self.log_system:
            return
            
        # 绘制背景
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, self.rect.topleft)
        
        # 绘制边框
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        # 绘制标题
        font = pygame.font.SysFont("simhei", 16)
        title = font.render("交互日志 (按 L 关闭)", True, (255, 255, 255))
        surface.blit(title, (self.rect.x + 10, self.rect.y + 5))
        
        # 获取要显示的条目
        entries = self.log_system.get_recent_entries()
        start_idx = self.scroll_offset
        end_idx = min(start_idx + self.max_visible_lines, len(entries))
        
        # 绘制日志条目
        content_y = self.rect.y + 30
        content_x = self.rect.x + 10
        
        for i in range(start_idx, end_idx):
            entry = entries[i]
            
            # 时间
            time_text = f"[{entry.get_formatted_time()}] "
            time_surface = font.render(time_text, True, (150, 150, 150))
            surface.blit(time_surface, (content_x, content_y))
            
            # 类型标记
            type_x = content_x + 70
            type_color = entry.get_type_color()
            type_marker = font.render(f"[{entry.entry_type.value}] ", True, type_color)
            surface.blit(type_marker, (type_x, content_y))
            
            # 消息
            msg_x = type_x + 80
            msg_surface = font.render(entry.message[:50], True, self.text_color)
            surface.blit(msg_surface, (msg_x, content_y))
            
            content_y += self.line_height
            
        # 绘制滚动条
        if len(entries) > self.max_visible_lines:
            self._draw_scrollbar(surface, len(entries))
            
    def _draw_scrollbar(self, surface: pygame.Surface, total_entries: int):
        """绘制滚动条"""
        # 滚动条背景
        pygame.draw.rect(surface, self.scrollbar_color, self.scrollbar_rect)
        
        # 计算滑块位置和大小
        visible_ratio = self.max_visible_lines / total_entries
        thumb_height = max(30, int(self.scrollbar_rect.height * visible_ratio))
        
        max_offset = max(0, total_entries - self.max_visible_lines)
        scroll_ratio = self.scroll_offset / max_offset if max_offset > 0 else 0
        thumb_y = self.scrollbar_rect.y + int(
            (self.scrollbar_rect.height - thumb_height) * scroll_ratio
        )
        
        # 绘制滑块
        thumb_rect = pygame.Rect(
            self.scrollbar_rect.x,
            thumb_y,
            self.scrollbar_rect.width,
            thumb_height
        )
        pygame.draw.rect(surface, self.scrollbar_thumb_color, thumb_rect)


class LogNotification:
    """
    日志通知
    在屏幕角落显示最新的日志消息
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 通知区域
        self.width = 300
        self.height = 80
        self.x = 20
        self.y = screen_height - 150
        
        # 当前显示的通知
        self.current_message = ""
        self.current_type = LogEntryType.SYSTEM
        self.display_timer = 0
        self.display_duration = 3000  # 显示3秒
        
        # 动画
        self.alpha = 0
        self.target_alpha = 230
        
    def show_notification(self, entry: LogEntry):
        """显示通知"""
        self.current_message = entry.message
        self.current_type = entry.entry_type
        self.display_timer = self.display_duration
        self.alpha = 0
        
    def update(self, dt: int):
        """更新通知状态"""
        # 淡入淡出动画
        if self.display_timer > 0:
            self.display_timer -= dt
            if self.alpha < self.target_alpha:
                self.alpha = min(self.target_alpha, self.alpha + 10)
        else:
            if self.alpha > 0:
                self.alpha = max(0, self.alpha - 10)
                
    def draw(self, surface: pygame.Surface):
        """绘制通知"""
        if self.alpha <= 0:
            return
            
        # 创建透明背景
        notification_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 背景色根据类型变化
        colors = {
            LogEntryType.STORY: (60, 50, 20, self.alpha),
            LogEntryType.INTERACTION: (20, 40, 60, self.alpha),
            LogEntryType.PUZZLE: (20, 60, 30, self.alpha),
            LogEntryType.ITEM: (60, 40, 10, self.alpha),
            LogEntryType.WARNING: (60, 20, 10, self.alpha),
            LogEntryType.SYSTEM: (30, 30, 30, self.alpha),
        }
        bg_color = colors.get(self.current_type, (30, 30, 30, self.alpha))
        
        notification_surface.fill(bg_color)
        
        # 边框
        border_color = (200, 200, 200, self.alpha)
        pygame.draw.rect(notification_surface, border_color, 
                        (0, 0, self.width, self.height), 2)
        
        # 文本
        font = pygame.font.SysFont("simhei", 14)
        
        # 类型标签
        type_text = f"[{self.current_type.value}]"
        type_surface = font.render(type_text, True, 
                                  self.current_type.get_type_color())
        notification_surface.blit(type_surface, (10, 10))
        
        # 消息（截断）
        msg_text = self.current_message[:35]
        if len(self.current_message) > 35:
            msg_text += "..."
        msg_surface = font.render(msg_text, True, (255, 255, 255))
        notification_surface.blit(msg_surface, (10, 35))
        
        # 提示
        hint_surface = font.render("按 L 查看完整日志", True, (150, 150, 150))
        notification_surface.blit(hint_surface, (10, 58))
        
        # 绘制到屏幕
        surface.blit(notification_surface, (self.x, self.y))
