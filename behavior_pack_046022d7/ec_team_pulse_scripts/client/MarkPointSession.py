# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod.client.system.clientSystem import ClientSystem

from .interaction.InteractionMouseKeyboard import InteractionMouseKeyboard
from ..uiScript.MarkHudScreenNode import MarkHudScreenNode
from .ClientMarkPoint import ClientMarkPoint

from ..config import *

class MarkPointSession(object):

    def __init__(self, client, config):
        self.client = client  # type: ClientSystem
        self.config = config  # type: dict
        self.mark_points = {}  # type: dict[tuple[float, float, float], ClientMarkPoint]
        self.last_point_pos = None  # type: tuple[float, float, float] | None
        self.hud_ui = None  # type: MarkHudScreenNode | None
        self.init_ui()
        self.interaction_mouse_keyboard = InteractionMouseKeyboard(self)

    def init_ui(self):
        clientApi.CreateUI(mod_name, mark_hud_ui_name, {"isHud": 1, })

    def add_point(self, pos, point_config):
        mark_type = point_config['type']
        # 最大数量限制，移除超过数量的点
        if mark_type in self.config['mark_type_limit']:
            limit = self.config['mark_type_limit'][mark_type]
            mark_type_count = self.collect_mark_type_count(mark_type)
            if mark_type_count >= limit:
                for i in range(mark_type_count - limit + 1):
                    for pos0, mark_point in self.mark_points.items():
                        if mark_point.mark_type == mark_type:
                            self.remove_point(pos0)

        self.mark_points[pos] = ClientMarkPoint(pos, mark_type, point_config['color'], point_config['texture'])
        self.mark_points[pos].show()
        self.last_point_pos = pos

    def collect_mark_type_count(self, mark_type):
        count = 0
        for pos, mark_point in self.mark_points.items():
            if mark_point.mark_type == mark_type:
                count += 1
        return count

    def remove_last_point(self):
        if self.last_point_pos and self.last_point_pos in self.mark_points:
            self.mark_points[self.last_point_pos].destroy()
            self.mark_points.pop(self.last_point_pos)
            self.last_point_pos = None

    def remove_point(self, pos):
        if pos in self.mark_points:
            self.mark_points[pos].destroy()
            self.mark_points.pop(pos)
            if self.last_point_pos == pos:
                self.last_point_pos = None

    def clear_all(self):
        for pos, mark_point in self.mark_points.items():
            mark_point.destroy()
        self.mark_points.clear()
        self.last_point_pos = None

    def destroy(self):
        self.clear_all()
        self.interaction_mouse_keyboard.destroy()
        if self.hud_ui:
            self.hud_ui.SetRemove()
            self.hud_ui = None