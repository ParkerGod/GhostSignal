import pygame
import time
from typing import List, Dict, Tuple, Optional
from constants import COLORS, LOG_RETENTION_SECONDS


class LogSystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.logs: List[Dict[str, any]] = []
        self.max_logs = 100
        self.retention_seconds = LOG_RETENTION_SECONDS
        
        self.panel_width = 300
        self.panel_height = 250
        self.panel_x = 10
        self.panel_y = screen_height - self.panel_height - 10
        
        self.scroll_offset = 0
        self.line_height = 20
        self.visible_lines = 10
        
        self.is_expanded = False
        self.expanded_height = 400
        self.expanded_y = screen_height - self.expanded_height - 10
        
        self.up_button = pygame.Rect(self.panel_x + self.panel_width - 25, self.panel_y + 5, 20, 20)
        self.down_button = pygame.Rect(self.panel_x + self.panel_width - 25, self.panel_y + self.panel_height - 25, 20, 20)
        self.expand_button = pygame.Rect(self.panel_x + self.panel_width - 50, self.panel_y + 5, 20, 20)
    
    def add_log(self, message: str, log_type: str = "info"):
        timestamp = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
        
        self.logs.append({
            'message': message,
            'type': log_type,
            'timestamp': timestamp,
            'time_str': time_str
        })
        
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        self.scroll_offset = max(0, len(self.logs) - self.visible_lines)
    
    def clean_old_logs(self):
        current_time = time.time()
        self.logs = [log for log in self.logs 
                     if current_time - log['timestamp'] <= self.retention_seconds]
    
    def get_recent_logs(self, minutes: int = 5) -> List[Dict]:
        current_time = time.time()
        cutoff = current_time - (minutes * 60)
        return [log for log in self.logs if log['timestamp'] >= cutoff]
    
    def scroll(self, direction: int):
        self.scroll_offset += direction
        max_offset = max(0, len(self.logs) - self.visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_offset))
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        current_panel_y = self.expanded_y if self.is_expanded else self.panel_y
        current_panel_height = self.expanded_height if self.is_expanded else self.panel_height
        
        up_rect = pygame.Rect(self.panel_x + self.panel_width - 25, current_panel_y + 5, 20, 20)
        down_rect = pygame.Rect(self.panel_x + self.panel_width - 25, current_panel_y + current_panel_height - 25, 20, 20)
        expand_rect = pygame.Rect(self.panel_x + self.panel_width - 50, current_panel_y + 5, 20, 20)
        
        if up_rect.collidepoint(mouse_pos):
            self.scroll(-1)
            return True
        
        if down_rect.collidepoint(mouse_pos):
            self.scroll(1)
            return True
        
        if expand_rect.collidepoint(mouse_pos):
            self.is_expanded = not self.is_expanded
            return True
        
        return False
    
    def handle_scroll(self, mouse_pos: Tuple[int, int], direction: int) -> bool:
        current_panel_y = self.expanded_y if self.is_expanded else self.panel_y
        current_panel_height = self.expanded_height if self.is_expanded else self.panel_height
        panel_rect = pygame.Rect(self.panel_x, current_panel_y, self.panel_width, current_panel_height)
        
        if panel_rect.collidepoint(mouse_pos):
            self.scroll(direction)
            return True
        return False
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font):
        self.clean_old_logs()
        
        current_panel_y = self.expanded_y if self.is_expanded else self.panel_y
        current_panel_height = self.expanded_height if self.is_expanded else self.panel_height
        
        panel_rect = pygame.Rect(self.panel_x, current_panel_y, self.panel_width, current_panel_height)
        pygame.draw.rect(surface, COLORS['log_bg'], panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['dim'], panel_rect, 2, border_radius=8)
        
        title = font.render("交互日志", True, COLORS['text'])
        surface.blit(title, (self.panel_x + 10, current_panel_y + 8))
        
        up_rect = pygame.Rect(self.panel_x + self.panel_width - 25, current_panel_y + 5, 20, 20)
        down_rect = pygame.Rect(self.panel_x + self.panel_width - 25, current_panel_y + current_panel_height - 25, 20, 20)
        expand_rect = pygame.Rect(self.panel_x + self.panel_width - 50, current_panel_y + 5, 20, 20)
        
        pygame.draw.rect(surface, COLORS['panel'], up_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS['panel'], down_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS['panel'], expand_rect, border_radius=3)
        
        up_text = small_font.render("▲", True, COLORS['text'])
        down_text = small_font.render("▼", True, COLORS['text'])
        expand_text = small_font.render("+" if not self.is_expanded else "-", True, COLORS['text'])
        
        surface.blit(up_text, up_text.get_rect(center=up_rect.center))
        surface.blit(down_text, down_text.get_rect(center=down_rect.center))
        surface.blit(expand_text, expand_text.get_rect(center=expand_rect.center))
        
        content_y = current_panel_y + 35
        content_height = current_panel_height - 70
        content_rect = pygame.Rect(self.panel_x + 5, content_y, self.panel_width - 35, content_height)
        
        surface.set_clip(content_rect)
        
        visible_logs = self.logs[self.scroll_offset:self.scroll_offset + self.visible_lines + 5]
        
        for i, log in enumerate(visible_logs):
            y_pos = content_y + i * self.line_height
            if y_pos > content_y + content_height:
                break
            
            color = COLORS['text']
            if log['type'] == 'success':
                color = COLORS['success']
            elif log['type'] == 'warning':
                color = COLORS['warning']
            elif log['type'] == 'highlight':
                color = COLORS['highlight']
            
            time_text = small_font.render(f"[{log['time_str']}]", True, COLORS['dim'])
            surface.blit(time_text, (self.panel_x + 10, y_pos))
            
            msg_text = small_font.render(log['message'][:25], True, color)
            surface.blit(msg_text, (self.panel_x + 70, y_pos))
        
        surface.set_clip(None)
        
        if len(self.logs) > self.visible_lines:
            max_scroll = len(self.logs) - self.visible_lines
            if max_scroll > 0:
                scroll_ratio = self.scroll_offset / max_scroll
                scrollbar_height = 50
                scrollbar_y = content_y + scroll_ratio * (content_height - scrollbar_height)
                scrollbar_rect = pygame.Rect(
                    self.panel_x + self.panel_width - 20,
                    scrollbar_y,
                    15,
                    scrollbar_height
                )
                pygame.draw.rect(surface, COLORS['dim'], scrollbar_rect, border_radius=3)
