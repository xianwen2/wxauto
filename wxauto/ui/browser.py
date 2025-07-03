#!/usr/bin/python3
# -*- coding:utf-8 -*-
# -------------------------------
# @author: dana
# @contact: xianwen_yao@163.com
# @file: uiplug.py
# @time: 2025/6/29 下午3:25
# @desc:内置浏览器相关
# -------------------------------
from wxauto.utils import (
    FindWindow,
    SetClipboardText
)
from wxauto.languages import *
from wxauto.ui.base import BaseUIWnd
from wxauto.uia import uiautomation as uia
from wxauto.uia import ControlFromHandle, PatternId
from wxauto.param import WxResponse, WxParam
from .component import SelectContactWnd
from wxauto.logger import wxlog
import time


class WxBrowser(BaseUIWnd):
    _ui_cls_name: str = 'Chrome_WidgetWin_0'
    _ui_name: str = '微信'

    def __init__(self, hwnd: int = None):
        if hwnd is None:
            hwnd = FindWindow(classname=self._ui_cls_name, name=self._ui_name)
        if hwnd:
            self.control = ControlFromHandle(hwnd)
        self.more_button = self.control.PaneControl(searchDepth=1, ClassName='').MenuItemControl(Name="更多")
        self.close_button = self.control.PaneControl(searchDepth=1, ClassName='').ButtonControl(Name="关闭")

    def _lang(self, text: str):
        return WECHAT_BROWSER.get(text, {WxParam.LANGUAGE: text}).get(WxParam.LANGUAGE)

    def search(self, url):
        search_btn_eles = [
            i for i in self.control.TabControl().GetChildren()
            if i.BoundingRectangle.height() == i.BoundingRectangle.width()
        ]
        t0 = time.time()
        while time.time() - t0 < 10:
            if search_btn_eles:
                search_btn_eles[0].Click()
                edit = self.control.TabControl().EditControl(Name='地址和搜索栏')
                SetClipboardText(url)
                edit.ShortcutPaste()
                edit.SendKeys('{Enter}')
                return True
            time.sleep(0.1)
        return False

    def forward(self, friend):
        """
        链接转发给其它人
        """
        t0 = time.time()
        while True:
            if time.time() - t0 > 10:
                # wxbrowser.PaneControl(searchDepth=1, ClassName='').ButtonControl(Name="关闭").Click()
                raise  # '[链接]无法获取url'
            self.more_button.Click()
            time.sleep(0.5)
            copyurl = self.control.PaneControl(ClassName='Chrome_WidgetWin_0').MenuItemControl(Name='转发给朋友')
            if copyurl.Exists(0):
                copyurl.Click()
                break
            self.control.PaneControl(ClassName='Chrome_WidgetWin_0').SendKeys('{Esc}')
        sendwnd = SelectContactWnd()
        return sendwnd.send(friend)

    def send_card(self, url, friend):
        try:
            if self.search(url):
                return self.forward(friend)
        except Exception as e:
            return WxResponse.failure(msg=str(e))
        finally:
            self.close()

    def close(self):
        try:
            self.close_button.Click(move=True, return_pos=False)
        except:
            pass


