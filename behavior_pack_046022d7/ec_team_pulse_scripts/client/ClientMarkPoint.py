# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())

class ClientMarkPoint(MarkPoint):

    def __init__(self, session, pos, mark_type, color, texture):
        super(ClientMarkPoint, self).__init__(pos, mark_type, color, texture)
        self.session = session
        self.ui_node = None  # type: MarkPointScreenNode | None

    def show(self):
        print('show', self.pos)
        self.ui_node = clientApi.CreateUI(
            mod_name,
            mark_point_ui_name,
            {
                "isHud": 1,
                "autoScale": 1,
                "bindWorldPosition": (comp_game.GetCurrentDimension(), (self.pos[0], self.pos[1], self.pos[2])),
                "color": self.color,
                "texture": self.texture
            }
        )
        self.ui_node.session = self.session

    def destroy(self):
        if self.ui_node:
            self.ui_node.SetRemove()
            # TODO 需要一个动画来移除，而不是瞬间消失
            self.ui_node = None
