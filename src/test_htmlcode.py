import unittest

from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        props_html = HTMLNode(props = {"color": "red"}).props_to_html()
        text = "color=red"
        self.assertEqual(props_html, text)
        props_set = set(HTMLNode(props = {"color": "red", "font": "arial"}).props_to_html().split(' '))
        text_set = set(["color=red", "font=arial"])
        self.assertEqual(props_set, text_set)

    def test_repr(self):
        node = HTMLNode("test_tag", "test_value", [HTMLNode("child_tag")], {"color": "red"})
        text = "HTMLNode(test_tag, test_value, [HTMLNode(child_tag, None, None, None)], {'color': 'red'})"
        self.assertEqual(str(node), text)


if __name__ == "__main__":
    unittest.main()

