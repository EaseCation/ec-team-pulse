# -*- coding: utf-8 -*-
#
import mod.server.extraServerApi as serverApi

from .ServerMarkPointSession import ServerMarkPointSession
from ..config import *


class ECTeamPulseServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(ECTeamPulseServer, self).__init__(namespace, name)
        self.listen_event()
        self.next_session_id = 0
        self.sessions = {}  # type: dict[int, ServerMarkPointSession]
        self.player_to_session = {}  # type: dict[str, int]
        
        # 标点功能控制状态
        self.waypoint_enabled = False

    # 在类初始化的时候开始监听
    def listen_event(self):
        self.ListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                            'LoadServerAddonScriptsAfter',
                            self, self.on_load_server_addon)
        self.ListenForEvent(mod_name, client_system_name,
                            "ClientUiInitFinished",
                            self, self.on_client_ui_init_finished)

    # 取消监听
    def un_listen_event(self):
        self.UnListenForEvent(serverApi.GetEngineNamespace(), serverApi.GetEngineSystemName(),
                              "LoadServerAddonScriptsAfter",
                              self, self.on_load_server_addon)

    # 在Destroy中调用反注册取消监听
    def Destroy(self):
        self.un_listen_event()
        print('==== 服务端完成反注册 ====')

    def create_session(self, config, default_interaction_config):
        session_id = self.next_session_id
        self.next_session_id += 1
        session = ServerMarkPointSession(session_id, self, config, default_interaction_config)
        self.sessions[session_id] = session
        return session

    def remove_session(self, session_id):
        session = self.sessions.pop(session_id)
        if session:
            session.destroy()

    def on_load_server_addon(self, data):
        print('===== ECTeamPulseServer 已加载 =====')
        self.test()

    def test(self):
        # 创建session但不自动启用标点功能
        # 标点功能需要通过enable_waypoint()方法由起床战争系统启用
        self.create_session(session_config_default, interaction_config_default)
        print("[ECTeamPulseServer] 标点session已创建，等待起床战争系统启用")

    def on_client_ui_init_finished(self, args):
        print('on_client_ui_init_finished', args)
        # 只有在标点功能启用时才自动添加玩家到session
        if self.waypoint_enabled:
            for session in self.sessions.values():
                session.add_player(args['__id__'])
    
    # 起床战争集成接口 - 启用标点功能
    def enable_waypoint(self):
        """启用标点功能 - 由起床战争系统调用"""
        try:
            self.waypoint_enabled = True
            print("[ECTeamPulseServer] 标点功能已启用")
            
            # 获取所有在线玩家并添加到session中
            import mod.server.extraServerApi as serverApi
            all_players = serverApi.GetPlayerList()
            print("[ECTeamPulseServer] 发现在线玩家: {}".format(all_players))
            
            for session in self.sessions.values():
                # 先确保所有在线玩家都在session中
                for player_id in all_players:
                    if player_id not in session.players:
                        session.add_player(player_id, read_only=False)
                        print("[ECTeamPulseServer] 玩家 {} 已加入标点session".format(player_id))
                
                # 然后为所有玩家启用标点功能
                session.enable_for_all_players()
            
            return True
        except Exception as e:
            print("[ECTeamPulseServer] 启用标点功能失败: {}".format(str(e)))
            return False
    
    # 起床战争集成接口 - 禁用标点功能
    def disable_waypoint(self):
        """禁用标点功能 - 由起床战争系统调用"""
        try:
            self.waypoint_enabled = False
            print("[ECTeamPulseServer] 标点功能已禁用")
            
            # 清理所有标点并禁用功能
            for session in self.sessions.values():
                session.clear_all_waypoints()
                session.disable_for_all_players()
            
            return True
        except Exception as e:
            print("[ECTeamPulseServer] 禁用标点功能失败: {}".format(str(e)))
            return False
    
    # 起床战争集成接口 - 添加玩家到标点session
    def add_player_to_session(self, player_id):
        """将中途加入的玩家添加到标点session中"""
        try:
            if not self.waypoint_enabled:
                print("[ECTeamPulseServer] 标点功能未启用，无法添加玩家到session")
                return False
            
            added_to_any_session = False
            for session in self.sessions.values():
                if player_id not in session.players:
                    session.add_player(player_id, read_only=False)
                    print("[ECTeamPulseServer] 玩家 {} 已加入session {}".format(player_id, session.session_id))
                    added_to_any_session = True
                else:
                    print("[ECTeamPulseServer] 玩家 {} 已在session {} 中".format(player_id, session.session_id))
                    added_to_any_session = True
            
            if not added_to_any_session:
                print("[ECTeamPulseServer] 警告：没有可用的session添加玩家 {}".format(player_id))
            
            return added_to_any_session
            
        except Exception as e:
            print("[ECTeamPulseServer] 添加玩家到session失败: {}".format(str(e)))
            return False
    
    # 起床战争集成接口 - 检查标点功能状态
    def is_waypoint_enabled(self):
        """检查标点功能是否已启用"""
        return self.waypoint_enabled
    
    # 起床战争集成接口 - 创建标点（带权限检查）
    def create_waypoint(self, player_id, position, waypoint_type):
        """创建标点 - 带权限检查"""
        try:
            # 权限检查
            if not self.waypoint_enabled:
                print("[ECTeamPulseServer] 标点功能未启用，拒绝创建标点")
                return None
            
            # 查找玩家所在的session
            if player_id not in self.player_to_session:
                print("[ECTeamPulseServer] 玩家不在任何session中")
                return None
            
            session_id = self.player_to_session[player_id]
            session = self.sessions.get(session_id)
            if not session:
                print("[ECTeamPulseServer] 找不到玩家的session")
                return None
            
            # 调用session创建标点
            waypoint_id = session.create_waypoint(player_id, position, waypoint_type)
            return waypoint_id
            
        except Exception as e:
            print("[ECTeamPulseServer] 创建标点失败: {}".format(str(e)))
            return None
    
    # 起床战争集成接口 - 移除标点
    def remove_waypoint(self, waypoint_id):
        """移除标点"""
        try:
            # 在所有session中查找并移除标点
            for session in self.sessions.values():
                if session.remove_waypoint(waypoint_id):
                    return True
            return False
            
        except Exception as e:
            print("[ECTeamPulseServer] 移除标点失败: {}".format(str(e)))
            return False
    
    # 起床战争集成接口 - 向特定玩家显示标点
    def show_waypoint_to_player(self, player_id, waypoint_id, position, waypoint_type):
        """向特定玩家显示标点"""
        try:
            if not self.waypoint_enabled:
                return False
                
            # 查找玩家所在session
            if player_id not in self.player_to_session:
                return False
                
            session_id = self.player_to_session[player_id]
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            return session.show_waypoint_to_player(player_id, waypoint_id, position, waypoint_type)
            
        except Exception as e:
            print("[ECTeamPulseServer] 显示标点失败: {}".format(str(e)))
            return False
    
    # 起床战争集成接口 - 从特定玩家隐藏标点
    def hide_waypoint_from_player(self, player_id, waypoint_id):
        """从特定玩家隐藏标点"""
        try:
            if player_id not in self.player_to_session:
                return False
                
            session_id = self.player_to_session[player_id]
            session = self.sessions.get(session_id)
            if not session:
                return False
            
            return session.hide_waypoint_from_player(player_id, waypoint_id)
            
        except Exception as e:
            print("[ECTeamPulseServer] 隐藏标点失败: {}".format(str(e)))
            return False
