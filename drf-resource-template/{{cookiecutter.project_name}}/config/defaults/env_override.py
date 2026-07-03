"""环境变量自动覆盖机制

SETTINGS_ 前缀的环境变量自动注入为 Django settings。
例如: SETTINGS_DEBUG=true → DEBUG=True
     SETTINGS_SECRET_KEY=xxx → SECRET_KEY=xxx

类型自动转换：true/false/none/int/str
"""
import os

_prefix = "SETTINGS_"
for _key, _value in os.environ.items():
    if _key.startswith(_prefix):
        _setting_name = _key[len(_prefix):]
        _lower = _value.lower()
        if _lower in ("true", "1", "yes"):
            _typed_value = True
        elif _lower in ("false", "0", "no"):
            _typed_value = False
        elif _lower in ("none", "null"):
            _typed_value = None
        else:
            try:
                _typed_value = int(_value)
            except ValueError:
                _typed_value = _value
        locals()[_setting_name] = _typed_value
