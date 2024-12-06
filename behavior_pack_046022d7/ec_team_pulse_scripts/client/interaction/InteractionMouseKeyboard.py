# -*- coding: utf-8 -*-
import time

try:
    from ..MarkPointSession import MarkPointSession
except:
    pass
import mod.client.extraClientApi as clientApi
import math
from ...Raycaster import Vector3, Raycaster, TYPE_BLOCK, TYPE_ENTITY
from ...config import mod_name, mark_point_ready_ui_name
from ...uiScript.MarkPointReadyScreenNode import MarkPointReadyScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())

double_click_time = 0.5

class InteractionMouseKeyboard(object):

    def __init__(self, session):
        self.session = session  # type: MarkPointSession

        self.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnScriptTickClient',
            self, self.on_tick
        )
        self.session.client.ListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnMouseMiddleDownClientEvent',
            self, self.on_mouse_middle_down)

        self.last_mark_time = 0
        self.point_ready_ui = None  # type: MarkPointReadyScreenNode | None

    def destroy(self):
        self.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'OnScriptTickClient',
            self, self.on_tick
        )
        self.session.client.UnListenForEvent(
            clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
            'RightClickBeforeClientEvent',
            self, self.on_mouse_middle_down
        )

    def create_point_ready_ui(self, pos):
        self.point_ready_ui = clientApi.CreateUI(
            mod_name,
            mark_point_ready_ui_name,
            {
                "isHud": 1,
                "autoScale": 0,
                "bindWorldPosition": (comp_game.GetCurrentDimension(), (pos[0], pos[1], pos[2])),
            }
        )

    def on_mouse_middle_down(self, args):
        player_id = clientApi.GetLocalPlayerId()
        pos_comp = clientApi.GetEngineCompFactory().CreatePos(player_id)
        rot_comp = clientApi.GetEngineCompFactory().CreateRot(player_id)
        player_pos = Vector3(*pos_comp.GetPos())
        pitch, yaw = rot_comp.GetRot()
        # Convert rotation to direction vector
        pitch_radians = math.radians(pitch)
        yaw_radians = math.radians(yaw)
        direction = Vector3(-math.sin(yaw_radians) * math.cos(pitch_radians),
                            -math.sin(pitch_radians),
                            math.cos(yaw_radians) * math.cos(pitch_radians))
        raycaster = Raycaster(player_pos, direction)
        hits = raycaster.raytraceAll()
        if hits:
            for hit in hits:
                if hit.target.typeOfHit == TYPE_BLOCK:
                    pos = (hit.target.hitVector.x, hit.target.hitVector.y, hit.target.hitVector.z)
                    now = time.time()
                    negative = now - self.last_mark_time < double_click_time
                    self.try_mark_point(pos, args['isDown'] == 0, negative)
                elif hit.target.typeOfHit == TYPE_ENTITY:
                    comp_pos = clientApi.GetEngineCompFactory().CreatePos(hit.target.entityHit)
                    pos = comp_pos.GetPos()
                    pos = (pos[0], pos[1] + 0.5, pos[2])
                    self.try_mark_point(pos, args['isDown'] == 0, True)
                break

    def try_mark_point(self, pos, confirm, negative=False):
        now = time.time()
        if now - self.last_mark_time < double_click_time:
            self.session.remove_last_point()
        elif confirm:
            self.create_point_ready_ui(pos)
        if confirm:
            self.last_mark_time = now
            if negative:
                mark_config = self.session.config['marks'][1]
            else:
                mark_config = self.session.config['marks'][0]
            self.session.add_point(pos, mark_config)

    def on_tick(self):
        pass