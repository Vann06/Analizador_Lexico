

from syntax_tree import Leaf, Concat, Star


def nullable(node):
    if isinstance(node, Leaf):
        return False
    elif isinstance(node, Concat):
        return nullable(node.left) and nullable(node.right)
    elif isinstance(node, Star):
        return True
    

def firstpos(node):
    if isinstance(node, Leaf):
        return {node.position}
    elif isinstance(node, Concat):
        if nullable(node.left):
            return firstpos(node.left).union(firstpos(node.right))
        else:
            return firstpos(node.left)
    elif isinstance(node, Star):
        return firstpos(node.child)
    
def lastpos(node):
    if isinstance(node, Leaf):
        return {node.position}
    elif isinstance(node, Concat):
        if nullable(node.right):
            return lastpos(node.left).union(lastpos(node.right))
        else:
            return lastpos(node.right)
    elif isinstance(node, Star):
        return lastpos(node.child)
    
def followpos(node, followpos_dict):
    if isinstance(node, Concat):
        for i in lastpos(node.left):
            if i in followpos_dict:
                followpos_dict[i] = followpos_dict[i].union(firstpos(node.right))
            else:
                followpos_dict[i] = firstpos(node.right)
    elif isinstance(node, Star):
        for i in lastpos(node.child):
            if i in followpos_dict:
                followpos_dict[i] = followpos_dict[i].union(firstpos(node.child))
            else:
                followpos_dict[i] = firstpos(node.child)