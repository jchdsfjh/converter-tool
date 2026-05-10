"""Streamlit web app for number and ASCII conversion."""

import streamlit as st


BASE_OPTIONS = {
    "1": ("Binary", 2),
    "2": ("Decimal", 10),
    "3": ("Hexadecimal", 16),
}


def strip_input(user_input):
    """Remove leading and trailing whitespace."""
    return user_input.strip()


def remove_base_prefix(value, base):
    """Remove a valid base prefix for the selected base."""
    if base == 2 and value.lower().startswith("0b"):
        return value[2:]
    if base == 16 and value.lower().startswith("0x"):
        return value[2:]
    return value


def normalize_number_text(value, base):
    """Normalize a number string without prefix or extra leading zeros."""
    value_without_prefix = remove_base_prefix(strip_input(value), base)
    normalized_value = value_without_prefix.lstrip("0") or "0"
    if base == 16:
        return normalized_value.lower()
    return normalized_value


def validate_number_input(number_str, base):
    """Validate unsigned integer input for the selected base."""
    cleaned_value = strip_input(number_str)
    if not cleaned_value:
        return False, "Error: Input value cannot be empty."
    if cleaned_value.startswith("-"):
        return False, "Error: Only unsigned positive integers are supported."
    if "." in cleaned_value:
        return False, "Error: Only integers are supported. Decimals are not allowed."

    value_without_prefix = remove_base_prefix(cleaned_value, base)
    if not value_without_prefix:
        return False, "Error: Input value cannot be empty after removing the base prefix."

    if base == 2:
        if not all(char in "01" for char in value_without_prefix):
            return False, "Error: Binary input can only contain 0 and 1."
    elif base == 10:
        if not value_without_prefix.isdigit():
            return False, "Error: Decimal input can only contain digits."
    elif base == 16:
        valid_hex_chars = "0123456789abcdefABCDEF"
        if not all(char in valid_hex_chars for char in value_without_prefix):
            return False, "Error: Hexadecimal input can only contain 0-9 and A-F."
    else:
        return False, "Error: Unsupported source base."

    return True, value_without_prefix


def bin_to_dec(binary_str):
    """Convert a binary string to a decimal string."""
    return str(int(binary_str, 2))


def dec_to_bin(decimal_num):
    """Convert a decimal integer to a binary string."""
    return format(decimal_num, "b")


def dec_to_hex(decimal_num):
    """Convert a decimal integer to a hexadecimal string."""
    return format(decimal_num, "x")


def hex_to_dec(hex_str):
    """Convert a hexadecimal string to a decimal string."""
    return str(int(hex_str, 16))


def convert_number(value, source_base, target_base):
    """Convert a value between the selected source and target bases."""
    if source_base == target_base:
        return normalize_number_text(value, source_base)

    # Convert through decimal first, then format into the target base.
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
    """Encode printable ASCII text into decimal ASCII codes."""
    if text == "":
        raise ValueError("Error: ASCII encode input cannot be empty.")

    ascii_codes = []
    for char in text:
        char_code = ord(char)
        if char_code < 32 or char_code > 126:
            raise ValueError(
                "Error: ASCII encoding only supports printable characters. "
                "Line breaks, tabs, and control characters are not allowed."
            )
        ascii_codes.append(str(char_code))
    return " ".join(ascii_codes)


def ascii_decode(ascii_list):
    """Decode decimal ASCII codes into text."""
    cleaned_value = strip_input(ascii_list)
    if not cleaned_value:
        raise ValueError("Error: ASCII decode input cannot be empty.")

    decoded_chars = []
    for item in cleaned_value.split():
        if "." in item:
            raise ValueError("Error: ASCII codes must be integers. Decimals are not allowed.")
        if not item.isdigit():
            raise ValueError("Error: ASCII codes can only contain decimal digits.")

        ascii_code = int(item)
        if ascii_code < 0 or ascii_code > 127:
            raise ValueError("Error: ASCII codes must be in the 0-127 range.")
        decoded_chars.append(chr(ascii_code))

    return "".join(decoded_chars)


