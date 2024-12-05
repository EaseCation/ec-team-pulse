# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()


class MarkPointScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.texture = param['texture']
		self.color = param['color']

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		img_control = self.GetBaseUIControl("/panel/image")
		if img_control:
			img_control.asImage().SetSprite(self.texture)
			img_control.asImage().SetSpriteColor((float(self.color[0]) / 255, float(self.color[1]) / 255, float(self.color[2]) / 255))
		else:
			print("MarkPointScreenNode Create img_control is None")

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
