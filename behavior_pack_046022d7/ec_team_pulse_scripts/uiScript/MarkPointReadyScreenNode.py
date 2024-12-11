# -*- coding: utf-8 -*-
import time

import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

path_hold = '/hold'

class MarkPointReadyScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.destroy_time = 0
		self.process_binding = self.override_process_binding

	def override_process_binding(self, screen_name):
		print('MarkPointReadyScreenNode.process_binding')
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

	def set_color(self, color):
		hold_img = self.GetBaseUIControl(path_hold + '/image')
		if hold_img:
			hold_img.asImage().SetSpriteColor((float(color[0]) / 255, float(color[1]) / 255, float(color[2]) / 255))

	def on_release(self):
		self.destroy_time = time.time() + 1
		self.GetBaseUIControl(path_hold).SetVisible(False)
		self.CreateChildControl("mark_point_ready.check", "check")

	def Update(self):
		if self.destroy_time and time.time() > self.destroy_time:
			self.SetRemove()