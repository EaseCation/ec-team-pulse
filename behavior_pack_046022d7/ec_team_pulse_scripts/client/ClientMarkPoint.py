# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())

class ClientMarkPoint(MarkPoint):

    def __init__(self, session, point_id, pos, owner, mark_type, color, texture, remove_time):
        super(ClientMarkPoint, self).__init__(point_id, pos, owner, mark_type, color, texture, remove_time)
        self.session = session
        self.ui_node = None  # type: MarkPointScreenNode | None

    def show(self):
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
            self.ui_node.pending_destroy()
            self.ui_node = None

    @staticmethod
    def from_mark_point(session, mark_point):
        """
        从MarkPoint对象创建ClientMarkPoint对象
        :type session: MarkPointSession
        :type mark_point: MarkPoint
        """
        return ClientMarkPoint(session, mark_point.point_id, mark_point.pos, mark_point.owner, mark_point.mark_type, mark_point.color, mark_point.texture)