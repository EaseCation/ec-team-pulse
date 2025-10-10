# -*- coding: utf-8 -*-
"""
UIKey对象池管理器
解决标点UI注册时的内存泄露问题，通过复用ui_key减少资源浪费
"""
import mod.client.extraClientApi as clientApi


class UIKeyPool(object):
    """UIKey对象池 - 单例模式"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        """单例模式：确保全局只有一个对象池实例"""
        if cls._instance is None:
            cls._instance = super(UIKeyPool, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, mod_name, ui_cls_path, ui_def):
        """
        初始化UIKey对象池
        :param mod_name: 模组名称
        :param ui_cls_path: UI类路径
        :param ui_def: UI定义路径
        """
        # 避免重复初始化
        if self._initialized:
            return

        self.mod_name = mod_name
        self.ui_cls_path = ui_cls_path
        self.ui_def = ui_def

        # 池状态
        self.available_keys = []  # 可用的ui_key列表
        self.used_keys = set()    # 正在使用的ui_key集合
        self.total_registered = 0  # 总共注册的ui_key数量

        self._initialized = True
        print("[UIKeyPool] 对象池初始化完成")

    def _generate_ui_key(self, index):
        """
        生成ui_key名称
        :param index: key的索引编号
        :return: ui_key字符串
        """
        return "mark_point_pool_{}".format(index)

    def acquire(self):
        """
        从池中获取一个可用的ui_key，如果池为空则创建新的
        :return: ui_key字符串，如果创建失败返回None
        """
        # 如果有可用的key，直接复用
        if self.available_keys:
            ui_key = self.available_keys.pop(0)
            self.used_keys.add(ui_key)
            print("[UIKeyPool] 复用 ui_key: {} (已用: {})".format(ui_key, len(self.used_keys)))
            return ui_key

        # 池为空，创建新的key
        ui_key = self._generate_ui_key(self.total_registered)
        try:
            clientApi.RegisterUI(self.mod_name, ui_key, self.ui_cls_path, self.ui_def)
            self.total_registered += 1
            self.used_keys.add(ui_key)
            print("[UIKeyPool] 创建 ui_key: {} (已用: {})".format(ui_key, len(self.used_keys)))
            return ui_key
        except Exception as e:
            print("[UIKeyPool] 创建 ui_key {} 失败: {}".format(ui_key, str(e)))
            return None

    def release(self, ui_key):
        """
        归还ui_key到池中供复用
        :param ui_key: 要归还的ui_key
        :return: 是否归还成功
        """
        if ui_key is None:
            return False

        if ui_key not in self.used_keys:
            print("[UIKeyPool] 警告: 尝试归还未被借用的 ui_key: {}".format(ui_key))
            return False

        self.used_keys.remove(ui_key)
        self.available_keys.append(ui_key)
        print("[UIKeyPool] 归还 ui_key: {} (已用: {})".format(ui_key, len(self.used_keys)))
        return True
