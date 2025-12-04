import os
import sys
from dataclasses import dataclass

@dataclass
class AppPath:
    if hasattr(sys, '_MEIPASS'):
        ProjectRoot = sys._MEIPASS
    else:
        ProjectRoot = os.path.abspath(".")
    UiResourcePath: str = os.path.join(ProjectRoot, "ui", "resource")
    QssPath: str = os.path.join(UiResourcePath, "qss")
    ImagePath: str = os.path.join(UiResourcePath, "image")