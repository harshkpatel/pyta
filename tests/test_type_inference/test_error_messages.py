import astroid
import nose
from hypothesis import settings
import tests.custom_hypothesis_support as cs
settings.load_profile("pyta")


def test_bad_attribute_access():
    """ User tries to access a non-existing attribute; or misspells the attribute name.
    """
    program = f'x = 1\n' \
              f'x.wrong_name\n'
    module, inferer = cs._parse_text(program)
    call_node = next(module.nodes_of_class(astroid.Call))
    expected_msg = "Attribute access error!\
    				In the Attribute node in line 2:\
    					the object "x" does not have the attribute "wrong_name"."
    assert call_node.type_constraints.type.msg == expected_msg


def test_builtin_method_call_bad_self():
    """ User tries to call a method on an object of the wrong type (self).
    """
    program = f'x = 1\n' \
              f'x.append(1.0)\n'
    module, inferer = cs._parse_text(program)
    call_node = next(module.nodes_of_class(astroid.Call))
    expected_msg = "In the Call node in line 2, when calling the method "append":\
                    this function expects to be called on an object of the class List, but was called on an object of\
                    inferred type int."
                   	# TODO: class versus type
    assert call_node.type_constraints.type.msg == expected_msg


def test_builtin_method_call_bad_argument():
    """ User tries to call a method on an argument of the wrong type.
    """
    program = f'x = 1\n' \
              f'x.extend(1)\n'
    module, inferer = cs._parse_text(program)
    call_node = next(module.nodes_of_class(astroid.Call))
    expected_msg = "In the Call node in line 2, when calling the method "extend":\
                    in parameter (1), the function was expecting an object of type iterable \
                    but was given an object of type int"
    assert call_node.type_constraints.type.msg == expected_msg


def test_non_annotated_function_call_bad_arguments():
    """ User tries to call a non-annotated function on arguments of the wrong type.
    """
    program = f'def add_num(num1, num2):\n' \
              f'    return num1 + num2\n' \
              f'\n' \
              f'add_num("bob", 1.0)\n'
    module, inferer = cs._parse_text(program)
    call_node = next(module.nodes_of_class(astroid.Call))
    expected_msg = "In the Call node in line 4, there was an error in calling the function "add_num":\
                     in parameter (1), the function was expecting an object of inferred type' \
                     int but was given an object of type str' \
                     in parameter (1), the function was expecting an object of inferred type' \
                     int but was given an object of type float"
                     # TODO: should we use the term inferred?
    assert call_node.type_constraints.type.msg == expected_msg


def test_user_defined_annotated_call_wrong_arguments_type():
    """ User tries to call an annotated user-defined function on the wrongly-typed arguments.
    """
    program = f'def add_3(num1: int, num2: int, num3: int) -> int:\n' \
              f'    return num1 + num2 + num3\n' \
              f'\n' \
              f'add_3(1, "bob", 1.0)\n'
    module, inferer = cs._parse_text(program)
    call_node = list(module.nodes_of_class(astroid.Call))[0]
    expected_msg = "In the Call node in line 4, there was an error in calling the annotated function "add_3":\
                     in parameter (2), the annotated type is int but was given an object of type str' \
                     in parameter (3), the annotated type is int but was given an object of type float"
    assert call_node.type_constraints.type.msg == expected_msg


def test_user_defined_annotated_call_wrong_arguments_number():
    """ User tries to call an annotated function on the wrong number of arguments.
    """
    program = f'def add_3(num1: int, num2: int, num3: int) -> int:\n' \
              f'    return num1 + num2 + num3\n' \
              f'\n' \
              f'add_3()\n'
    module, inferer = cs._parse_text(program)
    call_node = list(module.nodes_of_class(astroid.Call))[0]
    expected_msg = "In the Call node in line 4, there was an error in calling the function "add_3":\
                    the function was expecting 3 arguments, but was given 0."
    assert call_node.type_constraints.type.msg == expected_msg


def test_nested_annotated_function_conflicting_body():
    """ User tries to define an annotated function which has conflicting types within its body.
    """
    program = f'def random_func(int1: int) -> None:\n' \
              f'    int1 + "bob"\n' \
    module, inferer = cs._parse_text(program)
    functiondef_type = inferer.lookup_type(module, "return_int")
    expected_msg = "In the FunctionDef node in line 1, in the annotated Function Definition of "random_func" in line 1:\
                    in parameter (1), "int1", the annotated type is int, which conflicts with it's inferred type of' \
                    str from the function definition's body."
                    # TODO: where in the body, or is this too convoluted? Extract from sets.
    assert functiondef_type.msg == expected_msg


def test_annotated_functiondef_conflicting_return_type():
    """ User defines an annotated function with type errors in it's body;
    a discrepancy in annotated return type versus return type in it's body.
    """
    program = f'def return_str(num1: int, str1: str) -> int:\n' \
              f'    output = num1 + str1\n' \
              f'    return "bob"\n' \
              f'\n'
    module, inferer = cs._parse_text(program)
    functiondef_type = inferer.lookup_type(module, "return_str")
    expected_msg = "In the FunctionDef node in line 1, in the annotated Function Definition of "random_func" in line 1:\
                    the annotated return type is int, which conflicts with it's inferred type of' \
                    str from the function definition's body."
    assert functiondef_type.msg == expected_msg


if __name__ == '__main__':
    nose.main()
