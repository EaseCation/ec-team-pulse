# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

path_btn = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/btn_mark"


class MarkHudScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.session = None

	def Create(self):
		"""
		@description UI创建成功时调用
		"""
		btn_control = self.GetBaseUIControl(path_btn)
		if btn_control:
			btn_control.asButton().AddTouchEventParams({"isSwallow": 0})
			btn_control.asButton().SetButtonTouchDownCallback(self.on_btn_touch_down)
			btn_control.asButton().SetButtonTouchUpCallback(self.on_btn_touch_up)
			btn_control.asButton().SetButtonTouchCancelCallback(self.on_btn_touch_up)
		else:
			print("MarkHudScreenNode Create btn_control is None")

	def on_btn_touch_down(self, args):
		print("on_btn_touch_down", args)

	def on_btn_touch_up(self, args):
		print("on_btn_touch_up", args)

	@ViewBinder.binding(ViewBinder.BF_BindString, "#tick_refresh_auxiliary")
	def on_frame_tick(self):
		if self.session:
			self.session.on_frame_tick()

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
