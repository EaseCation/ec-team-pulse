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
        self.ui_key = None  # type: str | None

    def show(self):
        try:
            # 从对象池获取ui_key（替代原有的时间戳生成方式）
            if not self.session or not self.session.client or not hasattr(self.session.client, 'ui_key_pool'):
                print("[ClientMarkPoint] 错误: client或ui_key_pool未初始化")
                return

            self.ui_key = self.session.client.ui_key_pool.acquire()
            if not self.ui_key:
                print("[ClientMarkPoint] 错误: 无法从对象池获取ui_key")
                return

            self.ui_node = clientApi.CreateUI(
                mod_name,
                self.ui_key,
                {
                    "isHud": 1,
                    "autoScale": 1,
                    "bindWorldPosition": (comp_game.GetCurrentDimension(), (self.pos[0], self.pos[1], self.pos[2])),
                    "color": self.color,
                    "texture": self.texture,
                    "ui_key": self.ui_key,  # 传递ui_key供Destroy时归还
                    "client": self.session.client  # 传递client引用
                }
            )
            if self.ui_node:
                self.ui_node.session = self.session
                print("[ClientMarkPoint] 标点UI创建成功: key={}, pos={}".format(self.ui_key, self.pos))

                # 根据标点类型从配置中获取持续时间设置自动销毁定时器（兜底机制）
                def destroy_by_timer(mark_point):
                    """定时器回调：检查并销毁UI（兜底机制）"""
                    # 检查标点是否已被手动销毁
                    if mark_point.ui_node is None:
                        return

                    # 定时器到期，销毁UI
                    try:
                        mark_point.ui_node.pending_destroy()
                        print("[ClientMarkPoint] 定时器兜底销毁UI: key={}, point_id={}".format(
                            getattr(mark_point, 'ui_key', 'unknown'), mark_point.point_id))
                    except Exception as e:
                        print("[ClientMarkPoint] 定时器销毁UI失败: {}".format(str(e)))
                    finally:
                        mark_point.ui_node = None

                comp = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId())
                
                # 从session配置中获取当前标点类型的持续时间
                duration = 30.0  # 默认30秒
                if self.session and hasattr(self.session, 'config') and self.session.config:
                    marks = self.session.config.get('marks', [])
                    for mark_config in marks:
                        if mark_config.get('type') == self.mark_type:
                            duration = float(mark_config.get('duration', 30))
                            break
                
                # 设置定时器（传递ClientMarkPoint对象，让定时器可以检查销毁状态）
                comp.AddTimer(duration, destroy_by_timer, self)

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
        # 立即销毁UI，不依赖定时器
        # 当服务端主动移除标点时（如超过数量限制），需要立即清理UI
        if self.ui_node:
            try:
                self.ui_node.pending_destroy()
                print("[ClientMarkPoint] 标点UI已立即销毁: key={}".format(getattr(self, 'ui_key', 'unknown')))
            except Exception as e:
                print("[ClientMarkPoint] 销毁UI时出错: {}".format(str(e)))
            finally:
                self.ui_node = None

        # ui_key的归还由MarkPointScreenNode的Destroy生命周期函数处理
        # 这样可以确保在UI真正从引擎中移除后才归还，避免冲突
        self.ui_key = None

        # 调试信息
        print("[ClientMarkPoint] 标点 {} 已销毁 (类型: {}, 创建者: {})".format(
            self.point_id, self.mark_type, self.owner))
