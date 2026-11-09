# -*- coding: utf-8 -*-
import os
from win32com.client import Dispatch

def create_desktop_shortcut():
    shell = Dispatch('WScript.Shell')
    desktop = shell.SpecialFolders('Desktop')
    lnk_path = os.path.join(desktop, '賀華實業 - 智慧科技互動系統.lnk')
    ico_path = os.path.abspath('app.ico')

    exe_path = os.path.abspath(r'release\賀華實業\賀華實業.exe')
    if os.path.exists(exe_path):
        target = exe_path
        w_dir = os.path.dirname(exe_path)
    else:
        target = os.path.abspath('start_desktop.bat')
        w_dir = os.path.abspath('.')

    shortcut = shell.CreateShortCut(lnk_path)
    shortcut.TargetPath = target
    shortcut.WorkingDirectory = w_dir
    shortcut.IconLocation = f"{ico_path},0"
    shortcut.Description = "賀華實業股份有限公司 HARVARD ENTERPRISES INC. - 全方位鋁合金供應鏈與 CP-SAT 智慧科技系統"
    shortcut.Save()
    print("✓ 桌面捷徑已建立:", lnk_path)

if __name__ == '__main__':
    create_desktop_shortcut()
