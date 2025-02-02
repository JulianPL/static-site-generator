import unittest

from blocknode import markdown_to_blocks

class TestBlockSplit(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = "# This is a heading  \n\n  This is a paragraph of text. It has some **bold** and *italic* words inside of it.\n\n\n\n\n* This is the first list item in a list block\n* This is a list item\n* This is another list item"
        actual = markdown_to_blocks(markdown)
        expected = ["# This is a heading",
                    "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                    "* This is the first list item in a list block\n* This is a list item\n* This is another list item"]
        self.assertEqual(markdown_to_blocks(markdown), expected)

if __name__ == "__main__":
    unittest.main()
