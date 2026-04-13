import pygame
import time
from constants import COLORS, ITEM_DATA, LOG_MAX_ENTRIES, LOG_DISPLAY_LINES


class Inventory:
    def __init__(self, x, y, slot_size=60, max_slots=8):
        self.x = x
        self.y = y
        self.slot_size = slot_size
        self.max_slots = max_slots
        self.selected_item = None
        self.item_rects = []

    def get_slot_rect(self, index):
        col = index % 2
        row = index // 2
        return pygame.Rect(
            self.x + col * (self.slot_size + 10),
            self.y + row * (self.slot_size + 10),
            self.slot_size,
            self.slot_size
        )

    def handle_click(self, pos, game_state):
        inventory = game_state['inventory']
        for i, item_id in enumerate(inventory):
            rect = self.get_slot_rect(i)
            if rect.collidepoint(pos):
                if self.selected_item == item_id:
                    self.selected_item = None
                    game_state['log_system'].add_log("取消选择物品")
                else:
                    self.selected_item = item_id
                    game_state['log_system'].add_log(f"选择了: {ITEM_DATA[item_id]['name']}")
                return True
        return False

    def check_combination(self, target_object, game_state):
        if not self.selected_item:
            return False

        from constants import PUZZLE_SOLUTIONS
        combo_key = f"combo_{self.selected_item}_{target_object}"
        
        for puzzle_id, puzzle in PUZZLE_SOLUTIONS.items():
            if puzzle_id.startswith('combo'):
                items = puzzle['items']
                if self.selected_item in items and target_object in items:
                    if puzzle_id not in game_state['solved_puzzles']:
                        game_state['solved_puzzles'].append(puzzle_id)
                        game_state['log_system'].add_log(f"发现组合线索!")
                        game_state['current_message'] = f"使用{ITEM_DATA[self.selected_item]['name']}发现了新线索..."
                        self.selected_item = None
                        return True
        return False

    def draw(self, surface, fonts, inventory):
        title = fonts['normal'].render("物品栏", True, COLORS['WHITE'])
        surface.blit(title, (self.x, self.y - 30))

        for i in range(self.max_slots):
            rect = self.get_slot_rect(i)
            pygame.draw.rect(surface, COLORS['DARK_GRAY'], rect)
            pygame.draw.rect(surface, COLORS['LIGHT_GRAY'], rect, 2)

        from constants import ITEM_DATA
        self.item_rects = []
        for i, item_id in enumerate(inventory[:self.max_slots]):
            rect = self.get_slot_rect(i)
            self.item_rects.append((rect, item_id))
            
            item_info = ITEM_DATA.get(item_id, {})
            color = item_info.get('color', COLORS['WHITE'])
            
            pygame.draw.rect(surface, color, rect.inflate(-10, -10))
            
            if self.selected_item == item_id:
                pygame.draw.rect(surface, COLORS['CYAN'], rect, 4)


class LogSystem:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.entries = []
        self.scroll_offset = 0
        self.max_entries = LOG_MAX_ENTRIES

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.entries.append(f"[{timestamp}] {message}")
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)
        self.scroll_offset = max(0, len(self.entries) - LOG_DISPLAY_LINES)

    def scroll(self, direction):
        max_scroll = max(0, len(self.entries) - LOG_DISPLAY_LINES)
        self.scroll_offset = max(0, min(max_scroll, self.scroll_offset + direction))

    def draw(self, surface, fonts):
        pygame.draw.rect(surface, COLORS['BLACK'], (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLORS['LIGHT_GRAY'], (self.x, self.y, self.width, self.height), 2)

        title = fonts['normal'].render("通讯记录", True, COLORS['GREEN'])
        surface.blit(title, (self.x + 10, self.y + 5))

        start_y = self.y + 30
        line_height = 18
        visible_entries = LOG_DISPLAY_LINES

        start_idx = self.scroll_offset
        end_idx = min(start_idx + visible_entries, len(self.entries))

        for i, entry in enumerate(self.entries[start_idx:end_idx]):
            text_surf = fonts['small'].render(entry, True, COLORS['GREEN'])
            surface.blit(text_surf, (self.x + 10, start_y + i * line_height))

        if len(self.entries) > visible_entries:
            pygame.draw.rect(surface, COLORS['DARK_GRAY'], 
                           (self.x + self.width - 15, self.y + 30, 10, self.height - 35))
            scroll_pos = int(self.scroll_offset / max(1, len(self.entries) - visible_entries) * (self.height - 50))
            pygame.draw.rect(surface, COLORS['LIGHT_GRAY'],
                           (self.x + self.width - 14, self.y + 32 + scroll_pos, 8, 20))


class UIManager:
    def __init__(self):
        self.inventory = Inventory(20, 100)
        self.log_system = LogSystem(20, 500, 350, 200)
        self.elements = []

    def handle_event(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.log_system.x < event.pos[0] < self.log_system.x + self.log_system.width:
                    if self.log_system.y < event.pos[1] < self.log_system.y + self.log_system.height:
                        pass
                
                self.inventory.handle_click(event.pos, game_state)
        
        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if (self.log_system.x < mouse_x < self.log_system.x + self.log_system.width and
                self.log_system.y < mouse_y < self.log_system.y + self.log_system.height):
                self.log_system.scroll(-event.y)
                return True
        return False

    def draw(self, surface, fonts, game_state):
        border_rect = pygame.Rect(10, 80, 160, 380)
        pygame.draw.rect(surface, COLORS['DARK_GRAY'], border_rect)
        pygame.draw.rect(surface, COLORS['LIGHT_GRAY'], border_rect, 2)
        
        self.inventory.draw(surface, fonts, game_state['inventory'])
        self.log_system.draw(surface, fonts)
