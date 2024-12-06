# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi
import math
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())
comp_camera = clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId())

spawn_animation_duration = 0.3


def calculate_projection(distance, segment_length, screen_height, fov=90.0):
	"""
    计算在第一视角下，y轴线段在屏幕上的投影长度。

    参数：
        distance (float): 观察者到线段的距离。
        segment_length (float): y 轴上的线段长度。
        screen_height (int): 屏幕的高度（以像素为单位）。
        fov (float): 视场角（以度数表示），默认值为 90。

    返回：
        float: y轴线段在屏幕上的投影长度。
    """
	# 将视角转换为弧度
	fov_radians = math.radians(fov)

	# 计算屏幕上 1 单位距离对应的投影比例
	# 假设视角的中心点在屏幕中央，高度的一半用来计算
	scale_factor = (screen_height / 2.0) / math.tan(fov_radians / 2.0)

	# 投影长度 = 线段长度 * 投影比例 / 距离
	projected_length = (segment_length * scale_factor) / distance

	return projected_length


class MarkPointScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.texture = param['texture']
		self.color = param['color']
		self.spawn_percent = 0.0
		self.spawn_time = 0

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		img_control = self.GetBaseUIControl("/stack_panel/panel/image")
		if img_control:
			img_control.asImage().SetSprite(self.texture)
			img_control.asImage().SetSpriteColor((float(self.color[0]) / 255, float(self.color[1]) / 255, float(self.color[2]) / 255))
		else:
			print("MarkPointScreenNode Create img_control is None")
		bg_control = self.GetBaseUIControl("/stack_panel/panel/bg")
		if bg_control:
			bg_control.asImage().SetSpriteColor((float(self.color[0]) / 255, float(self.color[1]) / 255, float(self.color[2]) / 255))
		else:
			print("MarkPointScreenNode Create bg_control is None")
		self.spawn_time = time.time()
		print('mark spawn', self.color)

	def get_frame_height(self):
		dimension, pos = self.GetBindWorldPosition()
		# 获取玩家位置
		comp_pos = clientApi.GetEngineCompFactory().CreatePos(clientApi.GetLocalPlayerId())
		player_pos = comp_pos.GetPos()
		# 计算玩家到点的距离
		distance = math.sqrt((pos[0] - player_pos[0]) ** 2 + (pos[1] - player_pos[1]) ** 2 + (pos[2] - player_pos[2]) ** 2)
		# 计算点在屏幕上的投影长度
		screen_height = comp_game.GetScreenSize()[1]
		segment_length = 1.5
		projected_length = calculate_projection(distance, segment_length, screen_height, comp_camera.GetFov())
		return projected_length

	@ViewBinder.binding(ViewBinder.BF_BindString, "#tick_refresh_auxiliary")
	def on_frame_tick(self):
		if self.spawn_percent < 1:
			self.spawn_percent = math.sin(min(1.0, (time.time() - self.spawn_time) / spawn_animation_duration) * (math.pi / 2))
		panel_control = self.GetBaseUIControl("/stack_panel/padding")
		panel_control.SetFullSize("y", {
			"absoluteValue": self.get_frame_height() * self.spawn_percent
		})

	def Destroy(self):
		"""
		@description UI销毁时调用
		"""
		pass

	def OnActive(self):
		"""
		@description UI重新回到栈顶时调用
		"""
		pass

	def OnDeactive(self):
		"""
		@description 栈顶UI有其他UI入栈时调用
		"""
		pass
