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
        gamepad_hold_keys = interaction.session.interaction_config['gamepad_hold']  # type: list[GamepadKeyType]
        self.key_states = {key: False for key in gamepad_hold_keys}

    def destroy(self):
        self.interaction.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnGamepadKeyPressClientEvent',
            self, self.on_gamepad_key_press
        )

    def on_gamepad_key_press(self, args):
        key = args['key']
        is_down = args['isDown'] == '1'

        if key in self.key_states:
            self.key_states[key] = is_down

            if all(self.key_states.values()):
                self.interaction.on_down(force_show_ready_ui=True, show_tip=True)
            elif not is_down:
                self.interaction.on_up()