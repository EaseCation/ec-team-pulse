# -*- coding: utf-8 -*-

class SessionConfigFormatError(Exception):
    pass

def check_session_config(config):
    required_keys = {
        "entity_whitelist": list,
        "entity_blacklist": list,
        "mark_type_limit": dict,
        "show_distance_pixels": int,
        "mark_index_single_click": int,
        "mark_index_double_click": int,
        "marks": list
    }

    for key, expected_type in required_keys.items():
        if key not in config:
            raise SessionConfigFormatError("缺少必要的键: {}".format(key))
        if not isinstance(config[key], expected_type):
            raise SessionConfigFormatError("键 '{}' 应该是类型 {}".format(key, expected_type.__name__))

    for mark in config["marks"]:
        if not isinstance(mark, dict):
            raise SessionConfigFormatError("每个mark都应该是一个字典")
        required_mark_keys = {
            "type": str,
            "name": str,
            "color": list,
            "texture": str,
            "duration": int,
            "sound": (dict, list)
        }
        for key, expected_type in required_mark_keys.items():
            if key not in mark:
                raise SessionConfigFormatError("标记中缺少必要的键: {}".format(key))
            if not isinstance(mark[key], expected_type):
                raise SessionConfigFormatError("标记中的键 '{}' 应该是类型 {}".format(key, expected_type.__name__))


class InteractionConfigFormatError(Exception):
    pass

def check_interaction_config(config):
    required_keys = {
        "touch_mark_button_offset": list,
        "keyboard_switch": int,
        "gamepad_hold": list
    }

    for key, expected_type in required_keys.items():
        if key not in config:
            raise InteractionConfigFormatError("缺少必要的键: {}".format(key))
        if not isinstance(config[key], expected_type):
            raise InteractionConfigFormatError("键 '{}' 应该是类型 {}".format(key, expected_type.__name__))

    if len(config["touch_mark_button_offset"]) != 2:
        raise InteractionConfigFormatError("键 'touch_mark_button_offset' 应该包含两个浮点数")

    for item in config["touch_mark_button_offset"]:
        if not isinstance(item, (int, float)):
            raise InteractionConfigFormatError("键 'touch_mark_button_offset' 中的每个元素应该是浮点数")

    for item in config["gamepad_hold"]:
        if not isinstance(item, int):
            raise InteractionConfigFormatError("键 'gamepad_hold' 中的每个元素应该是 GamepadKeyType(int) 类型")

    print("配置有效")