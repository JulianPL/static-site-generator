import unittest

from textnode import TextNode, TextType, text_node_to_html_node, split_nodes_delimiter
from textnode import split_nodes_image, split_nodes_link, text_to_textnodes
from htmlnode import LeafNode

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

class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text_node_to_html_node(self):
        node = TextNode("normal", TextType.NORMAL)
        text = "normal"
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("bold", TextType.BOLD)
        text = "<b>bold</b>"
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("italic", TextType.ITALIC)
        text = "<i>italic</i>"
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("code", TextType.CODE)
        text = "<code>code</code>"
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("link", TextType.LINK, "libellen.tv")
        text = '<a href="libellen.tv">link</a>'
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("link", TextType.LINK)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)
        node = TextNode(None, TextType.IMAGE, "https://www.libellen.tv/images/viele-libellen.webp")
        text = '<img src="https://www.libellen.tv/images/viele-libellen.webp"></img>'
        self.assertEqual(text_node_to_html_node(node).to_html(), text)
        node = TextNode("image", TextType.IMAGE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_nodes_delimiter(self):
        node_list = split_nodes_delimiter(split_nodes_delimiter([TextNode("normal **bold** normal *italic*", TextType.NORMAL)], "**", TextType.BOLD), "*", TextType.ITALIC)
        expected = [TextNode("normal ", TextType.NORMAL), TextNode("bold", TextType.BOLD), TextNode(" normal ", TextType.NORMAL), TextNode("italic", TextType.ITALIC)]
        self.assertEqual(node_list, expected)
        node_list = split_nodes_delimiter([TextNode("`code`", TextType.NORMAL)], "`", TextType.CODE)
        expected = [TextNode("code", TextType.CODE)]
        self.assertEqual(node_list, expected)
        node_list = [TextNode("normal *problem", TextType.NORMAL)]
        with self.assertRaises(ValueError):
            split_nodes_delimiter(node_list, "*", TextType.ITALIC)

class TestLinkAndImageExtraction(unittest.TestCase):
    def test_split_images(self):
        text_node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)", TextType.NORMAL)
        expected = [TextNode("This is text with a ", TextType.NORMAL), TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"), TextNode(" and ", TextType.NORMAL), TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg")]
        self.assertEqual(split_nodes_image([text_node]), expected)
        text_node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link [to boot dev](https://www.boot.dev)", TextType.NORMAL)
        expected = [TextNode("This is text with a ", TextType.NORMAL), TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"), TextNode(" and a link [to boot dev](https://www.boot.dev)", TextType.NORMAL)]
        self.assertEqual(split_nodes_image([text_node]), expected)
    
    def test_split_links(self):
        text_node = TextNode("This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)", TextType.NORMAL)
        expected = [TextNode("This is text with a link ", TextType.NORMAL), TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"), TextNode(" and ", TextType.NORMAL), TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev")]
        self.assertEqual(split_nodes_link([text_node]), expected)
        text_node = TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link [to boot dev](https://www.boot.dev)", TextType.NORMAL)
        expected = [TextNode("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a link ", TextType.NORMAL), TextNode("to boot dev", TextType.LINK, "https://www.boot.dev")]
        self.assertEqual(split_nodes_link([text_node]), expected)
    
class TestTextToNodeText(unittest.TestCase):
    def test_text_to_textnodes(self):
        actual = text_to_textnodes("This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        expected = [
                        TextNode("This is ", TextType.NORMAL),
                        TextNode("text", TextType.BOLD),
                        TextNode(" with an ", TextType.NORMAL),
                        TextNode("italic", TextType.ITALIC),
                        TextNode(" word and a ", TextType.NORMAL),
                        TextNode("code block", TextType.CODE),
                        TextNode(" and an ", TextType.NORMAL),
                        TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                        TextNode(" and a ", TextType.NORMAL),
                        TextNode("link", TextType.LINK, "https://boot.dev"),
                    ]
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()

