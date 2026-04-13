# -*- coding: utf-8 -*-
"""
幽灵信号 - 场景管理器模块
采用事件驱动模型，当特定变量（如 solved_puzzles）达到指定数量时
自动修改主循环中的场景背景图以表现时间流逝
"""

import pygame
from typing import Dict, List, Optional, Callable, Any
from game_data import SCENE_CONFIGS, STORY_TEXTS, PUZZLE_SOLUTIONS
from interactable import (Interactable, RadioKnob, ClickableButton, 
                         CollectablePaper, FrequencyTuner, InteractiveDesk, 
                         LockedBox)


class GameEvent:
    """游戏事件基类"""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None):
        self.event_type = event_type
        self.data = data or {}
        self.timestamp = pygame.time.get_ticks()


class EventManager:
    """
    事件管理器
    处理游戏内的事件分发和监听
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[Callable]] = {}
        self.event_queue: List[GameEvent] = []
        
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
        
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self.listeners:
            if callback in self.listeners[event_type]:
                self.listeners[event_type].remove(callback)
                
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """触发事件"""
        event = GameEvent(event_type, data)
        self.event_queue.append(event)
        
    def process_events(self):
        """处理所有待处理的事件"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            
            if event.event_type in self.listeners:
                for callback in self.listeners[event.event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"事件处理错误: {e}")


class Scene:
    """场景类"""
    
    def __init__(self, scene_id: str, config: Dict):
        self.scene_id = scene_id
        self.name = config.get("name", "未知场景")
        self.bg_color = config.get("bg_color", (20, 20, 40))
        self.solved_count_required = config.get("solved_count_required", 0)
        self.object_names = config.get("objects", [])
        
        # 场景中的对象
        self.objects: List[Interactable] = []
        
        # 场景状态
        self.visited = False
        self.completed = False
        
    def add_object(self, obj: Interactable):
        """添加对象到场景"""
        self.objects.append(obj)
        
    def remove_object(self, obj: Interactable):
        """从场景移除对象"""
        if obj in self.objects:
            self.objects.remove(obj)
            
    def clear_objects(self):
        """清空所有对象"""
        self.objects.clear()
        
    def update(self, mouse_pos, mouse_clicked: bool = False):
        """更新场景中的对象"""
        for obj in self.objects:
            obj.update(mouse_pos, mouse_clicked)
            
    def draw(self, surface: pygame.Surface):
        """绘制场景"""
        # 绘制背景色
        surface.fill(self.bg_color)
        
        # 绘制所有对象
        for obj in self.objects:
            obj.draw(surface)


