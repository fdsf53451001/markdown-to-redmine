"""
Bidirectional converter between Redmine Textile format and Markdown.
"""
import re


def redmine_to_markdown(text: str) -> str:
    """Convert Redmine Textile format to Markdown."""
    if not text:
        return ""

    result = text

    # Preserve code blocks first (to avoid processing content inside them)
    code_blocks = []

    def preserve_code_block(match):
        code_blocks.append(match.group(1))
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    # Preserve <pre><code> blocks
    result = re.sub(r'<pre><code[^>]*>(.*?)</code></pre>', preserve_code_block, result, flags=re.DOTALL)
    result = re.sub(r'<pre>(.*?)</pre>', preserve_code_block, result, flags=re.DOTALL)

    # Preserve inline code @code@
    inline_codes = []

    def preserve_inline_code(match):
        inline_codes.append(match.group(1))
        return f"__INLINE_CODE_{len(inline_codes) - 1}__"

    result = re.sub(r'@([^@\n]+)@', preserve_inline_code, result)

    # Ordered lists FIRST (before headers, since # is used for both)
    # Multi-level: ##, ###, etc.
    # Only match # at the start of a line followed by space (list item)
    def convert_ordered_list(match):
        hashes = match.group(1)
        content = match.group(2)
        indent = "  " * (len(hashes) - 1)
        return f"__OL__{indent}1. {content}"

    result = re.sub(r'^(#+)\s+(.+)$', convert_ordered_list, result, flags=re.MULTILINE)

    # Headers: h1. text -> # text
    result = re.sub(r'^h1\.\s*(.+)$', r'# \1', result, flags=re.MULTILINE)
    result = re.sub(r'^h2\.\s*(.+)$', r'## \1', result, flags=re.MULTILINE)
    result = re.sub(r'^h3\.\s*(.+)$', r'### \1', result, flags=re.MULTILINE)
    result = re.sub(r'^h4\.\s*(.+)$', r'#### \1', result, flags=re.MULTILINE)
    result = re.sub(r'^h5\.\s*(.+)$', r'##### \1', result, flags=re.MULTILINE)
    result = re.sub(r'^h6\.\s*(.+)$', r'###### \1', result, flags=re.MULTILINE)

    # Remove the __OL__ marker
    result = result.replace("__OL__", "")

    # Bold: *text* -> **text** (but not for list items)
    # Need to be careful not to match list markers
    result = re.sub(r'(?<!\S)\*([^\*\n]+)\*(?!\S)', r'**\1**', result)

    # Italic: _text_ -> *text*
    result = re.sub(r'(?<![a-zA-Z0-9])_([^_\n]+)_(?![a-zA-Z0-9])', r'*\1*', result)

    # Strikethrough: -text- -> ~~text~~
    result = re.sub(r'(?<!\S)-([^\-\n]+)-(?!\S)', r'~~\1~~', result)

    # Underline: +text+ -> <u>text</u>
    result = re.sub(r'(?<!\S)\+([^\+\n]+)\+(?!\S)', r'<u>\1</u>', result)

    # Links: "text":url -> [text](url)
    result = re.sub(r'"([^"]+)":(\S+)', r'[\1](\2)', result)

    # Wiki links: [[page]] -> [page](page)
    result = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'[\2](\1)', result)
    result = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](\1)', result)

    # Images: !image.png! -> ![](image.png)
    result = re.sub(r'!([^\s!]+)!', r'![](\1)', result)

    # Unordered lists: Keep * as is or convert to -
    # Redmine uses * for unordered, # for ordered
    # Multi-level: **, ***, etc.
    def convert_unordered_list(match):
        asterisks = match.group(1)
        content = match.group(2)
        indent = "  " * (len(asterisks) - 1)
        return f"{indent}- {content}"

    result = re.sub(r'^(\*+)\s+(.+)$', convert_unordered_list, result, flags=re.MULTILINE)

    # Blockquote: bq. text -> > text
    result = re.sub(r'^bq\.\s*(.+)$', r'> \1', result, flags=re.MULTILINE)

    # Table conversion
    # Redmine: |_. Header |_. Header |
    #          | Cell | Cell |
    # Markdown: | Header | Header |
    #           |--------|--------|
    #           | Cell | Cell |

    def convert_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        result_lines = []
        header_processed = False

        for line in lines:
            if '|_.' in line:
                # Header row
                converted = re.sub(r'\|_\.', '|', line)
                result_lines.append(converted)
                # Add separator
                cells = converted.count('|') - 1
                separator = '|' + '|'.join(['---'] * cells) + '|'
                result_lines.append(separator)
                header_processed = True
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    # Match table blocks (consecutive lines starting with |)
    result = re.sub(r'((?:^\|.+\|\s*\n?)+)', convert_table, result, flags=re.MULTILINE)

    # Restore code blocks as markdown code blocks
    for i, code in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", f"```\n{code}\n```")

    # Restore inline code
    for i, code in enumerate(inline_codes):
        result = result.replace(f"__INLINE_CODE_{i}__", f"`{code}`")

    return result


