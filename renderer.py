import pygame
import os
from typing import Dict, List, Optional, Tuple
from constants import COLORS, SCENES, STORY_TEXTS


def get_chinese_font(size: int) -> pygame.font.Font:
    chinese_fonts = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "NSimSun",
        "FangSong",
        "KaiTi",
    ]
    
    for font_name in chinese_fonts:
        try:
            font = pygame.font.SysFont(font_name, size)
            test_surface = font.render("测试", True, (255, 255, 255))
            if test_surface.get_width() > 10:
                return font
        except:
            continue
    
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return pygame.font.Font(font_path, size)
            except:
                continue
    
    return pygame.font.Font(None, size)


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        self.background_layer = pygame.Surface((self.screen_width, self.screen_height))
        self.object_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.ui_layer = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        self.current_scene = "intro"
        self.scene_config = SCENES[self.current_scene]
        
        self.font_large = get_chinese_font(36)
        self.font_medium = get_chinese_font(28)
        self.font_small = get_chinese_font(22)
        
        self._render_background()
    
    def _render_background(self):
        self.background_layer.fill(self.scene_config['background_color'])
        
        self._draw_control_room_background()
    
    def _draw_control_room_background(self):
        for i in range(5):
            shelf_y = 100 + i * 120
            pygame.draw.rect(self.background_layer, (25, 25, 40), 
                           (50, shelf_y, self.screen_width - 120, 8))
        
        for i in range(8):
            led_x = 60 + i * 40
            led_color = (50, 200, 50) if i % 2 == 0 else (200, 50, 50)
            pygame.draw.circle(self.background_layer, led_color, (led_x, 60), 3)
        
        pygame.draw.rect(self.background_layer, (35, 35, 50),
                        (50, self.screen_height - 100, self.screen_width - 120, 80))
        pygame.draw.rect(self.background_layer, (45, 45, 60),
                        (50, self.screen_height - 100, self.screen_width - 120, 80), 2)
        
        for i in range(10):
            meter_x = 80 + i * 100
            pygame.draw.rect(self.background_layer, (20, 20, 30),
                           (meter_x, self.screen_height - 90, 60, 60))
            pygame.draw.rect(self.background_layer, (60, 60, 80),
                           (meter_x, self.screen_height - 90, 60, 60), 1)
            
            meter_level = 30 + (i * 7) % 30
            pygame.draw.rect(self.background_layer, (50, 150, 50),
                           (meter_x + 5, self.screen_height - 30 - meter_level, 50, meter_level))
        
        ambient_text = self.scene_config['ambient_text']
        text_surface = self.font_small.render(ambient_text, True, COLORS['dim'])
        self.background_layer.blit(text_surface, (20, 20))
    
    def change_scene(self, scene_name: str):
        if scene_name in SCENES:
            self.current_scene = scene_name
            self.scene_config = SCENES[scene_name]
            self._render_background()
    
    def clear_object_layer(self):
        self.object_layer.fill((0, 0, 0, 0))
    
    def clear_ui_layer(self):
        self.ui_layer.fill((0, 0, 0, 0))
    
    def draw_interactables(self, interactables: List):
        for item in interactables:
            item.draw(self.object_layer)
    
    def draw_tooltips(self, interactables: List):
        for item in interactables:
            item.draw_tooltip(self.ui_layer, self.font_small)
    
    def draw_suspicion_bar(self, suspicion_level: int, max_suspicion: int):
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 50
        
        pygame.draw.rect(self.ui_layer, COLORS['panel'],
                        (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        fill_width = int((suspicion_level / max_suspicion) * (bar_width - 4))
        ratio = suspicion_level / max_suspicion
        
        if ratio < 0.3:
            fill_color = COLORS['success']
        elif ratio < 0.6:
            fill_color = COLORS['highlight']
        elif ratio < 0.9:
            fill_color = (255, 165, 0)
        else:
            fill_color = COLORS['warning']
        
        if fill_width > 0:
            pygame.draw.rect(self.ui_layer, fill_color,
                           (bar_x + 2, bar_y + 2, fill_width, bar_height - 4), border_radius=3)
        
        pygame.draw.rect(self.ui_layer, COLORS['dim'],
                        (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
        
        label = self.font_small.render("信号稳定性", True, COLORS['text'])
        self.ui_layer.blit(label, (bar_x, bar_y - 18))
        
        level_text = self.font_small.render(f"{suspicion_level}/{max_suspicion}", True, COLORS['text'])
        self.ui_layer.blit(level_text, (bar_x + bar_width + 10, bar_y + 2))
    
    def draw_progress(self, solved: int, total: int, collected: int, total_clues: int):
        progress_text = f"谜题: {solved}/{total}  线索: {collected}/{total_clues}"
        text_surface = self.font_small.render(progress_text, True, COLORS['text'])
        self.ui_layer.blit(text_surface, (20, 90))
    
    def draw_story_text(self, story_key: str, alpha: int = 255):
        if story_key not in STORY_TEXTS:
            return
        
        story = STORY_TEXTS[story_key]
        
        box_width = 600
        box_height = 150
        box_x = (self.screen_width - box_width) // 2
        box_y = 20
        
        story_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(story_surface, (*COLORS['panel'], 220), 
                        (0, 0, box_width, box_height), border_radius=10)
        pygame.draw.rect(story_surface, COLORS['highlight'], 
                        (0, 0, box_width, box_height), 2, border_radius=10)
        
        title = self.font_medium.render(story['title'], True, COLORS['highlight'])
        story_surface.blit(title, (20, 15))
        
        for i, line in enumerate(story['content'][:3]):
            text = self.font_small.render(line, True, COLORS['text'])
            story_surface.blit(text, (20, 45 + i * 25))
        
        story_surface.set_alpha(alpha)
        self.ui_layer.blit(story_surface, (box_x, box_y))
    
    def draw_dialog(self, dialog_data: Dict, options: List, selected_index: int = -1):
        box_width = 500
        box_height = 200
        box_x = (self.screen_width - box_width) // 2
        box_y = self.screen_height - box_height - 50
        
        pygame.draw.rect(self.ui_layer, (*COLORS['panel'], 240),
                        (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(self.ui_layer, COLORS['highlight'],
                        (box_x, box_y, box_width, box_height), 2, border_radius=10)
        
        prompt = self.font_medium.render(dialog_data['prompt'], True, COLORS['text'])
        self.ui_layer.blit(prompt, (box_x + 20, box_y + 15))
        
        for i, option in enumerate(options):
            opt_y = box_y + 55 + i * 35
            opt_rect = pygame.Rect(box_x + 20, opt_y, box_width - 40, 30)
            
            bg_color = COLORS['highlight'] if i == selected_index else COLORS['inventory_bg']
            pygame.draw.rect(self.ui_layer, bg_color, opt_rect, border_radius=5)
            pygame.draw.rect(self.ui_layer, COLORS['dim'], opt_rect, 1, border_radius=5)
            
            opt_text = self.font_small.render(option['text'], True, COLORS['text'])
            self.ui_layer.blit(opt_text, (opt_rect.x + 10, opt_rect.y + 7))
    
    def draw_game_over(self, is_win: bool):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        title = "游戏结束"
        if is_win:
            title = "恭喜通关！"
            title_color = COLORS['success']
            story_key = 'ending_good'
        else:
            title_color = COLORS['warning']
            story_key = 'ending_bad'
        
        title_surface = self.font_large.render(title, True, title_color)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
        overlay.blit(title_surface, title_rect)
        
        if story_key in STORY_TEXTS:
            story = STORY_TEXTS[story_key]
            for i, line in enumerate(story['content'][:3]):
                text = self.font_medium.render(line, True, COLORS['text'])
                text_rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20 + i * 30))
                overlay.blit(text, text_rect)
        
        restart_text = self.font_small.render("按 R 重新开始  |  按 ESC 退出", True, COLORS['dim'])
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        overlay.blit(restart_text, restart_rect)
        
        self.ui_layer.blit(overlay, (0, 0))
    
    def render(self):
        self.screen.blit(self.background_layer, (0, 0))
        self.screen.blit(self.object_layer, (0, 0))
        self.screen.blit(self.ui_layer, (0, 0))
    
    def get_fonts(self) -> Tuple[pygame.font.Font, pygame.font.Font, pygame.font.Font]:
        return self.font_large, self.font_medium, self.font_small
