"""Structures for numpad language interpretation.

Importing this module will provide the following classes:
    NumpadError    : Error that is caught by an issue in numpad code, not
                   | Python code.
    Scope          : A level of variables and their associated values.
    NullScope      : Starting scope for a program.
    FuncExpression : A function that can be called with provided parameters.
    Expression     : A simple expression containing a single piece of data.
    OperExpression : Expression representing some operation between two other
                   | expressions.
    StatementBlock : Block of statements to all be run in a row.
    StatementSet   : Statement that sets the value of a variable to an
                   | expression's value.
    StatementDef   : Statement that defines a function.
    StatementIf    : Statement that runs its block if its expression doesn't
                   | equal 0.
    StatementWhile : Statement that runs its block as long as its expression
                   | doesn't equal 0.
"""

from math import log

VERBOSE = False


class NumpadError(Exception):
    """Error that is caught by an issue in numpad code, not Python code.

    Attributes:
        _message : str detailing the error that occurred.
    """


class Scope:
    """A level of variables and their associated values.

    Attributes:
        _parent    : Scope object appearing one level above.
        _variables : dict of variables defined within this scope.
    """

    def __init__(self, parent, variables=None):
        """Construct a new scope for keeping track of variables.

        Parameters:
            parent    : Scope object from which to inherit available variables.
            variables : A dict containing variables that have already been
                      | set.
                      | DEFAULT: Empty dict.
        """
        self._parent = parent
        if variables:
            self._variables = variables
        else:
            self._variables = {}

    def get_value(self, variable_name):
        """Get the value associated with the given variable name.

        Parameters:
            variable_name : A str object of the variable's name.
                          | REQ: The first character is '*'

        Returns:
            int or list associated with the given variable name.

        If not found within this scope, will search parent scopes.
        """
        assert variable_name and variable_name[0] == '*'

        if VERBOSE:
            print(self._variables)

        if variable_name in self._variables:
            return self._variables[variable_name]
        return self._parent.get_value(variable_name)

    def set_value(self, variable_name, value, indices=None):
        """Change one of the variables in this scope to the given value.

        Parameters:
            variable_name : A str object of the variable's name.
            value         : Expression object to be evaluated.
            indices       : list of indices of the value to be modified,
                          | assuming the variable is a list.
                          | The first int is the index, and the following
                          | are sub-indices.
        """
        if not indices:
            self._variables[variable_name] = value
        else:
            to_change = self._variables[variable_name]
            for i in indices[:-1]:
                if isinstance(i, str):
                    i = self.get_value(i)
                to_change = to_change[i]
            to_change[indices[-1]] = value

    def parent(self):
        """Get the parent scope.

        Returns:
            A reference to this scope's parent scope.
        """
        return self._parent

    def child(self, variables=None):
        """Create a new Scope with this object as its parent.

        Parameters:
            variables : A dict containing variables that have already been
                      | set.
                      | DEFAULT: Empty dict.

        Returns:
            Scope object with given variables and this object as a parent.
        """
        return Scope(self, variables)


class NullScope(Scope):
    """Starting scope for a program.

    Does not need a parent scope.

    Attributes:
        _variables : dict of variables defined within this scope.

    Inherits from Scope.
    """

    def __init__(self, variables=None):
        """Construct a new scope for keeping track of variables."""
        super().__init__(None, variables)

    def get_value(self, variable_name):
        """Get the value associated with the given variable name.

        Parameters:
            variable_name : A str object of the variable's name.
                          | REQ: The first character is '*'

        Returns:
            int or list associated with the given variable name.

        If not found within this scope, will raise "NOT FOUND" error.
        """
        assert variable_name and variable_name[0] == '*'

        if variable_name in self._variables:
            return self._variables[variable_name]

        raise NumpadError(f"Variable {variable_name} is not defined.")


class FuncExpression:
    """A function that can be called with provided parameters.

    Attributes:
        _param : list of default parameter values.
        _stmt  : StatementBlock object to potentially be run.
    """

    def __init__(self, paramlist, block):
        """Construct a function with the given default parameters and block.

        Parameters:
            paramlist : list of default parameter values.
            block     : StatementBlock object to potentially be run.
        """
        self._param = paramlist
        self._stmt = block

    def evaluate(self, _):
        """Return this object.

        This is odd, and I should probably change this, but function calling
        is handled pretty separately.
        """
        return self

    def run(self, scope, params=None):
        """Create a new child Scope and runs the statment block.

        Parameters:
            scope  : Scope object containing available variables.
            params : list of input parameter values.
        """
        params[len(params):] = self._param[len(params):]
        child = scope.child(
            {f"*0{str(i+1)}": val for i, val in enumerate(params)}
        )
        child.set_value("*00", 0)
        self._stmt.run(child)
        return child.get_value("*00")


