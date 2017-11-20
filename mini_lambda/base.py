from typing import Callable, Any, Tuple, Type

# see https://docs.python.org/3/reference/expressions.html#operator-precedence
from copy import copy

_CONSTANT_VAR_ID = -1

_PRECEDENCE_LAMBDA = 0
_PRECEDENCE_IF_ELSE = 1
_PRECEDENCE_OR = 2
_PRECEDENCE_AND = 3
_PRECEDENCE_NOT = 4
_PRECEDENCE_COMPARISON = 5
_PRECEDENCE_BITWISE_OR = 6
_PRECEDENCE_BITWISE_XOR = 7
_PRECEDENCE_BITWISE_AND = 8
_PRECEDENCE_SHIFTS = 9
_PRECEDENCE_ADD_SUB = 10
_PRECEDENCE_MUL_DIV_ETC = 11
_PRECEDENCE_POS_NEG_BITWISE_NOT = 12
_PRECEDENCE_EXPONENTIATION = 13  # Note: The power operator ** binds less tightly than _PRECEDENCE_POS_NEG_BITWISE_NOT on its right, that is, 2**-1 is 0.5.
_PRECEDENCE_AWAIT = 14
_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF = 15
_PRECEDENCE_BIND_TUP_DISPLAY = 16
_PRECEDENCE_MAX = 17


class FunctionDefinitionError(Exception):
    """ An exception thrown when defining a function incorrectly """


