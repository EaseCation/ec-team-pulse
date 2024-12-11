# -*- coding: utf-8 -*-

class InteractionTouch:

    def __init__(self, interaction):
        self.interaction = interaction

    def destroy(self):
        pass

    def on_btn_touch_down(self, args):
        self.interaction.on_down(force_show_ready_ui=True)

    def on_btn_touch_up(self, args):
        self.interaction.on_up()
