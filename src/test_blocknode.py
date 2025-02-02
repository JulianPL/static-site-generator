import unittest

from blocknode import BlockType, markdown_to_blocks, block_to_block_type, markdown_to_html

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
