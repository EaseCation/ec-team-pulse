# -*- coding: utf-8 -*-
import time

import mod.server.extraServerApi as serverApi

from .sessionConfigCheck import check_session_config, check_interaction_config

# try:
#     from .ECTeamPulseServer import ECTeamPulseServer
# except:
#     pass
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
        # 获取被移除标点的创建者，确定需要通知的队伍
        point_creator = None
        if point_id in self.mark_points:
            point_creator = self.mark_points[point_id].owner
        
        # 实现队伍标点过滤：只向同队伍玩家发送标点移除通知
        if point_creator:
            target_players = self._get_team_players_for_waypoint(point_creator)
        else:
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
        
        # 通知起床战争的TeamWaypointController标点被移除
        try:
            import Preset.Controller.PresetApi as presetApi
            bedwars_stage_preset = None
            
            # 获取BedWarsStageLogic预设
            all_presets = presetApi.GetAllPresets()
            for preset in all_presets:
                preset_name = getattr(preset, 'name', None)
                if preset_name == "BedWarsStageLogic":
                    bedwars_stage_preset = preset
                    break
            
            if bedwars_stage_preset:
                bedwars_part = bedwars_stage_preset.GetPartByType("ECBedWarsPart")
                if bedwars_part and hasattr(bedwars_part, 'waypoint_manager') and bedwars_part.waypoint_manager:
                    # 通知标点管理器标点被移除
                    if hasattr(bedwars_part.waypoint_manager, 'on_waypoint_remove_request'):
                        bedwars_part.waypoint_manager.on_waypoint_remove_request("-1", point_id)
                    elif bedwars_part.waypoint_manager.team_controller:
                        bedwars_part.waypoint_manager.team_controller.on_waypoint_removed(point_id)
                    print("[ServerMarkPointSession] 已通知起床战争系统标点 {} 被移除".format(point_id))
        except Exception as e:
            print("[ServerMarkPointSession] 通知起床战争系统标点移除失败: {}".format(str(e)))
        
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
        target_players = self._get_team_players_for_waypoint(owner)
        
        self.system.NotifyToMultiClients(
            target_players,
            "MarkPointAdd",
            {
                "point": mark_point.to_dict()
            }
        )
        
        print("[ServerMarkPointSession] 标点 {} 创建通知已发送给 {} 个同队伍客户端 (创建者队伍)".format(point_id, len(target_players)))
        return point_id
    
    def _get_team_players_for_waypoint(self, creator_id):
        """获取应该接收标点通知的同队伍玩家列表"""
        try:
            # 获取起床战争系统来查询队伍信息
            import Preset.Controller.PresetApi as presetApi
            bedwars_stage_preset = None
            
            # 获取BedWarsStageLogic预设
            all_presets = presetApi.GetAllPresets()
            for preset in all_presets:
                preset_name = getattr(preset, 'name', None)
                if preset_name == "BedWarsStageLogic":
                    bedwars_stage_preset = preset
                    break
            
            if bedwars_stage_preset:
                bedwars_part = bedwars_stage_preset.GetPartByType("ECBedWarsPart")
                if bedwars_part and hasattr(bedwars_part, 'team_module') and bedwars_part.team_module:
                    # 获取创建者的队伍ID - 使用正确的API
                    creator_team_id = bedwars_part.team_module.get_player_team(creator_id)
                    if creator_team_id:
                        # 获取同队伍的所有玩家 - 使用正确的API
                        team_players = bedwars_part.team_module.get_team_players_ids(creator_team_id)
                        if team_players:
                            # 只返回在session中的同队伍玩家
                            team_players_in_session = [player_id for player_id in team_players if player_id in self.players]
                            print("[ServerMarkPointSession] 创建者 {} 的队伍 {} 中session内的玩家: {}".format(creator_id, creator_team_id, team_players_in_session))
                            return team_players_in_session
                        else:
                            print("[ServerMarkPointSession] 队伍 {} 没有玩家，发送给所有玩家".format(creator_team_id))
                            return list(self.players)
                    else:
                        print("[ServerMarkPointSession] 创建者 {} 没有队伍，发送给所有玩家".format(creator_id))
                        return list(self.players)
                else:
                    print("[ServerMarkPointSession] 无法获取队伍模块，发送给所有玩家")
                    return list(self.players)
            else:
                print("[ServerMarkPointSession] 无法获取起床战争预设，发送给所有玩家")
                return list(self.players)
                
        except Exception as e:
            print("[ServerMarkPointSession] 获取队伍玩家失败: {}，发送给所有玩家".format(str(e)))
            return list(self.players)

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
        
        # 检查是否有起床战争系统接管标点处理
        bedwars_part = None
        try:
            # 通过预设API获取BedWarsStageLogic预设中的ECBedWarsPart零件
            import Preset.Controller.PresetApi as presetApi
            
            bedwars_stage_preset = None
            
            # 获取BedWarsStageLogic预设
            all_presets = presetApi.GetAllPresets()
            for preset in all_presets:
                preset_name = getattr(preset, 'name', None)
                if preset_name == "BedWarsStageLogic":
                    bedwars_stage_preset = preset
                    break
            
            if bedwars_stage_preset:
                # 使用GetPartByType方法获取ECBedWarsPart零件
                bedwars_part = bedwars_stage_preset.GetPartByType("ECBedWarsPart")
                    
        except Exception as e:
            print("[ServerMarkPointSession] 获取起床战争零件异常: {}".format(str(e)))
        
        # 无论是否有起床战争系统，都先执行标点数量限制检查
        if mark_type in self.config['mark_type_limit']:
            limit = self.config['mark_type_limit'][mark_type]
            mark_type_count = self.collect_mark_type_count(player, mark_type)
            print("[ServerMarkPointSession] 玩家 {} 当前 {} 类型标点数量: {}, 限制: {}".format(
                player, mark_type, mark_type_count, limit))
            
            # 如果超出限制，直接拒绝创建标点
            if mark_type_count >= limit:
                print("[ServerMarkPointSession] 玩家 {} 的 {} 类型标点已达到限制({}个)，拒绝创建新标点".format(
                    player, mark_type, limit))
                return  # 直接返回，不创建标点
        
        # 数量限制检查完成后，根据是否有起床战争系统选择处理方式
        if bedwars_part and hasattr(bedwars_part, 'waypoint_manager') and bedwars_part.waypoint_manager:
            # 让起床战争的标点管理器处理（包含队伍共享逻辑）
            waypoint_type = "positive" if mark_type == "here" else "negative"
            waypoint_id = bedwars_part.waypoint_manager.on_waypoint_create_request(
                player, pos, waypoint_type
            )
            return
        else:
            # 使用原有逻辑（所有玩家可见）
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
    
    # 起床战争集成方法 - 为所有玩家启用标点功能
    def enable_for_all_players(self):
        """为所有在线玩家启用标点功能"""
        try:
            # 将所有玩家添加到可操作列表中
            for player_id in self.players:
                if player_id not in self.players_can_operate:
                    self.players_can_operate.append(player_id)
                    print("[ServerMarkPointSession] 玩家 {} 已获得标点权限".format(player_id))
            
            # 通知所有客户端启用标点功能
            self.system.NotifyToMultiClients(
                self.players,
                "EnableMarkingFeature",
                {
                    "session_id": self.session_id
                }
            )
            print("[ServerMarkPointSession] 为所有玩家启用标点功能")
        except Exception as e:
            print("[ServerMarkPointSession] 启用标点功能失败: {}".format(str(e)))
    
    # 起床战争集成方法 - 为所有玩家禁用标点功能  
    def disable_for_all_players(self):
        """为所有玩家禁用标点功能"""
        try:
            # 将所有玩家从可操作列表中移除
            removed_players = []
            for player_id in self.players:
                if player_id in self.players_can_operate:
                    self.players_can_operate.remove(player_id)
                    removed_players.append(player_id)
            
            if removed_players:
                print("[ServerMarkPointSession] 已移除玩家标点权限: {}".format(removed_players))
            
            # 通知所有客户端禁用标点功能
            self.system.NotifyToMultiClients(
                self.players,
                "DisableMarkingFeature",
                {
                    "session_id": self.session_id
                }
            )
            print("[ServerMarkPointSession] 为所有玩家禁用标点功能")
        except Exception as e:
            print("[ServerMarkPointSession] 禁用标点功能失败: {}".format(str(e)))
    
    # 起床战争集成方法 - 清理所有标点
    def clear_all_waypoints(self):
        """清理session中的所有标点"""
        try:
            # 创建要删除的标点ID列表（避免在迭代时修改字典）
            point_ids_to_remove = list(self.mark_points.keys())
            
            # 逐个移除标点
            for point_id in point_ids_to_remove:
                self.remove_point(point_id)
            
            print("[ServerMarkPointSession] 已清理所有标点")
        except Exception as e:
            print("[ServerMarkPointSession] 清理标点失败: {}".format(str(e)))
    
    # 起床战争集成方法 - 创建标点
    def create_waypoint(self, player_id, position, waypoint_type):
        """创建标点并返回标点ID"""
        try:
            # 检查玩家是否有操作权限
            if player_id not in self.players_can_operate:
                print("[ServerMarkPointSession] 玩家没有标点操作权限")
                return None
            
            # 根据标点类型选择配置
            if waypoint_type == "positive":
                mark_config = self.config['marks'][0]  # "here" 类型
            elif waypoint_type == "negative": 
                mark_config = self.config['marks'][1]  # "danger" 类型
            else:
                # 使用默认配置（positive）
                mark_config = self.config['marks'][0]
            
            mark_type = mark_config['type']
            
            # 按标点类型进行数量限制检查
            if mark_type in self.config['mark_type_limit']:
                limit = self.config['mark_type_limit'][mark_type]
                mark_type_count = self.collect_mark_type_count(player_id, mark_type)
                print("[ServerMarkPointSession] 玩家 {} 当前 {} 类型标点数量: {}, 限制: {}".format(
                    player_id, mark_type, mark_type_count, limit))
                
                # 如果超出限制，移除最旧的标点直到符合限制
                if mark_type_count >= limit:
                    # 需要移除的数量 = 当前数量 - 限制 + 1（为新标点腾出位置）
                    need_remove = mark_type_count - limit + 1
                    print("[ServerMarkPointSession] 需要移除 {} 个旧标点为新标点腾出位置".format(need_remove))
                    
                    # 按创建时间排序，移除最旧的标点
                    player_points = []
                    for point_id, mark_point in self.mark_points.items():
                        if mark_point.owner == player_id and mark_point.mark_type == mark_type:
                            player_points.append((point_id, mark_point))
                    
                    # 按标点ID排序（较小的ID表示较早创建）
                    player_points.sort(key=lambda x: x[0])
                    
                    # 移除最旧的标点
                    for i in range(min(need_remove, len(player_points))):
                        point_id = player_points[i][0]
                        print("[ServerMarkPointSession] 移除旧的 {} 类型标点 {}".format(mark_type, point_id))
                        self.remove_point(point_id)
            
            # 创建标点
            waypoint_id = self.add_point(player_id, position, mark_config)
            return waypoint_id
            
        except Exception as e:
            print("[ServerMarkPointSession] 创建标点失败: {}".format(str(e)))
            return None
    
    # 起床战争集成方法 - 移除标点
    def remove_waypoint(self, waypoint_id):
        """移除指定标点"""
        try:
            if waypoint_id in self.mark_points:
                self.remove_point(waypoint_id)
                return True
            return False
        except Exception as e:
            print("[ServerMarkPointSession] 移除标点失败: {}".format(str(e)))
            return False
    
    # 起床战争集成方法 - 向特定玩家显示标点
    def show_waypoint_to_player(self, player_id, waypoint_id, position, waypoint_type):
        """向特定玩家显示标点"""
        try:
            if player_id not in self.players:
                return False
            
            # 查找标点信息
            if waypoint_id in self.mark_points:
                mark_point = self.mark_points[waypoint_id]
                self.system.NotifyToClient(
                    player_id,
                    "ShowWaypoint",
                    {
                        "session_id": self.session_id,
                        "waypoint": mark_point.to_dict()
                    }
                )
                return True
            return False
            
        except Exception as e:
            print("[ServerMarkPointSession] 显示标点失败: {}".format(str(e)))
            return False
    
    # 起床战争集成方法 - 从特定玩家隐藏标点
    def hide_waypoint_from_player(self, player_id, waypoint_id):
        """从特定玩家隐藏标点"""
        try:
            if player_id not in self.players:
                return False
            
            self.system.NotifyToClient(
                player_id,
                "HideWaypoint",
                {
                    "session_id": self.session_id,
                    "waypoint_id": waypoint_id
                }
            )
            return True
            
        except Exception as e:
            print("[ServerMarkPointSession] 隐藏标点失败: {}".format(str(e)))
            return False