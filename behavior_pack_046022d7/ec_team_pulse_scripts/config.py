# -*- coding: utf-8 -*-
from mod.common.minecraftEnum import KeyBoardType, GamepadKeyType

mod_name = 'ECTeamPulse'

server_system_name = 'ECTeamPulseServer'
server_class_path = 'ec_team_pulse_scripts.server.ECTeamPulseServer.ECTeamPulseServer'
client_system_name = 'ECTeamPulseClient'
client_class_path = 'ec_team_pulse_scripts.client.ECTeamPulseClient.ECTeamPulseClient'

mark_point_ui_name = 'MarkPointScreenNode'
mark_point_ui_cls_path = 'ec_team_pulse_scripts.uiScript.MarkPointScreenNode.MarkPointScreenNode'
mark_point_ui_def = 'mark_point.main'

mark_point_ready_ui_name = 'MarkPointReadyScreenNode'
mark_point_ready_ui_cls_path = 'ec_team_pulse_scripts.uiScript.MarkPointReadyScreenNode.MarkPointReadyScreenNode'
mark_point_ready_ui_def = 'mark_point_ready.main'

mark_hud_ui_name = 'MarkHudScreenNode'
mark_hud_ui_cls_path = 'ec_team_pulse_scripts.uiScript.MarkHudScreenNode.MarkHudScreenNode'
mark_hud_ui_def = 'mark_hud.main'

session_config_default = {
    "entity_whitelist": [],
    "entity_blacklist": [],
    "mark_type_limit": {
        "here": 2,
        "danger": 1
    },
    "show_distance_pixels": 20,
    "mark_index_single_click": 0,
    "mark_index_double_click": 1,
    "marks": [
        {
            "type": "here",
            "name": "前往这里",
            "color": [255, 210, 48],
            "texture": "textures/ui/ec_mark/mark_rhombus",
            "duration": 30,
            "sound": {
                "name": "note.bit",
                "volume": 1.0,
                "pitch": 1.5
            }
        },
        {
            "type": "danger",
            "name": "注意这里",
            "color": [250, 50, 50],
            "texture": "textures/ui/ec_mark/mark_rhombus",
            "duration": 10,
            "sound": [
                {
                    "name": "note.pling",
                    "volume": 1.0,
                    "pitch": 2.0
                },
                {
                    "name": "note.bass",
                    "volume": 1.0,
                    "pitch": 1.0
                },
            ]
        }
    ]
}

interaction_config_default = {
    "touch_mark_button_offset": [ -80.0, 40.0 ],
    "keyboard_switch": KeyBoardType.KEY_TAB,
    "gamepad_hold": [GamepadKeyType.KEY_RS]  # 支持同时按下多个按键来触发
}