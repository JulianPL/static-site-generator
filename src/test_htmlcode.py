import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        props_html = HTMLNode(props = {"color": "red"}).props_to_html()
        text = 'color="red"'
        self.assertEqual(props_html, text)
        props_set = set(HTMLNode(props = {"color": "red", "font": "arial"}).props_to_html().split(' '))
        text_set = set(['color="red"', 'font="arial"'])
        self.assertEqual(props_set, text_set)
    
    def test_to_html(self):
        node = HTMLNode(props = {"color": "red"})
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_repr(self):
        node = HTMLNode("test_tag", "test_value", [HTMLNode("child_tag")], {"color": "red"})
        text = "HTMLNode(test_tag, test_value, [HTMLNode(child_tag, None, None, None)], {'color': 'red'})"
        self.assertEqual(str(node), text)

class TestLeafNode(unittest.TestCase):
    def test_to_html(self):
        node = LeafNode("test_tag", None, {"color": "red"})
        with self.assertRaises(ValueError):
            node.to_html()
        node = LeafNode(None, "test_value", None)
        text = "test_value"
        self.assertEqual(node.to_html(), text)
        # if tag is None, props should be ignored
        node = LeafNode(None, "test_value", {"color": "red"})
        text = "test_value"
        self.assertEqual(node.to_html(), text)
        node = LeafNode("test_tag", "test_value", {"color": "red"})
        text = "<test_tag color=red>test_value</test_tag>"
    
    def test_repr(self):
        node = LeafNode("test_tag", "test_value", {"color": "red"})
        text = "LeafNode(test_tag, test_value, {'color': 'red'})"
        self.assertEqual(str(node), text)

class TestParentNode(unittest.TestCase):
    def test_to_html(self):
        child1 = LeafNode("test_tag", "test_value", {"color": "red"})
        child2 = LeafNode("test_tag2", "test_value2", {"color": "green"})
        childless = ParentNode("test_tag", None, {"color": "red"})
        with self.assertRaises(ValueError):
            childless.to_html()
        tagless = ParentNode(None, [child1], {"color": "red"})
        with self.assertRaises(ValueError):
            tagless.to_html()
        parent = ParentNode("outer_tag", [child1, child2], {"color": "yellow"})
        grandparent = ParentNode("outermost_tag", [parent], {"color": "black"})
        text = '<outermost_tag color="black"><outer_tag color="yellow"><test_tag color="red">test_value</test_tag><test_tag2 color="green">test_value2</test_tag2></outer_tag></outermost_tag>'
        self.assertEqual(grandparent.to_html(), text)
        
    
    def test_repr(self):
        node = ParentNode("test_tag", [HTMLNode("child_tag")], {"color": "red"})
        text = "ParentNode(test_tag, [HTMLNode(child_tag, None, None, None)], {'color': 'red'})"
        self.assertEqual(str(node), text)


if __name__ == "__main__":
    unittest.main()

