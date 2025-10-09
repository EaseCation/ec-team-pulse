# -*- coding: utf-8 -*-
#
import mod.server.extraServerApi as serverApi

from .ServerMarkPointSession import ServerMarkPointSession
from ..config import *

def get_system():
    # type: () -> ECTeamPulseServer
    return serverApi.GetSystem(mod_name, server_system_name)

class ECTeamPulseServer(serverApi.GetServerSystemCls()):
    def __init__(self, namespace, name):
        super(ECTeamPulseServer, self).__init__(namespace, name)
        self.listen_event()
        self.next_session_id = 0
        self.sessions = {}  # type: dict[int, ServerMarkPointSession]
        self.player_to_session = {}  # type: dict[str, int]

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
        print("[ECTeamPulseServer] 标点session已创建")

    def on_client_ui_init_finished(self, args):
        # 只有在标点功能启用时才自动添加玩家到session
        for session in self.sessions.values():
            session.add_player(args['__id__'])
