"""Streamlit网页交互式数值转换工具。"""

import streamlit as st


BASE_OPTIONS = {
    "1": ("二进制", 2),
    "2": ("十进制", 10),
    "3": ("十六进制", 16),
}


def strip_input(user_input):
    """去除输入内容前后的空白字符。"""
    return user_input.strip()


def remove_base_prefix(value, base):
    """按指定进制去除合法的进制前缀。"""
    if base == 2 and value.lower().startswith("0b"):
        return value[2:]
    if base == 16 and value.lower().startswith("0x"):
        return value[2:]
    return value


def normalize_number_text(value, base):
    """将数值字符串规范化为无前缀、无多余前导零的格式。"""
    value_without_prefix = remove_base_prefix(strip_input(value), base)
    normalized_value = value_without_prefix.lstrip("0") or "0"
    if base == 16:
        return normalized_value.lower()
    return normalized_value


def validate_number_input(number_str, base):
    """校验指定进制的无符号整数输入。"""
    cleaned_value = strip_input(number_str)
    if not cleaned_value:
        return False, "❌ 错误：数值输入不能为空，请重新输入"
    if cleaned_value.startswith("-"):
        return False, "❌ 错误：仅支持无符号正整数，不能输入负数"
    if "." in cleaned_value:
        return False, "❌ 错误：仅支持整数，不能输入小数"

    value_without_prefix = remove_base_prefix(cleaned_value, base)
    if not value_without_prefix:
        return False, "❌ 错误：去除进制前缀后数值不能为空"

    if base == 2:
        if not all(char in "01" for char in value_without_prefix):
            return False, "❌ 错误：二进制输入只能包含0和1，请重新输入"
    elif base == 10:
        if not value_without_prefix.isdigit():
            return False, "❌ 错误：十进制输入只能包含数字，请重新输入"
    elif base == 16:
        valid_hex_chars = "0123456789abcdefABCDEF"
        if not all(char in valid_hex_chars for char in value_without_prefix):
            return False, "❌ 错误：十六进制输入只能包含0-9和A-F，请重新输入"
    else:
        return False, "❌ 错误：不支持的源进制"

    return True, value_without_prefix


def bin_to_dec(binary_str):
    """将二进制字符串转换为十进制字符串。"""
    return str(int(binary_str, 2))


def dec_to_bin(decimal_num):
    """将十进制整数转换为二进制字符串。"""
    return format(decimal_num, "b")


def dec_to_hex(decimal_num):
    """将十进制整数转换为十六进制字符串。"""
    return format(decimal_num, "x")


def hex_to_dec(hex_str):
    """将十六进制字符串转换为十进制字符串。"""
    return str(int(hex_str, 16))


def convert_number(value, source_base, target_base):
    """按指定源进制和目标进制转换数值。"""
    if source_base == target_base:
        return normalize_number_text(value, source_base)

    # 先统一转为十进制整数，再格式化到目标进制。
    if source_base == 2:
        decimal_num = int(bin_to_dec(value))
    elif source_base == 10:
        decimal_num = int(value)
    else:
        decimal_num = int(hex_to_dec(value))

    if target_base == 2:
        return dec_to_bin(decimal_num)
    if target_base == 10:
        return str(decimal_num)
    return dec_to_hex(decimal_num)


def ascii_encode(text):
    """将可打印ASCII字符串编码为十进制ASCII码。"""
    if text == "":
        raise ValueError("❌ 错误：ASCII编码输入不能为空")

    ascii_codes = []
    for char in text:
        char_code = ord(char)
        if char_code < 32 or char_code > 126:
            raise ValueError("❌ 错误：ASCII编码仅支持可打印字符，不能包含换行、制表符或控制字符")
        ascii_codes.append(str(char_code))
    return " ".join(ascii_codes)


