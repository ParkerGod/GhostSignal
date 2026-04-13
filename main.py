import pygame
import sys
from typing import List, Dict, Optional

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLORS,
    PUZZLES, INTERACTABLES, CLUES, DIALOG_OPTIONS, STORY_TEXTS
)
from interactables import Interactable, FrequencyDevice, ClueItem, DialogOption
from inventory import InventorySystem
from frequency_tuner import FrequencyTuner
from log_system import LogSystem
from game_state import GameState, EventSystem
from renderer import Renderer


class GhostSignalGame:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("幽灵信号 - Ghost Signal")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.renderer = Renderer(self.screen)
        self.font_large, self.font_medium, self.font_small = self.renderer.get_fonts()
        
        self.game_state = GameState()
        self.inventory = InventorySystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frequency_tuner = FrequencyTuner(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.log_system = LogSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.interactables: List[Interactable] = []
        self.dialog_options: List[DialogOption] = []
        
        self.current_dialog_data: Optional[Dict] = None
        self.selected_dialog_index = -1
        
        self._setup_interactables()
        self._setup_event_handlers()
        self._show_intro()
    
    def _setup_interactables(self):
        self.interactables.clear()
        
        for item_id, item_data in INTERACTABLES.items():
            if item_data['type'] == 'frequency':
                puzzle_id = item_data['puzzle_id']
                puzzle = PUZZLES[puzzle_id]
                
                device = FrequencyDevice(
                    name=item_data['name'],
                    rect=item_data['rect'],
                    description=item_data['description'],
                    puzzle_id=puzzle_id,
                    target_range=puzzle['target_range'],
                    default_freq=puzzle['default_frequency'],
                    hint=puzzle['hint'],
                    success_text=puzzle['success_text'],
                    fail_text=puzzle['fail_text']
                )
                self.interactables.append(device)
                
            elif item_data['type'] == 'clue':
                clue_id = item_data['clue_id']
                clue = CLUES[clue_id]
                
                clue_item = ClueItem(
                    name=item_data['name'],
                    rect=item_data['rect'],
                    description=item_data['description'],
                    clue_id=clue_id,
                    clue_name=clue['name'],
                    clue_description=clue['description'],
                    icon_type=clue['icon']
                )
                self.interactables.append(clue_item)
    
    def _setup_event_handlers(self):
        self.game_state.event_system.register_event("scene_change", self._on_scene_change)
        self.game_state.event_system.register_event("game_over", self._on_game_over)
        self.game_state.event_system.register_event("game_win", self._on_game_win)
    
    def _on_scene_change(self, scene_name: str):
        self.renderer.change_scene(scene_name)
        self.log_system.add_log(f"进入新场景: {scene_name}", "highlight")
    
    def _on_game_over(self):
        self.log_system.add_log("信号中断...游戏结束", "warning")
    
    def _on_game_win(self):
        self.log_system.add_log("恭喜！你解开了所有谜题！", "success")
    
    def _show_intro(self):
        self.log_system.add_log("游戏开始 - 幽灵信号", "highlight")
        self.log_system.add_log("你是一名深夜电台技术员", "info")
        self.log_system.add_log("点击设备进行交互", "info")
    
    def _start_dialog(self, dialog_id: str):
        if dialog_id in DIALOG_OPTIONS:
            self.current_dialog_data = DIALOG_OPTIONS[dialog_id]
            self.dialog_options.clear()
            
            for i, opt in enumerate(self.current_dialog_data['options']):
                opt_rect = pygame.Rect(
                    (SCREEN_WIDTH - 460) // 2,
                    SCREEN_HEIGHT - 195 + i * 35,
                    460, 30
                )
                dialog_opt = DialogOption(
                    rect=opt_rect,
                    text=opt['text'],
                    is_correct=opt['correct'],
                    response=opt['response'],
                    option_index=i
                )
                self.dialog_options.append(dialog_opt)
            
            self.game_state.start_dialog(dialog_id)
    
    def _handle_dialog_click(self, mouse_pos) -> bool:
        for i, opt in enumerate(self.dialog_options):
            if opt.contains_point(mouse_pos):
                self.selected_dialog_index = i
                
                dialog_option = self.current_dialog_data['options'][i]
                self.log_system.add_log(f"选择: {dialog_option['text']}", "info")
                self.log_system.add_log(dialog_option['response'], "info")
                
                if not dialog_option['correct']:
                    self.game_state.make_mistake("错误的对话选择")
                    self.log_system.add_log("警告: 信号不稳定!", "warning")
                
                self.game_state.end_dialog()
                self.current_dialog_data = None
                self.dialog_options.clear()
                self.selected_dialog_index = -1
                
                return True
        return False
    
    def _handle_interactable_click(self, mouse_pos) -> bool:
        selected_clue = self.inventory.get_selected_clue()
        
        for item in self.interactables:
            if item.contains_point(mouse_pos) and item.enabled:
                if selected_clue:
                    self._handle_combination_interaction(item, selected_clue)
                    return True
                
                result = item.on_click({})
                if result:
                    self.log_system.add_log(result, "info")
                
                if isinstance(item, FrequencyDevice) and not item.is_solved:
                    puzzle = PUZZLES[item.puzzle_id]
                    self.frequency_tuner.activate(
                        device_name=item.name,
                        default_freq=item.default_frequency,
                        target_range=item.target_range,
                        hint=item.hint
                    )
                    return True
                
                elif isinstance(item, ClueItem) and not item.collected:
                    self.inventory.add_clue(item.clue_id)
                    self.game_state.collect_clue(item.clue_id)
                    self.log_system.add_log(f"获得线索: {item.clue_name}", "success")
                    return True
                
                return True
        
        return False
    
    def _handle_combination_interaction(self, item: Interactable, clue: Dict):
        self.log_system.add_log(f"尝试组合: {clue['name']} + {item.name}", "info")
        
        if isinstance(item, FrequencyDevice):
            if clue['icon'] == 'paper':
                self.log_system.add_log("纸条上的频率提示帮助你调整设备!", "success")
                puzzle = PUZZLES[item.puzzle_id]
                item.current_frequency = puzzle['target_range'][0]
        
        self.inventory.clear_selection()
    
    def _handle_frequency_confirm(self):
        success, message = self.frequency_tuner.check_frequency()
        
        if success:
            self.log_system.add_log(message, "success")
            
            for item in self.interactables:
                if isinstance(item, FrequencyDevice):
                    if item.name == self.frequency_tuner.device_name:
                        item.is_solved = True
                        puzzle = PUZZLES[item.puzzle_id]
                        self.log_system.add_log(puzzle['success_text'], "highlight")
                        self.game_state.solve_puzzle(item.puzzle_id)
                        break
        else:
            self.log_system.add_log(message, "warning")
            self.game_state.make_mistake("错误的频率调整")
            self.log_system.add_log("信号不稳定!", "warning")
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.frequency_tuner.is_active:
                        self.frequency_tuner.deactivate()
                    elif self.game_state.show_dialog:
                        self.game_state.end_dialog()
                    else:
                        self.running = False
                    return
                
                if event.key == pygame.K_r:
                    if self.game_state.game_over or self.game_state.game_won:
                        self._restart_game()
                    return
            
            if self.game_state.game_over or self.game_state.game_won:
                continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.frequency_tuner.is_active:
                        result = self.frequency_tuner.handle_click(mouse_pos)
                        if result:
                            if "关闭" in result:
                                self.frequency_tuner.deactivate()
                            elif "正确" in result or "不在" in result:
                                self._handle_frequency_confirm()
                        continue
                    
                    if self.game_state.show_dialog:
                        if self._handle_dialog_click(mouse_pos):
                            continue
                    
                    if self.log_system.handle_click(mouse_pos):
                        continue
                    
                    clue_id = self.inventory.handle_click(mouse_pos)
                    if clue_id:
                        self.inventory.select_clue(clue_id)
                        self.log_system.add_log(f"选中线索: {CLUES[clue_id]['name']}", "info")
                        continue
                    
                    self._handle_interactable_click(mouse_pos)
                
                elif event.button == 4:
                    if self.frequency_tuner.is_active:
                        self.frequency_tuner.handle_scroll(1)
                    elif self.log_system.handle_scroll(mouse_pos, -1):
                        pass
                
                elif event.button == 5:
                    if self.frequency_tuner.is_active:
                        self.frequency_tuner.handle_scroll(-1)
                    elif self.log_system.handle_scroll(mouse_pos, 1):
                        pass
            
            if event.type == pygame.MOUSEWHEEL:
                if self.frequency_tuner.is_active:
                    self.frequency_tuner.handle_scroll(event.y)
    
    def _restart_game(self):
        self.game_state = GameState()
        self.inventory = InventorySystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.frequency_tuner = FrequencyTuner(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.log_system = LogSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
        self._setup_interactables()
        self._setup_event_handlers()
        self._show_intro()
        self.renderer.change_scene("intro")
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for item in self.interactables:
            item.update_hover(mouse_pos)
        
        self.inventory.update_hover(mouse_pos)
    
    def render(self):
        self.renderer.clear_object_layer()
        self.renderer.clear_ui_layer()
        
        self.renderer.draw_interactables(self.interactables)
        
        progress = self.game_state.get_progress()
        self.renderer.draw_suspicion_bar(
            progress['suspicion'],
            progress['max_suspicion']
        )
        self.renderer.draw_progress(
            progress['solved_puzzles'],
            progress['total_puzzles'],
            progress['collected_clues'],
            progress['total_clues']
        )
        
        story_key = f"chapter{self.game_state.current_chapter}" if self.game_state.current_chapter <= 3 else "intro"
        if self.game_state.current_chapter == 1:
            story_key = "intro"
        self.renderer.draw_story_text(story_key)
        
        self.renderer.draw_tooltips(self.interactables)
        
        self.inventory.draw(self.renderer.ui_layer, self.font_small)
        self.log_system.draw(self.renderer.ui_layer, self.font_small, self.font_small)
        
        if self.frequency_tuner.is_active:
            self.frequency_tuner.draw(
                self.renderer.ui_layer,
                self.font_medium,
                self.font_small
            )
        
        if self.game_state.show_dialog and self.current_dialog_data:
            self.renderer.draw_dialog(
                self.current_dialog_data,
                self.dialog_options,
                self.selected_dialog_index
            )
        
        if self.game_state.game_over or self.game_state.game_won:
            self.renderer.draw_game_over(self.game_state.game_won)
        
        self.renderer.render()
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    game = GhostSignalGame()
    game.run()


if __name__ == "__main__":
    main()