class Expression:
    """A simple expression containing a single piece of data.

    Attributes:
        _value : Value of the expression.
               | Either a string containing a number or variable name, or
               | a list.
        _type  : Either 'int', 'str', or 'list'.
               | Determines how the expression should be evaluated.
    """

    def __init__(self, value):
        """Construct a simple Expression object.

        Parameters:
            value  : Either a string containing a number or variable name, or
                   | a list.
        """
        self._value = value
        self._type = type(value)

        if self._type == str and self._value[0] != '*':
            self._value = int(self._value)
            self._type = int

    def evaluate(self, scope):
        """Provide the evaluated value of this Expression.

        Parameters:
            scope : Scope object containing available variables.

        Returns:
            Either a list or an integer, depending on what was provided. Will
            resolve variables to their values.
        """
        if self._type == str:
            value = scope.get_value(self._value)
        elif self._type == list:
            value = [ele.evaluate(scope) for ele in self._value]
        else:
            value = self._value
        if VERBOSE:
            print("Expression:", self._value, "->", value)
        return value


class OperExpression:
    """Expression representing some operation between two other expressions.

    Attributes:
        _l     : Expression object on the left side.
        _op    : str object representing some operation.
        _r     : Expression object on the right side.
    """

    @staticmethod
    def _float_to_list(dec):
        """Create a list representing the decimal result of a division.

        Parameters:
            dec : float.

        Returns:
            list with two features:
                2. Integer representation, scaled up to keep decimal detail.
                3. Exponent.

        To transform back into a float, multiply the first element by 10 to
        the power of the second element.
        """
        power = 0
        while dec % 1 and power < 10:
            power -= 1
            dec *= 10
        return [int(dec), power]

    oper_int_int = {
        '..': lambda x, y: int(x == y),
        '.+': lambda x, y: int(x > y),
        '.-': lambda x, y: int(x < y),
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: OperExpression._float_to_list(x / y),
        '*+': lambda x, y: x ** y,
        '*-': lambda x, y: OperExpression._float_to_list(log(x) / log(y)),
        '/+': lambda x, y: x % y,
        '/-': lambda x, y: x // y
    }

    oper_list_int = {
        '..': lambda x, y: int(len(x) == y),
        '.+': lambda x, y: int(len(x) > y),
        '.-': lambda x, y: int(len(x) < y),
        '+': lambda x, y: x + [y],
        '-': lambda x, y: x[:y] + x[y+1:],
        '/': lambda x, y: x[y],
        '/+': lambda x, y: x[y:],
        '/-': lambda x, y: x[:y]
    }

    oper_int_list = {
        '..': lambda x, y: int(x == len(y)),
        '.+': lambda x, y: int(x > len(y)),
        '.-': lambda x, y: int(x < len(y))
    }

    oper_list_list = {
        '..': lambda x, y: int(x == y),
        '.+': lambda x, y: int(len(x) > len(y)),
        '.-': lambda x, y: int(len(x) < len(y)),
        '+': lambda x, y: x + [y],
        '*': lambda x, y: x + y,
        '/+': lambda x, y: int(all(i in x for i in y)),
        '/-': lambda x, y: int(all(i in y for i in x))
    }

    def __init__(self, expr_l, oper, expr_r):
        """Construct an operator expression.

        Parameters:
            expr_l : Expression object on the left side.
            oper   : str object representing some operation.
            espr_r : Expression object on the right side.
        """
        self._l, self._r = expr_l, expr_r
        self._op = oper

    def evaluate(self, scope):
        """Provide the evaluated value of this Expression.

        Parameters:
            scope : Scope object containing available variables.

        Returns:
            Either a list or an integer, depending on what was provided. Will
            resolve variables to their values.
        """
        val_l = self._l.evaluate(scope)
        val_r = self._r.evaluate(scope)

        type_l = type(val_l)
        type_r = type(val_r)

        if type_l == int and type_r == int:
            operation = OperExpression.oper_int_int[self._op]
            value = operation(val_l, val_r)
            if VERBOSE:
                print("OperExpression:", val_l, self._op, val_r, "->", value)
            return value

        if type_l == FuncExpression and type_r == list:
            if self._op != '-':
                raise NumpadError(
                    f"'{self._op}' operation not supported for func and list."
                )
            value = val_l.run(scope, val_r)
            if VERBOSE:
                print("Function call:", val_l, val_r, "->", value)
            return value

        if type_l == list and type_r == int:
            if self._op not in OperExpression.oper_list_int:
                raise NumpadError(
                    f"'{self._op}' not supported between list and int."
                )
            operation = OperExpression.oper_list_int[self._op]
            value = operation(val_l, val_r)
            if VERBOSE:
                print("OperExpression:", val_l, self._op, val_r, "->", value)
            return value

        if type_l == int and type_r == list:
            if self._op not in OperExpression.oper_int_list:
                raise NumpadError(
                    f"'{self._op}' not supported between int and list."
                )
            operation = OperExpression.oper_int_list[self._op]
            value = operation(val_l, val_r)
            if VERBOSE:
                print("OperExpression:", val_l, self._op, val_r, "->", value)
            return value

        if type_l == list and type_r == list:
            if self._op not in OperExpression.oper_list_list:
                raise NumpadError(
                    f"'{self._op}' not supported between list and list."
                )
            operation = OperExpression.oper_list_list[self._op]
            value = operation(val_l, val_r)
            if VERBOSE:
                print("OperExpression:", val_l, self._op, val_r, "->", value)
            return value

        raise NumpadError(
            "Operations between these types are not yet supported."
        )


