import pygame
import sys
from constants import *
from interactables import Knob, Button, Paper, RadioDial, FaxMachine
from ui_system import UIManager, Inventory


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("幽灵信号 - Ghost Signal")
        self.clock = pygame.time.Clock()
        self.running = True

        self.background_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.object_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.ui_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        self.game_state = {
            'inventory': [],
            'solved_puzzles': [],
            'suspicion': 0,
            'current_message': [],
            'selected_object': None,
            'current_background': 0,
            'game_over': False,
            'victory': False,
            'pending_story': None
        }

        self.ui_manager = UIManager()
        self.game_state['log_system'] = self.ui_manager.log_system

        self.interactables = []
        self.setup_scene()

        self.message_timer = 0
        self.show_story_text(STORY_TEXT['intro'])

    def setup_scene(self):
        self.radio_dial = RadioDial(500, 200, 200, 80, "radio_main")
        self.interactables.append(self.radio_dial)

        self.power_knob = Knob(450, 350, 30, "power_knob")
        self.interactables.append(self.power_knob)

        self.volume_knob = Knob(550, 350, 30, "volume_knob")
        self.interactables.append(self.volume_knob)

        self.tune_knob = Knob(650, 350, 30, "radio_knob")
        self.interactables.append(self.tune_knob)

        self.fax_machine = FaxMachine(800, 150, 150, 120, "fax_machine")
        self.interactables.append(self.fax_machine)

        self.note1 = Paper(850, 350, 80, 60, "警长便签", 
                          "\"记得在码头与线人会面\"", "clue_photo")
        self.interactables.append(self.note1)

        self.reset_btn = Button(600, 450, 100, 40, "reset_btn", "重置收音机")
        self.interactables.append(self.reset_btn)

        self.increase_suspicion_btn = Button(750, 450, 120, 40, "wrong_btn", "错误回复")
        self.interactables.append(self.increase_suspicion_btn)

    def show_story_text(self, text_lines):
        self.game_state['current_message'] = text_lines
        self.message_timer = 300
        for line in text_lines:
            self.game_state['log_system'].add_log(line)

    def increase_suspicion(self, amount=1):
        self.game_state['suspicion'] += amount
        self.game_state['log_system'].add_log(f"怀疑度: {self.game_state['suspicion']}/{SUSPICION_THRESHOLD}")
        
        if self.game_state['suspicion'] >= SUSPICION_THRESHOLD:
            self.game_state['game_over'] = True
            self.show_story_text(STORY_TEXT['signal_lost'])

    def check_scene_transition(self):
        if 'pending_story' in self.game_state and self.game_state['pending_story']:
            self.show_story_text(self.game_state['pending_story'])
            self.game_state['pending_story'] = None
            
        solved_count = len(self.game_state['solved_puzzles'])
        
        for bg_id, bg_data in BACKGROUNDS.items():
            if solved_count >= bg_data['solved_required']:
                self.game_state['current_background'] = bg_id

        if solved_count >= 5 and not self.game_state['victory']:
            self.game_state['victory'] = True
            self.show_story_text(STORY_TEXT['victory'])

    def render_background_layer(self):
        bg_color = BACKGROUNDS[self.game_state['current_background']]['color']
        self.background_layer.fill(bg_color)

        console_rect = pygame.Rect(400, 100, 400, 400)
        pygame.draw.rect(self.background_layer, COLORS['DARK_GRAY'], console_rect)
        pygame.draw.rect(self.background_layer, COLORS['LIGHT_GRAY'], console_rect, 4)

        for i in range(0, SCREEN_HEIGHT, 4):
            pygame.draw.line(self.background_layer, COLORS['SCANLINE'], 
                           (0, i), (SCREEN_WIDTH, i), 1)

        title = FONTS['title'].render("GHOST SIGNAL", True, COLORS['GREEN'])
        self.background_layer.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))

        suspicion_text = FONTS['normal'].render(
            f"怀疑度: {'█' * self.game_state['suspicion']}{'░' * (SUSPICION_THRESHOLD - self.game_state['suspicion'])}", 
            True, COLORS['RED'] if self.game_state['suspicion'] > 2 else COLORS['YELLOW']
        )
        self.background_layer.blit(suspicion_text, (SCREEN_WIDTH - 200, 30))

        progress_text = FONTS['normal'].render(
            f"已解谜题: {len(self.game_state['solved_puzzles'])}/5", True, COLORS['CYAN']
        )
        self.background_layer.blit(progress_text, (SCREEN_WIDTH - 200, 60))

    def render_object_layer(self):
        self.object_layer.fill((0, 0, 0, 0))
        
        for obj in self.interactables:
            obj.draw(self.object_layer, FONTS)

        if self.ui_manager.inventory.selected_item:
            hint = FONTS['small'].render(
                f"已选择: {ITEM_DATA[self.ui_manager.inventory.selected_item]['name']}", 
                True, COLORS['CYAN']
            )
            self.object_layer.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 50))

    def render_ui_layer(self):
        self.ui_layer.fill((0, 0, 0, 0))
        
        self.ui_manager.draw(self.ui_layer, FONTS, self.game_state)

        if self.message_timer > 0 and self.game_state['current_message']:
            msg_box = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT - 180, 600, 120)
            pygame.draw.rect(self.ui_layer, COLORS['BLACK'], msg_box)
            pygame.draw.rect(self.ui_layer, COLORS['GREEN'], msg_box, 2)
            
            for i, line in enumerate(self.game_state['current_message']):
                text = FONTS['normal'].render(line, True, COLORS['WHITE'])
                self.ui_layer.blit(text, (msg_box.x + 20, msg_box.y + 20 + i * 25))
            
            self.message_timer -= 1

        if self.game_state['game_over'] or self.game_state['victory']:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLORS['BLACK'])
            self.screen.blit(overlay, (0, 0))
            
            end_text = "游戏结束" if self.game_state['game_over'] else "通关成功！"
            text = FONTS['title'].render(end_text, True, COLORS['WHITE'])
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            restart = FONTS['normal'].render("按 R 重新开始", True, COLORS['LIGHT_GRAY'])
            self.screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, SCREEN_HEIGHT//2 + 50))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.__init__()

            if event.type == pygame.MOUSEWHEEL:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.ui_manager.handle_event(event, self.game_state):
                    continue
                    
                if not (self.game_state['game_over'] or self.game_state['victory']):
                    if self.radio_dial.rect.collidepoint(mouse_pos):
                        self.radio_dial.adjust_frequency(event.y, self.game_state)
                continue

            if (self.game_state['game_over'] or self.game_state['victory']) and event.type != pygame.QUIT:
                if event.type != pygame.KEYDOWN or event.key != pygame.K_r:
                    continue

            if self.ui_manager.handle_event(event, self.game_state):
                continue

            if event.type == pygame.MOUSEMOTION:
                for obj in self.interactables:
                    obj.on_hover(event.pos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    clicked = False
                    for obj in self.interactables:
                        if obj.on_click(event.pos, self.game_state):
                            clicked = True
                            
                            if obj.name == "wrong_btn":
                                self.increase_suspicion(1)
                                self.show_story_text(STORY_TEXT['wrong_choice'])
                            
                            if obj.name == "reset_btn":
                                self.radio_dial.locked = False
                                self.game_state['log_system'].add_log("收音机已重置")
                            
                            if self.ui_manager.inventory.selected_item:
                                self.ui_manager.inventory.check_combination(obj.name, self.game_state)
                            
                            break

    def run(self):
        while self.running:
            self.handle_events()
            self.check_scene_transition()

            self.render_background_layer()
            self.render_object_layer()
            self.render_ui_layer()

            self.screen.blit(self.background_layer, (0, 0))
            self.screen.blit(self.object_layer, (0, 0))
            self.screen.blit(self.ui_layer, (0, 0))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
