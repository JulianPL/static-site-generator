import logging

from enum import Enum
import re
from htmlnode import ParentNode
from textnode import text_to_textnodes, text_node_to_html_node

logger = logging.getLogger(__name__)

class BlockType(Enum):
    MAIN = "main"
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

class BlockNode:
    def __init__(self, content, block_type):
        self.content = content
        self.block_type = block_type
    
    def __eq__(self, other):
        return self.content == other.content and self.block_type == other.block_type

    def __repr__(self):
        return f"BlockNode({self.content}, {self.block_type.value})"

def extract_title(markdown):
    # Search for line with "# {Title}" preceded and succeeded by only whitespace
    titles = re.findall(r"(?:^|\n\s*)# ([^\n]*)(?:$|\n)", markdown)
    if not titles:
        logger.warning(f"No title found")
        return ""
    return titles[0].strip()

def markdown_to_block_nodes(markdown):
    if markdown == "":
        return []
    
    head, tail, _ = split_in_two(markdown, '\n')
    
    # Ignore empty heads
    if head.strip() == "":
        return markdown_to_block_nodes(tail)
    
    # Headings start with 1-6 times '#' and are followed by a space and at least one none-whitespace
    # Headings are single lines
    if re.fullmatch(r"\s*#{1,6} .*\S.*", head):
        return [BlockNode(head.strip(), BlockType.HEADING)] + markdown_to_block_nodes(tail)
    
    # Code blocks both start as well as end with "```"
    # Code blocks end at the second "```" or at the end of the markdown block (with a logger warning)
    # Line with the closing "```" is defined to end with "```"
    if re.match(r"\s*```", head):
        space, code, tail_raw, count = split_in_three(markdown, "```")
        if count <= 2:
            logger.warning(f"Unclosed code block starting at: {head}")
        _, tail, _ = split_in_two(tail_raw, '\n')
        return [BlockNode(code.rstrip(), BlockType.CODE)] + markdown_to_block_nodes(tail)
    
    # Quotes start with "> " at each line, independent of indentation
    # Quotes end with first line without "> " or at the end of the file
    if re.match(r"\s*> ", head):
        content = ""
        while re.match(r"\s*> ", head):
            content += head.split('> ', 1)[1] + "\n"
            head, tail, _ = split_in_two(tail, '\n')
        return [BlockNode(content.rstrip(), BlockType.QUOTE)] + markdown_to_block_nodes(f"{head}\n{tail}")
    
    # Unordered lists start with either "s* " or "s- " in each line for some single line whitestring
    # Unordered lists end with first line without "s* " or "s- " or "s " or at the end of the file
    if re.match(r"\s*(\*|-) ", head):
        space = re.match(r"(\s*)(\*|-) ", head)[1]
        content = ""
        while re.match(rf"{space}(\*|-|) ", head):
            content += head[len(space):] + "\n"
            head, tail, _ = split_in_two(tail, '\n')
        return [BlockNode(content.rstrip(), BlockType.UNORDERED_LIST)] + markdown_to_block_nodes(f"{head}\n{tail}")
    
    # Ordered lists start with either "s\d+. " in each line for some single line whitestring
    # Ordered lists end with first line without "s\d+. " or "s " or at the end of the file
    if re.match(r"\s*\d+\. ", head):
        space = re.match(r"(\s*)\d+\. ", head)[1]
        content = ""
        while re.match(rf"{space}(\d+\.|) ", head):
            content += head[len(space):] + "\n"
            head, tail, _ = split_in_two(tail, '\n')
        return [BlockNode(content.rstrip(), BlockType.ORDERED_LIST)] + markdown_to_block_nodes(f"{head}\n{tail}")
    
    # Paragraphs are the default case
    # A paragraph ends with an empty line or the start of a non-paragraph-block
    markdown_split = re.split(r"\n(\s*(?:#{1,6} |```|> |\* |- |\d+\. |\n))", markdown, 1)
    head = markdown_split[0]
    tail = "" if len(markdown_split) <= 2 else markdown_split[1]+markdown_split[2]
    return [BlockNode(head.strip(), BlockType.PARAGRAPH)] + markdown_to_block_nodes(tail)

def split_in_two(text, separator):
    text_split = text.split(separator, 1)
    head = text_split[0]
    tail = "" if len(text_split) == 1 else text_split[1]
    return head, tail, len(text_split)

def split_in_three(text, separator):
    text_split = text.split(separator, 2)
    head = text_split[0]
    middle = "" if len(text_split) <= 1 else text_split[1]
    tail = "" if len(text_split) <= 2 else text_split[2]
    return head, middle, tail, len(text_split)

def split_into_list_item_nodes(content, delimiter):
    list_items = re.split(delimiter, content)
    children = []
    for list_item in list_items:
        grand_children = list(map(lambda block_node: block_node_to_html_node(block_node), markdown_to_block_nodes(list_item)))
        if len(grand_children) != 0:
            child_new = ParentNode("li", grand_children)
            children.append(child_new)
    return children

def block_node_to_html_node(block_node):
    match block_node.block_type:
        # A paragraph does not contain inner blocks and the content is already text
        case BlockType.PARAGRAPH:
            content = block_node.content
            return ParentNode("p", text_to_children(content))
        # A heading does not contain inner blocks
        # The content is level-many '#', a space and the text
        case BlockType.HEADING:
            level, content = block_node.content.split(' ', 1)
            return ParentNode(f"h{len(level)}", text_to_children(content))
        # A code block contains the chosen language in the first line
        # each other line is already text
        case BlockType.CODE:
            language, code, _ = split_in_two(block_node.content, '\n')
            return ParentNode("pre", [ParentNode("code", text_to_children(code), {"class": f"language-{language}"})])
        # A quote-block may contain any other blocks. The block-prefixes are already cut off.
        case BlockType.QUOTE:
            children = list(map(lambda block_node: block_node_to_html_node(block_node), markdown_to_block_nodes(block_node.content)))
            return ParentNode("blockquote", children)
        # An unordered-list-block may contain any other blocks. The block-prefixes are not yet cut off.
        case BlockType.UNORDERED_LIST:
            children = split_into_list_item_nodes(block_node.content, r"^. |\n\* |\n- ")
            return ParentNode("ul", children)
        # An ordered-list-block may contain any other blocks. The block-prefixes are not yet cut off.
        case BlockType.ORDERED_LIST:
            children = split_into_list_item_nodes(block_node.content, r"^\d+\. |\n\d+\. ")
            return ParentNode("ol", children)
        # The main node contain all inner blocks which are not parsed yet
        case BlockType.MAIN:
            children = list(map(lambda block_node: block_node_to_html_node(block_node), markdown_to_block_nodes(block_node.content)))
            return ParentNode("div", children)
    logger.warning(f"Unknown BlockType in {block_node} - treat as paragraph instead")
    content = block_node.content
    return ParentNode("p", text_to_children(content))

def markdown_to_html(content):
    return block_node_to_html_node(BlockNode(content, BlockType.MAIN)).to_html()

def text_to_children(text):
    return [text_node_to_html_node(text_node) for text_node in text_to_textnodes(text)]

