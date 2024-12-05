# -*- coding: utf-8 -*-
import math
import mod.client.extraClientApi as clientApi
from .ClientMarkPoint import ClientMarkPoint
from ..Raycaster import Vector3, Raycaster, TYPE_BLOCK, TYPE_ENTITY
from ..config import *

class MarkPointSession(object):

    def __init__(self, client, config):
        self.client = client
        self.config = config  # type: dict
        self.mark_points = {}  # type: dict[tuple[float, float, float], ClientMarkPoint]
        self.listen_events()
        self.init_ui()

    def listen_events(self):
        self.client.ListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'RightClickBeforeClientEvent',
                            self, self.on_right_click_before)

    def un_listen_events(self):
        self.client.UnListenForEvent(clientApi.GetEngineNamespace(), clientApi.GetEngineSystemName(),
                            'RightClickBeforeClientEvent',
                            self, self.on_right_click_before)

    def init_ui(self):
        clientApi.CreateUI(mod_name, mark_hud_ui_name, {"isHud": 1, })

    def add_point(self, pos, point_config):
        self.mark_points[pos] = ClientMarkPoint(pos, point_config['color'], point_config['texture'])
        self.mark_points[pos].show()

    def clear_all(self):
        for pos, mark_point in self.mark_points.items():
            mark_point.destroy()
        self.mark_points.clear()

    def on_right_click_before(self, args):
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
            self.clear_all()
            for hit in hits:
                if hit.target.typeOfHit == TYPE_BLOCK:
                    pos = hit.target.blockPos
                    pos = (pos[0] + 0.5, pos[1] + 1.5, pos[2] + 0.5)
                    self.add_point(pos, self.config['marks'][0])
                elif hit.target.typeOfHit == TYPE_ENTITY:
                    comp_pos = clientApi.GetEngineCompFactory().CreatePos(hit.target.entityHit)
                    pos = comp_pos.GetPos()
                    pos = (pos[0], pos[1] + 1.5, pos[2])
                    self.add_point(pos, self.config['marks'][1])
                break

    def destroy(self):
        self.clear_all()
        self.un_listen_events()