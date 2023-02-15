# -*- coding: UTF-8 -*-
"""Functions related to expression evaluation.

"""
import ast
try:
    import __builtin__ as builtins
except ImportError:
    import builtins
from collections import deque

from .common import set_exception


__all__ = __features__ = ["eval_ast_nodes", "eval_free_variables"]  # eval2 is bound to the builtins, hence not included


BL_BUILTINS = ("breakpoint", "classmethod", "compile", "delattr", "eval", "exec", "exit", "getattr", "globals", "help",
               "hasattr", "input", "locals", "memoryview", "open", "print", "property", "quit", "staticmethod", "super")
WL_NODES = ("add", "and", "binop", "bitand", "bitor", "bitxor", "boolop", "call", "cmpop", "compare", "comprehension",
            "constant", "dict", "div", "eq", "expr", "expr_context", "expression", "floordiv", "for", "generatorexp",
            "gt", "gte", "in", "index", "invert", "is", "isnot", "list", "listcomp", "load", "lshift", "lt", "lte",
            "matmult", "mod", "mult", "name", "nameconstant", "not", "noteq", "notin", "num", "operator", "or", "pow",
            "rshift", "set", "slice", "store", "str", "sub", "subscript", "tuple", "uadd", "unaryop", "usub")


set_exception("ForbiddenNameError", "NameError")
set_exception("ForbiddenNodeError", "ValueError")
set_exception("UnknownNameError", "NameError")


def __eval(expr, globals=None, locals=None, bl_builtins=BL_BUILTINS, wl_nodes=WL_NODES, eval_=True):
    if globals is None:
        globals = {n: getattr(builtins, n) for n in dir(builtins)}
    if locals is None:
        locals = {}
    names = list(globals.keys()) + list(locals.keys())
    # forbid code objects
    code_obj = type(compile("None", "<string>", "exec"))
    for name in names:
        if isinstance(globals.get(name, locals.get(name)), code_obj):
            raise TypeError("code objects are forbidden")
    # walk the AST and only allow the whitelisted nodes
    extra_names = []
    for node in __walk(ast.parse(expr, mode="eval")):
        if any(n in list(map(lambda x: x.name, node.parents)) for n in ("Lambda", "ListComp", "GeneratorExp")) and \
           hasattr(node, "id") and node.id not in extra_names:
            extra_names.append(node.id)
        # blacklist dunders and input list
        if isinstance(node, ast.Name) and (node.id.startswith("__") or node.id in bl_builtins):
            raise ForbiddenNameError("name '%s' is not allowed" % node.id)
        # check if the node's identifier exists in the known names
        if isinstance(node, ast.Name) and node.id not in (names + extra_names):
            raise UnknownNameError("name '%s' is not defined" % node.id)
        # whitelist AST nodes based on the input list
        if node.name.lower() not in wl_nodes:
            e = ForbiddenNodeError("node '%s' is not allowed" % node.name)
            e.node = node.name
            raise e
    if eval_:
        return eval(expr, globals, locals)


def __walk(node):
    node.depth = 0
    node.parents = []
    todo = deque([node])
    while todo:
        node = todo.popleft()
        node.name = node.__class__.__name__
        children = list(ast.iter_child_nodes(node))
        for child in children:
            child.depth = node.depth + 1
            child.parents = node.parents + [node]
        todo.extend(children)
        yield node


def eval_ast_nodes(*expressions, **variables):
    """
    This allows to compute the list of AST nodes that are necessary to be whitelisted for running the given expressions.
    
    :param expressions: list of expressions to be evaluated
    :param variables:   dictionary of variables for use with the expressions
    """
    nodes = []
    for expression in expressions:
        while True:
            try:
                __eval(expression, None, variables, wl_nodes=nodes, eval_=False)
                break
            except ValueError as e:
                nodes.append(e.node.lower())
    return nodes


def eval_free_variables(expression, **variables):
    """
    This allows to identify the free variables from a given expression.
    
    :param expression: expression to be evaluated
    :param variables:  dictionary of variables for use with the expression
    """
    free_vars = []
    for node in __walk(ast.parse(expression, mode="eval")):
        if any(n in list(map(lambda x: x.name, node.parents)) for n in ("Lambda", "ListComp", "GeneratorExp")) and \
           hasattr(node, "id") and node.id not in variables and node.id not in free_vars:
            free_vars.append(node.id)
    return free_vars


def eval2(expression, globals=None, locals=None, blacklist_builtins=BL_BUILTINS, whitelist_nodes=WL_NODES):
    """
    This evaluates an expression while excluding dangerous built-ins or built-ins that are not necessary for simple
     expressions and only allowing a predefined or given set of AST nodes.
    
    NB: ts.eval_ast_nodes can be used to identify the necessary nodes for a predefined list of expressions, for the sake
         of restricting evaluation as much as possible and eventually making it safe.
    
    :param expression: expression to be evaluated
    :param globals:    dictionary of globals
    :param locals:     dictionary of locals
    :param nodes:      allowed AST nodes
    """
    return __eval(expression, globals, locals, blacklist_builtins, whitelist_nodes)
builtins.eval2 = eval2

