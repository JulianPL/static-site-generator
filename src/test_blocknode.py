import unittest

from blocknode import BlockType, BlockNode, extract_title, markdown_to_block_nodes, block_node_to_html_node

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
        actual = markdown_to_block_nodes("###### Heading")
        expected = [BlockNode("###### Heading", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("####### Nonsense")
        expected = [BlockNode("####### Nonsense", BlockType.PARAGRAPH)]
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
        expected = [BlockNode("This is a paragraph", BlockType.PARAGRAPH), BlockNode("# with a second line", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        actual = markdown_to_block_nodes("This is a paragraph\n   \n# with a second line\n")
        expected = [BlockNode("This is a paragraph", BlockType.PARAGRAPH), BlockNode("# with a second line", BlockType.HEADING)]
        self.assertEqual(actual, expected)
        
class TestBlockNodeConversion(unittest.TestCase):
    def test_block_node_to_html_node(self):
        actual = str(block_node_to_html_node(BlockNode("# Heading", BlockType.MAIN)))
        expected = "ParentNode(div, [ParentNode(h1, [LeafNode(None, Heading, None)], None)], None)"
        self.assertEqual(actual, expected)
        actual = str(block_node_to_html_node(BlockNode("```python\ndef function():\n    pass:```", BlockType.MAIN)))
        expected = "ParentNode(div, [ParentNode(pre, [ParentNode(code, [LeafNode(None, def function():\n    pass:, None)], {'class': 'language-python'})], None)], None)"
        self.assertEqual(actual, expected)
        actual = str(block_node_to_html_node(BlockNode("> This is the mail\n> I was meant to forward:\n> > It is not a big of a deal!", BlockType.MAIN)))
        expected = "ParentNode(div, [ParentNode(blockquote, [ParentNode(p, [LeafNode(None, This is the mail\nI was meant to forward:, None)], None), ParentNode(blockquote, [ParentNode(p, [LeafNode(None, It is not a big of a deal!, None)], None)], None)], None)], None)"
        self.assertEqual(actual, expected)
        actual = str(block_node_to_html_node(BlockNode("* item\n* another item\n  * item in sublist\n  * another item in sublist\n* an item in the original list", BlockType.MAIN)))
        expected = "ParentNode(div, [ParentNode(ul, [ParentNode(li, [ParentNode(p, [LeafNode(None, item, None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, another item, None)], None), ParentNode(ul, [ParentNode(li, [ParentNode(p, [LeafNode(None, item in sublist, None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, another item in sublist, None)], None)], None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, an item in the original list, None)], None)], None)], None)], None)"
        self.assertEqual(actual, expected)
        actual = str(block_node_to_html_node(BlockNode("1. item\n2. another item\n  1. item in sublist\n  2. another item in sublist\n3. an item in the original list", BlockType.MAIN)))
        expected = "ParentNode(div, [ParentNode(ol, [ParentNode(li, [ParentNode(p, [LeafNode(None, item, None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, another item, None)], None), ParentNode(ol, [ParentNode(li, [ParentNode(p, [LeafNode(None, item in sublist, None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, another item in sublist, None)], None)], None)], None)], None), ParentNode(li, [ParentNode(p, [LeafNode(None, an item in the original list, None)], None)], None)], None)], None)"
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
