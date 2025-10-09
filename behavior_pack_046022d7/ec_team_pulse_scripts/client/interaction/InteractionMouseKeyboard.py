# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod.common.minecraftEnum import KeyBoardType


class InteractionMouseKeyboard:

    def __init__(self, interaction):
        self.interaction = interaction
        self.interaction.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnMouseMiddleDownClientEvent',
            self, self.on_mouse_middle_down)
        self.interaction.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnKeyPressInGame',
            self, self.on_key_press_in_game
        )

    def destroy(self):
        self.interaction.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnMouseMiddleDownClientEvent',
            self, self.on_mouse_middle_down
        )
        self.interaction.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnKeyPressInGame',
            self, self.on_key_press_in_game
        )

    def on_mouse_middle_down(self, args):
        is_down = args['isDown'] == 1 or args['isDown'] == '1'
        if is_down:
            self.interaction.on_down(show_tip=False)
        else:
            self.interaction.on_up()

    def on_key_press_in_game(self, args):
        if not self.interaction.holding:
            return
        if args['key'] != str(self.interaction.session.interaction_config['keyboard_switch']) or args['screenName'] != 'hud_screen':
            return
        if args['isDown'] == '0':
            self.interaction.holding_mark_type_auto = False
            self.interaction.holding_mark_type_index += 1
            if self.interaction.holding_mark_type_index >= len(self.interaction.session.config['marks']):
                self.interaction.holding_mark_type_index = 0
