from .wx import (
    WeChat,
    Chat,
    LoginWnd,
    get_wx_clients
)
from .param import WxParam
import pythoncom

pythoncom.CoInitialize()

__all__ = [
    'WeChat',
    'Chat',
    'WxParam',
    'LoginWnd',
    'get_wx_clients'
]
