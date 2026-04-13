import pygame
from typing import Tuple, Optional, Callable
from constants import COLORS


class FrequencyTuner:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.current_frequency = 0.0
        self.target_range = (0.0, 0.0)
        self.default_frequency = 0.0
        
        self.is_active = False
        self.is_solved = False
        self.hint = ""
        self.device_name = ""
        
        self.tuner_width = 400
        self.tuner_height = 200
        self.tuner_x = (screen_width - self.tuner_width) // 2
        self.tuner_y = (screen_height - self.tuner_height) // 2
        
        self.frequency_bar_width = 350
        self.frequency_bar_height = 30
        self.frequency_bar_x = self.tuner_x + 25
        self.frequency_bar_y = self.tuner_y + 80
        
        self.min_freq = 0.0
        self.max_freq = 150.0
        
        self.scroll_sensitivity = 0.5
        
        self.confirm_button = pygame.Rect(
            self.tuner_x + self.tuner_width // 2 - 60,
            self.tuner_y + self.tuner_height - 50,
            120, 35
        )
        self.close_button = pygame.Rect(
            self.tuner_x + self.tuner_width - 30,
            self.tuner_y + 10,
            20, 20
        )
        
        self.on_success: Optional[Callable] = None
        self.on_fail: Optional[Callable] = None
    
    def activate(self, device_name: str, default_freq: float, 
                 target_range: Tuple[float, float], hint: str):
        self.device_name = device_name
        self.current_frequency = default_freq
        self.default_frequency = default_freq
        self.target_range = target_range
        self.hint = hint
        self.is_active = True
        self.is_solved = False
    
    def deactivate(self):
        self.is_active = False
        self.current_frequency = self.default_frequency
    
    def adjust_frequency(self, delta: float):
        if self.is_active and not self.is_solved:
            self.current_frequency += delta * self.scroll_sensitivity
            self.current_frequency = max(self.min_freq, min(self.max_freq, self.current_frequency))
    
    def check_frequency(self) -> Tuple[bool, str]:
        if self.target_range[0] <= self.current_frequency <= self.target_range[1]:
            self.is_solved = True
            return True, "频率正确！信号已锁定。"
        return False, "频率不在目标范围内，信号不稳定。"
    
    def is_in_target_range(self) -> bool:
        return self.target_range[0] <= self.current_frequency <= self.target_range[1]
    
    def handle_scroll(self, y: int) -> bool:
        if self.is_active and not self.is_solved:
            self.adjust_frequency(-y)
            return True
        return False
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        if not self.is_active:
            return None
        
        if self.close_button.collidepoint(mouse_pos):
            self.deactivate()
            return "关闭调谐器"
        
        if self.confirm_button.collidepoint(mouse_pos) and not self.is_solved:
            success, message = self.check_frequency()
            return message
        
        return None
    
    def update(self, mouse_pos: Tuple[int, int]):
        pass
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font):
        if not self.is_active:
            return
        
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        tuner_rect = pygame.Rect(self.tuner_x, self.tuner_y, self.tuner_width, self.tuner_height)
        pygame.draw.rect(surface, COLORS['panel'], tuner_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['highlight'], tuner_rect, 2, border_radius=10)
        
        title = font.render(f"频率调节器 - {self.device_name}", True, COLORS['highlight'])
        title_rect = title.get_rect(centerx=tuner_rect.centerx, top=tuner_rect.top + 15)
        surface.blit(title, title_rect)
        
        pygame.draw.line(surface, COLORS['dim'], 
                        (tuner_rect.left + 20, tuner_rect.top + 45),
                        (tuner_rect.right - 20, tuner_rect.top + 45), 1)
        
        freq_bar_rect = pygame.Rect(self.frequency_bar_x, self.frequency_bar_y, 
                                    self.frequency_bar_width, self.frequency_bar_height)
        pygame.draw.rect(surface, COLORS['inventory_bg'], freq_bar_rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['dim'], freq_bar_rect, 1, border_radius=5)
        
        target_start = (self.target_range[0] / self.max_freq) * self.frequency_bar_width
        target_end = (self.target_range[1] / self.max_freq) * self.frequency_bar_width
        target_rect = pygame.Rect(
            self.frequency_bar_x + target_start,
            self.frequency_bar_y,
            target_end - target_start,
            self.frequency_bar_height
        )
        pygame.draw.rect(surface, (*COLORS['frequency_target'], 100), target_rect, border_radius=3)
        
        freq_pos = (self.current_frequency / self.max_freq) * self.frequency_bar_width
        indicator_x = self.frequency_bar_x + freq_pos
        
        indicator_color = COLORS['success'] if self.is_in_target_range() else COLORS['frequency_bar']
        pygame.draw.line(surface, indicator_color,
                        (indicator_x, self.frequency_bar_y - 5),
                        (indicator_x, self.frequency_bar_y + self.frequency_bar_height + 5), 3)
        
        freq_text = font.render(f"{self.current_frequency:.1f} MHz", True, COLORS['text'])
        freq_text_rect = freq_text.get_rect(centerx=indicator_x, bottom=self.frequency_bar_y - 10)
        surface.blit(freq_text, freq_text_rect)
        
        min_label = small_font.render(f"{self.min_freq:.0f}", True, COLORS['dim'])
        max_label = small_font.render(f"{self.max_freq:.0f}", True, COLORS['dim'])
        surface.blit(min_label, (self.frequency_bar_x, self.frequency_bar_y + self.frequency_bar_height + 5))
        surface.blit(max_label, (self.frequency_bar_x + self.frequency_bar_width - 20, 
                                 self.frequency_bar_y + self.frequency_bar_height + 5))
        
        hint_text = small_font.render(f"提示: {self.hint}", True, COLORS['dim'])
        surface.blit(hint_text, (self.frequency_bar_x, self.frequency_bar_y + self.frequency_bar_height + 25))
        
        scroll_hint = small_font.render("使用鼠标滚轮调整频率", True, COLORS['dim'])
        surface.blit(scroll_hint, (self.frequency_bar_x, self.frequency_bar_y + self.frequency_bar_height + 45))
        
        btn_color = COLORS['highlight'] if not self.is_solved else COLORS['success']
        pygame.draw.rect(surface, btn_color, self.confirm_button, border_radius=5)
        btn_text = font.render("确认" if not self.is_solved else "已解决", True, COLORS['text'])
        btn_text_rect = btn_text.get_rect(center=self.confirm_button.center)
        surface.blit(btn_text, btn_text_rect)
        
        pygame.draw.rect(surface, COLORS['warning'], self.close_button, border_radius=3)
        close_text = small_font.render("X", True, COLORS['text'])
        close_rect = close_text.get_rect(center=self.close_button.center)
        surface.blit(close_text, close_rect)
