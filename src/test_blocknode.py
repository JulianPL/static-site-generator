import unittest

from blocknode import BlockType, BlockNode, markdown_to_block_nodes, markdown_to_blocks, block_to_block_type, markdown_to_html, extract_title

class TestTitleExtraction(unittest.TestCase):
    def test_extract_title(self):
        with self.assertNoLogs('blocknode', level='WARNING') as logs:
            actual = extract_title("# Hello")
        expected = "Hello"
        self.assertEqual(actual, expected)
        with self.assertNoLogs('blocknode', level='WARNING') as logs:
            actual = extract_title("test\n# Hello\ntest")
        expected = "Hello"
        self.assertEqual(actual, expected)
        with self.assertNoLogs('blocknode', level='WARNING') as logs:
            actual = extract_title("test\n  # Hello\ntest")
        expected = "Hello"
        self.assertEqual(actual, expected)
        with self.assertLogs('blocknode', level='WARNING') as logs:
            actual = extract_title("test\nHello\ntest")
        expected = ""
        self.assertEqual(actual, expected)
        self.assertEqual(len(logs.output), 1)

class TestMarkdownToBlockNodeConversion(unittest.TestCase):
    def test_markdown_to_block_nodes(self):
        actual = markdown_to_block_nodes("")
        expected = []
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("   \n ")
        expected = []
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("# Heading")
        expected = [BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("# Heading \n  ## Subheading")
        expected = [BlockNode("# Heading", BlockType.HEADING), BlockNode("## Subheading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("```language\ncode```")
        expected = [BlockNode("language\ncode", BlockType.CODE)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("```\ncode```")
        expected = [BlockNode("\ncode", BlockType.CODE)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("> Quoteline 1\n> Quoteline 2\n> Quoteline 3\n# Heading")
        expected = [BlockNode("Quoteline 1\nQuoteline 2\nQuoteline 3", BlockType.QUOTE), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("- This\n- is\n- unordered 3\n# Heading")
        expected = [BlockNode("- This\n- is\n- unordered 3", BlockType.UNORDERED_LIST), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("- This\n- is\n unordered 3\n# Heading")
        expected = [BlockNode("- This\n- is\n unordered 3", BlockType.UNORDERED_LIST), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("- This\n* is\n unordered 3\n# Heading")
        expected = [BlockNode("- This\n* is\n unordered 3", BlockType.UNORDERED_LIST), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("* This\n* is\n unordered 3\n# Heading")
        expected = [BlockNode("* This\n* is\n unordered 3", BlockType.UNORDERED_LIST), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("42. This\n12. is\n ordered 3\n# Heading")
        expected = [BlockNode("42. This\n12. is\n ordered 3", BlockType.ORDERED_LIST), BlockNode("# Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("This is a paragraph")
        expected = [BlockNode("This is a paragraph", BlockType.PARAGRAPH)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("This is a paragraph\n# with a second line\n")
        expected = [BlockNode("This is a paragraph\n# with a second line", BlockType.PARAGRAPH)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("This is a paragraph\n   \n# with a second line\n")
        expected = [BlockNode("This is a paragraph", BlockType.PARAGRAPH), BlockNode("# with a second line", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        

class TestBlockSplit(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = "# This is a heading  \n\n  This is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n\n\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item"
        actual = markdown_to_blocks(markdown)
        expected = ["# This is a heading",
                    "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                    "* This is the first list item in a list block\n* This is a list item\n* This is another list item"]
        self.assertEqual(markdown_to_blocks(markdown), expected)

class TestBlocksClassification(unittest.TestCase):
    def test_block_to_block_type(self):
        actual = block_to_block_type("# This is a heading")
        expected = BlockType.HEADING
        self.assertEqual(actual, expected)
        actual = block_to_block_type("###### This is a heading")
        expected = BlockType.HEADING
        self.assertEqual(actual, expected)
        actual = block_to_block_type("####### This is a nonsense")
        expected = BlockType.PARAGRAPH
        self.assertEqual(actual, expected)
        actual = block_to_block_type("``` This is code ```")
        expected = BlockType.CODE
        self.assertEqual(actual, expected)
        actual = block_to_block_type("``` This is \nmultiline code ```")
        expected = BlockType.CODE
        self.assertEqual(actual, expected)
        actual = block_to_block_type("> This is a quote\n> with\n> multiple lines")
        expected = BlockType.QUOTE
        self.assertEqual(actual, expected)
        actual = block_to_block_type("> This is a not quote\nwith\n> multiple lines")
        expected = BlockType.PARAGRAPH
        self.assertEqual(actual, expected)
        actual = block_to_block_type("* This is a \n- an unordered list")
        expected = BlockType.UNORDERED_LIST
        self.assertEqual(actual, expected)
        actual = block_to_block_type("1. This is a \n2. an ordered list")
        expected = BlockType.ORDERED_LIST
        self.assertEqual(actual, expected)
        actual = block_to_block_type("1. This is a \n3. nothing")
        expected = BlockType.PARAGRAPH
        self.assertEqual(actual, expected)

class TestBlockConversion(unittest.TestCase):
    def test_block_to_html_node(self):
        actual = str(markdown_to_html("```CODE```"))
        expected = "ParentNode(div, [ParentNode(pre, [ParentNode(code, [LeafNode(None, CODE, None)], None)], None)], None)"
        self.assertEqual(actual, expected)
        actual = str(markdown_to_html("1. 1\n2. 2"))
        expected = "ParentNode(div, [ParentNode(ol, [ParentNode(li, [LeafNode(None, 1, None)], None), ParentNode(li, [LeafNode(None, 2, None)], None)], None)], None)"
        self.assertEqual(actual, expected)



if __name__ == "__main__":
    unittest.main()
