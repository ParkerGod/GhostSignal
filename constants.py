SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

COLORS = {
    'background': (15, 15, 25),
    'panel': (30, 30, 45),
    'text': (220, 220, 230),
    'highlight': (100, 200, 255),
    'warning': (255, 100, 100),
    'success': (100, 255, 150),
    'dim': (100, 100, 120),
    'inventory_bg': (20, 20, 35),
    'log_bg': (25, 25, 40),
    'frequency_bar': (50, 150, 200),
    'frequency_target': (255, 200, 50),
}

PUZZLES = {
    'radio_frequency': {
        'name': '神秘频率',
        'description': '调整收音机频率接收神秘信号',
        'target_range': (87.5, 88.5),
        'default_frequency': 90.0,
        'hint': '信号似乎在87-89MHz之间...',
        'success_text': '【信号接收成功】\n一个沙哑的声音从杂音中浮现："他们在...旧钟楼...午夜..."',
        'fail_text': '【信号中断】\n只有刺耳的杂音...',
    },
    'decoder_dial': {
        'name': '解码器旋钮',
        'description': '旋转解码器旋钮对齐信号',
        'target_range': (42.0, 43.0),
        'default_frequency': 45.0,
        'hint': '解码手册提到关键数值在42附近',
        'success_text': '【解码成功】\n信号解码完成："失踪者的名字...以M开头..."',
        'fail_text': '【解码失败】\n信号无法解析...',
    },
    'antenna_tuner': {
        'name': '天线调谐器',
        'description': '调整天线增益捕捉微弱信号',
        'target_range': (66.0, 67.5),
        'default_frequency': 70.0,
        'hint': '微弱信号需要精确的天线角度',
        'success_text': '【信号增强成功】\n"我看到了...他们在地下...不要相信..."',
        'fail_text': '【信号过载】\n天线反馈导致信号丢失...',
    },
}

STORY_TEXTS = {
    'intro': {
        'title': '第一章：深夜来电',
        'content': [
            '午夜时分，电台控制室的灯光昏暗闪烁。',
            '你是一名深夜值班的技术员，负责监控各种信号。',
            '今晚，一个奇怪的频率开始出现在你的设备上...',
            '这个频率不属于任何已知的广播站。',
        ],
    },
    'chapter2': {
        'title': '第二章：消失的声音',
        'content': [
            '随着你成功解码第一个信号，更多的线索浮现。',
            '小镇上已经失踪了三个人。',
            '所有线索都指向一个古老的传说...',
        ],
    },
    'chapter3': {
        'title': '第三章：真相',
        'content': [
            '你终于拼凑出了真相。',
            '那些信号来自另一个维度...',
            '现在，你必须做出选择。',
        ],
    },
    'ending_good': {
        'title': '结局：信号连接',
        'content': [
            '你成功解开了所有谜题。',
            '失踪者的灵魂得到了安息。',
            '电台恢复了平静，但你永远不会忘记这个夜晚。',
        ],
    },
    'ending_bad': {
        'title': '结局：信号中断',
        'content': [
            '太多的错误触发了警报。',
            '神秘信号突然消失...',
            '你永远无法知道真相了。',
        ],
    },
}

DIALOG_OPTIONS = {
    'first_contact': {
        'prompt': '信号中传来模糊的声音，你选择如何回应？',
        'options': [
            {'text': '尝试调整频率', 'correct': True, 'response': '你小心翼翼地调整频率...'},
            {'text': '忽略这个信号', 'correct': False, 'response': '你错过了重要的线索...'},
            {'text': '记录信号特征', 'correct': True, 'response': '你仔细记录了信号的波形特征...'},
        ],
    },
    'mysterious_voice': {
        'prompt': '声音说："你能听到我吗？"你选择：',
        'options': [
            {'text': '"我能听到，你是谁？"', 'correct': True, 'response': '"我是...被困在...这里的人..."'},
            {'text': '"这不是真的..."', 'correct': False, 'response': '信号开始变得不稳定...'},
            {'text': '保持沉默倾听', 'correct': True, 'response': '你听到了更多细节...'},
        ],
    },
    'final_choice': {
        'prompt': '你发现了真相的入口，选择：',
        'options': [
            {'text': '继续深入调查', 'correct': True, 'response': '你决定揭开真相...'},
            {'text': '关闭电台离开', 'correct': False, 'response': '你选择了放弃...'},
        ],
    },
}

CLUES = {
    'old_paper': {
        'name': '泛黄的纸条',
        'description': '一张泛黄的纸条，上面写着："频率87.5，午夜，钟楼"',
        'icon': 'paper',
    },
    'recording': {
        'name': '录音片段',
        'description': '一段模糊的录音，提到"地下通道"',
        'icon': 'tape',
    },
    'photo': {
        'name': '模糊的照片',
        'description': '一张模糊的照片，显示一个奇怪的符号',
        'icon': 'photo',
    },
    'key': {
        'name': '生锈的钥匙',
        'description': '一把生锈的钥匙，上面刻着"M"',
        'icon': 'key',
    },
}

INTERACTABLES = {
    'radio': {
        'name': '老式收音机',
        'rect': (100, 150, 200, 150),
        'type': 'frequency',
        'puzzle_id': 'radio_frequency',
        'description': '一台老式收音机，旋钮已经磨损',
    },
    'decoder': {
        'name': '信号解码器',
        'rect': (350, 200, 180, 120),
        'type': 'frequency',
        'puzzle_id': 'decoder_dial',
        'description': '专业的信号解码设备',
    },
    'antenna': {
        'name': '天线控制台',
        'rect': (600, 180, 200, 140),
        'type': 'frequency',
        'puzzle_id': 'antenna_tuner',
        'description': '控制外部天线的方向和增益',
    },
    'paper_stack': {
        'name': '文件堆',
        'rect': (900, 400, 150, 100),
        'type': 'clue',
        'clue_id': 'old_paper',
        'description': '一堆旧文件和纸条',
    },
    'tape_recorder': {
        'name': '录音机',
        'rect': (200, 450, 120, 80),
        'type': 'clue',
        'clue_id': 'recording',
        'description': '一台老式磁带录音机',
    },
    'photo_frame': {
        'name': '相框',
        'rect': (500, 500, 100, 80),
        'type': 'clue',
        'clue_id': 'photo',
        'description': '墙上挂着一个旧相框',
    },
    'drawer': {
        'name': '抽屉',
        'rect': (800, 550, 120, 80),
        'type': 'clue',
        'clue_id': 'key',
        'description': '一个半开的抽屉',
    },
}

SCENES = {
    'intro': {
        'background_color': (15, 15, 25),
        'time_of_day': 'midnight',
        'ambient_text': '控制室 - 午夜',
    },
    'chapter2': {
        'background_color': (20, 18, 30),
        'time_of_day': 'late_night',
        'ambient_text': '控制室 - 深夜',
    },
    'chapter3': {
        'background_color': (25, 15, 35),
        'time_of_day': 'dawn',
        'ambient_text': '控制室 - 黎明前',
    },
}

MAX_SUSPICION = 5
LOG_RETENTION_SECONDS = 300
INVENTORY_SLOT_SIZE = 60
INVENTORY_PADDING = 10
