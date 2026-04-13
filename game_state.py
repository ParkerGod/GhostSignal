from typing import Callable, Dict, List, Optional
from constants import MAX_SUSPICION, COLORS


class SuspicionSystem:
    def __init__(self):
        self.suspicion_level = 0
        self.max_suspicion = MAX_SUSPICION
        self.warnings: List[str] = []
        self.on_max_suspicion: Optional[Callable] = None
        self.on_suspicion_change: Optional[Callable] = None
        
    def increase_suspicion(self, reason: str = "") -> bool:
        if self.suspicion_level >= self.max_suspicion:
            return False
        
        self.suspicion_level += 1
        
        if reason:
            self.warnings.append(reason)
        
        if self.on_suspicion_change:
            self.on_suspicion_change(self.suspicion_level, reason)
        
        if self.suspicion_level >= self.max_suspicion:
            if self.on_max_suspicion:
                self.on_max_suspicion()
            return True
        
        return False
    
    def decrease_suspicion(self, amount: int = 1):
        self.suspicion_level = max(0, self.suspicion_level - amount)
        if self.on_suspicion_change:
            self.on_suspicion_change(self.suspicion_level, "")
    
    def reset_suspicion(self):
        self.suspicion_level = 0
        self.warnings.clear()
    
    def is_maxed(self) -> bool:
        return self.suspicion_level >= self.max_suspicion
    
    def get_suspicion_ratio(self) -> float:
        return self.suspicion_level / self.max_suspicion
    
    def get_warning_level(self) -> str:
        ratio = self.get_suspicion_ratio()
        if ratio < 0.3:
            return "low"
        elif ratio < 0.6:
            return "medium"
        elif ratio < 0.9:
            return "high"
        return "critical"


class EventSystem:
    def __init__(self):
        self.events: Dict[str, List[Callable]] = {}
        self.event_flags: Dict[str, bool] = {}
        self.event_counters: Dict[str, int] = {}
        
    def register_event(self, event_name: str, callback: Callable):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(callback)
    
    def trigger_event(self, event_name: str, *args, **kwargs):
        if event_name in self.events:
            for callback in self.events[event_name]:
                callback(*args, **kwargs)
    
    def set_flag(self, flag_name: str, value: bool = True):
        self.event_flags[flag_name] = value
        self.trigger_event(f"flag_{flag_name}", value)
    
    def get_flag(self, flag_name: str) -> bool:
        return self.event_flags.get(flag_name, False)
    
    def increment_counter(self, counter_name: str, amount: int = 1) -> int:
        if counter_name not in self.event_counters:
            self.event_counters[counter_name] = 0
        self.event_counters[counter_name] += amount
        
        self.trigger_event(f"counter_{counter_name}", self.event_counters[counter_name])
        return self.event_counters[counter_name]
    
    def get_counter(self, counter_name: str) -> int:
        return self.event_counters.get(counter_name, 0)
    
    def check_condition(self, condition_name: str, target_value: int) -> bool:
        current = self.get_counter(condition_name)
        if current >= target_value:
            self.trigger_event(f"condition_met_{condition_name}", current)
            return True
        return False


class GameState:
    def __init__(self):
        self.suspicion_system = SuspicionSystem()
        self.event_system = EventSystem()
        
        self.current_scene = "intro"
        self.current_chapter = 1
        self.solved_puzzles: List[str] = []
        self.collected_clues: List[str] = []
        self.dialog_history: List[str] = []
        
        self.game_over = False
        self.game_won = False
        self.show_dialog = False
        self.current_dialog_id: Optional[str] = None
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        self.event_system.register_event("counter_solved_puzzles", self._on_puzzle_solved)
        self.suspicion_system.on_max_suspicion = self._on_max_suspicion
    
    def _on_puzzle_solved(self, count: int):
        if count >= 1 and self.current_chapter < 2:
            self.current_chapter = 2
            self.current_scene = "chapter2"
            self.event_system.trigger_event("scene_change", "chapter2")
        
        if count >= 2 and self.current_chapter < 3:
            self.current_chapter = 3
            self.current_scene = "chapter3"
            self.event_system.trigger_event("scene_change", "chapter3")
        
        if count >= 3:
            self.game_won = True
            self.event_system.trigger_event("game_win")
    
    def _on_max_suspicion(self):
        self.game_over = True
        self.event_system.trigger_event("game_over")
    
    def solve_puzzle(self, puzzle_id: str) -> bool:
        if puzzle_id not in self.solved_puzzles:
            self.solved_puzzles.append(puzzle_id)
            self.event_system.increment_counter("solved_puzzles")
            return True
        return False
    
    def collect_clue(self, clue_id: str) -> bool:
        if clue_id not in self.collected_clues:
            self.collected_clues.append(clue_id)
            self.event_system.increment_counter("collected_clues")
            return True
        return False
    
    def make_mistake(self, reason: str = "") -> bool:
        return self.suspicion_system.increase_suspicion(reason)
    
    def start_dialog(self, dialog_id: str):
        self.current_dialog_id = dialog_id
        self.show_dialog = True
    
    def end_dialog(self):
        self.show_dialog = False
        self.current_dialog_id = None
    
    def get_progress(self) -> Dict:
        return {
            'chapter': self.current_chapter,
            'solved_puzzles': len(self.solved_puzzles),
            'total_puzzles': 3,
            'collected_clues': len(self.collected_clues),
            'total_clues': 4,
            'suspicion': self.suspicion_system.suspicion_level,
            'max_suspicion': self.suspicion_system.max_suspicion,
        }
