# -*- coding: utf-8 -*-

import mod.client.extraClientApi as clientApi
from .InteractionBase import InteractionBase
from ...config import *
from ...uiScript.MarkHudScreenNode import MarkHudScreenNode


class InteractionTouch(InteractionBase):

    def __init__(self, session):
        super(InteractionTouch, self).__init__(session)

        self.hud_ui = None  # type: MarkHudScreenNode | None
        self.hud_ui = clientApi.CreateUI(
            mod_name,
            mark_hud_ui_name,
            {
                "isHud": 1,
                "interaction": self
            }
        )

    def on_btn_touch_down(self, args):
        if self.hud_ui:
            self.hud_ui.init_select()
        self.on_down(True)

    def on_btn_touch_up(self, args):
        self.on_up()
        if self.hud_ui:
            self.hud_ui.destroy_select()
