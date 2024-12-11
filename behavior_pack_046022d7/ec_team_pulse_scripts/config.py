# -*- coding: utf-8 -*-
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
        "here": 1,
        "danger": 1
    },
    "interaction": {
        "touch_mark_button_offset": [ -80.0, 40.0 ]
    },
    "show_distance_pixels": 20,
    "marks": [
        {
            "type": "here",
            "name": "前往这里",
            "color": [255, 210, 48],
            "texture": "textures/ui/ec_mark/mark_rhombus",
            "duration": 30
        },
        {
            "type": "danger",
            "name": "注意这里",
            "color": [250, 50, 50],
            "texture": "textures/ui/ec_mark/mark_rhombus",
            "duration": 10
        }
    ]
}