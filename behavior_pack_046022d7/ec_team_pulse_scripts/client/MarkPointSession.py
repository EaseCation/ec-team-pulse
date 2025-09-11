# -*- coding: utf-8 -*-
from mod.client.system.clientSystem import ClientSystem

from .ClientMarkPoint import ClientMarkPoint
from .interaction.MarkingInteraction import MarkingInteraction
from ..MarkPoint import MarkPoint

class MarkPointSession(object):

    def __init__(self, client, session_id, config, interaction_config, read_only):
        self.client = client  # type: ClientSystem
        self.session_id = session_id
        self.config = config  # type: dict
        self.interaction_config = interaction_config  # type: dict
        self.read_only = read_only
        self.mark_points = {}  # type: dict[int, ClientMarkPoint]
        if not self.read_only:
            self.interaction = MarkingInteraction(self)
        else:
            self.interaction = None

    def init_points(self, points):
        for point in points:
            self.add_client_point(MarkPoint.from_dict(point), False)

    def on_client_ui_init_finished(self):
        if self.interaction:
            self.interaction.destroy()
            self.interaction = MarkingInteraction(self)

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
        :param play_sound: 是否播放音效
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
        # 创建一个副本列表来避免字典修改期间迭代的问题
        mark_points_to_destroy = list(self.mark_points.items())
        for point_id, mark_point in mark_points_to_destroy:
            try:
                mark_point.destroy()
            except Exception as e:
                print("[MarkPointSession] 销毁标点 {} 时出错: {}".format(point_id, str(e)))
        self.mark_points.clear()
        print("[MarkPointSession] 所有标点已清理完成")

    def on_frame_tick(self):
        # 检查并清理过期的标点
        # 注意：UI已通过定时器自动销毁，这里主要是清理标点数据对象
        expired_points = []
        for point_id, mark_point in self.mark_points.items():
            if mark_point.is_expired():
                expired_points.append(point_id)
                print("[MarkPointSession] 标点 {} 已过期，清理数据对象（UI已通过定时器自动销毁）".format(point_id))
            elif mark_point.ui_node:
                mark_point.ui_node.on_frame_tick()
        
        # 移除过期的标点数据对象
        for point_id in expired_points:
            self.remove_point(point_id)
            
        if self.interaction:
            self.interaction.on_frame_tick()

    def destroy(self):
        self.clear_all()
        if self.interaction:
            self.interaction.destroy()