def is_displayable_text(text):
    """Return whether decoded text can be displayed normally."""
    return all(char.isprintable() for char in text)


def apply_dark_style():
    """Apply minimal black and white base styling."""
    st.markdown(
        """
        <style>
        .stApp {
            background: #000000;
            color: #FFFFFF;
        }
        [data-testid="stHeader"] {
            background: #000000;
        }
        [data-testid="stToolbar"] {
            color: #FFFFFF;
        }
        .block-container {
            max-width: 860px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
        div[data-testid="stForm"] {
            border: 1px solid #FFFFFF;
            border-radius: 18px;
            background: #000000;
            padding: 1.25rem;
        }
        label, p, span, h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF;
        }
        input, textarea, [data-baseweb="input"] {
            background: #000000;
            color: #FFFFFF;
        }
        input::placeholder, textarea::placeholder {
            color: #FFFFFF;
            opacity: 0.7;
        }
        div[data-baseweb="select"] > div,
        div[data-baseweb="popover"] {
            background: #000000;
            color: #FFFFFF;
            border-color: #FFFFFF;
        }
        code, pre {
            background: #000000;
            color: #FFFFFF;
            border: 1px solid #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_base_conversion():
    """Render the base conversion section."""
    base_labels = {key: name for key, (name, _) in BASE_OPTIONS.items()}

    with st.form("base_conversion_form"):
        st.subheader("Base Converter")
        source_choice = st.selectbox(
            "Source Base",
            options=list(BASE_OPTIONS.keys()),
            format_func=lambda choice: base_labels[choice],
        )
        number_input = st.text_input("Input Value", placeholder="Example: 1010, 10, 0x1a")
        target_choice = st.selectbox(
            "Target Base",
            options=list(BASE_OPTIONS.keys()),
            format_func=lambda choice: base_labels[choice],
        )
        submitted = st.form_submit_button("Convert", use_container_width=True)

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
    st.success(f"Conversion successful: {source_name} {display_value} -> {target_name} = {result}")
    st.caption("Conversion Result")
    st.code(result, language=None)


def render_ascii_encode():
    """Render the ASCII encode section."""
    with st.form("ascii_encode_form"):
        st.subheader("ASCII Encoder")
        text = st.text_input("Text to Encode", placeholder="Enter printable ASCII text")
        submitted = st.form_submit_button("Encode", use_container_width=True)

    if not submitted:
        return

    try:
        result = ascii_encode(text)
        st.success(f"Encoding successful: {text} -> {result}")
        st.caption("Encoding Result")
        st.code(result, language=None)
    except ValueError as error:
        st.error(str(error))


def render_ascii_decode():
    """Render the ASCII decode section."""
    with st.form("ascii_decode_form"):
        st.subheader("ASCII Decoder")
        ascii_input = st.text_input("Decimal ASCII Codes", placeholder="Example: 72 101 108 108 111")
        submitted = st.form_submit_button("Decode", use_container_width=True)

    if not submitted:
        return

    try:
        result = ascii_decode(ascii_input)
        if not is_displayable_text(result):
            st.code("Cannot display", language=None)
            return

        st.success(f"Decoding successful: {ascii_input.strip()} -> {result}")
        st.caption("Decoding Result")
        st.code(result, language=None)
    except ValueError as error:
        st.error(str(error))


def main():
    """Run the Streamlit app."""
    st.set_page_config(
        page_title="Number Conversion Tool",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    apply_dark_style()

    st.title("Number Conversion Tool")
    st.caption("Base conversion, ASCII encoding, and ASCII decoding")
    st.divider()

    conversion_type = st.radio(
        "Select Tool",
        options=("Base Converter", "ASCII Encoder", "ASCII Decoder"),
        horizontal=True,
    )

    st.divider()

    if conversion_type == "Base Converter":
        render_base_conversion()
    elif conversion_type == "ASCII Encoder":
        render_ascii_encode()
    else:
        render_ascii_decode()


if __name__ == "__main__":
    main()
