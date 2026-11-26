# -*- coding: utf-8 -*-
#
import mod.client.extraClientApi as clientApi

from ..MarkPoint import MarkPoint
from ..config import *
from .MarkPointSession import MarkPointSession
from .UIKeyPool import UIKeyPool


BEDWARS_MARK_POINT_SOUNDS = frozenset((
    "quicktalk.point.goto", "quicktalk.point.warning", "quicktalk.point.attack",
))


class ECTeamPulseClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(ECTeamPulseClient, self).__init__(namespace, name)
        self.listen_event()
        self.level_id = clientApi.GetLevelId()
        self.mark_point_session = None  # type: MarkPointSession | None
        self.mark_point_preferences = {
            key: interaction_config_default[key] for key in ("keyboard_hold", "show_mark_points")
        }
        self.ui_registered = False  # 防止重复注册UI

        # 初始化全局UIKey对象池（跨所有session复用）
        self.ui_key_pool = UIKeyPool(mod_name, mark_point_ui_cls_path, mark_point_ui_def)

    # 在类初始化的时候开始监听
    def listen_event(self):
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'LoadClientAddonScriptsAfter',
                            self, self.on_load_client_addon)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'UiInitFinished',
                            self, self.on_ui_init_finished)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            "PlaySoundClientEvent",
                            self, self.on_play_sound)
        self.ListenForEvent(mod_name, server_system_name,
                            "SetupMarkSession",
                            self, self.on_setup_session)
        self.ListenForEvent(mod_name, server_system_name,
                            "SyncMarkPointPreferences",
                            self, self.on_sync_mark_point_preferences)
        self.ListenForEvent(mod_name, server_system_name,
                            "MarkPointAdd",
                            self, self.on_mark_point_add)
        self.ListenForEvent(mod_name, server_system_name,
                            "MarkPointRemove",
                            self, self.on_mark_point_remove)
        self.ListenForEvent(mod_name, server_system_name,
                            "UpdateMarkSessionConfig",
                            self, self.on_update_session_config)
        self.ListenForEvent(mod_name, server_system_name,
                            "DestroyMarkSession",
                            self, self.on_destroy_session)

    # 取消监听
    def un_listen_event(self):
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              "LoadClientAddonScriptsAfter",
                              self, self.on_load_client_addon)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                                "UiInitFinished",
                                self, self.on_ui_init_finished)
        self.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                              "PlaySoundClientEvent",
                              self, self.on_play_sound)
        self.UnListenForEvent(mod_name, server_system_name,
                                "SetupMarkSession",
                                self, self.on_setup_session)
        self.UnListenForEvent(mod_name, server_system_name,
                                "SyncMarkPointPreferences",
                                self, self.on_sync_mark_point_preferences)
        self.UnListenForEvent(mod_name, server_system_name,
                                "MarkPointAdd",
                                self, self.on_mark_point_add)
        self.UnListenForEvent(mod_name, server_system_name,
                                "MarkPointRemove",
                                self, self.on_mark_point_remove)
        self.UnListenForEvent(mod_name, server_system_name,
                                "UpdateMarkSessionConfig",
                                self, self.on_update_session_config)
        self.UnListenForEvent(mod_name, server_system_name,
                                "DestroyMarkSession",
                                self, self.on_destroy_session)

    # 在Destroy中调用反注册取消监听
    def Destroy(self):
        if self.mark_point_session:
            self.mark_point_session.destroy()
            self.mark_point_session = None
        self.un_listen_event()
        print('==== ECTeamPulseClient 完成反注册 ====')

    def on_load_client_addon(self, data):
        print('==== ECTeamPulseClient 已加载 ====')

    def on_ui_init_finished(self, args):
        # UI初始化完成后必须重新注册基础UI模板才能正常创建动态UI
        try:
            # 注意：NetEase clientApi没有UnregisterUI方法，UI会自动管理生命周期
            # 直接注册基础UI模板（如果已存在会覆盖）
            # clientApi.RegisterUI(mod_name, mark_point_ui_name, mark_point_ui_cls_path, mark_point_ui_def)
            clientApi.RegisterUI(mod_name, mark_point_ready_ui_name, mark_point_ready_ui_cls_path, mark_point_ready_ui_def)
            clientApi.RegisterUI(mod_name, mark_hud_ui_name, mark_hud_ui_cls_path, mark_hud_ui_def)
            self.ui_registered = True
            print("[ECTeamPulseClient] 基础UI模板注册成功")
        except Exception as e:
            print("[ECTeamPulseClient] UI注册失败: {}".format(str(e)))
            self.ui_registered = False
        
        self.NotifyToServer("ClientUiInitFinished", {})
        if self.mark_point_session:
            self.mark_point_session.on_client_ui_init_finished()

    def on_sync_mark_point_preferences(self, args):
        # 旧服不发送这两个字段。设置跟随本次连接，对局结束后仍要保留。
        for key in self.mark_point_preferences:
            if key in args:
                self.mark_point_preferences[key] = args[key]

    def on_play_sound(self, args):
        # 旧版起床战争还会单独发送标点语音。
        if not self.mark_point_preferences["show_mark_points"] and args["name"] in BEDWARS_MARK_POINT_SOUNDS:
            args["cancel"] = True

    def on_setup_session(self, args):
        if self.mark_point_session:
            self.mark_point_session.destroy()
        session_id = args['session_id']
        config = args['config']
        server_interaction_config = args['interaction_config']
        self.on_sync_mark_point_preferences(server_interaction_config)
        interaction_config = interaction_config_default.copy()
        interaction_config.update(server_interaction_config)
        interaction_config.update(self.mark_point_preferences)
        read_only = args['read_only']
        self.mark_point_session = MarkPointSession(self, session_id, config, interaction_config, read_only)
        self.mark_point_session.init_points(args['points'])
        #self.mark_point_manager.client_add_point((0, -60, 0), self.mark_point_manager.config['marks'][0])

    def on_mark_point_add(self, args):
        if self.mark_point_session:
            self.mark_point_session.add_client_point(MarkPoint.from_dict(args['point']))

    def on_mark_point_remove(self, args):
        if self.mark_point_session and args['session_id'] == self.mark_point_session.session_id:
            self.mark_point_session.remove_point(args['point_id'])

    def on_update_session_config(self, args):
        if self.mark_point_session and args['session_id'] == self.mark_point_session.session_id:
            self.mark_point_session.config = args['config']

    def on_destroy_session(self, args):
        if self.mark_point_session:
            self.mark_point_session.destroy()
            self.mark_point_session = None