class _LambdaExpressionBase:
    """
    A _LambdaExpressionBase is a wrapper for a function (self._fun) with a SINGLE argument.
    It can be evaluated on any input by calling the 'evaluate' method. This will execute self._fun() on this input.

    A _LambdaExpressionBase offers the capability to add (stack) a function on top of the inner function. This
    operation does not modify the instance but rather returns a new object. Two versions of this operation are provided:
     * add_unbound_method_to_stack: this would execute the provided method (meth) on the result of the execution of
     self._fun (res) by doing meth(res, *other_args)
     * add_bound_method_to_stack: this would execute the provided method (meth) on the result of the execution of
     self._fun (res) by doing res.meth(*other_args)
    """

    __slots__ = ['_fun', '_str_expr', '_root_var', '_precedence_level']

    def __init__(self, str_expr: str=None, is_constant: bool=False, constant_value: Any=None,
                 precedence_level: int=None, fun: Callable=None, root_var=None):
        """
        Constructor with an optional nested evaluation function. If no argument is provided, the nested evaluation
        function is the identity function with one single parameter x

        :param str_expr: a string representation of this expression. By default this is 'x'
        :param is_constant: False (default) will create a variable, while True will create a constant
        :param constant_value: the value for the constant
        :param precedence_level: the precedence level of this expression. It is used by the get_repr() method to decide
        if there is a need to surround it with parenthesis. By default this is the highest precedence.
        :param fun:
        :param root_var:
        """
        # case 1: constant
        if is_constant:
            if precedence_level is not None or fun is not None or root_var is not None:
                raise ValueError('precedence_level, fun, and root_var should not be provided when creating a Constant')

            # symbol for the constant
            str_expr = str_expr or str(constant_value)

            # contents = constant_value
            def fun(x):
                return constant_value

            # unique id for the variable
            root_var = _CONSTANT_VAR_ID

            # precedence level is maximum
            precedence_level = _PRECEDENCE_MAX

        # case 2: variable. No function nor root_var should be provided, and the inner method will be the identity
        elif fun is None and root_var is None and precedence_level is None and constant_value is None:
            # symbol for the variable
            str_expr = str_expr or 'x'

            # contents = identity function
            def fun(x):
                return x

            # unique id for the variable
            root_var = id(self)

            # precedence level is maximum
            # precedence_level = precedence_level or _PRECEDENCE_MAX
            precedence_level = _PRECEDENCE_MAX

        # case 3 (internal only): expression
        elif fun is not None and str_expr is not None and root_var is not None and precedence_level is not None:
            if constant_value is not None:
                raise ValueError('constant_value should be None if is_constant is not True')

        else:
            raise ValueError('Unsupported combination of parameters, see documentation for details')

        # remember for later use
        self._fun = fun
        self._str_expr = str_expr
        self._root_var = root_var
        self._precedence_level = precedence_level

    def evaluate(self, arg):
        """
        The method that should be used to evaluate this expression for a given input. Indeed, by default the
        expression is not callable: if your expression is x, doing x(0) will not execute the identity function on
        input 0, but will instead create a new expression x(0), able to perform y(0) for any input y.

        If you wish to 'freeze' an expression so that calling it triggers an evaluation, you should use x.as_function().

        :param arg:
        :return:
        """
        return self._fun(arg)

    def to_string(self):
        """
        Returns a string representation of this InputEvaluator (Since str() does not work, it would return a new
        InputEvaluator).
        :return:
        """
        return self._str_expr

    def assert_has_same_root_var(self, other: Any) -> Any:
        """
        Asserts that if other is also a _LambdaExpressionBase, then it has the same root variable.
        It returns the root variable to use for expressions combining self and other.

        :param other:
        :return:
        """
        if isinstance(other, _LambdaExpressionBase):
            # check that both work on the same variable. Reminder: None means constant
            if (self._root_var is not _CONSTANT_VAR_ID) and (other._root_var is not _CONSTANT_VAR_ID) \
                    and (self._root_var != other._root_var):
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')
            else:
                # always try to return the non-constant variable
                return self._root_var if (self._root_var != _CONSTANT_VAR_ID) else other._root_var
        else:
            return self._root_var

    def add_unbound_method_to_stack(self, method, *m_args, **m_kwargs):
        """
        Returns a new _LambdaExpressionBase whose inner function will be

            method(self.evaluate(input), input, *m_args, **m_kwargs)

        Note: this internal function only works if this expression is the first positional argument of the method.
        In general to transform a method to an acceptable lambda-friendly method, use `make_lambda_friendly_method`

        :param method:
        :param m_args: optional args to apply in method calls
        :param m_kwargs: optional kwargs to apply in method calls
        :return:
        """
        return _get_expr_or_result_for_method(method, self, *m_args, **m_kwargs)

    def add_bound_method_to_stack(self, method_name, *m_args, **m_kwargs):
        """
        Returns a new _LambdaExpressionBase whose inner function will be

            self.evaluate(inputs).method_name(*m_args)

        :param method_name:
        :param m_args: optional args to apply in method calls
        :param m_kwargs: optional kwargs to apply in method calls
        :return:
        """
        root_var, _ = _get_root_var(self, m_args, m_kwargs)

        def evaluate_inner_function_and_apply_object_method(raw_input):
            # first evaluate the inner function
            res = self.evaluate(raw_input)
            # then retrieve the (bound) method on the result object, from its name
            object_method = getattr(res, method_name)
            # finally call the method
            return object_method(*[evaluate(other, input) for other in m_args],
                                 **{arg_name: evaluate(arg, input) for arg_name, arg in m_kwargs.items()})

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, _PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '.' + method_name + '(' \
                      + ', '.join([get_repr(arg, None) for arg in m_args]) \
                      + ', '.join([arg_name + '=' + get_repr(arg, None) for arg_name, arg in m_kwargs.items()]) + ')'
        return type(self)(fun=evaluate_inner_function_and_apply_object_method,
                          precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr,
                          root_var=root_var)


