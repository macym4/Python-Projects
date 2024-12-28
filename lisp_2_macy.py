"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """

    def tokenize_recur(source, final=[]):
        next_ix = 1

        if not source:
            return final
        cur = source[0]
        rest = source[next_ix:]

        if cur in ("(", ")"):
            final.append(cur)

        elif cur == ";":
            while next_ix < len(source) and source[next_ix] != "\n":
                next_ix += 1
            next_ix += 1

        elif cur not in (" ", ";", "\n"):
            whole_cur = cur
            while next_ix < len(source) and source[next_ix] not in (
                " ",
                "(",
                ")",
                "\n",
            ):
                whole_cur += source[next_ix]
                next_ix += 1
            final.append(whole_cur)

        rest = source[next_ix:]

        if rest:
            tokenize_recur(rest, final)
        return final

    return tokenize_recur(source, [])


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    check_tokens(tokens)

    def parse_recur(tokens, final=[]):
        if not tokens:
            return final

        cur = number_or_symbol(tokens[0])
        next_ix = 1

        if isinstance(cur, (float, int)):
            final.append(cur)

        elif isinstance(cur, str) and cur not in ("()"):
            final.append(cur)

        elif cur == "(":
            close = find_close(tokens)
            next_ix = close + 1
            final.append(parse_recur(tokens[1:close], []))

        elif cur == ")":
            next_ix += 1

        rest = tokens[next_ix:]
        if rest:
            parse_recur(rest, final)
        return final

    final_result = parse_recur(tokens)

    if len(final_result) > 1:
        raise SchemeSyntaxError

    return final_result[0]


def find_close(tokens):
    count = 0
    for ix, cur in enumerate(tokens):
        if cur == "(":
            count += 1
        elif cur == ")" and count == 1:
            return ix
        elif cur == ")" and count != 1:
            count -= 1
    return None


def count_paranthesis(tokens):
    count = 0
    for cur in tokens:
        if cur == "(":
            count += 1
        if cur == ")":
            count -= 1
    return count


def check_paranthesis(tokens):
    """
    Counts the number of paranthesis in an expression
    to make sure that they always begin with an open
    and end with the right number of closed. Returns with
    failure if that is ever not the case.
    """
    count = 0
    index = 0
    for cur in tokens:
        if index == len(tokens) - 1:
            return None
        elif cur == "(":
            count += 1
        elif cur == ")":
            count -= 1
        if count < 0:
            return "failure"
    return None


def check_tokens(tokens):
    """
    Checks that the tokens begins with open paranthesis (not closed)
    and that it contains the right number of paranthesis so that
    they are all paired.
    """
    if count_paranthesis(tokens) != 0:
        raise SchemeSyntaxError

    if check_paranthesis(tokens) == "failure":
        raise SchemeSyntaxError


######################
# Built-in Functions #
######################


def multiply(args):
    final = 1
    for arg in args:
        final *= arg
    return final


def divide(args):
    final = args[0]
    for arg in args[1:]:
        final /= arg
    return final


def check_equality(args):
    for ix in range(len(args) - 1):
        if args[ix] != args[ix + 1]:
            return False
    return True


def greater_than(args):
    for ix in range(len(args) - 1):
        if args[ix] <= args[ix + 1]:
            return False
    return True


def greater_than_eq(args):
    for ix in range(len(args) - 1):
        if args[ix] < args[ix + 1]:
            return False
    return True


def less_than(args):
    for ix in range(len(args) - 1):
        if args[ix] >= args[ix + 1]:
            return False
    return True


def less_than_eq(args):
    for ix in range(len(args) - 1):
        if args[ix] > args[ix + 1]:
            return False
    return True


def handle_append(exprs):
    if not exprs:
        return []

    if exprs[0] == []:
        return handle_append(exprs[1:])

    try:
        return Pair(exprs[0].car, handle_append([exprs[0].cdr] + exprs[1:]))
    except AttributeError:
        raise SchemeEvaluationError


def append_exec(exprs):
    for expr in exprs:
        if expr == ():
            expr = []

    for ix in range(len(exprs)):
        if not isinstance(exprs[ix], Pair) and not exprs[ix] == []:
            raise SchemeEvaluationError

    return handle_append(exprs)


def indexed_list(expr, ix):
    if expr == []:
        raise SchemeEvaluationError

    cur_val = expr.cdr
    if cur_val == []:
        if ix != 0:
            raise SchemeEvaluationError
        return expr.car
    if ix > 0:
        ix -= 1
        return indexed_list(cur_val, ix)
    else:
        return expr.car