class StatementBlock:
    """Block of statements to all be run in a row.

    Attributes:
        _stmts : list of objects that all start with 'Statement'.
    """

    def __init__(self):
        """Create a block of statements that starts empty."""
        self._stmts = []

    def append(self, stmt):
        """Add another statement to the block."""
        self._stmts.append(stmt)

    def run(self, scope):
        """Run all statements in this block in order."""
        for stmt in self._stmts:
            stmt.run(scope)


class StatementSet:
    """Statement that sets the value of a variable to an expression's value.

    Attributes:
        _variable : str representation of the variable being changed.
        _r        : Expression object on the right side.
    """

    def __init__(self, number, expr):
        """Construct a statement that will set a variable's value.

        Parameters:
            number : int representing the variable to be set.
            expr   : Expression object to be evaluated.
        """
        self._variable = f"*{str(number)}"
        self._r = expr

    def run(self, scope):
        """Evaluate the variable's value to the evaluated expression.

        Paramters:
            scope : Scope object containing available variables.
        """
        value = self._r.evaluate(scope)
        scope.set_value(self._variable, value)
        if VERBOSE:
            print("Set", self._variable, "to", value)


class StatementSetIndex:
    """Statement that sets the value of a variable to an expression's value.

    Attributes:
        _variable : str representation of the variable being changed.
        _indices  : list of index and sub-indices
        _r        : Expression object on the right side.
    """

    def __init__(self, number, indices):
        """Construct a statement that will set a variable's value.

        Parameters:
            number : int representing the variable to be set.
            expr   : int representing index of the list to be modified.
        """
        self._variable = f"*{str(number)}"
        self._indices = indices
        self._r = None

    def add_sub_index(self, index):
        """Add a sub-index to be set (for lists of lists).

        Parameters:
            index : int of the index to be modified.
                  | Index of the list at the last index provided.
        """
        self._indices.append(index)

    def set_expr(self, expr):
        """Set the expression to be evaluated and sent to the list.

        Paramters:
            expr : Expression object to be evaluated.
        """
        self._r = expr

    def run(self, scope):
        """Evaluate the variable's value to the evaluated expression.

        Paramters:
            scope : Scope object containing available variables.
        """
        value = self._r.evaluate(scope)
        scope.set_value(self._variable, value, self._indices)
        if VERBOSE:
            print_ind = '[' + ']['.join(map(str, self._indices)) + ']'
            print("Set", f"{self._variable}{print_ind}", "to", value)


class StatementDef:
    """Statement that defines a function.

    Attributes:
        _variable : str representation of the variable being changed.
        _params   : list of default parameter values.
        _stmt     : StatementBlock object to potentially be run.

    Note: This function acts as a variable.
    """

    def __init__(self, number, paramlist, block):
        """Construct a statement that defines a given function.

        Parameters:
            number    : int representing the variable to be set.
            paramlist : list of default parameter values.
            block     : StatementBlock object to potentially be run.
        """
        self._variable = f"*{str(number)}"
        self._params = paramlist
        self._stmt = block

    def run(self, scope):
        """Evaluate the variable's value to the defined function.

        Parameters:
            scope : Scope object containing available variables.
        """
        value = FuncExpression(self._params, self._stmt)
        scope.set_value(self._variable, value)
        if VERBOSE:
            print("Defined function", self._variable)


class StatementIf:
    """Statement that runs its block if its expression doesn't equal 0.

    Attributes:
        _expr      : Expression object to be evaluated and checked.
        _stmt      : StatementBlock object to potentially be run.
        _else_stmt : StatementBlock object to be run if the expression fails.
    """

    def __init__(self, expression, block):
        """Construct a statement that only runs if expression isn't 0.

        Parameters:
            expression : Expression object to be evaluated and checked.
            block      : StatementBlock object to potentially be run.
        """
        self._expr = expression
        self._stmt = block
        self._else_stmt = None

    def set_else(self, block):
        """Add an else statement to be run if the expression is 0.

        Parameters:
            block : StatementBlock object to potentially be run.
        """
        self._else_stmt = block

    def run(self, scope):
        """Evaluate the expression and run the block if not 0."""
        value = self._expr.evaluate(scope)
        if value:
            if VERBOSE:
                print("If statement passed")
            self._stmt.run(scope)
        else:
            if VERBOSE:
                print("If statement failed")
            if self._else_stmt:
                self._else_stmt.run(scope)


class StatementWhile(StatementIf):
    """Statement that runs its block as long as its expression doesn't equal 0.

    Attributes:
        _expr  : Expression object to be evaluated and checked.
        _stmt  : StatementBlock object to potentially be run.
    """

    def run(self, scope):
        """Evaluate the expression and run the block while not 0."""
        value = self._expr.evaluate(scope)
        while value:
            if VERBOSE:
                print("While statement continued")
            self._stmt.run(scope)
            value = self._expr.evaluate(scope)
        if VERBOSE:
            print("While statement ended")
