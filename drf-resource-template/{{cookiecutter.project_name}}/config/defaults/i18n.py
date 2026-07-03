"""国际化配置 — 仅 enable_i18n=yes 时生成"""
import os
from config import BASE_DIR

LANGUAGE_CODE = "zh-hans"
LANGUAGES = [
    ("zh-hans", "简体中文"),
    ("en", "English"),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
USE_I18N = True
USE_L10N = True
