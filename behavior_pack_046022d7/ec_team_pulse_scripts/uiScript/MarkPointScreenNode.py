# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi
import math

try:
	from ..client.MarkPointSession import MarkPointSession
except:
	pass

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

comp_game = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLocalPlayerId())
comp_camera = clientApi.GetEngineCompFactory().CreateCamera(clientApi.GetLevelId())

class MarkPointScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.session = None  # type: MarkPointSession | None
		self.texture = param['texture']
		self.color = param['color']
		self.destroy_time = 0
		self.process_binding = self.override_process_binding

	def override_process_binding(self, screen_name):
		print('MarkPointScreenNode.process_binding')
		for key in dir(self):
			func = getattr(self, key)
			if hasattr(func, 'collection_name'):
				self._process_collection(func, screen_name)
			elif hasattr(func, 'binding_flags'):
				self._process_default(func, screen_name)


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
		padding_control = self.GetBaseUIControl("/stack_panel/padding")
		if padding_control:
			padding_control.asImage().SetSpriteColor((float(self.color[0]) / 255, float(self.color[1]) / 255, float(self.color[2]) / 255))
		else:
			print("MarkPointScreenNode Create padding_control is None")
		print('mark spawn', self.color)

	def Update(self):
		if self.destroy_time and time.time() > self.destroy_time:
			self.SetRemove()
			return
		# 动态显示距离文字
		if self.session and self.session.config['show_distance_pixels']:
			dimension, pos = self.GetBindWorldPosition()
			# 获取玩家位置
			comp_pos = clientApi.GetEngineCompFactory().CreatePos(clientApi.GetLocalPlayerId())
			player_pos = comp_pos.GetPos()
			# 计算玩家到点的距离
			distance = math.sqrt((pos[0] - player_pos[0]) ** 2 + (pos[1] - player_pos[1]) ** 2 + (pos[2] - player_pos[2]) ** 2)
			show_distance_pixels = self.session.config['show_distance_pixels']
			main_panel = self.GetBaseUIControl("/stack_panel/panel")
			panel_x, panel_y = main_panel.GetGlobalPosition()
			panel_width, panel_height = main_panel.GetSize()
			panel_x += panel_width / 2
			panel_y += panel_height / 2
			screen_width, screen_height = comp_game.GetScreenSize()
			distance_label = self.GetBaseUIControl("/stack_panel/panel/distance_label")
			if abs(screen_width / 2 - panel_x) <= show_distance_pixels and abs(screen_height / 2 - panel_y) <= show_distance_pixels:
				distance_label.SetVisible(True)
				distance_label.asLabel().SetText(str(round(distance, 2)) + "m")
			else:
				distance_label.SetVisible(False)

	def pending_destroy(self):
		self.destroy_time = time.time() + 0.4
		self.GetBaseUIControl("/stack_panel").SetAnimation("alpha", "mark_point", "global_alpha_ease_out", True)

	def on_frame_tick(self):
		pass

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