def _get_root_var(*args, **kwargs) -> Tuple[Any, _LambdaExpressionBase]:
    """
    Returns the root variable to use when the various arguments are used in the same expression, or raises an exception
    if two arguments have incompatible root variables

    :param args:
    :param kwargs:
    :return: the root variable to use and the first lambda expression found
    """
    first_expression = None
    root_var = None

    for arg in (args + tuple(kwargs.values())):
        if first_expression is None:
            # we look for the first expression
            if isinstance(arg, _LambdaExpressionBase):
                first_expression = arg
        else:
            # check compliance
            root_var = first_expression.assert_has_same_root_var(arg)

    root_var = root_var or first_expression._root_var
    return root_var, first_expression


def evaluate(statement: Any, input):
    """
    A helper function to evaluate something, whether it is a _LambdaExpressionBase, a callable, or a non-callable.
    * if that something is not callable, it returns it directly
    * if it is a _LambdaExpressionBase, it evaluates it on the given input
    * if it is another type of callable, it calls it on the given input.

    :param statement:
    :return:
    """
    if isinstance(statement, _LambdaExpressionBase):
        # a _LambdaExpressionBase
        return statement.evaluate(input)
    else:
        # a constant value
        return statement


def get_repr(statement: Any, target_precedence_level: float = None):
    """
    A helper function to return the representation of something, whether it is a _LambdaExpressionBase,
    a callable, or a non-callable.
    * if that something is not callable, it returns its str() representation
    * if it is a _LambdaExpressionBase, it returns its .to_string()
    * if it is another type of callable, it returns its __name__

    :param statement:
    :param target_precedence_level: the precedence level of the operation requesting a representation. High numbers have higher
     priority than lower. If the statement is a _LambdaExpressionBase and the precedence level is higher than the
     one used in the statement, parenthesis will be applied around the statement.
     See https://docs.python.org/3/reference/expressions.html#operator-precedence
    :return:
    """
    if not callable(statement):
        # a non-callable object
        if isinstance(statement, slice):
            # special case of a slice [0:10, 0:2:4]
            return str(statement.start) + (':' + str(statement.step) if statement.step else '') \
                   + ':' + str(statement.stop)
        else:
            # general case
            return repr(statement)

    elif isinstance(statement, _LambdaExpressionBase):
        # a _LambdaExpressionBase
        if target_precedence_level is not None and target_precedence_level > statement._precedence_level:
            # we need to 'protect' the statement by surrounding it as it will be used inside a higher-precedence context
            return '(' + statement.to_string() + ')'
        else:
            return statement.to_string()

    else:
        # a standard callable
        return statement.__name__


