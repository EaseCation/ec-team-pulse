# -*- coding: utf-8 -*-
from mod.client.system.clientSystem import ClientSystem

from .interaction.InteractionMouseKeyboard import InteractionMouseKeyboard
from .interaction.InteractionTouch import InteractionTouch
from .ClientMarkPoint import ClientMarkPoint
from ..MarkPoint import MarkPoint

class MarkPointSession(object):

    def __init__(self, client, session_id, config):
        self.client = client  # type: ClientSystem
        self.session_id = session_id
        self.config = config  # type: dict
        self.mark_points = {}  # type: dict[int, ClientMarkPoint]
        self.interaction_mouse_keyboard = InteractionMouseKeyboard(self)
        self.interaction_touch = InteractionTouch(self)

    def init_points(self, points):
        for point in points:
            self.add_client_point(MarkPoint.from_dict(point))

    def request_add_point(self, pos, point_config):
        self.client.NotifyToServer(
            "ClientMarkPointAdd",
            {
                "session_id": self.session_id,
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
        point = ClientMarkPoint(self, point.point_id, point.pos, point.owner, point.mark_type, point.color, point.texture, point.remove_time)
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
        self.interaction_mouse_keyboard.on_frame_tick()
        self.interaction_touch.on_frame_tick()

    def destroy(self):
        self.clear_all()
        self.interaction_mouse_keyboard.destroy()
        self.interaction_touch.destroy()
        if self.hud_ui:
            self.hud_ui.SetRemove()
            self.hud_ui = None