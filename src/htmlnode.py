class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        return ' '.join(list(map(lambda key: f"{key}={self.props[key]}", self.props)))

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.value:
            raise ValueError("LeafNode without value is not allowed")
        if not self.tag:
            return self.value
        return f"<{self.tag} {self.props_to_html()}>{self.value}</{self.tag}>"
        
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
       
    def to_html(self):
        if not self.tag:
            raise ValueError("ParentNode without tag is not allowed")
        if not self.children:
            raise ValueError("ParentNode without children is not allowed")
        content = ''.join(list(map(lambda child: child.to_html(), self.children)))
        return f"<{self.tag} {self.props_to_html()}>{content}</{self.tag}>"
    
    def __repr__(self):
        return f"ParentNode({self.tag}, {self.children}, {self.props})"
