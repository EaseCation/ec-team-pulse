if False:
    from .server.ECTeamPulseServer import ECTeamPulseServer
    from .server.ServerMarkPointSession import ServerMarkPointSession

import mod.server.extraServerApi as serverApi
from .config import *


def get_system():
    # type: () -> None | ECTeamPulseServer
    return serverApi.GetSystem(mod_name, server_system_name)

def create_session(config, default_interaction_config):
    """
    服务端API
    创建一个新的标点会话
    该函数返回创建的ServerMarkPointSession对象
    如果系统未初始化或在客户端中调用，则返回None
    :param config: 格式详见 config.py
    :param default_interaction_config: 格式详见 config.py
    :rtype: ServerMarkPointSession | None
    """
    system = get_system()
    if system:
        return system.create_session(config, default_interaction_config)
    return None

def remove_session(session_id):
    """
    服务端API
    移除一个标点会话
    如果系统未初始化或在客户端中调用，则无效
    :param session_id: 会话ID 由 create_session 返回
    :return: None
    """
    system = get_system()
    if system:
        system.remove_session(session_id)

def get_all_sessions():
    """
    服务端API
    获取所有标点会话
    如果系统未初始化或在客户端中调用，则返回空字典
    :rtype: dict[int, ServerMarkPointSession]
    :return: 所有会话的字典，键为会话ID，值为 ServerMarkPointSession 对象
    """
    system = get_system()
    if system:
        return system.sessions
    return {}

def get_player_session(player_name):
    """
    服务端API
    获取玩家所在的标点会话
    如果玩家不在任何会话中，或系统未初始化，或在客户端中调用，则返回None
    :param player_name: 玩家名称
    :return: 玩家所在的 ServerMarkPointSession 对象，或None
    :rtype: ServerMarkPointSession | None
    """
    system = get_system()
    if system:
        session_id = system.player_to_session.get(player_name)
        if session_id is not None:
            return system.sessions.get(session_id)
    return None