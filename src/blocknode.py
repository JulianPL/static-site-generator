from enum import Enum
from htmlnode import ParentNode
from textnode import text_to_textnodes, text_node_to_html_node

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

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
    
    # Unordered lists start with either "*" or "-" in each line
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

def markdown_to_html(markdown):
    blocks_text = markdown_to_blocks(markdown)
    blocks_with_types = [(block_text, block_to_block_type(block_text)) for block_text in blocks_text]
    children = [block_to_html_node(blocks_with_types[0])]
    return ParentNode("div", children)
    