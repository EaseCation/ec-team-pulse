# -*- coding: utf-8 -*-
from mod.common.minecraftEnum import GamepadKeyType

import mod.client.extraClientApi as clientApi


class InteractionGamepad:

    def __init__(self, interaction):
        self.interaction = interaction
        self.interaction.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnGamepadKeyPressClientEvent',
            self, self.on_gamepad_key_press)

    def destroy(self):
        self.interaction.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnGamepadKeyPressClientEvent',
            self, self.on_gamepad_key_press
        )

    def on_gamepad_key_press(self, args):
        print(args)
        if args['key'] != GamepadKeyType.KEY_RS or args['screenName'] != 'hud_screen':
            return
        is_down = args['isDown'] == '1'
        if is_down:
            self.interaction.on_down(force_show_ready_ui=True, show_tip=True)
        else:
            self.interaction.on_up()
