# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from mod.client.ui.controls.baseUIControl import BaseUIControl

try:
	from ..client.interaction.InteractionTouch import InteractionTouch
except:
	pass

ViewBinder = clientApi.GetViewBinderCls()
ViewRequest = clientApi.GetViewViewRequestCls()
ScreenNode = clientApi.GetScreenNodeCls()

path_btn = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/btn_mark"
path_select = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel/mark_type_select"
path_select_stack = path_select + "/mark_type_select_stack"
path_select_current = path_select + "/mark_type_select_current"

class MarkHudScreenNode(ScreenNode):
	def __init__(self, namespace, name, param):
		ScreenNode.__init__(self, namespace, name, param)
		self.interaction = param['interaction']  # type: InteractionTouch | None

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
		self.update_select_current()
		if self.interaction.session:
			self.interaction.session.on_frame_tick()

	# region TOGGLE

	def init_select(self):
		for child_path in self.GetAllChildrenPath(path_select_stack):
			self.RemoveChildControl(self.GetBaseUIControl(child_path))
		stack = self.GetBaseUIControl(path_select_stack)
		select = self.GetBaseUIControl(path_select)
		select.SetVisible(True)
		marks = self.interaction.session.config['marks']
		index = 0
		for mark in marks:
			child_name = "mark_type_select_toggle_item_" + str(index)
			item_control = self.CreateChildControl(
				"mark_hud.mark_type_select_toggle_item",
				child_name,
				stack,
				False
			)  # type: BaseUIControl
			item_control.asButton().AddTouchEventParams({"isSwallow": False})
			item_control.asButton().SetButtonTouchUpCallback(self.on_toggle_changed)
			icon = item_control.GetChildByName("icon")  # type: BaseUIControl
			icon.asImage().SetSprite(mark['texture'])
			icon.asImage().SetSpriteColor((mark['color'][0] / 255.0, mark['color'][1] / 255.0, mark['color'][2] / 255.0))
			label = item_control.GetChildByName("label")  # type: BaseUIControl
			label.asLabel().SetText(mark['name'])
			index += 1
		self.UpdateScreen()

	def destroy_select(self):
		select = self.GetBaseUIControl(path_select)
		select.SetVisible(False)
		for child_path in self.GetAllChildrenPath(path_select_stack):
			self.RemoveChildControl(self.GetBaseUIControl(child_path))

	def update_select_current(self):
		control_current = self.GetBaseUIControl(path_select_current)
		if self.interaction.holding:
			control_stack = self.GetBaseUIControl(path_select_stack)
			stack_pos = control_stack.GetPosition()
			control_current.SetVisible(True)
			index = self.interaction.holding_mark_type_index
			if index < len(self.interaction.session.config['marks']):
				child_path = path_select_stack + "/mark_type_select_toggle_item_" + str(index)
				child_control = self.GetBaseUIControl(child_path)
				if child_control:
					pos = child_control.GetPosition()
					new_pos = (pos[0] + stack_pos[0], pos[1] + stack_pos[1])
					if new_pos != control_current.GetPosition():
						control_current.RemoveAnimation("offset")
						clientApi.RegisterUIAnimations({
							"namespace": "mark_hud",
							"mark_type_select_current_move": {
								"anim_type": "offset",
								"duration": 0.05,
								"from": control_current.GetPosition(),
								"to": new_pos,
								"next": ""
							}
						}, True)
						#control_current.SetPosition(new_pos)
						control_current.SetAnimation("offset", "mark_hud", "mark_type_select_current_move", True)
		else:
			control_current.SetVisible(False)

	def on_toggle_changed(self, args):
		button_path = args['ButtonPath']
		index = int(button_path.split('_')[-1])
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
