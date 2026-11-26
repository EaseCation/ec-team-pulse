# -*- coding: utf-8 -*-
from mod.common.minecraftEnum import GamepadKeyType
import mod.client.extraClientApi as clientApi

class InteractionGamepad(object):

    def __init__(self, interaction):
        self.interaction = interaction
        self.interaction.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(),
            clientApi.GetEngineSystemName(),
            'OnGamepadKeyPressClientEvent',
            self,
            self.on_gamepad_key_press
        )

        # 需要按住的手柄键列表
        gamepad_hold_keys = interaction.session.interaction_config['gamepad_hold']  # type: list[GamepadKeyType]
        # key_states 用于记录这些键是按下(True)还是松开(False)
        self.key_states = {key: False for key in gamepad_hold_keys}

        # _was_all_down 标记是否“所有目标键已经全部处于按下状态”
        self._was_all_down = False

    def destroy(self):
        self.interaction.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(),
            clientApi.GetEngineSystemName(),
            'OnGamepadKeyPressClientEvent',
            self,
            self.on_gamepad_key_press
        )

    def on_gamepad_key_press(self, args):
        """
        逻辑说明：
        1. 如果所有 target key 都处于按下状态（all(self.key_states.values())为True），
           且之前还没标记 _was_all_down，则触发 on_down() 并标记 _was_all_down=True。
        2. 如果当前按键是松开（is_down=False），检查之前是否是 _was_all_down=True：
           - 若是，则触发 on_up() 并标记 _was_all_down=False。
           - 若否，则说明还没到「全部按下后松开一个」的阶段，不触发 on_up。
        """
        key = args['key']
        is_down = (args['isDown'] == '1')

        # 如果当前 key 在要监控的按键列表中，则更新它的状态
        if key in self.key_states:
            self.key_states[key] = is_down

            # 当前是否所有按键都处于按下状态
            all_down_now = all(self.key_states.values())

            if all_down_now:
                # 如果现在所有按键都按下，但还没有标记 _was_all_down，则触发 on_down
                if not self._was_all_down:
                    self._was_all_down = True
                    self.interaction.on_down(self, force_show_ready_ui=True, show_tip=True)
            else:
                # 如果不是全部按下，但是 _was_all_down 为真，说明从「全部按下」转变为「松开某一个」
                if self._was_all_down and not is_down:
                    self.interaction.on_up(self)
                    self._was_all_down = False