# -*- coding: utf-8 -*-
import time

import mod.server.extraServerApi as serverApi

from .sessionConfigCheck import check_session_config, check_interaction_config

if False:
    from .ECTeamPulseServer import ECTeamPulseServer
from ..MarkPoint import MarkPoint
from ..config import *


class ServerMarkPointSession:

    def __init__(self, session_id, system, config, default_interaction_config):
        """
        :type session_id: int
        :type system: ECTeamPulseServer
        :type config: dict
        :type default_interaction_config: dict
        :param session_id: 会话ID
        :param system: ServerSystem
        :param config: 会话配置
        :param default_interaction_config: 默认交互配置
        """
        self.session_id = session_id
        self.system = system
        self.config = config
        check_session_config(config)
        self.default_interaction_config = default_interaction_config
        check_interaction_config(default_interaction_config)
        self.players = []  # type: list[str]
        self.players_can_operate = []  # type: list[str]
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

    def add_player(self, player_id, read_only=False, interaction_config=None):
        if player_id in self.players:
            self.remove_player(player_id)
        self.players.append(player_id)
        self.system.player_to_session[player_id] = self.session_id
        if not read_only:
            self.players_can_operate.append(player_id)
        self.system.NotifyToClient(
            player_id,
            "SetupMarkSession",
            {
                "session_id": self.session_id,
                "config": self.config,
                "interaction_config": self.default_interaction_config if interaction_config is None else interaction_config,
                "read_only": read_only,
                "points": [mark_point.to_dict() for mark_point in self.mark_points.values()]
            }
        )

    def remove_player(self, player_id):
        self.players.remove(player_id)
        self.players_can_operate.remove(player_id)
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
        current_time = time.time()
        for point_id, mark_point in self.mark_points.items():
            if mark_point.owner == player and mark_point.mark_type == mark_type:
                # 检查标点是否即将过期（剩余时间小于1秒视为即将过期，不计入限制）
                if mark_point.remove_time and (mark_point.remove_time - current_time) < 1.0:
                    print("[ServerMarkPointSession] 标点 {} 即将过期(剩余{}秒)，不计入数量限制".format(
                        point_id, round(mark_point.remove_time - current_time, 2)))
                    continue
                count += 1
        return count

    def remove_last_point(self, player):
        if player in self.players_last_point:
            last_point_id = self.players_last_point[player]
            if last_point_id in self.mark_points:
                self.remove_point(last_point_id)

    def remove_point(self, point_id):
        target_players = list(self.players)  # 如果找不到创建者，发送给所有人

        self.system.NotifyToMultiClients(
            target_players,
            "MarkPointRemove",
            {
                "session_id": self.session_id,
                "point_id": point_id
            }
        )
        
        print("[ServerMarkPointSession] 标点 {} 移除通知已发送给 {} 个同队伍客户端".format(point_id, len(target_players)))

        # 从本地映射中移除标点
        self.mark_points.pop(point_id, None)
        
        # 删除players_last_point中的value符合point_id的项
        players_to_remove = []
        for player, last_point_id in self.players_last_point.items():
            if last_point_id == point_id:
                players_to_remove.append(player)
        for player in players_to_remove:
            self.players_last_point.pop(player)

    def add_point(self, owner, pos, mark_config):
        mark_type = mark_config['type']
        point_id = self.next_point_id
        self.next_point_id += 1
        mark_point = MarkPoint(point_id, pos, owner, mark_type, mark_config['color'], mark_config['texture'], time.time() + mark_config['duration'])
        self.mark_points[point_id] = mark_point
        self.players_last_point[owner] = point_id
        
        print("[ServerMarkPointSession] 创建标点 {} (类型: {}, 创建者: {}, 过期时间: {}秒后)".format(
            point_id, mark_type, owner, mark_config['duration']))
        
        # 实现队伍标点过滤：只向同队伍玩家发送标点创建通知
        target_players = self.players
        
        self.system.NotifyToMultiClients(
            target_players,
            "MarkPointAdd",
            {
                "point": mark_point.to_dict()
            }
        )
        
        print("[ServerMarkPointSession] 标点 {} 创建通知已发送给 {} 个同队伍客户端 (创建者队伍)".format(point_id, len(target_players)))
        return point_id

    def on_player_request_add_point(self, args):
        player = args['__id__']
        session_id = args['session_id']
        if session_id != self.session_id:
            return
        if player not in self.players:
            return
        if player not in self.players_can_operate:
            return
        pos = args['pos']
        point_config = args['point_config']
        mark_type = point_config['type']

        # 无论是否有起床战争系统，都先执行标点数量限制检查
        if mark_type in self.config['mark_type_limit']:
            limit = self.config['mark_type_limit'][mark_type]
            mark_type_count = self.collect_mark_type_count(player, mark_type)
            print("[ServerMarkPointSession] 玩家 {} 当前 {} 类型标点数量: {}, 限制: {}".format(
                player, mark_type, mark_type_count, limit))

            # 如果超出限制，移除最旧的标点为新标点腾出位置
            if mark_type_count >= limit:
                # 需要移除的数量 = 当前数量 - 限制 + 1（为新标点腾出位置）
                need_remove = mark_type_count - limit + 1
                print("[ServerMarkPointSession] 玩家 {} 的 {} 类型标点已达到限制({}个)，需要移除 {} 个旧标点".format(
                    player, mark_type, limit, need_remove))

                # 按创建时间排序，移除最旧的标点
                player_points = []
                for point_id, mark_point in self.mark_points.items():
                    if mark_point.owner == player and mark_point.mark_type == mark_type:
                        player_points.append((point_id, mark_point))

                # 按标点ID排序（较小的ID表示较早创建）
                player_points.sort(key=lambda x: x[0])

                # 移除最旧的标点
                for i in range(min(need_remove, len(player_points))):
                    point_id = player_points[i][0]
                    print("[ServerMarkPointSession] 移除旧的 {} 类型标点 {}".format(mark_type, point_id))
                    self.remove_point(point_id)

        # 数量限制检查已在前面完成，直接创建标点
        self.add_point(player, pos, point_config)

    def on_tick(self):
        now = time.time()
        expired_points = []
        for point_id, mark_point in self.mark_points.items():
            if mark_point.remove_time and now > mark_point.remove_time:
                expired_points.append(point_id)
        
        # 移除过期的标点
        for point_id in expired_points:
            self.remove_point(point_id)

    def update_config(self, config):
        self.config = config
        self.system.NotifyToMultiClients(
            self.players,
            "UpdateMarkSessionConfig",
            {
                "session_id": self.session_id,
                "config": self.config
            }
        )
