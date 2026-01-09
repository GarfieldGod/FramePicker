import os
import sys
from pathlib import Path
from dataclasses import dataclass

from platformdirs import user_data_dir


@dataclass
class Key:
    FramePicker = "FramePicker"

@dataclass
class AppPath:
    if sys.platform.startswith('win'):
        LogRoot = user_data_dir("log", Key.FramePicker)
        DataRoot = user_data_dir("data", Key.FramePicker)
        AppRoot = os.path.dirname(DataRoot)
    else:
        AppRoot = user_data_dir(Key.FramePicker, Key.FramePicker)
        LogRoot = os.path.join(AppRoot, "log")
        DataRoot = os.path.join(AppRoot, "data")

    if hasattr(sys, '_MEIPASS'):
        ProjectRoot = sys._MEIPASS
    else:
        ProjectRoot = os.path.abspath(".")
    ConfigJson: str = os.path.join(ProjectRoot, "config.json")
    UiResourcePath: str = os.path.join(ProjectRoot, "ui", "resource")
    QssPath: str = os.path.join(UiResourcePath, "qss")
    ImagePath: str = os.path.join(UiResourcePath, "image")

@dataclass
class WebPath:
    AppConfigPathGitHub: str = "https://github.com/garfieldgod/FramePicker/raw/master/config.json"
    AppConfigPathGitee: str = "https://gitee.com/garfieldgod/FramePicker/raw/master/config.json"
    AppProjectPath: str = "https://github.com/GarfieldGod/FramePicker"