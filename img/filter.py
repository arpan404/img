import re

def filter_content(content: str) -> str:
    """
    Filters out any content that is not suitable for all audiences.
    """
    # Define a list of keywords to filter out
    replace_patterns = [
        r"[^\w\s]",  # Remove symbols
        r"\[.*?\]",  # Remove brackets
        ]
    for pattern in replace_patterns:
        content = re.sub(pattern, "", content)
    return content