def ascii_decode(ascii_list):
    """将十进制ASCII码解码为字符串。"""
    cleaned_value = strip_input(ascii_list)
    if not cleaned_value:
        raise ValueError("❌ 错误：ASCII解码输入不能为空")

    decoded_chars = []
    for item in cleaned_value.split():
        if "." in item:
            raise ValueError("❌ 错误：ASCII码必须是整数，不能输入小数")
        if not item.isdigit():
            raise ValueError("❌ 错误：ASCII码只能包含十进制数字")

        ascii_code = int(item)
        if ascii_code < 0 or ascii_code > 127:
            raise ValueError("❌ 错误：ASCII码必须在0-127范围内")
        decoded_chars.append(chr(ascii_code))

    return "".join(decoded_chars)


def apply_dark_style():
    """使用少量样式固定深色视觉。"""
    st.markdown(
        """
        <style>
        .stApp {
            background: #0f1117;
            color: #e6e8ee;
        }
        [data-testid="stHeader"] {
            background: #0f1117;
        }
        .block-container {
            max-width: 860px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid #242936;
            border-radius: 18px;
            background: #151923;
            padding: 1.25rem;
        }
        div[data-testid="stMetric"],
        div[data-testid="stAlert"] {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_base_conversion():
    """渲染进制转换页面区域。"""
    base_labels = {key: name for key, (name, _) in BASE_OPTIONS.items()}

    with st.form("base_conversion_form"):
        st.subheader("进制转换")
        source_choice = st.selectbox(
            "源进制",
            options=list(BASE_OPTIONS.keys()),
            format_func=lambda choice: base_labels[choice],
        )
        number_input = st.text_input("待转换数值", placeholder="例如：1010、10、0x1a")
        target_choice = st.selectbox(
            "目标进制",
            options=list(BASE_OPTIONS.keys()),
            format_func=lambda choice: base_labels[choice],
        )
        submitted = st.form_submit_button("开始转换", use_container_width=True)

    if not submitted:
        return

    source_name, source_base = BASE_OPTIONS[source_choice]
    target_name, target_base = BASE_OPTIONS[target_choice]
    is_valid, checked_value = validate_number_input(number_input, source_base)
    if not is_valid:
        st.error(checked_value)
        return

    result = convert_number(checked_value, source_base, target_base)
    display_value = normalize_number_text(checked_value, source_base)
    st.success(f"✅ 转换成功：{source_name} {display_value} → {target_name} = {result}")
    st.code(result, language=None)


def render_ascii_encode():
    """渲染ASCII编码页面区域。"""
    with st.form("ascii_encode_form"):
        st.subheader("ASCII编码")
        text = st.text_input("要进行ASCII编码的字符串", placeholder="请输入可打印ASCII字符")
        submitted = st.form_submit_button("开始编码", use_container_width=True)

    if not submitted:
        return

    try:
        result = ascii_encode(text)
        st.success(f"✅ 编码成功：{text} → {result}")
        st.code(result, language=None)
    except ValueError as error:
        st.error(str(error))


def render_ascii_decode():
    """渲染ASCII解码页面区域。"""
    with st.form("ascii_decode_form"):
        st.subheader("ASCII解码")
        ascii_input = st.text_input("十进制ASCII码", placeholder="例如：72 101 108 108 111")
        submitted = st.form_submit_button("开始解码", use_container_width=True)

    if not submitted:
        return

    try:
        result = ascii_decode(ascii_input)
        st.success(f"✅ 解码成功：{ascii_input.strip()} → {result}")
        st.code(result, language=None)
    except ValueError as error:
        st.error(str(error))


def main():
    """程序主入口，负责网页交互调度。"""
    st.set_page_config(
        page_title="数值转换工具",
        page_icon="🔢",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    apply_dark_style()

    st.title("数值转换工具")
    st.caption("进制转换、ASCII编码、ASCII解码")
    st.divider()

    conversion_type = st.radio(
        "选择功能",
        options=("进制转换", "ASCII编码", "ASCII解码"),
        horizontal=True,
    )

    st.divider()

    if conversion_type == "进制转换":
        render_base_conversion()
    elif conversion_type == "ASCII编码":
        render_ascii_encode()
    else:
        render_ascii_decode()


if __name__ == "__main__":
    main()
