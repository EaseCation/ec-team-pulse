# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())

class ClientMarkPoint(MarkPoint):

    def __init__(self, pos, color, texture):
        super(ClientMarkPoint, self).__init__(pos, color, texture)
        self.ui_node = None  # type: MarkPointScreenNode | None

    def show(self):
        self.ui_node = clientApi.CreateUI(
            mod_name,
            mark_point_ui_name,
            {
                "isHud": 1,
                "bindWorldPosition": (comp_game.GetCurrentDimension(), (self.pos[0], self.pos[1], self.pos[2])),
                "color": self.color,
                "texture": self.texture,
            }
        )

    def destroy(self):
        if self.ui_node:
            self.ui_node.SetRemove()
            self.ui_node = None