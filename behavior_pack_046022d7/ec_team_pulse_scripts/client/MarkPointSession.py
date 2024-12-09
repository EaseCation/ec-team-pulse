# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod.client.system.clientSystem import ClientSystem

from .interaction.InteractionMouseKeyboard import InteractionMouseKeyboard
from ..uiScript.MarkHudScreenNode import MarkHudScreenNode
from .ClientMarkPoint import ClientMarkPoint
from ..MarkPoint import MarkPoint

from ..config import *

class MarkPointSession(object):

    def __init__(self, client, config):
        self.client = client  # type: ClientSystem
        self.config = config  # type: dict
        self.mark_points = {}  # type: dict[int, ClientMarkPoint]
        self.hud_ui = None  # type: MarkHudScreenNode | None
        self.init_ui()
        self.interaction_mouse_keyboard = InteractionMouseKeyboard(self)

    def init_points(self, points):
        for point in points:
            self.add_client_point(MarkPoint.from_dict(point))

    def init_ui(self):
        self.hud_ui = clientApi.CreateUI(mod_name, mark_hud_ui_name, {"isHud": 1, })
        self.hud_ui.session = self

    def request_add_point(self, pos, point_config):
        self.client.NotifyToServer(
            "ClientMarkPointAdd",
            {
                "pos": pos,
                "point_config": point_config
            }
        )

    def remove_point(self, point_id):
        if point_id in self.mark_points:
            self.mark_points[point_id].destroy()
            self.mark_points.pop(point_id)

    def add_client_point(self, point):
        """
        从MarkPoint对象添加一个点
        :type point: MarkPoint
        """
        point = ClientMarkPoint(self, point.point_id, point.pos, point.owner, point.mark_type, point.color, point.texture)
        self.mark_points[point.point_id] = point
        point.show()

    def clear_all(self):
        for pos, mark_point in self.mark_points.items():
            mark_point.destroy()
        self.mark_points.clear()

    def on_frame_tick(self):
        for mark_point in self.mark_points.values():
            if mark_point.ui_node:
                mark_point.ui_node.on_frame_tick()

    def destroy(self):
        self.clear_all()
        self.interaction_mouse_keyboard.destroy()
        if self.hud_ui:
            self.hud_ui.SetRemove()
            self.hud_ui = None