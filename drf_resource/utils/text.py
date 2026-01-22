"""
文本处理工具模块

提供命名风格转换等文本处理功能。
"""

import io


def camel_to_underscore(camel_str):
    """
    将驼峰命名法转换为下划线命名法。

    示例:
        - "HelloWorld" -> "hello_world"
        - "XMLParser" -> "xml_parser"
        - "getHTTPResponse" -> "get_http_response"

    :param camel_str: 驼峰命名法字符串
    :return: 转换后的下划线命名法字符串
    """
    # 确保输入是字符串
    assert isinstance(camel_str, str), "camel_str must be a string"

    # 使用 StringIO 作为缓冲区来构建转换后的字符串
    buf = io.StringIO()
    str_len = len(camel_str)

    # 遍历输入字符串的每个字符
    for i in range(str_len):
        cur_letter = camel_str[i]
        # 如果当前字符是大写，且不是字符串的第一个字符，则考虑插入下划线
        if i and cur_letter == cur_letter.upper():
            prev_letter = camel_str[i - 1]
            next_letter = camel_str[i + 1] if i < str_len - 1 else "A"
            # 如果当前字符是字母，并且前一个字符或后一个字符不是大写，则插入下划线
            if cur_letter.isalpha():
                if (
                    prev_letter != prev_letter.upper()
                    or next_letter != next_letter.upper()
                ):
                    buf.write("_")
        # 将当前字符写入缓冲区
        buf.write(cur_letter)

    # 从缓冲区获取转换后的字符串
    result = buf.getvalue()
    # 关闭缓冲区
    buf.close()

    # 将转换后的字符串转为小写并返回
    return result.lower()


def underscore_to_camel(underscore_str):
    """
    将下划线命名法转换为驼峰命名法（大驼峰/Pascal Case）。

    示例:
        - "hello_world" -> "HelloWorld"
        - "get_http_response" -> "GetHttpResponse"

    :param underscore_str: 下划线命名法字符串
    :return: 转换后的驼峰命名法字符串
    """
    assert isinstance(underscore_str, str), "underscore_str must be a string"

    return "".join([x.capitalize() for x in underscore_str.split("_")])
