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
pending_delay_time = 0.2

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

        self.point_ready_ui = None  # type: MarkPointReadyScreenNode | None
        self.last_click_time = 0
        self.pending_mark = None  # type: tuple[tuple[float, float, float], dict] | None
        self.pending_mark_apply_time = 0

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

    def create_point_ready_ui(self):
        if self.point_ready_ui is not None:
            self.point_ready_ui.SetRemove()
            self.point_ready_ui = None
        self.point_ready_ui = clientApi.CreateUI(
            mod_name,
            mark_point_ready_ui_name,
            {
                "isHud": 1,
                "autoScale": 0,
                #"bindWorldPosition": (comp_game.GetCurrentDimension(), (pos[0], pos[1], pos[2])),
            }
        )

    def on_mouse_middle_down(self, args):
        now = time.time()
        is_down = args['isDown'] == 1
        if is_down:
            if not self.pending_mark and now - self.last_click_time > double_click_time:
                self.create_point_ready_ui()
            return
        else:
            if self.point_ready_ui and self.point_ready_ui.destroy_time == 0:
                self.point_ready_ui.on_release()
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
                    if not self.pending_mark and now - self.last_click_time > double_click_time:  # 之前没点过，这次是第一次点击，所以延迟生效
                        self.pending_mark = (pos, self.session.config['marks'][0])
                        self.pending_mark_apply_time = now + pending_delay_time
                    else:  # 之前点过，而且还未生效，表示是双击，这次是第二次点击，所以立即生效（负面）
                        mark_config = self.session.config['marks'][1]
                        self.pending_mark = None
                        self.pending_mark_apply_time = 0
                        self.session.request_add_point(pos, mark_config)
                elif hit.target.typeOfHit == TYPE_ENTITY:
                    comp_pos = clientApi.GetEngineCompFactory().CreatePos(hit.target.entityHit)
                    pos = comp_pos.GetPos()
                    pos = (pos[0], pos[1] + 0.5, pos[2])
                    self.pending_mark = None
                    self.pending_mark_apply_time = 0
                    self.session.request_add_point(pos, self.session.config['marks'][1])  # 直接负面效果
                break
            self.last_click_time = time.time()

    def on_tick(self):
        if 0 < self.pending_mark_apply_time < time.time() and self.pending_mark:
            pos = self.pending_mark[0]
            mark_config = self.pending_mark[1]
            self.session.request_add_point(pos, mark_config)
            self.pending_mark = None
            self.pending_mark_apply_time = 0