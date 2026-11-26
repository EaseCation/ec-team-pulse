# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod.common.minecraftEnum import KeyBoardType


class InteractionMouseKeyboard:

    def __init__(self, interaction):
        self.interaction = interaction
        self._hold_key_down = False
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
        if self.interaction.session.interaction_config['keyboard_hold'] != KeyBoardType.KEY_MOUSE_Middle:
            return
        self._on_hold_key(args['isDown'] in (1, '1'))

    def _on_hold_key(self, is_down, can_start=True):
        # Consume the press even if another input already owns the selection.
        if self._hold_key_down == is_down:
            return
        self._hold_key_down = is_down
        if is_down:
            if can_start:
                self.interaction.on_down(self, show_tip=False)
        else:
            self.interaction.on_up(self)

    def on_key_press_in_game(self, args):
        hold_key = self.interaction.session.interaction_config['keyboard_hold']
        if hold_key != KeyBoardType.KEY_MOUSE_Middle and args['key'] == str(hold_key):
            is_down = args['isDown'] in (1, '1')
            self._on_hold_key(is_down, can_start=args.get('screenName') == 'hud_screen')
            return
        if not self.interaction.holding:
            return
        if args['key'] != str(self.interaction.session.interaction_config['keyboard_switch']) or args['screenName'] != 'hud_screen':
            return
        if args['isDown'] == '0':
            self.interaction.holding_mark_type_auto = False
            self.interaction.holding_mark_type_index += 1
            if self.interaction.holding_mark_type_index >= len(self.interaction.session.config['marks']):
                self.interaction.holding_mark_type_index = 0
