"""
Tests for the Redmine <-> Markdown converter.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from converter import redmine_to_markdown, markdown_to_redmine


class TestRedmineToMarkdown:
    """Tests for Redmine to Markdown conversion."""

    def test_empty_string(self):
        assert redmine_to_markdown("") == ""
        assert redmine_to_markdown(None) == ""

    def test_headers(self):
        assert redmine_to_markdown("h1. Title") == "# Title"
        assert redmine_to_markdown("h2. Subtitle") == "## Subtitle"
        assert redmine_to_markdown("h3. Section") == "### Section"
        assert redmine_to_markdown("h4. Subsection") == "#### Subsection"
        assert redmine_to_markdown("h5. Minor") == "##### Minor"
        assert redmine_to_markdown("h6. Smallest") == "###### Smallest"

    def test_bold(self):
        assert redmine_to_markdown("*bold text*") == "**bold text**"
        assert redmine_to_markdown("This is *bold* text") == "This is **bold** text"

    def test_italic(self):
        assert redmine_to_markdown("_italic text_") == "*italic text*"
        assert redmine_to_markdown("This is _italic_ text") == "This is *italic* text"

    def test_strikethrough(self):
        assert redmine_to_markdown("-deleted text-") == "~~deleted text~~"

    def test_underline(self):
        assert redmine_to_markdown("+underlined+") == "<u>underlined</u>"

    def test_links(self):
        assert redmine_to_markdown('"Google":https://google.com') == "[Google](https://google.com)"
        assert redmine_to_markdown('"Click here":http://example.com') == "[Click here](http://example.com)"

    def test_wiki_links(self):
        assert redmine_to_markdown("[[WikiPage]]") == "[WikiPage](WikiPage)"
        assert redmine_to_markdown("[[WikiPage|Display Text]]") == "[Display Text](WikiPage)"

    def test_images(self):
        assert redmine_to_markdown("!image.png!") == "![](image.png)"
        assert redmine_to_markdown("!path/to/image.jpg!") == "![](path/to/image.jpg)"

    def test_unordered_list(self):
        assert redmine_to_markdown("* Item 1") == "- Item 1"
        assert redmine_to_markdown("** Nested item") == "  - Nested item"
        assert redmine_to_markdown("*** Deep nested") == "    - Deep nested"

    def test_ordered_list(self):
        assert redmine_to_markdown("# Item 1") == "1. Item 1"
        assert redmine_to_markdown("## Nested item") == "  1. Nested item"

    def test_blockquote(self):
        assert redmine_to_markdown("bq. This is a quote") == "> This is a quote"

    def test_inline_code(self):
        assert redmine_to_markdown("Use @code@ here") == "Use `code` here"

    def test_code_block(self):
        result = redmine_to_markdown("<pre>code here</pre>")
        assert "```" in result
        assert "code here" in result

    def test_multiline(self):
        input_text = """h1. Title

This is *bold* and _italic_.

* Item 1
* Item 2

"Link":https://example.com"""
        result = redmine_to_markdown(input_text)
        assert "# Title" in result
        assert "**bold**" in result
        assert "*italic*" in result
        assert "- Item 1" in result
        assert "[Link](https://example.com)" in result


class TestMarkdownToRedmine:
    """Tests for Markdown to Redmine conversion."""

    def test_empty_string(self):
        assert markdown_to_redmine("") == ""
        assert markdown_to_redmine(None) == ""

    def test_headers(self):
        assert markdown_to_redmine("# Title") == "h1. Title"
        assert markdown_to_redmine("## Subtitle") == "h2. Subtitle"
        assert markdown_to_redmine("### Section") == "h3. Section"
        assert markdown_to_redmine("#### Subsection") == "h4. Subsection"
        assert markdown_to_redmine("##### Minor") == "h5. Minor"
        assert markdown_to_redmine("###### Smallest") == "h6. Smallest"

    def test_bold(self):
        assert markdown_to_redmine("**bold text**") == "*bold text*"

    def test_italic(self):
        assert markdown_to_redmine("*italic text*") == "_italic text_"

    def test_strikethrough(self):
        assert markdown_to_redmine("~~deleted~~") == "-deleted-"

    def test_underline(self):
        assert markdown_to_redmine("<u>underlined</u>") == "+underlined+"

    def test_links(self):
        assert markdown_to_redmine("[Google](https://google.com)") == '"Google":https://google.com'

    def test_images(self):
        assert markdown_to_redmine("![alt](image.png)") == "!image.png!"
        assert markdown_to_redmine("![](image.png)") == "!image.png!"

    def test_unordered_list(self):
        assert markdown_to_redmine("- Item 1") == "* Item 1"
        assert markdown_to_redmine("  - Nested item") == "** Nested item"

    def test_ordered_list(self):
        assert markdown_to_redmine("1. Item 1") == "# Item 1"
        assert markdown_to_redmine("   1. Nested item") == "## Nested item"

    def test_blockquote(self):
        assert markdown_to_redmine("> This is a quote") == "bq. This is a quote"

    def test_inline_code(self):
        assert markdown_to_redmine("Use `code` here") == "Use @code@ here"

    def test_code_block(self):
        result = markdown_to_redmine("```python\ncode here\n```")
        assert "<pre>" in result
        assert "code here" in result

    def test_multiline(self):
        input_text = """# Title

This is **bold** and *italic*.

- Item 1
- Item 2

[Link](https://example.com)"""
        result = markdown_to_redmine(input_text)
        assert "h1. Title" in result
        assert "*bold*" in result
        assert "_italic_" in result
        assert "* Item 1" in result
        assert '"Link":https://example.com' in result


class TestRoundTrip:
    """Test round-trip conversion."""

    def test_headers_roundtrip(self):
        original = "h1. My Title"
        converted = redmine_to_markdown(original)
        back = markdown_to_redmine(converted)
        assert back == original

    def test_list_roundtrip(self):
        original = "* Item one\n* Item two"
        converted = redmine_to_markdown(original)
        back = markdown_to_redmine(converted)
        assert back == original

    def test_link_roundtrip(self):
        original = '"Example":https://example.com'
        converted = redmine_to_markdown(original)
        back = markdown_to_redmine(converted)
        assert back == original
