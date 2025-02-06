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
            content += head + "\n"
            head, tail, _ = split_in_two(tail, '\n')
        return [BlockNode(content.rstrip(), BlockType.UNORDERED_LIST)] + markdown_to_block_nodes(f"{head}\n{tail}")
    
    # Ordered lists start with either "s\d+. " in each line for some single line whitestring
    # Ordered lists end with first line without "s\d+. " or "s " or at the end of the file
    if re.match(r"\s*\d+. ", head):
        space = re.match(r"(\s*)\d+. ", head)[1]
        content = ""
        while re.match(rf"{space}(\d+.|) ", head):
            content += head + "\n"
            head, tail, _ = split_in_two(tail, '\n')
        return [BlockNode(content.rstrip(), BlockType.ORDERED_LIST)] + markdown_to_block_nodes(f"{head}\n{tail}")
    
    # Paragraphs are the default case
    # A paragraph ends with an empty line
    markdown_split = re.split(r"\n\s*\n", markdown, 1)
    head = markdown_split[0]
    tail = "" if len(markdown_split) == 1 else markdown_split[1]
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








def markdown_to_html(markdown):
    blocks_text = markdown_to_blocks(markdown)
    blocks_with_types = [(block_text, block_to_block_type(block_text)) for block_text in blocks_text]
    children = [block_to_html_node(block_with_type) for block_with_type in blocks_with_types]
    return ParentNode("div", children)

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    return [block.strip() for block in blocks if block.strip() != ""]
    
def block_to_block_type(block):
    # Headings start with 1-6 times '#' and are followed by a space
    for i in range (1, 7):
        prefix = "#"*i+" "
        if block.startswith(prefix):
            return BlockType.HEADING
    
    # Code blocks both start as well as end with "```"
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
        
    lines = block.split("\n")
    
    # Quotes start with ">" at each line
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    # Unordered lists start with either "* " or "- " in each line
    if all(line.startswith("* ") or line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    if all(line.startswith(f"{i+1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST
        
    # Paragraphs are the default case
    return BlockType.PARAGRAPH

def block_to_html_node(block_with_type):
    match block_with_type[1]:
        case BlockType.PARAGRAPH:
            content = block_with_type[0]
            return ParentNode("p", text_to_children(content))
        case BlockType.HEADING:
            level, content = block_with_type[0].split(' ', 1)
            return ParentNode(f"h{len(level)}", text_to_children(content))
        case BlockType.CODE:
            content = block_with_type[0][3:-3].strip()
            return ParentNode("pre", [ParentNode("code", text_to_children(content))])
        case BlockType.QUOTE:
            raw_content = block_with_type[0]
            content = '\n'.join([line[1:].strip() for line in raw_content.split("\n")])
            return ParentNode("blockquote", text_to_children(content))
        case BlockType.UNORDERED_LIST:
            raw_content = block_with_type[0]
            content = '\n'.join([line.split(" ", 1)[1].strip() for line in raw_content.split("\n")])
            children = [ParentNode("li", text_to_children(line)) for line in content.split("\n")]
            return ParentNode("ul", children)
        case BlockType.ORDERED_LIST:
            raw_content = block_with_type[0]
            content = '\n'.join([line.split(" ", 1)[1].strip() for line in raw_content.split("\n")])
            children = [ParentNode("li", text_to_children(line)) for line in content.split("\n")]
            return ParentNode("ol", children)
    raise ValueError("Unknown BlockType")
        

def text_to_children(text):
    return [text_node_to_html_node(text_node) for text_node in text_to_textnodes(text)]



