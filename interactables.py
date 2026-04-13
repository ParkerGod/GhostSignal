import pygame
import os
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from constants import COLORS


def get_chinese_font(size: int) -> pygame.font.Font:
    chinese_fonts = ["Microsoft YaHei", "SimHei", "SimSun", "NSimSun", "FangSong", "KaiTi"]
    
    for font_name in chinese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            test_surface = font.render("测试", True, (255, 255, 255))
            if test_surface.get_width() > 10:
                return font
        except:
            continue
    
    font_paths = ["C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf", "C:/Windows/Fonts/simsun.ttc"]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    return pygame.font.Font(None, size)


class Interactable(ABC):
    def __init__(self, name: str, rect: Tuple[int, int, int, int], description: str):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.description = description
        self.is_hovered = False
        self.is_active = False
        self.is_solved = False
        self.enabled = True
        
    @abstractmethod
    def on_click(self, game_state: Dict[str, Any]) -> Optional[str]:
        pass
    
    @abstractmethod
    def on_hover(self, mouse_pos: Tuple[int, int]) -> str:
        pass
    
    def contains_point(self, point: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(point)
    
    def update_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        self.is_hovered = self.contains_point(mouse_pos) and self.enabled
        return self.is_hovered
    
    def draw(self, surface: pygame.Surface):
        color = COLORS['highlight'] if self.is_hovered else COLORS['dim']
        if self.is_solved:
            color = COLORS['success']
        
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)
        
        if self.is_hovered:
            inner_rect = self.rect.inflate(-4, -4)
            pygame.draw.rect(surface, (*color[:3], 50), inner_rect, border_radius=3)
    
    def draw_tooltip(self, surface: pygame.Surface, font: pygame.font.Font):
        if self.is_hovered and self.enabled:
            tooltip_text = self.on_hover(pygame.mouse.get_pos())
            text_surface = font.render(tooltip_text, True, COLORS['text'])
            tooltip_rect = text_surface.get_rect()
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tooltip_rect.bottomleft = (mouse_x + 15, mouse_y - 10)
            
            if tooltip_rect.right > surface.get_width():
                tooltip_rect.right = surface.get_width() - 10
            if tooltip_rect.top < 0:
                tooltip_rect.top = 10
            
            bg_rect = tooltip_rect.inflate(10, 6)
            pygame.draw.rect(surface, COLORS['panel'], bg_rect, border_radius=3)
            pygame.draw.rect(surface, COLORS['highlight'], bg_rect, 1, border_radius=3)
            surface.blit(text_surface, tooltip_rect)


class FrequencyDevice(Interactable):
    def __init__(self, name: str, rect: Tuple[int, int, int, int], description: str,
                 puzzle_id: str, target_range: Tuple[float, float], default_freq: float,
                 hint: str, success_text: str, fail_text: str):
        super().__init__(name, rect, description)
        self.puzzle_id = puzzle_id
        self.target_range = target_range
        self.current_frequency = default_freq
        self.default_frequency = default_freq
        self.hint = hint
        self.success_text = success_text
        self.fail_text = fail_text
        self.tuner_active = False
        
    def on_click(self, game_state: Dict[str, Any]) -> Optional[str]:
        if self.is_solved or not self.enabled:
            return None
        
        self.tuner_active = True
        return f"激活频率调节器: {self.name}"
    
    def on_hover(self, mouse_pos: Tuple[int, int]) -> str:
        status = " [已解决]" if self.is_solved else ""
        return f"{self.name}{status}"
    
    def adjust_frequency(self, delta: float) -> bool:
        if not self.tuner_active or self.is_solved:
            return False
        
        self.current_frequency += delta
        self.current_frequency = max(0, min(150, self.current_frequency))
        return True
    
    def check_frequency(self) -> Tuple[bool, str]:
        if self.target_range[0] <= self.current_frequency <= self.target_range[1]:
            self.is_solved = True
            self.tuner_active = False
            return True, self.success_text
        return False, self.fail_text
    
    def reset_frequency(self):
        self.current_frequency = self.default_frequency
        self.tuner_active = False
    
    def draw(self, surface: pygame.Surface):
        super().draw(surface)
        
        if self.is_solved:
            indicator_rect = pygame.Rect(self.rect.right - 15, self.rect.top + 5, 10, 10)
            pygame.draw.circle(surface, COLORS['success'], indicator_rect.center, 5)


class ClueItem(Interactable):
    def __init__(self, name: str, rect: Tuple[int, int, int, int], description: str,
                 clue_id: str, clue_name: str, clue_description: str, icon_type: str):
        super().__init__(name, rect, description)
        self.clue_id = clue_id
        self.clue_name = clue_name
        self.clue_description = clue_description
        self.icon_type = icon_type
        self.collected = False
        
    def on_click(self, game_state: Dict[str, Any]) -> Optional[str]:
        if self.collected or not self.enabled:
            return None
        
        self.collected = True
        self.is_solved = True
        return f"获得线索: {self.clue_name}"
    
    def on_hover(self, mouse_pos: Tuple[int, int]) -> str:
        if self.collected:
            return f"{self.name} (已收集)"
        return f"{self.name}"
    
    def draw(self, surface: pygame.Surface):
        if self.collected:
            color = COLORS['dim']
            pygame.draw.rect(surface, color, self.rect, 1, border_radius=5)
        else:
            super().draw(surface)
            
            icon_color = COLORS['highlight'] if self.is_hovered else COLORS['text']
            center = self.rect.center
            pygame.draw.circle(surface, icon_color, center, 15, 2)


class Button(Interactable):
    def __init__(self, name: str, rect: Tuple[int, int, int, int], description: str,
                 action_id: str, label: str):
        super().__init__(name, rect, description)
        self.action_id = action_id
        self.label = label
        self.click_callback = None
        
    def on_click(self, game_state: Dict[str, Any]) -> Optional[str]:
        if not self.enabled:
            return None
        return f"点击: {self.label}"
    
    def on_hover(self, mouse_pos: Tuple[int, int]) -> str:
        return self.label
    
    def draw(self, surface: pygame.Surface):
        color = COLORS['highlight'] if self.is_hovered else COLORS['panel']
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        font = get_chinese_font(24)
        text = font.render(self.label, True, COLORS['text'])
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class DialogOption(Interactable):
    def __init__(self, rect: Tuple[int, int, int, int], text: str, is_correct: bool,
                 response: str, option_index: int):
        super().__init__(f"dialog_option_{option_index}", rect, text)
        self.text = text
        self.is_correct = is_correct
        self.response = response
        self.option_index = option_index
        self.selected = False
        
    def on_click(self, game_state: Dict[str, Any]) -> Optional[str]:
        if not self.enabled:
            return None
        self.selected = True
        return self.response
    
    def on_hover(self, mouse_pos: Tuple[int, int]) -> str:
        return self.text
    
    def draw(self, surface: pygame.Surface):
        bg_color = COLORS['panel'] if not self.is_hovered else (50, 50, 70)
        border_color = COLORS['highlight'] if self.is_hovered else COLORS['dim']
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        
        font = get_chinese_font(22)
        text = font.render(self.text, True, COLORS['text'])
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