class SceneManager:
    """
    场景管理器
    管理游戏中的所有场景和场景切换
    """
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.current_scene_id: str = ""
        
        # 游戏进度
        self.solved_puzzles = 0
        self.total_puzzles = 4
        
        # 场景切换回调
        self.on_scene_changed: Optional[Callable[[str], None]] = None
        
        # 初始化场景
        self._init_scenes()
        
        # 订阅事件
        self._subscribe_events()
        
    def _init_scenes(self):
        """初始化所有场景"""
        for scene_id, config in SCENE_CONFIGS.items():
            scene = Scene(scene_id, config)
            self.scenes[scene_id] = scene
            
    def _subscribe_events(self):
        """订阅相关事件"""
        self.event_manager.subscribe("puzzle_solved", self._on_puzzle_solved)
        self.event_manager.subscribe("item_collected", self._on_item_collected)
        
    def _on_puzzle_solved(self, event: GameEvent):
        """处理谜题解决事件"""
        self.solved_puzzles += 1
        
        # 检查是否需要切换场景
        self._check_scene_transition()
        
        # 触发进度更新事件
        self.event_manager.emit("progress_updated", {
            "solved": self.solved_puzzles,
            "total": self.total_puzzles
        })
        
    def _on_item_collected(self, event: GameEvent):
        """处理物品收集事件"""
        item_id = event.data.get("item_id")
        # 可以在这里添加物品收集后的逻辑
        
    def _check_scene_transition(self):
        """检查是否需要切换场景"""
        # 根据已解决谜题数量决定场景
        if self.solved_puzzles >= 3:
            new_scene_id = "scene_4"
        elif self.solved_puzzles >= 2:
            new_scene_id = "scene_3"
        elif self.solved_puzzles >= 1:
            new_scene_id = "scene_2"
        else:
            new_scene_id = "scene_1"
            
        # 如果场景变化，切换场景
        if new_scene_id != self.current_scene_id:
            self.switch_scene(new_scene_id)
            
    def switch_scene(self, scene_id: str):
        """切换到指定场景"""
        if scene_id not in self.scenes:
            print(f"场景 {scene_id} 不存在")
            return False
            
        # 保存当前场景
        if self.current_scene:
            self.current_scene.visited = True
            
        # 切换场景
        self.current_scene = self.scenes[scene_id]
        self.current_scene_id = scene_id
        self.current_scene.visited = True
        
        # 触发场景切换事件
        self.event_manager.emit("scene_changed", {
            "from": self.current_scene_id,
            "to": scene_id,
            "solved_puzzles": self.solved_puzzles
        })
        
        # 回调
        if self.on_scene_changed:
            self.on_scene_changed(scene_id)
            
        return True
        
    def get_current_scene(self) -> Optional[Scene]:
        """获取当前场景"""
        return self.current_scene
        
    def get_current_bg_color(self) -> tuple:
        """获取当前场景背景色"""
        if self.current_scene:
            return self.current_scene.bg_color
        return (20, 20, 40)
        
    def get_progress_percentage(self) -> float:
        """获取游戏进度百分比"""
        return self.solved_puzzles / self.total_puzzles
        
    def reset(self):
        """重置场景管理器"""
        self.solved_puzzles = 0
        self.current_scene = None
        self.current_scene_id = ""
        
        # 重置所有场景
        for scene in self.scenes.values():
            scene.visited = False
            scene.completed = False
            scene.clear_objects()
            
    def create_scene_objects(self, scene_id: str) -> List[Interactable]:
        """
        为指定场景创建交互对象
        返回对象列表
        """
        objects = []
        
        if scene_id == "scene_1":
            # 场景1：无线电室 - 深夜
            # 书桌
            desk = InteractiveDesk(200, 300, 300, 150, "书桌")
            objects.append(desk)
            
            # 无线电设备
            radio = FrequencyTuner(250, 200, 200, 40, "无线电")
            objects.append(radio)
            
            # 旧报纸
            newspaper = CollectablePaper(220, 280, 60, 80, "旧报纸", "old_newspaper")
            objects.append(newspaper)
            
            # 台灯
            lamp = ClickableButton(450, 250, 40, 60, "台灯")
            objects.append(lamp)
            
        elif scene_id == "scene_2":
            # 场景2：无线电室 - 黎明
            desk = InteractiveDesk(200, 300, 300, 150, "书桌")
            objects.append(desk)
            
            radio = FrequencyTuner(250, 200, 200, 40, "无线电")
            objects.append(radio)
            
            # 频率表
            freq_table = CollectablePaper(350, 280, 60, 80, "频率表", "frequency_table")
            objects.append(freq_table)
            
            # 锁盒
            locked_box = LockedBox(400, 350, 80, 60, "锁盒", "strange_key")
            objects.append(locked_box)
            
        elif scene_id == "scene_3":
            # 场景3：无线电室 - 日出
            desk = InteractiveDesk(200, 300, 300, 150, "书桌")
            objects.append(desk)
            
            radio = FrequencyTuner(250, 200, 200, 40, "无线电")
            objects.append(radio)
            
            # 摩斯密码本
            codebook = CollectablePaper(280, 280, 60, 80, "密码本", "morse_codebook")
            objects.append(codebook)
            
            # 消息记录板
            message_pad = ClickableButton(400, 320, 100, 80, "记录板")
            objects.append(message_pad)
            
        elif scene_id == "scene_4":
            # 场景4：无线电室 - 清晨
            desk = InteractiveDesk(200, 300, 300, 150, "书桌")
            objects.append(desk)
            
            radio = FrequencyTuner(250, 200, 200, 40, "无线电")
            objects.append(radio)
            
            # 最终交互按钮
            final_button = ClickableButton(300, 350, 120, 50, "发送信号", "发送")
            objects.append(final_button)
            
        return objects


class ProgressTracker:
    """
    进度追踪器
    跟踪游戏进度并触发相应事件
    """
    
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager
        
        # 谜题状态
        self.puzzle_states = {
            "frequency_puzzle": False,
            "newspaper_puzzle": False,
            "frequency_table_puzzle": False,
            "morse_code_puzzle": False
        }
        
        # 收集的物品
        self.collected_items: List[str] = []
        
        # 订阅事件
        self._subscribe_events()
        
    def _subscribe_events(self):
        """订阅事件"""
        self.event_manager.subscribe("puzzle_solved", self._handle_puzzle_solved)
        self.event_manager.subscribe("item_collected", self._handle_item_collected)
        
    def _handle_puzzle_solved(self, event: GameEvent):
        """处理谜题解决"""
        puzzle_id = event.data.get("puzzle_id")
        if puzzle_id and puzzle_id in self.puzzle_states:
            self.puzzle_states[puzzle_id] = True
            
    def _handle_item_collected(self, event: GameEvent):
        """处理物品收集"""
        item_id = event.data.get("item_id")
        if item_id and item_id not in self.collected_items:
            self.collected_items.append(item_id)
            
    def is_puzzle_solved(self, puzzle_id: str) -> bool:
        """检查谜题是否已解决"""
        return self.puzzle_states.get(puzzle_id, False)
        
    def has_item(self, item_id: str) -> bool:
        """检查是否拥有某物品"""
        return item_id in self.collected_items
        
    def get_solved_count(self) -> int:
        """获取已解决谜题数量"""
        return sum(1 for solved in self.puzzle_states.values() if solved)
        
    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        return self.get_solved_count() / len(self.puzzle_states)
        
    def reset(self):
        """重置进度"""
        for key in self.puzzle_states:
            self.puzzle_states[key] = False
        self.collected_items.clear()
        
    def get_state(self) -> Dict:
        """获取当前状态"""
        return {
            "puzzle_states": self.puzzle_states.copy(),
            "collected_items": self.collected_items.copy(),
            "solved_count": self.get_solved_count(),
            "progress": self.get_progress_percentage()
        }
