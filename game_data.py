# -*- coding: utf-8 -*-
"""
幽灵信号 - 游戏数据常量模块
所有关卡谜题的解法映射和文本数据直接以常量字典形式写在代码中
"""

# ==================== 剧情文本数据 ====================
STORY_TEXTS = {
    "intro": [
        "深夜，你独自坐在无线电接收站...",
        "耳机中传来沙沙的杂音，突然，一个微弱的声音穿透了噪音。",
        "'求救...这里是...北纬...'信号中断了。",
        "你决定调整频率，尝试重新连接这个神秘的信号。"
    ],
    "frequency_found": [
        "频率对准了！那个声音再次响起...",
        "'谢谢你...我被困在...时间循环中...'",
        "'只有你能帮我...找到...三个碎片...'"
    ],
    "first_clue": [
        "'第一个线索...在旧报纸的背面...'",
        "'日期是...信号发出的那一天...'"
    ],
    "second_clue": [
        "'第二个线索...隐藏在频率表中...'",
        "'寻找...重复的数字模式...'"
    ],
    "third_clue": [
        "'最后一个线索...在密码本中...'",
        "'用摩斯电码...解读真相...'"
    ],
    "success_ending": [
        "你成功解开了所有谜题！",
        "'谢谢你...我终于可以安息了...'",
        "信号渐渐消失，留下一阵温暖的静电声。",
        "【结局：灵魂救赎】"
    ],
    "failure_ending": [
        "怀疑度达到临界值...",
        "信号突然变得尖锐刺耳！",
        "'你不值得信任！！！'",
        "无线电冒出青烟，彻底损坏。",
        "【结局：信号中断】"
    ]
}

# ==================== 谜题解法映射 ====================
PUZZLE_SOLUTIONS = {
    "frequency_puzzle": {
        "target_frequency": 142.857,
        "tolerance": 0.5,
        "hint": "调整频率到 142.857 MHz 附近",
        "failure_hint": "频率不对，再试一次"
    },
    "newspaper_puzzle": {
        "target_date": "1945-08-15",
        "clue_item": "old_newspaper",
        "solution": "victory_day",
        "hint": "查看报纸背面的日期标记"
    },
    "frequency_table_puzzle": {
        "pattern": [3, 6, 9, 3, 6, 9],
        "clue_item": "frequency_table",
        "solution": "369_pattern",
        "hint": "寻找重复的数字序列"
    },
    "morse_code_puzzle": {
        "code": "... --- ...",
        "translation": "SOS",
        "clue_item": "morse_codebook",
        "solution": "sos_signal",
        "hint": "用密码本翻译摩斯电码"
    }
}

# ==================== 物品数据 ====================
ITEMS_DATA = {
    "old_newspaper": {
        "name": "旧报纸",
        "description": "1945年8月15日的报纸，背面有奇怪的标记",
        "icon_color": (139, 69, 19),
        "usable_on": ["desk", "radio"]
    },
    "frequency_table": {
        "name": "频率表",
        "description": "记录着各种频率的表格，有些数字被圈起来了",
        "icon_color": (34, 139, 34),
        "usable_on": ["radio", "tuner"]
    },
    "morse_codebook": {
        "name": "摩斯密码本",
        "description": "一本破旧的密码本，用于翻译神秘信号",
        "icon_color": (70, 130, 180),
        "usable_on": ["radio", "message_pad"]
    },
    "strange_key": {
        "name": "奇怪的钥匙",
        "description": "从信号中获得的钥匙，不知道能打开什么",
        "icon_color": (218, 165, 32),
        "usable_on": ["locked_box", "drawer"]
    }
}

# ==================== 场景配置 ====================
SCENE_CONFIGS = {
    "scene_1": {
        "name": "无线电室 - 深夜",
        "bg_color": (20, 20, 40),
        "solved_count_required": 0,
        "objects": ["radio", "desk", "lamp", "paper_stack"]
    },
    "scene_2": {
        "name": "无线电室 - 黎明",
        "bg_color": (40, 30, 50),
        "solved_count_required": 1,
        "objects": ["radio", "desk", "lamp", "frequency_table"]
    },
    "scene_3": {
        "name": "无线电室 - 日出",
        "bg_color": (60, 50, 70),
        "solved_count_required": 2,
        "objects": ["radio", "desk", "morse_codebook", "locked_box"]
    },
    "scene_4": {
        "name": "无线电室 - 清晨",
        "bg_color": (80, 70, 90),
        "solved_count_required": 3,
        "objects": ["radio", "desk", "message_pad"]
    }
}

# ==================== 交互提示文本 ====================
INTERACTION_HINTS = {
    "hover_radio": "无线电接收器 - 点击调整频率",
    "hover_desk": "旧书桌 - 可能藏着线索",
    "hover_lamp": "台灯 - 照亮黑暗",
    "hover_paper": "一叠纸张 - 点击查看",
    "hover_tuner": "频率调节器 - 使用滚轮微调",
    "hover_inventory_item": "点击选择物品，再点击场景使用",
    "frequency_close": "频率接近了...再微调一下",
    "frequency_correct": "频率对准了！信号清晰了！",
    "item_combination_success": "物品组合成功！",
    "item_combination_fail": "这两个物品无法组合使用",
    "suspicion_warning": "怀疑度上升...小心操作",
    "suspicion_critical": "怀疑度临界！再错一次就危险了！"
}

# ==================== 怀疑度配置 ====================
SUSPICION_CONFIG = {
    "initial_value": 0,
    "max_value": 100,
    "failure_threshold": 100,
    "wrong_frequency_penalty": 5,      # 降低频率错误惩罚
    "wrong_combination_penalty": 10,
    "hint_usage_penalty": 3,
    "correct_action_reduction": 10
}

# ==================== 日志配置 ====================
LOG_CONFIG = {
    "max_entries": 50,
    "time_window_minutes": 5,
    "entry_types": ["story", "interaction", "puzzle", "item", "warning"]
}
