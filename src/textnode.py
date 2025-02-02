from enum import Enum
import re
from htmlnode import LeafNode

class TextType(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        return self.text == other.text and self.text_type == other.text_type and self.url == other.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
            
            
                
                
def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.NORMAL:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            if not text_node.url:
                raise ValueError("Missing url in TextNode with TextType LINK")
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            if not text_node.url:
                raise ValueError("Missing url in TextNode with TextType IMAGE")
            if text_node.text:
                return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
            return LeafNode("img", "", {"src": text_node.url})
        case _:
            raise ValueError("Invalid TextType in TextNode")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    splitted_nodes = [node.text.split(delimiter) if node.text_type == TextType.NORMAL else [node] for node in old_nodes]
    translated_nodes = [    [TextNode(node_text, text_type) if index % 2 == 1 else TextNode(node_text, TextType.NORMAL) 
                            for index, node_text
                            in enumerate(node_list)]   
                        if type(node_list[0]) is str
                            else node_list 
                        for node_list 
                        in splitted_nodes]
    if any(len(node_list) % 2 == 0 for node_list in translated_nodes):
        raise ValueError("Mismatched delimiter")
    return [node for node in sum(translated_nodes, []) if node.text != ""]

def split_nodes_image(old_nodes):
    return sum([split_single_node_image(node) for node in old_nodes] , [])

def split_nodes_link(old_nodes):
    return sum([split_single_node_link(node) for node in old_nodes] , [])

def split_single_node_image(node):
    def extract_markdown_images(text):
        return re.findall(r"(!\[([^\[\]]*)\]\(([^\(\)]*)\))", text)
    ret = []
    image_matches = extract_markdown_images(node.text)
    text = node.text
    for image_match in image_matches:
        split = text.split(image_match[0] , 1)
        if split[0]:
            ret.append(TextNode(split[0], TextType.NORMAL))
        ret.append(TextNode(image_match[1], TextType.IMAGE, image_match[2]))
        text = split[1]
    if text:
        ret.append(TextNode(text, TextType.NORMAL))
    return ret

def split_single_node_link(node):
    def extract_markdown_links(text):
        return re.findall(r"((?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\))", text)
    ret = []
    link_matches = extract_markdown_links(node.text)
    text = node.text
    for link_match in link_matches:
        split = text.split(link_match[0] , 1)
        if split[0]:
            ret.append(TextNode(split[0], TextType.NORMAL))
        ret.append(TextNode(link_match[1], TextType.LINK, link_match[2]))
        text = split[1]
    if text:
        ret.append(TextNode(text, TextType.NORMAL))
    return ret