def markdown_to_redmine(text: str) -> str:
    """Convert Markdown to Redmine Textile format."""
    if not text:
        return ""

    result = text

    # Preserve fenced code blocks first
    code_blocks = []

    def preserve_code_block(match):
        lang = match.group(1) or ""
        code = match.group(2)
        code_blocks.append((lang, code))
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    result = re.sub(r'```(\w*)\n(.*?)```', preserve_code_block, result, flags=re.DOTALL)

    # Preserve inline code
    inline_codes = []

    def preserve_inline_code(match):
        inline_codes.append(match.group(1))
        return f"__INLINE_CODE_{len(inline_codes) - 1}__"

    result = re.sub(r'`([^`\n]+)`', preserve_inline_code, result)

    # Images FIRST (before links, since ![](url) would match [](url) link pattern)
    result = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'!\2!', result)

    # Headers: # text -> h1. text (process from most # to least to avoid partial matches)
    result = re.sub(r'^###### (.+)$', r'h6. \1', result, flags=re.MULTILINE)
    result = re.sub(r'^##### (.+)$', r'h5. \1', result, flags=re.MULTILINE)
    result = re.sub(r'^#### (.+)$', r'h4. \1', result, flags=re.MULTILINE)
    result = re.sub(r'^### (.+)$', r'h3. \1', result, flags=re.MULTILINE)
    result = re.sub(r'^## (.+)$', r'h2. \1', result, flags=re.MULTILINE)
    result = re.sub(r'^# (.+)$', r'h1. \1', result, flags=re.MULTILINE)

    # Bold: **text** -> *text* (use placeholder to avoid italic conversion)
    def convert_bold(match):
        return f"__BOLD__{match.group(1)}__ENDBOLD__"

    result = re.sub(r'\*\*([^\*]+)\*\*', convert_bold, result)

    # Italic: *text* -> _text_ (but not the converted bold)
    result = re.sub(r'(?<!\*)\*([^\*]+)\*(?!\*)', r'_\1_', result)

    # Restore bold
    result = re.sub(r'__BOLD__(.+?)__ENDBOLD__', r'*\1*', result)

    # Strikethrough: ~~text~~ -> -text-
    result = re.sub(r'~~([^~]+)~~', r'-\1-', result)

    # Underline: <u>text</u> -> +text+
    result = re.sub(r'<u>([^<]+)</u>', r'+\1+', result)

    # Links: [text](url) -> "text":url
    result = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'"\1":\2', result)

    # Unordered lists: - item or * item -> * item
    def convert_unordered_list(match):
        indent = match.group(1)
        content = match.group(2)
        level = len(indent) // 2 + 1
        return '*' * level + ' ' + content

    result = re.sub(r'^(\s*)[-\*]\s+(.+)$', convert_unordered_list, result, flags=re.MULTILINE)

    # Ordered lists: 1. item -> # item
    def convert_ordered_list(match):
        indent = match.group(1)
        content = match.group(2)
        level = len(indent) // 2 + 1
        return '#' * level + ' ' + content

    result = re.sub(r'^(\s*)\d+\.\s+(.+)$', convert_ordered_list, result, flags=re.MULTILINE)

    # Blockquote: > text -> bq. text
    result = re.sub(r'^>\s*(.+)$', r'bq. \1', result, flags=re.MULTILINE)

    # Table conversion
    # Remove markdown table separator lines
    def convert_table(match):
        table_text = match.group(0)
        lines = table_text.strip().split('\n')
        result_lines = []
        is_first_row = True

        for line in lines:
            # Skip separator lines
            if re.match(r'^\|[\s\-:|]+\|$', line):
                continue
            if is_first_row:
                # Convert first row to header
                converted = re.sub(r'\|([^|]+)', r'|_.\1', line)
                result_lines.append(converted)
                is_first_row = False
            else:
                result_lines.append(line)

        return '\n'.join(result_lines)

    result = re.sub(r'((?:^\|.+\|\s*\n?)+)', convert_table, result, flags=re.MULTILINE)

    # Restore code blocks
    for i, (lang, code) in enumerate(code_blocks):
        result = result.replace(f"__CODE_BLOCK_{i}__", f"<pre><code class=\"{lang}\">\n{code}</code></pre>")

    # Restore inline code
    for i, code in enumerate(inline_codes):
        result = result.replace(f"__INLINE_CODE_{i}__", f"@{code}@")

    return result