def make_lambda_friendly_method(method: Callable, name: str = None):
    """
    Utility method to transform any method whatever their signature (positional and/or keyword arguments,
    variable-length included) into a method usable inside lambda expressions, even if some of the arguments are
    expressions themselves.

    In particular you may wish to convert:

    * standard or user-defined functions. Note that by default the name appearing in the expression is func.__name__

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method
        from math import log

        # transform standard function `log` into lambda-friendly function `Log`
        Log = make_lambda_friendly_method(log)

        # now you can use it in your lambda expressions
        complex_identity = _( Log(10 ** x, 10) )
        complex_identity(3.5)    # returns 3.5
        print(complex_identity)  # "log(10 ** x, 10)"
        ```

    * anonymous functions such as lambdas and partial. In which case you HAVE to provide a name

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method
        from math import log

        # ** partial function (to fix leftmost positional arguments and/or keyword arguments)
        from functools import partial
        is_superclass_of_bool = make_lambda_friendly_method(partial(issubclass, bool), name='is_superclass_of_bool')

        # now you can use it in your lambda expressions
        expr = _(is_superclass_of_bool(x))
        expr(int)    # True
        expr(str)    # False
        print(expr)  # "is_superclass_of_bool(x)"

        # ** lambda function
        Log10 = make_lambda_friendly_method(lambda x: log(x, 10), name='log10')

        # now you can use it in your lambda expressions
        complex_identity = _(Log10(10 ** x))
        complex_identity(3.5)    # 3.5
        print(complex_identity)  # "log10(10 ** x)"
        ```

    * class functions. Note that by default the name appearing in the expression is func.__name__

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method

        # ** standard class function
        StartsWith = make_lambda_friendly_method(str.startswith)

        # now you can use it in your lambda expressions
        str_tester = _(StartsWith('hello', 'el', x))
        str_tester(0)      # False
        str_tester(1)      # True
        print(str_tester)  # "startswith('hello', 'el', x)"

        # ** static and class functions
        class Foo:
            @staticmethod
            def bar1(times, num, den):
                return times * num / den

            @classmethod
            def bar2(cls, times, num, den):
                return times * num / den

        FooBar1 = make_lambda_friendly_method(Foo.bar1)
        fun1 = _( FooBar1(x, den=x, num=1) )

        FooBar2a = make_lambda_friendly_method(Foo.bar2)  # the `cls` argument is `Foo` and cant be changed
        fun2a = _( FooBar2a(x, den=x, num=1) )

        FooBar2b = make_lambda_friendly_method(Foo.bar2.__func__)  # the `cls` argument can be changed
        fun2b = _( FooBar2b(Foo, x, den=x, num=1) )
        ```

        Note: although the above is valid, it is much more recommended to convert the whole class


    :param method:
    :param name: an optional name for the method when used to display the expressions. It is mandatory if the method
    does not have a name, otherwise the default name is method.__name__
    :return:
    """

    # If the provided method does not have a name then name is mandatory
    if (not hasattr(method, '__name__') or method.__name__ == '<lambda>') and name is None:
            raise ValueError('This method does not have a name (it is either a partial or a lambda) so you have to '
                             'provide one: the \'name\' argument is mandatory')

    # create a named method if a new name is provided
    if name is not None:
        # work on a copy to rename it
        def new_method(*args, **kwargs):
            return method(*args, **kwargs)
        new_method.__name__ = name
    else:
        new_method = method

    # construct the lambda-friendly method
    def lambda_friendly_method(*args, **kwargs):
        """ A replacement method for `method`, that is able to either execute directly if no arguments are expressions,
        or to return a new expression if at least one argument is an expression """
        return _get_expr_or_result_for_method(new_method, *args, **kwargs)

    return lambda_friendly_method


def _get_expr_or_result_for_method(method, *args, **kwargs):
    """
    This method is called when a lambda-friendly converted method is used in a lambda expression.

    It first performs some checks on its arguments to be sure that if there are some expressions inside, they are
    compliant with each other.

    Then it either returns
    * the direct result of the method execution (if no expression is present in the arguments)
    * or a new expression that when evaluated later, will evaluate the expressions used in the arguments and finally
    call the method

    :param method:
    :param args: the arguments for the method. they may contain lambda expressions
    :param kwargs: the arguments for the method. they may contain lambda expressions
    :return:
    """
    # first we check here if all expressions in the arguments are compliant
    root_var, first_expression = _get_root_var(*args, **kwargs)

    if first_expression is None:
        # there are no expressions in the arguments so the method can be executed right now
        return method(*args, **kwargs)

    else:
        # there are expressions in the arguments: we have to create a new expression
        def evaluate_all_and_apply_method(input):
            # this basically calls your method on the same arguments (positional and keyword),
            # except that all of the arguments are first  evaluated if they are expressions
            return method(*[evaluate(arg, input) for arg in args],
                          **{arg_name: evaluate(arg, input) for arg_name, arg in kwargs.items()})

        # return a new expression of the same type than first_expression, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = method.__name__ + '(' \
                      + ', '.join([get_repr(arg, None) for arg in args]) \
                      + (', ' if (len(args) > 0 and len(kwargs) > 0) else '') \
                      + ', '.join([arg_name + '=' + get_repr(arg, None) for arg_name, arg in kwargs.items()]) \
                      + ')'

        return type(first_expression)(fun=evaluate_all_and_apply_method,
                                      precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                                      str_expr=string_expr, root_var=root_var)
