# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

try:
	from ..client.interaction.InteractionTouch import InteractionTouch
except:
	pass

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

path_btn = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/btn_mark"


class MarkHudScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.interaction = param['interaction']  # type: InteractionTouch | None

		self.process_binding = self.override_process_binding

	def override_process_binding(self, screen_name):
		print('MarkHudScreenNode.process_binding')
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
		btn_control = self.GetBaseUIControl(path_btn)
		if btn_control:
			touch_mark_button_offset = self.interaction.session.config['interaction']['touch_mark_button_offset']
			if touch_mark_button_offset:
				btn_control.SetFullPosition('x', {"absoluteValue": touch_mark_button_offset[0]})
				btn_control.SetFullPosition('y', {"absoluteValue": touch_mark_button_offset[1]})
			btn_control.asButton().AddTouchEventParams({"isSwallow": 0})
			btn_control.asButton().SetButtonTouchDownCallback(self.on_btn_touch_down)
			btn_control.asButton().SetButtonTouchUpCallback(self.on_btn_touch_up)
			btn_control.asButton().SetButtonTouchCancelCallback(self.on_btn_touch_up)
		else:
			print("MarkHudScreenNode Create btn_control is None")

	def on_btn_touch_down(self, args):
		self.interaction.on_btn_touch_down(args)

	def on_btn_touch_up(self, args):
		self.interaction.on_btn_touch_up(args)

	@ViewBinder.binding(ViewBinder.BF_BindString, "#tick_refresh_auxiliary")
	def on_frame_tick(self):
		if self.interaction.session:
			self.interaction.session.on_frame_tick()

	# region TOGGLE

	@ViewBinder.binding(ViewBinder.BF_BindInt, "#mark_type_select_stack.item_count")
	def on_toggle_grid_resize(self):
		return len(self.interaction.session.config['marks'])

	@ViewBinder.binding_collection(ViewBinder.BF_BindString, "mark_type_select_stack", "#label_name.text")
	def on_refresh_item_label(self, index):
		return self.interaction.session.config['marks'][index]['name']

	@ViewBinder.binding_collection(ViewBinder.BF_BindString, "mark_type_select_stack", "#texture")
	def on_refresh_item_icon(self, index):
		texture = self.interaction.session.config['marks'][index]['texture']
		return texture

	@ViewBinder.binding_collection(ViewBinder.BF_BindColor, "mark_type_select_stack", "#color")
	def on_refresh_item_icon(self, index):
		color = self.interaction.session.config['marks'][index]['color']
		return color[0] / 255.0, color[1] / 255.0, color[2] / 255.0

	@ViewBinder.binding_collection(ViewBinder.BF_BindBool, "mark_type_select_stack", "#selected")
	def on_refresh_toggle_selected(self, index):
		return self.interaction.holding_mark_type_index == index

	@ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#mark_type_toggle")
	def on_toggle_changed(self, args):
		index = args['index']
		if index >= len(self.interaction.session.config['marks']):
			index = 0
		self.interaction.holding_mark_type_auto = False
		self.interaction.holding_mark_type_index = index

	# endregion

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
