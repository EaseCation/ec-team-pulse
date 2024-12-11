# -*- coding: utf-8 -*-
import time

import mod.server.extraServerApi as serverApi

try:
    from .ECTeamPulseServer import ECTeamPulseServer
except:
    pass
from ..MarkPoint import MarkPoint
from ..config import *


class ServerMarkPointSession:

    def __init__(self, session_id, system, config):
        self.session_id = session_id
        self.system = system  # type: ECTeamPulseServer
        self.config = config
        self.players = []  # type: list[str]
        self.next_point_id = 0
        self.mark_points = {}  # type: dict[int, MarkPoint]
        self.players_last_point = {}  # type: dict[str, int]
        self.init_listeners()

    def init_listeners(self):
        self.system.ListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            'OnScriptTickServer',
            self, self.on_tick
        )
        self.system.ListenForEvent(
            mod_name,
            client_system_name,
            "ClientMarkPointAdd",
            self,
            self.on_player_request_add_point
        )

    def destroy(self):
        self.system.UnListenForEvent(
            serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
            'OnScriptTickServer',
            self, self.on_tick
        )
        self.system.UnListenForEvent(
            mod_name,
            client_system_name,
            "ClientMarkPointAdd",
            self,
            self.on_player_request_add_point
        )
        for player in self.players:
            self.system.player_to_session.pop(player)
        self.system.NotifyToMultiClients(
            self.players,
            "DestroyMarkSession",
            {
                "session_id": self.session_id
            }
        )

    def add_player(self, player_id):
        self.players.append(player_id)
        self.system.player_to_session[player_id] = self.session_id
        self.system.NotifyToClient(
            player_id,
            "SetupMarkSession",
            {
                "session_id": self.session_id,
                "config": session_config_default,
                "points": [mark_point.to_dict() for mark_point in self.mark_points.values()]
            }
        )

    def remove_player(self, player_id):
        self.players.remove(player_id)
        self.system.player_to_session.pop(player_id)
        self.system.NotifyToClient(
            player_id,
            "DestroyMarkSession",
            {
                "session_id": self.session_id
            }
        )

    def collect_mark_type_count(self, player, mark_type):
        count = 0
        for point_id, mark_point in self.mark_points.items():
            if mark_point.owner == player and mark_point.mark_type == mark_type:
                count += 1
        return count

    def remove_last_point(self, player):
        if player in self.players_last_point:
            last_point_id = self.players_last_point[player]
            if last_point_id in self.mark_points:
                self.remove_point(last_point_id)

    def remove_point(self, point_id):
        self.system.NotifyToMultiClients(
            self.players,
            "MarkPointRemove",
            {
                "point_id": point_id
            }
        )
        self.mark_points.pop(point_id)
        # 删除players_last_point中的value符合point_id的项
        for player, last_point_id in self.players_last_point.items():
            if last_point_id == point_id:
                self.players_last_point.pop(player)

    def add_point(self, owner, pos, mark_config):
        mark_type = mark_config['type']
        point_id = self.next_point_id
        self.next_point_id += 1
        mark_point = MarkPoint(point_id, pos, owner, mark_type, mark_config['color'], mark_config['texture'], time.time() + mark_config['duration'])
        self.mark_points[point_id] = mark_point
        self.players_last_point[owner] = point_id
        self.system.NotifyToMultiClients(
            self.players,
            "MarkPointAdd",
            {
                "point": mark_point.to_dict()
            }
        )

    def on_player_request_add_point(self, args):
        player = args['__id__']
        session_id = args['session_id']
        if session_id != self.session_id:
            return
        if player not in self.players:
            return
        pos = args['pos']
        point_config = args['point_config']
        mark_type = point_config['type']
        # 最大数量限制，移除超过数量的点
        if mark_type in self.config['mark_type_limit']:
            limit = self.config['mark_type_limit'][mark_type]
            mark_type_count = self.collect_mark_type_count(player, mark_type)
            if mark_type_count >= limit:
                for i in range(mark_type_count - limit + 1):
                    for point_id, mark_point in self.mark_points.items():
                        if mark_point.mark_type == mark_type:
                            self.remove_point(point_id)
        self.add_point(player, pos, point_config)

    def on_tick(self):
        now = time.time()
        for point_id, mark_point in self.mark_points.items():
            if mark_point.remove_time and now > mark_point.remove_time:
                self.remove_point(point_id)

