import pygame
from typing import Dict, List, Optional, Tuple
from constants import COLORS, INVENTORY_SLOT_SIZE, INVENTORY_PADDING, CLUES


class InventorySystem:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.clues: Dict[str, dict] = {}
        self.selected_clue_id: Optional[str] = None
        self.max_slots = 8
        
        self.panel_width = INVENTORY_SLOT_SIZE + INVENTORY_PADDING * 2
        self.panel_height = screen_height - 100
        self.panel_x = screen_width - self.panel_width - 10
        self.panel_y = 50
        
        self.slot_rects: List[pygame.Rect] = []
        self._create_slot_rects()
        
    def _create_slot_rects(self):
        self.slot_rects = []
        start_y = self.panel_y + 40
        for i in range(self.max_slots):
            slot_x = self.panel_x + INVENTORY_PADDING
            slot_y = start_y + i * (INVENTORY_SLOT_SIZE + INVENTORY_PADDING)
            self.slot_rects.append(pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE))
    
    def add_clue(self, clue_id: str) -> bool:
        if clue_id in CLUES and clue_id not in self.clues:
            if len(self.clues) < self.max_slots:
                self.clues[clue_id] = CLUES[clue_id].copy()
                return True
        return False
    
    def remove_clue(self, clue_id: str) -> bool:
        if clue_id in self.clues:
            del self.clues[clue_id]
            if self.selected_clue_id == clue_id:
                self.selected_clue_id = None
            return True
        return False
    
    def select_clue(self, clue_id: str) -> bool:
        if clue_id in self.clues:
            self.selected_clue_id = clue_id if self.selected_clue_id != clue_id else None
            return True
        return False
    
    def get_selected_clue(self) -> Optional[dict]:
        if self.selected_clue_id:
            return self.clues.get(self.selected_clue_id)
        return None
    
    def clear_selection(self):
        self.selected_clue_id = None
    
    def handle_click(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                clue_ids = list(self.clues.keys())
                if i < len(clue_ids):
                    return clue_ids[i]
        return None
    
    def update_hover(self, mouse_pos: Tuple[int, int]) -> Optional[str]:
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                clue_ids = list(self.clues.keys())
                if i < len(clue_ids):
                    return self.clues[clue_ids[i]]['name']
        return None
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        pygame.draw.rect(surface, COLORS['inventory_bg'], panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLORS['dim'], panel_rect, 2, border_radius=8)
        
        title = font.render("物品栏", True, COLORS['text'])
        title_rect = title.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 10)
        surface.blit(title, title_rect)
        
        for i, rect in enumerate(self.slot_rects):
            pygame.draw.rect(surface, COLORS['panel'], rect, border_radius=4)
            pygame.draw.rect(surface, COLORS['dim'], rect, 1, border_radius=4)
            
            clue_ids = list(self.clues.keys())
            if i < len(clue_ids):
                clue_id = clue_ids[i]
                clue = self.clues[clue_id]
                
                if self.selected_clue_id == clue_id:
                    pygame.draw.rect(surface, COLORS['highlight'], rect, 2, border_radius=4)
                
                self._draw_clue_icon(surface, rect, clue['icon'])
        
        if self.selected_clue_id and self.selected_clue_id in self.clues:
            selected = self.clues[self.selected_clue_id]
            self._draw_clue_detail(surface, selected, font)
    
    def _draw_clue_icon(self, surface: pygame.Surface, rect: pygame.Rect, icon_type: str):
        center = rect.center
        color = COLORS['highlight']
        
        if icon_type == 'paper':
            paper_rect = pygame.Rect(center[0] - 12, center[1] - 15, 24, 30)
            pygame.draw.rect(surface, color, paper_rect, 2, border_radius=2)
            for i in range(3):
                line_y = center[1] - 8 + i * 8
                pygame.draw.line(surface, color, (center[0] - 8, line_y), (center[0] + 8, line_y), 1)
                
        elif icon_type == 'tape':
            pygame.draw.rect(surface, color, (center[0] - 15, center[1] - 10, 30, 20), 2, border_radius=3)
            pygame.draw.circle(surface, color, (center[0] - 7, center[1]), 5, 2)
            pygame.draw.circle(surface, color, (center[0] + 7, center[1]), 5, 2)
            
        elif icon_type == 'photo':
            pygame.draw.rect(surface, color, (center[0] - 15, center[1] - 12, 30, 24), 2, border_radius=2)
            pygame.draw.circle(surface, color, (center[0] - 5, center[1] - 3), 4, 1)
            pygame.draw.polygon(surface, color, [
                (center[0] - 10, center[1] + 8),
                (center[0], center[1]),
                (center[0] + 10, center[1] + 8)
            ], 1)
            
        elif icon_type == 'key':
            pygame.draw.circle(surface, color, (center[0] - 5, center[1] - 5), 8, 2)
            pygame.draw.line(surface, color, (center[0], center[1]), (center[0] + 15, center[1] + 10), 2)
            pygame.draw.line(surface, color, (center[0] + 10, center[1] + 7), (center[0] + 10, center[1] + 12), 2)
    
    def _draw_clue_detail(self, surface: pygame.Surface, clue: dict, font: pygame.font.Font):
        detail_width = 200
        detail_height = 80
        detail_x = self.panel_x - detail_width - 10
        detail_y = self.panel_y
        
        detail_rect = pygame.Rect(detail_x, detail_y, detail_width, detail_height)
        pygame.draw.rect(surface, COLORS['panel'], detail_rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['highlight'], detail_rect, 2, border_radius=5)
        
        name_text = font.render(clue['name'], True, COLORS['highlight'])
        surface.blit(name_text, (detail_x + 10, detail_y + 10))
        
        desc_lines = self._wrap_text(clue['description'], font, detail_width - 20)
        for i, line in enumerate(desc_lines[:3]):
            desc_text = font.render(line, True, COLORS['text'])
            surface.blit(desc_text, (detail_x + 10, detail_y + 35 + i * 18))
    
    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        words = list(text)
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        return lines
