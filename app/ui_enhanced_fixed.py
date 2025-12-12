# -*- coding: utf-8 -*-
# ui_enhanced_fixed.py
# 用途：提供進階的GUI元件，包含顏色標籤、hover效果、文字格式化等
# 此文件现在作为兼容性入口，重新导出所有UI组件

from .ui.enhanced_treeview import EnhancedTreeview
from .ui.enhanced_text import EnhancedText
from .ui.fail_details_panel import FailDetailsPanel
from .ui.utils import extract_error_block

__all__ = [
    'EnhancedTreeview',
    'EnhancedText',
    'FailDetailsPanel',
    'extract_error_block'
]