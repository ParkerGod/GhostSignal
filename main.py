# -*- coding: utf-8 -*-
"""
幽灵信号 - 主游戏模块
整合所有子系统的完整游戏实现
"""

import pygame
import sys
import random
from typing import Optional

# 导入自定义模块
from game_data import (STORY_TEXTS, PUZZLE_SOLUTIONS, ITEMS_DATA, 
                       INTERACTION_HINTS, SCENE_CONFIGS)
from interactable import (Interactable, RadioKnob, ClickableButton, 
                         CollectablePaper, FrequencyTuner, InteractiveDesk, 
                         LockedBox)
from inventory import InventorySystem, CombinationSystem
from renderer import LayeredRenderer
from suspicion_system import SuspicionSystem, FailureEnding, SuccessEnding
from scene_manager import EventManager, SceneManager, ProgressTracker, GameEvent
from log_system import LogSystem, LogViewer, LogNotification, LogEntryType


class GhostSignalGame:
    """
    幽灵信号游戏主类
    整合所有游戏系统
    """
    
    def __init__(self):
        # 初始化 Pygame
        pygame.init()
        pygame.font.init()
        
        # 屏幕设置
        self.SCREEN_WIDTH = 1024
        self.SCREEN_HEIGHT = 768
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("幽灵信号 - Ghost Signal")
        
        # 时钟
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        # 游戏状态
        self.running = True
        self.game_started = False
        self.game_ended = False
        
        # 初始化所有系统
        self._init_systems()
        
        # 当前选中的频率调节器
        self.selected_tuner: Optional[FrequencyTuner] = None
        
        # 频率调整惩罚冷却时间（毫秒）
        self.frequency_penalty_cooldown = 2000
        self.last_frequency_penalty_time = 0
        
        # 故事文本索引
        self.story_index = 0
        self.showing_story = True
        self.current_story_texts = STORY_TEXTS["intro"]
        
    def _init_systems(self):
        """初始化所有游戏系统"""
        # 事件管理器
        self.event_manager = EventManager()
        
        # 分层渲染器
        self.renderer = LayeredRenderer(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 物品栏系统
        self.inventory = InventorySystem(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.inventory.on_item_selected = self._on_item_selected
        self.inventory.on_item_used = self._on_item_used
        
        # 组合系统
        self.combination_system = CombinationSystem()
        
        # 怀疑度系统
        self.suspicion_system = SuspicionSystem()
        self.suspicion_system.on_failure = self._on_failure
        self.suspicion_system.on_warning = self._on_suspicion_warning
        self.suspicion_system.on_value_changed = self._on_suspicion_changed
        
        # 结局管理器
        self.failure_ending = FailureEnding(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.success_ending = SuccessEnding(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 场景管理器
        self.scene_manager = SceneManager(self.event_manager)
        self.scene_manager.on_scene_changed = self._on_scene_changed
        
        # 进度追踪器
        self.progress_tracker = ProgressTracker(self.event_manager)
        
        # 日志系统
        self.log_system = LogSystem()
        self.log_system.on_new_entry = self._on_new_log_entry
        
        # 日志查看器
        self.log_viewer = LogViewer(
            self.SCREEN_WIDTH // 4,
            self.SCREEN_HEIGHT // 4,
            self.SCREEN_WIDTH // 2,
            self.SCREEN_HEIGHT // 2
        )
        self.log_viewer.set_log_system(self.log_system)
        
        # 日志通知
        self.log_notification = LogNotification(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 订阅事件
        self._subscribe_events()
        
    def _subscribe_events(self):
        """订阅游戏事件"""
        self.event_manager.subscribe("puzzle_solved", self._handle_puzzle_solved)
        self.event_manager.subscribe("item_collected", self._handle_item_collected)
        self.event_manager.subscribe("scene_changed", self._handle_scene_changed)
        self.event_manager.subscribe("progress_updated", self._handle_progress_updated)
        
    def _on_scene_changed(self, scene_id: str):
        """场景切换回调"""
        self._setup_scene_objects(scene_id)
        self.log_system.add_system_log(f"进入场景: {SCENE_CONFIGS[scene_id]['name']}")
        
    def _on_item_selected(self, item):
        """物品选择回调"""
        self.renderer.show_hint(f"选中了: {item.name}", 2000)
        self.log_system.add_item_log(f"选中物品: {item.name}", item.item_id)
        
    def _on_item_used(self, item, target_id: str) -> bool:
        """物品使用回调"""
        self.log_system.add_interaction_log(
            f"尝试使用 {item.name} 在 {target_id}", 
            target_id
        )
        return True
        
    def _on_failure(self):
        """怀疑度达到阈值，触发失败结局"""
        self.failure_ending.start()
        self.game_ended = True
        self.log_system.add_warning_log("怀疑度达到临界值！")
        
    def _on_suspicion_warning(self):
        """怀疑度警告"""
        self.renderer.show_hint("警告：怀疑度即将达到临界值！", 3000)
        self.log_system.add_warning_log("怀疑度警告")
        
    def _on_suspicion_changed(self, value: int):
        """怀疑度变化回调"""
        self.renderer.update_suspicion(value)
        
    def _on_new_log_entry(self, entry):
        """新日志条目回调"""
        self.log_notification.show_notification(entry)
        self.renderer.add_log(entry.message)
        
    def _handle_puzzle_solved(self, event: GameEvent):
        """处理谜题解决事件"""
        puzzle_id = event.data.get("puzzle_id")
        self.log_system.add_puzzle_log(f"谜题已解决: {puzzle_id}", puzzle_id)
        self.suspicion_system.on_correct_action()
        
        # 检查是否完成所有谜题
        if self.progress_tracker.get_solved_count() >= 4:
            self._trigger_success_ending()
            
    def _handle_item_collected(self, event: GameEvent):
        """处理物品收集事件"""
        item_id = event.data.get("item_id")
        if item_id:
            self.inventory.add_item(item_id)
            item_data = ITEMS_DATA.get(item_id, {})
            item_name = item_data.get("name", item_id)
            self.renderer.show_hint(f"获得物品: {item_name}", 3000)
            self.log_system.add_item_log(f"获得物品: {item_name}", item_id)
            
    def _handle_scene_changed(self, event: GameEvent):
        """处理场景切换事件"""
        to_scene = event.data.get("to")
        solved = event.data.get("solved_puzzles", 0)
        self.log_system.add_system_log(f"场景切换至: {to_scene}, 已解决谜题: {solved}")
        
    def _handle_progress_updated(self, event: GameEvent):
        """处理进度更新事件"""
        solved = event.data.get("solved", 0)
        total = event.data.get("total", 4)
        self.log_system.add_system_log(f"进度更新: {solved}/{total}")
        
    def _trigger_success_ending(self):
        """触发成功结局"""
        self.success_ending.start()
        self.game_ended = True
        self.log_system.add_story_log("游戏完成！")
        
    def _setup_scene_objects(self, scene_id: str):
        """设置场景对象"""
        # 清空现有对象
        self.renderer.clear_objects()
        
        # 创建场景对象
        objects = self.scene_manager.create_scene_objects(scene_id)
        
        # 设置回调并添加到渲染器
        for obj in objects:
            obj.set_callbacks(
                on_click=self._on_object_clicked,
                on_hover=self._on_object_hovered
            )
            self.renderer.add_object(obj)
            
    def _on_object_clicked(self, obj: Interactable):
        """对象点击处理"""
        # 检查是否使用物品
        selected_item_id = self.inventory.get_selected_item_id()
        
        if selected_item_id and isinstance(obj, LockedBox):
            # 尝试解锁
            if obj.try_unlock(selected_item_id):
                self.renderer.show_hint("锁打开了！", 3000)
                self.inventory.deselect_all()
                self.event_manager.emit("puzzle_solved", {"puzzle_id": "locked_box"})
                self.log_system.add_item_log("使用钥匙打开锁盒", selected_item_id)
                return
            else:
                self.renderer.show_hint("这把钥匙打不开这个锁", 2000)
                self.suspicion_system.on_wrong_combination()
                return
                
        # 处理频率调节器
        if isinstance(obj, FrequencyTuner):
            self.selected_tuner = obj
            self.renderer.show_hint("使用鼠标滚轮微调频率", 3000)
            
        # 处理可收集纸张
        if isinstance(obj, CollectablePaper) and not obj.collected:
            obj.on_click()
            if obj.collected:
                self.event_manager.emit("item_collected", {"item_id": obj.item_id})
                
        # 处理按钮
        if isinstance(obj, ClickableButton):
            if obj.name == "发送信号":
                self._check_final_solution()
                
        self.log_system.add_interaction_log(f"点击了 {obj.name}", obj.name)
        
    def _on_object_hovered(self, obj: Interactable):
        """对象悬停处理"""
        hint = INTERACTION_HINTS.get(f"hover_{obj.name}", f"{obj.name}")
        self.renderer.show_hint(hint, 1500)
        
    def _check_final_solution(self):
        """检查最终解决方案"""
        # 检查是否收集了所有必要物品
        required_items = ["old_newspaper", "frequency_table", "morse_codebook"]
        has_all = all(self.inventory.has_item(item) for item in required_items)
        
        if has_all:
            self._trigger_success_ending()
        else:
            self.renderer.show_hint("还需要收集更多线索...", 2000)
            self.suspicion_system.on_wrong_combination()
            
    def _check_frequency_solution(self):
        """检查频率谜题解决方案"""
        if self.selected_tuner:
            target = PUZZLE_SOLUTIONS["frequency_puzzle"]["target_frequency"]
            tolerance = PUZZLE_SOLUTIONS["frequency_puzzle"]["tolerance"]
            
            current_freq = self.selected_tuner.frequency
            diff = abs(current_freq - target)
            
            if diff <= tolerance:
                # 频率正确，解决谜题
                self.renderer.show_hint("频率对准了！信号清晰了！", 3000)
                self.event_manager.emit("puzzle_solved", {"puzzle_id": "frequency_puzzle"})
                self.suspicion_system.on_correct_action()
                self.current_story_texts = STORY_TEXTS["frequency_found"]
                self.showing_story = True
                self.story_index = 0
            elif diff <= tolerance * 3:
                # 接近目标，给予提示但不惩罚
                self.renderer.show_hint("频率接近了...再微调一下", 1500)
            else:
                # 偏离较远，检查冷却时间后给予惩罚
                current_time = pygame.time.get_ticks()
                if current_time - self.last_frequency_penalty_time >= self.frequency_penalty_cooldown:
                    self.renderer.show_hint("频率偏离太远，信号混乱...", 2000)
                    self.suspicion_system.on_wrong_frequency()
                    self.last_frequency_penalty_time = current_time
                
    def handle_events(self):
        """处理输入事件"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
                
            # 处理结局事件
            if self.failure_ending.is_showing:
                if self.failure_ending.handle_event(event):
                    self.reset_game()
                    continue
                    
            if self.success_ending.is_showing:
                if self.success_ending.handle_event(event):
                    self.reset_game()
                    continue
                    
            # 处理日志查看器事件
            if self.log_viewer.handle_event(event):
                continue
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.log_viewer.toggle_visibility()
                elif event.key == pygame.K_SPACE:
                    if self.showing_story:
                        self.story_index += 1
                        if self.story_index >= len(self.current_story_texts):
                            self.showing_story = False
                            if not self.game_started:
                                self.game_started = True
                                self._start_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    # 检查是否点击物品栏
                    if self.inventory.handle_click(mouse_pos):
                        continue
                    mouse_clicked = True
                    
                elif event.button == 4:  # 滚轮上
                    if self.selected_tuner:
                        self.selected_tuner.adjust_frequency(1)
                        self._check_frequency_solution()
                        
                elif event.button == 5:  # 滚轮下
                    if self.selected_tuner:
                        self.selected_tuner.adjust_frequency(-1)
                        self._check_frequency_solution()
                        
        # 更新渲染器
        dt = self.clock.tick(self.FPS)
        self.renderer.update(mouse_pos, mouse_clicked, dt)
        
        # 更新结局动画
        self.failure_ending.update(dt)
        self.success_ending.update(dt)
        
        # 更新日志通知
        self.log_notification.update(dt)
        
        # 处理事件队列
        self.event_manager.process_events()
        
    def _start_game(self):
        """开始游戏"""
        self.scene_manager.switch_scene("scene_1")
        self.log_system.add_system_log("游戏开始")
        self.log_system.add_story_log("深夜，无线电接收站...")
        
    def reset_game(self):
        """重置游戏"""
        self.game_started = False
        self.game_ended = False
        self.showing_story = True
        self.story_index = 0
        self.current_story_texts = STORY_TEXTS["intro"]
        
        # 重置所有系统
        self.suspicion_system.reset()
        self.scene_manager.reset()
        self.progress_tracker.reset()
        self.inventory = InventorySystem(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        self.inventory.on_item_selected = self._on_item_selected
        self.inventory.on_item_used = self._on_item_used
        self.log_system.clear()
        self.renderer.clear_objects()
        self.failure_ending.reset()
        self.success_ending.reset()
        
        # 重置惩罚冷却时间
        self.last_frequency_penalty_time = 0
        
    def update(self):
        """更新游戏逻辑"""
        # 清理过期日志
        self.log_system.clear_old_entries()
        
    def draw(self):
        """渲染游戏画面"""
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 绘制结局
        if self.failure_ending.is_showing:
            self.failure_ending.draw(self.screen)
            pygame.display.flip()
            return
            
        if self.success_ending.is_showing:
            self.success_ending.draw(self.screen)
            pygame.display.flip()
            return
        
        # 绘制游戏场景
        if self.game_started:
            # 更新背景颜色
            bg_color = self.scene_manager.get_current_bg_color()
            self.renderer.set_background_color(bg_color)
            
            # 渲染所有层
            self.renderer.render(self.screen)
            
            # 绘制物品栏
            self.inventory.draw(self.screen)
            
            # 绘制物品栏提示
            mouse_pos = pygame.mouse.get_pos()
            self.inventory.draw_tooltip(self.screen, mouse_pos)
            
        else:
            # 显示开始界面
            self._draw_start_screen()
            
        # 绘制故事文本
        if self.showing_story:
            self._draw_story_text()
            
        # 绘制日志查看器
        self.log_viewer.draw(self.screen)
        
        # 绘制日志通知
        self.log_notification.draw(self.screen)
        
        # 更新显示
        pygame.display.flip()
        
    def _draw_start_screen(self):
        """绘制开始界面"""
        # 背景
        self.screen.fill((10, 10, 25))
        
        # 标题
        font = pygame.font.SysFont("simhei", 48)
        title = font.render("幽灵信号", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # 副标题
        sub_font = pygame.font.SysFont("simhei", 24)
        subtitle = sub_font.render("Ghost Signal", True, (150, 150, 150))
        subtitle_rect = subtitle.get_rect(center=(self.SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 提示
        hint_font = pygame.font.SysFont("simhei", 18)
        hint = hint_font.render("按空格键开始游戏", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.SCREEN_WIDTH // 2, 500))
        self.screen.blit(hint, hint_rect)
        
    def _draw_story_text(self):
        """绘制故事文本"""
        if self.story_index < len(self.current_story_texts):
            # 半透明背景
            overlay = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            # 文本框
            box_width = 700
            box_height = 150
            box_x = (self.SCREEN_WIDTH - box_width) // 2
            box_y = (self.SCREEN_HEIGHT - box_height) // 2
            
            pygame.draw.rect(self.screen, (30, 30, 50), 
                           (box_x, box_y, box_width, box_height))
            pygame.draw.rect(self.screen, (150, 150, 200), 
                           (box_x, box_y, box_width, box_height), 3)
            
            # 文本
            font = pygame.font.SysFont("simhei", 20)
            text = self.current_story_texts[self.story_index]
            
            # 自动换行
            words = text
            lines = []
            current_line = ""
            
            for char in words:
                test_line = current_line + char
                if font.size(test_line)[0] < box_width - 60:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
                
            # 绘制每一行
            line_height = 28
            start_y = box_y + 30
            for i, line in enumerate(lines):
                text_surface = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (box_x + 30, start_y + i * line_height))
                
            # 继续提示
            hint_font = pygame.font.SysFont("simhei", 16)
            hint = hint_font.render("按空格键继续...", True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(self.SCREEN_WIDTH // 2, box_y + box_height - 20))
            self.screen.blit(hint, hint_rect)
            
    def run(self):
        """主游戏循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
            
        pygame.quit()
        sys.exit()


def main():
    """游戏入口"""
    game = GhostSignalGame()
    game.run()


if __name__ == "__main__":
    main()
