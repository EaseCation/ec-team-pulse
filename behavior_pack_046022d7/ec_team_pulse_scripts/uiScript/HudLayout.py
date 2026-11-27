# -*- coding: utf-8 -*-
"""
玩家自定义 HUD 按钮布局（本地配置 ec_hud_layout_v1）的读取与应用。
存储格式与 ecnukkituimod 的按钮布局编辑器共用；本包是独立 mod，不 import ecnukkituimod。
"""
import mod.client.extraClientApi as clientApi

HUD_LAYOUT_CONFIG_KEY = "ec_hud_layout_v1"

# 字段名、最小值、最大值
_FIELD_LIMITS = (
	("x", 0.0, 1.0),
	("y", 0.0, 1.0),
	("scale", 0.5, 2.0),
	("alpha", 0.2, 1.0),
)

try:
	_NUMBER_TYPES = (int, long, float)
except NameError:
	_NUMBER_TYPES = (int, float)

# common.button 模板中随按钮状态切换的贴图子控件
_STATE_IMAGES = ("default", "hover", "pressed")


def _read_number(value, low, high):
	if isinstance(value, bool) or not isinstance(value, _NUMBER_TYPES):
		return None
	number = float(value)
	if number != number or number < low or number > high:
		return None
	return number


def load_button_layout(key):
	"""
	读取指定按钮的布局，返回 {"x", "y", "scale", "alpha"}。
	没有该按钮的配置、读取失败或数据非法时返回 None。
	"""
	try:
		comp_config = clientApi.GetEngineCompFactory().CreateConfigClient(clientApi.GetLevelId())
		data = comp_config.GetConfigData(HUD_LAYOUT_CONFIG_KEY, True)
		if not isinstance(data, dict) or data.get("version") != 1:
			return None
		buttons = data.get("buttons")
		if not isinstance(buttons, dict):
			return None
		item = buttons.get(key)
		if not isinstance(item, dict):
			return None
		layout = {}
		for name, low, high in _FIELD_LIMITS:
			number = _read_number(item.get(name), low, high)
			if number is None:
				return None
			layout[name] = number
		return layout
	except Exception:
		return None


# 界面的全屏层：部分 mod 界面的 GetGlobalPosition 整体带有平移误差，相对同一界面的全屏层计算即可抵消
_FULLSCREEN_PATH = "/variables_button_mappings_and_controls"


def _global_position(screen, path):
	try:
		control = screen.GetBaseUIControl(path)
		position = control.GetGlobalPosition() if control else None
		if position is None:
			return None
		x, y = float(position[0]), float(position[1])
	except Exception:
		return None
	if x != x or y != y:
		return None
	return x, y


def _parent_global_position(screen, control_path):
	"""父控件左上角相对同一界面全屏层的坐标（即全屏坐标）；父控件为全屏根或接口不可用时取 (0, 0)。"""
	parent_path = control_path.rsplit("/", 1)[0]
	if not parent_path:
		return 0.0, 0.0
	parent = _global_position(screen, parent_path)
	if parent is None:
		return 0.0, 0.0
	layer = _global_position(screen, _FULLSCREEN_PATH)
	if layer is None:
		return parent
	return parent[0] - layer[0], parent[1] - layer[1]


def apply_button_layout(screen, button_path, key, default_size, extra_children=None):
	"""
	把本地布局应用到 common.button 按钮：锚点 top_left，尺寸 = 默认尺寸 × scale，
	offset = (x·W − w/2 − PX, y·H − h/2 − PY)，(PX, PY) 为父控件左上角的全屏坐标，贴图透明度 = alpha。
	extra_children：{子控件名: 默认尺寸}，这些额外的图片子控件随 scale 同比缩放并使用同一透明度。
	已应用返回 True；没有配置或无法应用时返回 False，调用方保持默认布局。
	"""
	layout = load_button_layout(key)
	if layout is None:
		return False
	control = screen.GetBaseUIControl(button_path)
	if control is None:
		return False
	try:
		screen_size = clientApi.GetEngineCompFactory().CreateGame(clientApi.GetLevelId()).GetScreenSize()
		screen_width, screen_height = float(screen_size[0]), float(screen_size[1])
	except Exception:
		return False
	if screen_width <= 0 or screen_height <= 0:
		return False

	scale = layout["scale"]
	alpha = layout["alpha"]
	width = float(default_size[0]) * scale
	height = float(default_size[1]) * scale
	parent_x, parent_y = _parent_global_position(screen, button_path)
	try:
		control.SetAnchorFrom("top_left")
		control.SetAnchorTo("top_left")
		control.SetSize((width, height))
		control.SetPosition((
			layout["x"] * screen_width - width / 2.0 - parent_x,
			layout["y"] * screen_height - height / 2.0 - parent_y,
		))
		for name in _STATE_IMAGES:
			child = screen.GetBaseUIControl(button_path + "/" + name)
			if child:
				child.SetSize((width, height))
				child.asImage().SetAlpha(alpha)
		if extra_children:
			for name, child_size in extra_children.items():
				child = screen.GetBaseUIControl(button_path + "/" + name)
				if child:
					child.SetSize((float(child_size[0]) * scale, float(child_size[1]) * scale))
					child.asImage().SetAlpha(alpha)
	except Exception:
		return False
	return True
