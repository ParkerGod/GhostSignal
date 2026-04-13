import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'DARK_GRAY': (40, 40, 45),
    'GRAY': (70, 70, 75),
    'LIGHT_GRAY': (120, 120, 125),
    'GREEN': (50, 200, 50),
    'RED': (200, 50, 50),
    'YELLOW': (200, 200, 50),
    'CYAN': (50, 200, 200),
    'DARK_GREEN': (20, 80, 20),
    'AMBER': (255, 191, 0),
    'NIGHT_BLUE': (10, 10, 40),
    'SCANLINE': (0, 255, 0, 30)
}

PUZZLE_SOLUTIONS = {
    'frequency_1': {'target': 88.6, 'tolerance': 0.2, 'reward': 'clue_photo'},
    'frequency_2': {'target': 104.3, 'tolerance': 0.2, 'reward': 'clue_letter'},
    'frequency_3': {'target': 92.1, 'tolerance': 0.2, 'reward': 'final_clue'},
    'combo_photo_radio': {'items': ['clue_photo', 'radio_knob'], 'unlocks': 'dialog_1'},
    'combo_letter_fax': {'items': ['clue_letter', 'fax_machine'], 'unlocks': 'dialog_2'}
}

STORY_TEXT = {
    'intro': [
        "【第0天 23:47】",
        "你坐在午夜电台的控制室里。",
        "雨点敲打着窗户，收音机发出轻微的静电噪音...",
        "突然，一个微弱的信号穿透了杂音。"
    ],
    'frequency_success_1': [
        "信号变得清晰了...",
        "...救救我...他们带走了她...",
        "一张照片从传真机中滑出。"
    ],
    'frequency_success_2': [
        "一个颤抖的声音：",
        "\"湖景路17号...不要相信警长...\"",
        "信号中断了，但你收到了一封匿名信。"
    ],
    'frequency_success_3': [
        "那是...警长的声音！",
        "\"今晚午夜，码头...处理掉最后的证据。\"",
        "你掌握了关键证据！"
    ],
    'combo_photo_reveal': [
        "你将照片对准灯光，发现了一个模糊的车牌...",
        "号码最后三位是：427"
    ],
    'combo_letter_reveal': [
        "信件背面有淡淡的荧光墨水写着：",
        "\"第四个受害者就在灯塔下\""
    ],
    'wrong_choice': [
        "你感觉电话那头的人停顿了一下...",
        "好像，他们知道了什么。"
    ],
    'signal_lost': [
        "=== 信号中断 ===",
        "电话线被切断了。",
        "你听到门外传来脚步声...",
        "GAME OVER"
    ],
    'victory': [
        "=== 真相大白 ===",
        "你将所有证据发送给了州检察官。",
        "警长及其腐败团伙被一网打尽。",
        "失踪的女孩们终于找到了正义。"
    ]
}

ITEM_DATA = {
    'clue_photo': {'name': '神秘照片', 'color': COLORS['WHITE'], 'description': '一张模糊的湖边照片'},
    'clue_letter': {'name': '匿名信', 'color': COLORS['YELLOW'], 'description': '用打字机打出的信件'},
    'final_clue': {'name': '录音带', 'color': COLORS['RED'], 'description': '警长的罪证录音'}
}

BACKGROUNDS = {
    0: {'name': 'night_early', 'color': (15, 15, 35), 'solved_required': 0},
    1: {'name': 'night_mid', 'color': (10, 10, 25), 'solved_required': 1},
    2: {'name': 'night_late', 'color': (5, 5, 15), 'solved_required': 2},
    3: {'name': 'rainy_dawn', 'color': (20, 25, 40), 'solved_required': 3}
}

SUSPICION_THRESHOLD = 5
LOG_MAX_ENTRIES = 50
LOG_DISPLAY_LINES = 10

pygame.font.init()

def get_chinese_font(size):
    font_names = ['microsoftyahei', 'msyh', 'simhei', 'simsun', 'pingfang', 'stkaiti']
    for name in font_names:
        try:
            font = pygame.font.SysFont(name, size)
            test = font.render("测试", True, (255, 255, 255))
            return font
        except:
            continue
    return pygame.font.SysFont(None, size)

FONTS = {
    'small': get_chinese_font(12),
    'normal': get_chinese_font(16),
    'large': get_chinese_font(24),
    'title': get_chinese_font(32)
}
