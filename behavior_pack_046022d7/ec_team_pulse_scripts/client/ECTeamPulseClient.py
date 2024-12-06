# -*- coding: utf-8 -*-
#
import mod.client.extraClientApi as clientApi
from ..config import *
from .MarkPointSession import MarkPointSession


class ECTeamPulseClient(clientApi.GetClientSystemCls()):
    def __init__(self, namespace, name):
        super(ECTeamPulseClient, self).__init__(namespace, name)
        self.listen_event()
        self.level_id = clientApi.GetLevelId()
        self.mark_point_manager = None  # type: MarkPointSession | None

    # 在类初始化的时候开始监听
    def listen_event(self):
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'LoadClientAddonScriptsAfter',
                            self, self.on_load_client_addon)
        self.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'UiInitFinished',
                            self, self.on_ui_init_finished)
        self.ListenForEvent(mod_name, server_system_name,
                            "SetupMarkSession",
                            self, self.on_setup_session)
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

    # 在Destroy中调用反注册取消监听
    def Destroy(self):
        self.un_listen_event()
        print('==== ECTeamPulseClient 完成反注册 ====')

    def on_load_client_addon(self, data):
        print('==== ECTeamPulseClient 已加载 ====')

    def on_ui_init_finished(self, args):
        clientApi.RegisterUI(mod_name, mark_point_ready_ui_name, mark_point_ready_ui_cls_path, mark_point_ready_ui_def)
        clientApi.RegisterUI(mod_name, mark_hud_ui_name, mark_hud_ui_cls_path, mark_hud_ui_def)
        self.NotifyToServer("ClientUiInitFinished", {})

    def on_setup_session(self, args):
        if self.mark_point_manager:
            self.mark_point_manager.destroy()
        self.mark_point_manager = MarkPointSession(self, args)

    def on_destroy_session(self, args):
        if self.mark_point_manager:
            self.mark_point_manager.destroy()
            self.mark_point_manager = None
