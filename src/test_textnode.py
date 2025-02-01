import unittest

from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node_copy = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node_copy)
        node_normal = TextNode("This is a text node", TextType.NORMAL)
        self.assertNotEqual(node, node_normal)
        node_alttext = TextNode("Another text", TextType.BOLD)
        self.assertNotEqual(node, node_alttext)
        node_url = TextNode("This is a text node", TextType.BOLD, "https://www.libellen.tv/images/viele-libellen.webp")
        self.assertNotEqual(node, node_url)
    
    def test_repr(self):
        node = TextNode("Text node representing a nice image by my father", TextType.IMAGE, "https://www.libellen.tv/images/viele-libellen.webp")
        text = "TextNode(Text node representing a nice image by my father, image, https://www.libellen.tv/images/viele-libellen.webp)"
        self.assertEqual(str(node), text)

if __name__ == "__main__":
    unittest.main()