def list_ref_exec(exprs):
    try:
        expr = exprs[0]
        ix = exprs[1]

        if exprs[2:]:
            raise SchemeEvaluationError

    except IndexError:
        raise SchemeEvaluationError

    if not expr:
        raise SchemeEvaluationError
    try:
        if expr.is_list() is True:
            return indexed_list(expr, ix)
        else:
            if ix != 0:
                raise SchemeEvaluationError
            else:
                return expr.car
    except AttributeError:
        raise SchemeEvaluationError


def cars_exec(exprs):
    if len(exprs) > 1 or not isinstance(exprs[0], Pair):
        raise SchemeEvaluationError
    return exprs[0].car


def cdrs_exec(exprs):
    if len(exprs) > 1 or not isinstance(exprs[0], Pair):
        raise SchemeEvaluationError
    return exprs[0].cdr


def cons_exec(exprs):
    if len(exprs) != 2:
        raise SchemeEvaluationError
    return Pair(exprs[0], exprs[1])


def handle_lists(exprs):
    if not exprs:
        return []
    return Pair(exprs[0], handle_lists(exprs[1:]))


def list_exec(exprs):
    if not exprs:
        return []
    return handle_lists(exprs)


def list_ques_exec(exprs):
    if len(exprs) > 1:
        raise SchemeEvaluationError

    cur_val = exprs[0]

    if cur_val == []:
        return True

    if isinstance(cur_val, Pair):
        if isinstance(cur_val.cdr, (Pair, list, tuple)):
            if cur_val.is_list() is False:
                return False
            return True

    if isinstance(cur_val, list):
        if cur_val == [] or cur_val[:0] in ("list", "cons"):
            return True
        return False


def begin_exec(exprs):
    return exprs[-1]


def length_exec(exprs):
    '''
    This executes the function for length
    '''
    if exprs:
        if len(exprs) > 1:
            raise SchemeEvaluationError

        if isinstance(exprs[:0], list):
            cur_val = exprs[0]
        else:
            cur_val = exprs

        if cur_val == []:
            return 0
    else:
        raise SchemeEvaluationError
    return find_length(cur_val)


def not_exec(tree, frame):
    if len(tree) != 2:
        raise SchemeEvaluationError

    if evaluate(tree[1], frame) is True:
        return False
    return True


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": multiply,
    "/": divide,
    "equal?": check_equality,
    ">": greater_than,
    ">=": greater_than_eq,
    "<": less_than,
    "<=": less_than_eq,
    "car": cars_exec,
    "cdr": cdrs_exec,
    "cons": cons_exec,
    "list": list_exec,
    "list?": list_ques_exec,
    "length": length_exec,
    "list-ref": list_ref_exec,
    "append": append_exec,
    "begin": begin_exec,
}


##############
# Classes #
##############


class Frame:
    """
    A frame contains the bindings from a variable name to what it
    evaluates to. It possibly contains a parent frame as well.

    You need to be able to add new values to this frame as well as
    lookup values in this frame and look up its parent frame.
    """

    def __init__(self, parent):
        # parent is another frame!
        self.parent = parent

        # this is an empty dictionary that this frame's variable assignments
        # will eventually go in
        self.vars = {}

    def add_value(self, new_var, new_var_val):
        self.vars.update({new_var: new_var_val})

    def add_value_dict(self, dictionary):
        self.vars = dictionary

    def look_up_value(self, var):
        try:
            return self.vars[var]
        except KeyError:
            if self.parent:
                return self.parent.look_up_value(var)
            raise SchemeNameError

    def look_up_frame(self, var):
        """
        Returns frame a certain value is in.
        """
        if var in self.vars:
            return self
        else:
            if self.parent:
                return self.parent.look_up_frame(var)
            else:
                raise SchemeNameError


class Function:
    """
    A class that stores information about user-made
    functions. It stores the expression the function will run,
    the names of the function's parameters, and a pointer to
    the frame in which the function was defined.
    """

    def __init__(self, params, expr, frame):
        """
        Params is a dictionary, expr is a expression (inside paranthesis)
        and frame is a Frame, which I have already defined the class
        for.
        """
        self.params = params
        self.expr = expr
        self.frame = frame

    def __get__(self):
        return self.expr

    def __call__(self, values):
        if not isinstance(self, Function):
            raise SchemeEvaluationError("This self is not a function")
        if len(self.params) != len(values):
            raise SchemeEvaluationError("Too many or too little parameters inputted")
        new_frame = Frame(self.frame)
        for ix, param in enumerate(self.params):
            new_frame.add_value(param, values[ix])
        return evaluate(self.expr, new_frame)


