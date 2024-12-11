# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

try:
    from .MarkPointSession import MarkPointSession
except:
    pass

from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())
comp_audio = clientApi.GetEngineCompFactory().CreateCustomAudio(clientApi.GetLocalPlayerId())


class ClientMarkPoint(MarkPoint):

    def __init__(self, session, point_id, pos, owner, mark_type, color, texture, remove_time, sound_config):
        super(ClientMarkPoint, self).__init__(point_id, pos, owner, mark_type, color, texture, remove_time)
        self.session = session  # type: MarkPointSession
        self.sound_config = sound_config
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

    def play_sound(self):
        if self.sound_config:
            if type(self.sound_config) == dict:
                comp_audio.PlayCustomUIMusic(self.sound_config['name'], self.sound_config['volume'], self.sound_config['pitch'], False)
            elif type(self.sound_config) == list:
                for sound in self.sound_config:
                    comp_audio.PlayCustomUIMusic(sound['name'], sound['volume'], sound['pitch'], False)

    def destroy(self):
        if self.ui_node:
            self.ui_node.pending_destroy()
            self.ui_node = None