class WxVideo(WxBrowser):
    """
    视频号
    """

    def Show(self):
        """显示窗口"""
        self._show()

    def clear_search(self):
        search_clear_ele = self.control.EditControl(Name="搜索").GetNextSiblingControl()
        if search_clear_ele:
            # search_clear_ele.Click(move=True, return_pos=False)
            search_clear_ele.Click()  # 不占用鼠标
            time.sleep(0.5)
            wxlog.debug(f"""清空搜索框数据""")
        else:
            wxlog.debug(f"""搜索框内没用内容，不需要处理""")

    def search(self, text):
        self.clear_search()
        wxlog.debug(f"""[+]输入搜索内容:{text}""")
        # self.Show()
        search_edit_ele = self.control.EditControl(Name="搜索")
        t0 = time.time()
        while time.time() - t0 < 10:
            if search_edit_ele:
                # search_edit_ele.Click(move=True, return_pos=False)
                search_edit_ele.Click()
                search_edit_ele.SendKeys(text, api=False)
                search_edit_ele.SendKeys('{Enter}', api=False)
                wxlog.debug(f"""[-]输入搜索内容:{text}""")

                # # 不占用鼠标操作
                # search_edit_ele.SendKeys(text, api=True)
                # search_edit_ele.SendKeys('{Enter}', api=True)
                return True
            time.sleep(0.1)
        return False

    def get_more_channel_name(self):
        """
        单击获取更多视频号
        """
        _ele = self.control.TextControl(Name=self._lang("账号"))
        if not _ele.Exists():
            wxlog.warning("未找到视频号")
            return False
        _group_ele = _ele.GetParentControl().GetParentControl()
        first_account_count = len(_group_ele.GetChildren())
        more_but_ele = _group_ele.TextControl(Name=self._lang("更多"))
        if not more_but_ele.Exists():
            return True
        while True:
            # more_but_ele.Click(move=True, return_pos=False) # 占用鼠标
            more_but_ele.Click()  # 不占用鼠标
            if len(_group_ele.GetChildren()) > first_account_count:
                return True
            elif len(_group_ele.GetChildren()) == first_account_count:
                return True

    def get_all_channel_name(self):
        """
        获取所有视频号昵称
        """
        self.Show()
        self.get_more_channel_name()
        _account_parent_ele = self.control.TextControl(Name=self._lang("账号")).GetParentControl().GetParentControl()
        channel_names = []
        for _group in _account_parent_ele.GetChildren():
            if len(_group.GetChildren()) < 2:
                continue
            _name_ele = _group.GetChildren()[1]
            if _name_ele.Name and _name_ele.Name in [self._lang("账号"), self._lang("更多")]:
                continue
            if _name_ele.Name:
                channel_names.append(_name_ele.Name)
        return channel_names

    def select_channel_name(self, name) -> bool:
        """
        选择指定账号
        :param name:指定视频号昵称
        """
        # self.Show()
        self.get_more_channel_name()
        _ele = self.control.TextControl(Name=self._lang("账号")).GetParentControl().GetParentControl().GroupControl(
            Name=name)
        if not _ele.Exists():
            wxlog.info(f"""未找到对应的视频号""")
            return False

        # _ele.Click(move=True, return_pos=False)
        _ele.Click()
        return True

    def follow_video_channel(self, name):
        """
        关注视频号 仅实现点击关注功能
        :param name:视频号昵称
        """
        # self.Show()
        # res = self.search(name)
        # if not res:
        #     return False
        # res = self.select_channel_name(name)
        # if not res:
        #     return False

        channel_info_ele = self.control.TextControl().GetParentControl().GetParentControl().GetChildren()[2]
        nick_name = channel_info_ele.TextControl().Name
        if nick_name != name:
            wxlog.info(f"""视频号昵称不一致，当前视频号:{nick_name}，目标视频号:{name}""")
            return False
        but_ele = channel_info_ele.GetChildren()[1].ButtonControl()
        if but_ele and but_ele.Name == self._lang("关注"):
            # but_ele.Click(move=True, return_pos=False)
            but_ele.Click()
            wxlog.debug(f"""关注视频号`{name}`成功""")
            time.sleep(0.5)
            return True
        elif but_ele and but_ele.Name == self._lang("已关注"):
            wxlog.debug(f"""视频号`{name}`已关注，不需要重复关注""")
            time.sleep(0.5)
            return True

        from wxauto.utils import print_control_tree
        print_control_tree(channel_info_ele)

    def switch_to_tab(self, name):
        """
        切换到指定标签页
        :param name:标签页名字
        :return bool
        """
        self.Show()  # 需要激活才能获取到正确的窗口
        tab_item = self.control.TabControl().TabItemControl(Name=name)
        if tab_item.ButtonControl(Name=self._lang("关闭")).Exists():
            return True
        index = 1
        while True:
            if len(self.control.TabControl().FindAll(control_type='TabItemControl')) <= index:
                # 未找到指定的标签页
                return False
            # uia.SendKeys('{CTRL}{Tab}')
            tab_item.Click()
            # tab_item.Click(move=True, return_pos=False)
            time.sleep(0.5)
            if tab_item.ButtonControl(Name=self._lang("关闭")).Exists():
                wxlog.debug(f"""切换到 {name} 标签页成功""")
                return True
            index += 1
            time.sleep(0.5)

    def get_all_tab(self):
        """
        获取所有标签页名字
        """
        self.Show()  # 需要激活才能获取到正确的窗口
        tab_names = []
        tab_ele = self.control.TabControl()
        if not tab_ele.Exists():
            return tab_names
        tab_item = tab_ele.TabItemControl()
        if not tab_item.Exists():
            return tab_names
        for _tab_item in tab_item.GetParentControl().GetChildren():
            # print(_tab_item)
            if _tab_item and _tab_item.Name:
                tab_names.append(_tab_item.Name)
        return tab_names

    def close_tab(self, name=None):
        """
        关闭标签页
        :param name: 如果没用指定时默认关闭当前标签页
        """
        if name:
            self.switch_to_tab(name)

        tab_ele = self.control.TabItemControl().GetParentControl().ButtonControl(Name=self._lang('关闭'))
        if tab_ele.Exists():
            tab_name = tab_ele.GetParentControl().Name
            # tab_ele.Click(move=True, return_pos=False)
            tab_ele.Click()
            wxlog.debug(f"""视频号-标签页`{tab_name}`关闭成功""")
