# ----
# This file is generated by mini_lambda_methods_generation.py - do not modify it !
# ----
from typing import Any

from mini_lambda.base import StackableFunctionEvaluator, evaluate, get_repr, FunctionDefinitionError
from mini_lambda.base import PRECEDENCE_ADD_SUB, PRECEDENCE_MUL_DIV_ETC, PRECEDENCE_COMPARISON, \
    PRECEDENCE_EXPONENTIATION, PRECEDENCE_SHIFTS, PRECEDENCE_POS_NEG_BITWISE_NOT, \
    PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF
from sys import getsizeof


class _LambdaExpressionGenerated(StackableFunctionEvaluator):
    """
    This generated class implements a bunch of magic methods, so that calling these magic methods on an object will
    result in adding that magic method to the StackableFunctionEvaluator's stack.
    This allows for example x[1] to return a new _LambdaExpressionGenerated whose stack is able to call [1] (getitem(1))
    on the result of the current stack's evaluation

    The methods added below belong to two categories
     * All magic methods that 'just' need to be implemented (for example __add__), or remapped to the original method
     calling them because on some built-in data types the magic method does not exist (for example, __getattr__ should
     not add __getattr__ to the stack but getattr)
     * All magic methods that do not work because the python framework does not allow them to return another type than
     the expected one. For all of them there are two methods: one in the class throwing an exception, and one at
     package-level to provide a replacement (The exception message provides the replacement method name).
    """

    # ******* All magic methods that need to be implemented ********

    ## For each method to override
    % for o in to_override:
        % if o.uni_operator:
    ## ----------unitary operator such as '-'-------------------
    def ${o.method_name}(self):
        """ Returns a new _LambdaExpression performing '${o.uni_operator}<r>' on the result <r> of this evaluator's evaluation """
        ## def _${o.method_name}(r, input):
        ##     return ${o.uni_operator}r
        ## return self.add_unbound_method_to_stack(_${o.method_name})
        def _${o.method_name}(input):
            # first evaluate the inner function
            res = self.evaluate(input)
            # then call the method
            return ${o.uni_operator}res

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = '${o.uni_operator}' + get_repr(self, ${o.precedence_level})
        return type(self)(fun=_${o.method_name}, precedence_level=${o.precedence_level}, str_expr=string_expr, root_var=self._root_var)

    ## -----------------------------
        % elif o.pair_operator:
            % if o.is_operator_left:
    ## --------pairwise operator - left---------------------
    def ${o.method_name}(self, other):
        """ Returns a new _LambdaExpression performing '<r> ${o.pair_operator} other' on the result <r> of this evaluator's evaluation """
        ## def _${o.method_name}(r, input):
        ##    return r ${o.pair_operator} evaluate(other, input)
        ## return self.add_unbound_method_to_stack(_${o.method_name})
        self.assert_has_same_root_var(other)
        def _${o.method_name}(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r ${o.pair_operator} evaluate(other, input)

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = get_repr(self, ${o.precedence_level}) + ' ${o.pair_operator} ' + get_repr(other, ${o.precedence_level})
        return type(self)(fun=_${o.method_name}, precedence_level=${o.precedence_level}, str_expr=string_expr, root_var=self._root_var)

    ## -----------------------------
            % else:
    ## --------pairwise operator - left---------------------
    def ${o.method_name}(self, other):
        """ Returns a new _LambdaExpression performing 'other ${o.pair_operator} <r>' on the result <r> of this evaluator's evaluation """
        ## def _${o.method_name}(r, input):
        ##     return evaluate(other, input) ${o.pair_operator} r
        ## return self.add_unbound_method_to_stack(_${o.method_name})
        self.assert_has_same_root_var(other)
        def _${o.method_name}(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return evaluate(other, input) ${o.pair_operator} r

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = get_repr(other, ${o.precedence_level}) + ' ${o.pair_operator} ' + get_repr(self, ${o.precedence_level})
        return type(self)(fun=_${o.method_name}, precedence_level=${o.precedence_level}, str_expr=string_expr, root_var=self._root_var)

    ## -----------------------------
            % endif
        % elif o.unbound_method:
    ## --------unbound method---------------------
    def ${o.method_name}(self, *args):
        """ Returns a new _LambdaExpression performing '${o.unbound_method.__name__}(<r>, *args)' on the result <r> of this evaluator's evaluation """
        ## def _${o.method_name}(r, input, *args):
        ##     return ${o.unbound_method.__name__}(r, input, *args)
        ## return self.add_unbound_method_to_stack(_${o.method_name}, *args)
        for other in args:
            self.assert_has_same_root_var(other)
        def _${o.method_name}(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return ${o.unbound_method.__name__}(r, *[evaluate(other, input) for other in args])

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = '${o.unbound_method.__name__}(' + get_repr(self, None) + ', ' + ', '.join([get_repr(arg, None) for arg in args]) + ')'
        return type(self)(fun=_${o.method_name}, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF, 
                          str_expr=string_expr, root_var=self._root_var)

    ## -----------------------------
        % else:
    ## --------general case---------------------
    def ${o.method_name}(self, *args):
        """ Returns a new _LambdaExpression performing '<r>.${o.method_name}(*args)' on the result <r> of this evaluator's evaluation """
        # return self.add_bound_method_to_stack('${o.method_name}', *args)
        for other in args:
            self.assert_has_same_root_var(other)
        def _${o.method_name}(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r.${o.method_name}(*[evaluate(other, input) for other in args])

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '.${o.method_name}(' + ', '.join([get_repr(arg, None) for arg in args]) + ')'
        return type(self)(fun=_${o.method_name}, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF, 
                          str_expr=string_expr, root_var=self._root_var)

    ## -----------------------------
        % endif
    % endfor
    # ******* All magic methods that need to raise an exception ********
    ## For each method to override
    % for o in to_override_with_exception:
    def ${o.method_name}(self, *args):
        """
        This magic method can not be used on an _LambdaExpression, because unfortunately python checks the
        result type and does not allow it to be a custom type.
        """
        raise FunctionDefinitionError('${o.method_name} is not supported by _LambdaExpression, since python raises an'
                                      ' error when its output is not directly an object of the type it expects.'
                                      'Please use the ${o.module_method_name}() method provided at mini_lambda package'
                                      ' level instead. If you did not use ${o.method_name} in your expression, you '
                                      'probably used a standard method such as math.log(x) instead of a method '
                                      ' converted to mini_lambda such as Log(x). Please check the documentation for '
                                      'details.')

    % endfor

# ******* All replacement methods for the magic methods throwing exceptions ********
% for o in to_override_with_exception:
def ${o.module_method_name}(evaluator: _LambdaExpressionGenerated):
    """ This is a replacement method for _LambdaExpression '${o.method_name}' magic method """
    % if o.unbound_method:
    return evaluator.add_unbound_method_to_stack(${o.unbound_method.__name__})
    % else:
    return evaluator.add_bound_method_to_stack('${o.method_name}')
    % endif


% endfor