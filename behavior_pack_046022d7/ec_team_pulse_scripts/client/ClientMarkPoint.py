# -*- coding: utf-8 -*-
import random
import time

import mod.client.extraClientApi as clientApi

try:
    from .MarkPointSession import MarkPointSession
except:
    pass

from ..config import *
from ..MarkPoint import MarkPoint
from ..uiScript.MarkPointScreenNode import MarkPointScreenNode

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())
comp_audio = clientApi.GetEngineCompFactory().CreateCustomAudio(clientApi.GetLocalPlayerId())


class ClientMarkPoint(MarkPoint):

    def __init__(self, session, point_id, pos, owner, mark_type, color, texture, remove_time, sound_config):
        super(ClientMarkPoint, self).__init__(point_id, pos, owner, mark_type, color, texture, remove_time)
        self.session = session  # type: MarkPointSession
        self.sound_config = sound_config
        self.ui_node = None  # type: MarkPointScreenNode | None

    def show(self):
        try:
            # 使用时间戳确保UI key的唯一性，避免重复注册冲突
            import time
            timestamp = int(time.time() * 1000000)  # 微秒级时间戳
            self.ui_key = "waypoint_{}_{}_{}".format(self.mark_type, self.point_id, timestamp)
            
            # 检查UI是否已注册，如果已注册则先注销
            try:
                clientApi.RegisterUI(mod_name, self.ui_key, mark_point_ui_cls_path, mark_point_ui_def)
                print("[ClientMarkPoint] UI key {} 注册成功".format(self.ui_key))
            except Exception as reg_e:
                print("[ClientMarkPoint] UI注册失败: {} - 尝试不同的key".format(str(reg_e)))
                # 如果注册失败，使用随机数作为备用方案
                import random
                random_suffix = random.randint(100000, 999999)
                self.ui_key = "waypoint_{}_{}_{}_{}".format(self.mark_type, self.point_id, timestamp, random_suffix)
                clientApi.RegisterUI(mod_name, self.ui_key, mark_point_ui_cls_path, mark_point_ui_def)
                print("[ClientMarkPoint] 备用UI key {} 注册成功".format(self.ui_key))
            
            self.ui_node = clientApi.CreateUI(
                mod_name,
                self.ui_key,
                {
                    "isHud": 1,
                    "autoScale": 1,
                    "bindWorldPosition": (comp_game.GetCurrentDimension(), (self.pos[0], self.pos[1], self.pos[2])),
                    "color": self.color,
                    "texture": self.texture
                }
            )
            if self.ui_node:
                self.ui_node.session = self.session
                print("[ClientMarkPoint] 标点UI创建成功: key={}, pos={}".format(self.ui_key, self.pos))

                # 根据标点类型从配置中获取持续时间设置自动销毁定时器
                def destroy(ui_node):
                    if ui_node:
                        ui_node.pending_destroy()
                        print("[ClientMarkPoint] 定时器自动销毁UI: key={}".format(self.ui_key))
                
                comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
                
                # 从session配置中获取当前标点类型的持续时间
                duration = 30.0  # 默认30秒
                if self.session and hasattr(self.session, 'config') and self.session.config:
                    marks = self.session.config.get('marks', [])
                    for mark_config in marks:
                        if mark_config.get('type') == self.mark_type:
                            duration = float(mark_config.get('duration', 30))
                            print("[ClientMarkPoint] 从配置获取标点类型 {} 的持续时间: {}秒".format(self.mark_type, duration))
                            break
                    else:
                        print("[ClientMarkPoint] 未找到标点类型 {} 的配置，使用默认{}秒".format(self.mark_type, duration))
                else:
                    print("[ClientMarkPoint] 无法获取session配置，使用默认{}秒".format(duration))
                
                # 设置定时器
                comp.AddTimer(duration, destroy, self.ui_node)
                print("[ClientMarkPoint] 已设置{}秒后自动销毁UI".format(duration))

            else:
                print("[ClientMarkPoint] UI创建失败 - CreateUI返回None")
        except Exception as e:
            print("[ClientMarkPoint] UI创建异常: {}".format(str(e)))
            self.ui_node = None

    def play_sound(self):
        if self.sound_config:
            if type(self.sound_config) == dict:
                comp_audio.PlayCustomUIMusic(self.sound_config['name'], self.sound_config['volume'], self.sound_config['pitch'], False)
            elif type(self.sound_config) == list:
                for sound in self.sound_config:
                    comp_audio.PlayCustomUIMusic(sound['name'], sound['volume'], sound['pitch'], False)

    def is_expired(self):
        """检查标点是否已过期"""
        if self.remove_time is None:
            return False
        return time.time() > self.remove_time

    def destroy(self):
        # 注意：UI已通过定时器自动销毁（3秒后），这里只需要清理引用
        # 定时器会调用ui_node.pending_destroy()，所以不需要手动调用
        if self.ui_node:
            print("[ClientMarkPoint] 标点UI将通过定时器自动销毁: key={}".format(getattr(self, 'ui_key', 'unknown')))
            self.ui_node = None
        
        # 清理UI key引用
        if hasattr(self, 'ui_key') and self.ui_key:
            print("[ClientMarkPoint] UI key {} 已标记销毁".format(self.ui_key))
            self.ui_key = None
        
        # 清理调试信息
        print("[ClientMarkPoint] 标点 {} 已销毁 (类型: {}, 创建者: {}) - UI将通过定时器自动清理".format(
            self.point_id, self.mark_type, self.owner))
