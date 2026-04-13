import pygame
from constants import COLORS


class Interactable:
    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.hovered = False
        self.active = True
        self.visible = True

    def on_hover(self, mouse_pos):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos) and self.active and self.visible
        return self.hovered and not was_hovered

    def on_click(self, mouse_pos, game_state):
        if self.rect.collidepoint(mouse_pos) and self.active and self.visible:
            self.execute_click(game_state)
            return True
        return False

    def execute_click(self, game_state):
        pass

    def draw(self, surface, fonts):
        pass


class Knob(Interactable):
    def __init__(self, x, y, radius, name):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, name)
        self.radius = radius
        self.center_x = x
        self.center_y = y
        self.angle = 0

    def draw(self, surface, fonts):
        if not self.visible:
            return
        
        color = COLORS['CYAN'] if self.hovered else COLORS['LIGHT_GRAY']
        pygame.draw.circle(surface, color, (self.center_x, self.center_y), self.radius, 3)
        pygame.draw.circle(surface, COLORS['DARK_GRAY'], (self.center_x, self.center_y), self.radius - 5)
        
        import math
        end_x = self.center_x + int(math.cos(self.angle) * (self.radius - 10))
        end_y = self.center_y + int(math.sin(self.angle) * (self.radius - 10))
        pygame.draw.line(surface, COLORS['GREEN'], (self.center_x, self.center_y), (end_x, end_y), 3)

    def execute_click(self, game_state):
        game_state['selected_object'] = self.name


class Button(Interactable):
    def __init__(self, x, y, width, height, name, text):
        super().__init__(x, y, width, height, name)
        self.text = text
        self.pressed = False

    def draw(self, surface, fonts):
        if not self.visible:
            return
        
        color = COLORS['GREEN'] if self.hovered else COLORS['GRAY']
        border_color = COLORS['CYAN'] if self.hovered else COLORS['LIGHT_GRAY']
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)
        
        text_surf = fonts['normal'].render(self.text, True, COLORS['BLACK'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def execute_click(self, game_state):
        game_state['log_system'].add_log(f"按下了: {self.text}")


class Paper(Interactable):
    def __init__(self, x, y, width, height, name, content, item_id=None):
        super().__init__(x, y, width, height, name)
        self.content = content
        self.item_id = item_id
        self.collected = False

    def draw(self, surface, fonts):
        if not self.visible or self.collected:
            return
        
        color = COLORS['YELLOW'] if self.hovered else (220, 220, 180)
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, COLORS['BLACK'], self.rect, 1)
        
        text_surf = fonts['small'].render(self.name, True, COLORS['BLACK'])
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))

    def execute_click(self, game_state):
        if not self.collected:
            game_state['log_system'].add_log(f"获得物品: {self.name}")
            if self.item_id and self.item_id not in game_state['inventory']:
                game_state['inventory'].append(self.item_id)
            self.collected = True
            game_state['current_message'] = self.content


class RadioDial(Interactable):
    def __init__(self, x, y, width, height, name):
        super().__init__(x, y, width, height, name)
        self.frequency = 88.0
        self.target_frequency = None
        self.locked = False

    def draw(self, surface, fonts):
        if not self.visible:
            return
        
        bg_color = COLORS['DARK_GREEN'] if self.locked else COLORS['BLACK']
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, COLORS['GREEN'], self.rect, 2)
        
        freq_text = f"{self.frequency:.1f} MHz"
        text_surf = fonts['large'].render(freq_text, True, COLORS['GREEN'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        if self.hovered:
            hint = fonts['small'].render("使用滚轮调整频率", True, COLORS['CYAN'])
            surface.blit(hint, (self.rect.x, self.rect.y - 20))

    def adjust_frequency(self, delta, game_state):
        if self.locked:
            return
        
        self.frequency = max(80.0, min(120.0, self.frequency + delta * 0.1))
        game_state['log_system'].add_log(f"频率: {self.frequency:.1f} MHz")
        
        from constants import PUZZLE_SOLUTIONS, STORY_TEXT, ITEM_DATA
        for puzzle_id, puzzle in PUZZLE_SOLUTIONS.items():
            if puzzle_id.startswith('frequency'):
                target = puzzle['target']
                tolerance = puzzle['tolerance']
                if abs(self.frequency - target) <= tolerance:
                    if puzzle_id not in game_state['solved_puzzles']:
                        game_state['solved_puzzles'].append(puzzle_id)
                        self.locked = True
                        story_key = f"frequency_success_{puzzle_id[-1]}"
                        if story_key in STORY_TEXT:
                            game_state['log_system'].add_log(f"--- 信号锁定在 {target} MHz ---")
                            game_state['pending_story'] = STORY_TEXT[story_key]
                        reward = puzzle['reward']
                        if reward and reward not in game_state['inventory']:
                            game_state['inventory'].append(reward)
                            game_state['log_system'].add_log(f"获得线索: {ITEM_DATA[reward]['name']}")

    def execute_click(self, game_state):
        game_state['log_system'].add_log("点击了收音机 - 使用鼠标滚轮调整频率")


class FaxMachine(Interactable):
    def __init__(self, x, y, width, height, name):
        super().__init__(x, y, width, height, name)
        self.has_paper = True

    def draw(self, surface, fonts):
        if not self.visible:
            return
        
        color = COLORS['CYAN'] if self.hovered else COLORS['GRAY']
        pygame.draw.rect(surface, COLORS['DARK_GRAY'], self.rect)
        pygame.draw.rect(surface, color, self.rect, 3)
        
        text_surf = fonts['normal'].render("传真机", True, COLORS['WHITE'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def execute_click(self, game_state):
        game_state['selected_object'] = self.name
        game_state['log_system'].add_log("检查传真机...")
