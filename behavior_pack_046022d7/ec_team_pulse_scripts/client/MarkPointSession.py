# -*- coding: utf-8 -*-
from mod.client.system.clientSystem import ClientSystem

from .ClientMarkPoint import ClientMarkPoint
from .interaction.MarkingInteraction import MarkingInteraction
from ..MarkPoint import MarkPoint

class MarkPointSession(object):

    def __init__(self, client, session_id, config, read_only):
        self.client = client  # type: ClientSystem
        self.session_id = session_id
        self.config = config  # type: dict
        self.read_only = read_only
        self.mark_points = {}  # type: dict[int, ClientMarkPoint]
        if not self.read_only:
            self.interaction = MarkingInteraction(self)
        else:
            self.interaction = None

    def init_points(self, points):
        for point in points:
            self.add_client_point(MarkPoint.from_dict(point), False)

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

    def add_client_point(self, point, play_sound=True):
        """
        从MarkPoint对象添加一个点
        :type point: MarkPoint
        """
        point_config = None
        for config in self.config['marks']:
            if config['type'] == point.mark_type:
                point_config = config
                break
        point_sound_config = None
        if point_config:
            point_sound_config = point_config['sound']

        point = ClientMarkPoint(self, point.point_id, point.pos, point.owner, point.mark_type, point.color, point.texture, point.remove_time, point_sound_config)
        self.mark_points[point.point_id] = point

        point.show()
        if play_sound:
            point.play_sound()

    def clear_all(self):
        for pos, mark_point in self.mark_points.items():
            mark_point.destroy()
        self.mark_points.clear()

    def on_frame_tick(self):
        for mark_point in self.mark_points.values():
            if mark_point.ui_node:
                mark_point.ui_node.on_frame_tick()
        if self.interaction:
            self.interaction.on_frame_tick()

    def destroy(self):
        self.clear_all()
        if self.interaction:
            self.interaction.destroy()