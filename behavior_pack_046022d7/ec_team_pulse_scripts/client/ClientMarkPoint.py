# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())

class ClientMarkPoint(MarkPoint):

    def __init__(self, pos, mark_type, color, texture):
        super(ClientMarkPoint, self).__init__(pos, mark_type, color, texture)
        self.ui_node = None  # type: MarkPointScreenNode | None

    def show(self):
        print('show', self.pos)
        ui_key = mark_point_ui_name + str(self.pos)
        clientApi.RegisterUI(mod_name, ui_key, mark_point_ui_cls_path, mark_point_ui_def)
        self.ui_node = clientApi.CreateUI(
            mod_name,
            ui_key,
            {
                "isHud": 1,
                "autoScale": 0,
                "bindWorldPosition": (comp_game.GetCurrentDimension(), (self.pos[0], self.pos[1], self.pos[2])),
                "color": self.color,
                "texture": self.texture
            }
        )

    def destroy(self):
        if self.ui_node:
            self.ui_node.SetRemove()
            # TODO 需要一个动画来移除，而不是瞬间消失
            self.ui_node = None
