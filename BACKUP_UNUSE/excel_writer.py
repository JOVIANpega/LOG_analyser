# -*- coding: utf-8 -*-
"""
ExcelWriter Facade Module
Compatibility layer for modularized ExcelWriter system.
"""
from .excel.excel_writer import ExcelWriter
from .excel.excel_utils import extract_total_secs

# Re-exporting for backward compatibility
__all__ = ['ExcelWriter', 'extract_total_secs']