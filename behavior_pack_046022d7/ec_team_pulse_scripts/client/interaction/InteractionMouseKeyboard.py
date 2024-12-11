# -*- coding: utf-8 -*-
import time
from .InteractionBase import InteractionBase
import mod.client.extraClientApi as clientApi


class InteractionMouseKeyboard(InteractionBase):

    def __init__(self, session):
        super(InteractionMouseKeyboard, self).__init__(session)

        self.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnMouseMiddleDownClientEvent',
            self, self.on_mouse_middle_down)

    def destroy(self):
        super().destroy()
        self.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'RightClickBeforeClientEvent',
            self, self.on_mouse_middle_down
        )

    def on_mouse_middle_down(self, args):
        is_down = args['isDown'] == 1
        if is_down:
            self.on_down(show_tip=False)
        else:
            self.on_up()
