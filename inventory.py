# -*- coding: utf-8 -*-
"""
幽灵信号 - 物品栏系统模块
玩家通过交互获取的线索以图标形式存放在屏幕侧边
点击线索后再点击场景物体可触发特殊的"组合交互"逻辑
"""

import pygame
from typing import List, Optional, Dict, Callable, Tuple
from game_data import ITEMS_DATA


class InventoryItem:
    """物品栏中的物品"""
    
    def __init__(self, item_id: str):
        self.item_id = item_id
        self.data = ITEMS_DATA.get(item_id, {})
        self.name = self.data.get("name", "未知物品")
        self.description = self.data.get("description", "")
        self.icon_color = self.data.get("icon_color", (128, 128, 128))
        self.usable_on = self.data.get("usable_on", [])
        self.selected = False
        
    def get_icon_surface(self, size: int = 50) -> pygame.Surface:
        """生成物品图标表面"""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 背景
        pygame.draw.rect(surface, self.icon_color, (0, 0, size, size), border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, size, size), 2, border_radius=5)
        
        # 选中效果
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), (0, 0, size, size), 4, border_radius=5)
        
        # 物品首字
        font = pygame.font.SysFont("simhei", 20)
        text = font.render(self.name[0], True, (255, 255, 255))
        text_rect = text.get_rect(center=(size // 2, size // 2))
        surface.blit(text, text_rect)
        
        return surface


class InventorySystem:
    """
    物品栏系统
    管理玩家收集的所有线索和物品
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 物品栏位置和尺寸
        self.width = 120
        self.x = screen_width - self.width - 10
        self.y = 50
        self.item_size = 50
        self.item_spacing = 10
        
        # 物品列表
        self.items: List[InventoryItem] = []
        self.selected_item: Optional[InventoryItem] = None
        
        # 回调函数
        self.on_item_selected: Optional[Callable[[InventoryItem], None]] = None
        self.on_item_used: Optional[Callable[[InventoryItem, str], bool]] = None
        
        # 视觉属性
        self.bg_color = (30, 30, 40, 200)
        self.border_color = (100, 100, 120)
        self.title_color = (255, 255, 255)
        
    def add_item(self, item_id: str) -> bool:
        """添加物品到物品栏"""
        # 检查是否已存在
        for item in self.items:
            if item.item_id == item_id:
                return False
                
        new_item = InventoryItem(item_id)
        self.items.append(new_item)
        return True
        
    def has_item(self, item_id: str) -> bool:
        """检查是否拥有某物品"""
        return any(item.item_id == item_id for item in self.items)
        
    def select_item(self, index: int) -> Optional[InventoryItem]:
        """选择物品栏中的物品"""
        if 0 <= index < len(self.items):
            # 取消之前的选择
            if self.selected_item:
                self.selected_item.selected = False
                
            item = self.items[index]
            
            # 如果点击已选中的物品，则取消选择
            if self.selected_item == item:
                self.selected_item = None
                return None
            else:
                item.selected = True
                self.selected_item = item
                if self.on_item_selected:
                    self.on_item_selected(item)
                return item
        return None
        
    def deselect_all(self):
        """取消所有选择"""
        if self.selected_item:
            self.selected_item.selected = False
            self.selected_item = None
            
    def try_use_item(self, target_id: str) -> Tuple[bool, Optional[InventoryItem]]:
        """
        尝试使用当前选中的物品与目标交互
        返回: (是否成功, 使用的物品)
        """
        if not self.selected_item:
            return False, None
            
        item = self.selected_item
        
        # 检查物品是否可以用在目标上
        if target_id in item.usable_on:
            success = True
            if self.on_item_used:
                success = self.on_item_used(item, target_id)
                
            if success:
                # 使用后取消选择
                self.deselect_all()
                return True, item
                
        return False, None
        
    def get_item_at_position(self, pos: Tuple[int, int]) -> Optional[int]:
        """获取指定位置的物品索引"""
        x, y = pos
        
        # 检查是否在物品栏区域内
        if not (self.x <= x <= self.x + self.width):
            return None
            
        # 计算点击的是哪个物品
        start_y = self.y + 40  # 标题下方
        for i, item in enumerate(self.items):
            item_y = start_y + i * (self.item_size + self.item_spacing)
            item_rect = pygame.Rect(self.x + 10, item_y, self.item_size, self.item_size)
            
            if item_rect.collidepoint(x, y):
                return i
                
        return None
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """
        处理点击事件
        返回: 是否点击了物品栏
        """
        item_index = self.get_item_at_position(pos)
        if item_index is not None:
            self.select_item(item_index)
            return True
        return False
        
    def get_selected_item_id(self) -> Optional[str]:
        """获取当前选中物品的ID"""
        if self.selected_item:
            return self.selected_item.item_id
        return None
        
    def draw(self, surface: pygame.Surface):
        """绘制物品栏"""
        # 绘制背景
        bg_surface = pygame.Surface((self.width, self.screen_height - 100), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, (self.x, self.y))
        
        # 绘制边框
        pygame.draw.rect(surface, self.border_color, 
                        (self.x, self.y, self.width, self.screen_height - 100), 2)
        
        # 绘制标题
        font = pygame.font.SysFont("simhei", 18)
        title = font.render("物品栏", True, self.title_color)
        title_rect = title.get_rect(center=(self.x + self.width // 2, self.y + 20))
        surface.blit(title, title_rect)
        
        # 绘制物品
        start_y = self.y + 40
        for i, item in enumerate(self.items):
            item_y = start_y + i * (self.item_size + self.item_spacing)
            icon = item.get_icon_surface(self.item_size)
            surface.blit(icon, (self.x + 10, item_y))
            
            # 绘制物品名称（悬停时显示）
            if item.selected:
                name_font = pygame.font.SysFont("simhei", 12)
                name_text = name_font.render(item.name, True, (255, 255, 200))
                surface.blit(name_text, (self.x + 10, item_y + self.item_size + 2))
                
    def draw_tooltip(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]):
        """绘制物品提示信息"""
        item_index = self.get_item_at_position(mouse_pos)
        if item_index is not None:
            item = self.items[item_index]
            
            # 提示框
            tooltip_x = self.x - 210
            tooltip_y = mouse_pos[1]
            tooltip_width = 200
            tooltip_height = 60
            
            # 绘制提示背景
            pygame.draw.rect(surface, (0, 0, 0, 220), 
                           (tooltip_x, tooltip_y, tooltip_width, tooltip_height))
            pygame.draw.rect(surface, (200, 200, 200), 
                           (tooltip_x, tooltip_y, tooltip_width, tooltip_height), 1)
            
            # 绘制物品信息
            font = pygame.font.SysFont("simhei", 14)
            name_text = font.render(item.name, True, (255, 255, 0))
            surface.blit(name_text, (tooltip_x + 10, tooltip_y + 10))
            
            desc_font = pygame.font.SysFont("simhei", 12)
            # 截断描述文本
            desc = item.description[:30] + "..." if len(item.description) > 30 else item.description
            desc_text = desc_font.render(desc, True, (200, 200, 200))
            surface.blit(desc_text, (tooltip_x + 10, tooltip_y + 35))


class CombinationSystem:
    """
    物品组合系统
    管理物品之间的组合逻辑
    """
    
    def __init__(self):
        # 定义物品组合规则
        self.combinations: Dict[Tuple[str, str], str] = {
            ("old_newspaper", "morse_codebook"): "decoded_message",
            ("frequency_table", "strange_key"): "frequency_key",
        }
        
        # 组合结果描述
        self.combination_results: Dict[str, Dict] = {
            "decoded_message": {
                "name": "解码信息",
                "description": "报纸和密码本组合后得到的隐藏信息",
                "icon_color": (255, 215, 0)
            },
            "frequency_key": {
                "name": "频率钥匙",
                "description": "可以打开特殊频率的钥匙",
                "icon_color": (255, 0, 255)
            }
        }
        
    def can_combine(self, item1_id: str, item2_id: str) -> bool:
        """检查两个物品是否可以组合"""
        return (item1_id, item2_id) in self.combinations or \
               (item2_id, item1_id) in self.combinations
               
    def combine(self, item1_id: str, item2_id: str) -> Optional[str]:
        """
        组合两个物品
        返回: 新物品的ID，如果无法组合则返回None
        """
        # 检查正向组合
        if (item1_id, item2_id) in self.combinations:
            return self.combinations[(item1_id, item2_id)]
            
        # 检查反向组合
        if (item2_id, item1_id) in self.combinations:
            return self.combinations[(item2_id, item1_id)]
            
        return None
        
    def get_combination_result(self, result_id: str) -> Dict:
        """获取组合结果的详细信息"""
        return self.combination_results.get(result_id, {})