class Pair:
    """
    Pair creates a pair where the first value
    is called car and the second is called cdr.
    """

    def __init__(self, car, cdr):
        self.name = self
        self.car = car
        self.cdr = cdr

    def find_length(self):
        if not self.cdr:
            return 1
        if isinstance(self.cdr, Pair):
            return 1 + self.cdr.find_length()
        return 2

    def is_list(self):
        if isinstance(self.car, int) and isinstance(self.cdr, int):
            return False
        elif isinstance(self.cdr, Pair):
            return self.cdr.is_list()
        return True


##############
# Evaluation #
##############


def make_initial_frame():
    built_in = Frame(None)
    for operation in scheme_builtins:
        built_in.add_value(operation, scheme_builtins[operation])

    return Frame(built_in)


def define(tree, frame):
    eval_value = evaluate(tree[2], frame)
    frame.add_value(tree[1], eval_value)
    return eval_value


def check_and(args, frame):
    for arg in args:
        if evaluate(arg, frame) is False:
            return False
    return True


def check_or(args, frame):
    for arg in args:
        if evaluate(arg, frame) is True:
            return True
    return False


def find_length(val):
    if not val:
        return 0

    if not isinstance(val, Pair):
        raise SchemeEvaluationError

    if val.is_list() is True:
        return list_len_recur(val)
    raise SchemeEvaluationError


def list_len_recur(val):
    if not val.cdr:
        return 1
    else:
        return 1 + list_len_recur(val.cdr)


def evaluate(tree, frame=make_initial_frame()):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    if isinstance(tree, (int, float)):
        return tree

    elif isinstance(tree, str):
        if tree == "#t":
            return True
        elif tree == "#f":
            return False
        return frame.look_up_value(tree)

    elif isinstance(tree, list):
        return list_options(tree, frame)


def list_options(tree, frame):
    """
    Executes one of the options avaliable to a list
    and returns it appropriately
    """
    if not tree:
        return []

    if tree[0] == "define":
        if isinstance(tree[1], list):
            new_expr = ["define", tree[1][0], ["lambda", tree[1][1:], tree[2]]]
            return evaluate(new_expr, frame)
        else:
            return define(tree, frame)

    elif isinstance(tree[0], (int, float)):
        raise SchemeEvaluationError("If its a list and its only containing numbers")

    elif tree[0] == "lambda":
        return Function(tree[1], tree[2], frame)

    elif tree[0] in ("if", "and", "or"):
        return conditionals(tree, frame)

    elif tree[0] == "not" and tree[0] not in frame.vars:
        return not_exec(tree, frame)

    elif tree[0] in ("del", "let", "set!"):
        return modify_variables(tree, frame)

    else:
        try:
            op = evaluate(tree[0], frame)
            elements = [evaluate(ele, frame) for ele in tree[1:]]
            return op(elements)
        except IndexError as exc:
            raise SchemeEvaluationError from exc


def conditionals(tree, frame):
    if tree[0] == "if":
        if evaluate(tree[1], frame) is True:
            return evaluate(tree[2], frame)
        else:
            return evaluate(tree[3], frame)
    elif tree[0] == "and":
        return check_and(tree[1:], frame)

    elif tree[0] == "or":
        return check_or(tree[1:], frame)

def modify_variables(tree, frame):
    if tree[0] == "del":
        if tree[1] in frame.vars:
            returning = frame.vars.pop(tree[1])
            return returning
        else:
            raise SchemeNameError

    elif tree[0] == "let":
        new_frame = Frame(frame)
        for pair in tree[1]:
            new_frame.add_value(pair[0], evaluate(pair[1], frame))

        return evaluate(tree[2], new_frame)

    elif tree[0] == "set!":
        next_frame = frame.look_up_frame(tree[1])

        if next_frame:
            new_val = evaluate(tree[2], frame)
            next_frame.vars[tree[1]] = new_val
            return new_val
        else:
            raise SchemeEvaluationError


def evaluate_file(file_name, frame=make_initial_frame()):
    with open(file_name, "r") as the_file:
        read_file = parse(tokenize(the_file.read()))
    return evaluate(read_file, frame)


if __name__ == "__main__":
    # NOTE THERE HAVE BEEN CHANGES TO THE REPL, KEEP THIS CODE BLOCK AS WELL
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    g_frame = make_initial_frame()
    for files in sys.argv[1:]:
        evaluate_file(files, g_frame)

    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, global_frame=g_frame
    ).cmdloop()

    opt = parse(tokenize("(list-ref (list 9 8 7) 2)"))
    print(evaluate(opt))
