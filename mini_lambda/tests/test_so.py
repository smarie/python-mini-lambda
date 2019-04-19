from __future__ import print_function


def test_so1(capsys):
    """Test for the solution at https://stackoverflow.com/a/55760092/7262247"""
    with capsys.disabled():

        # your source code util

        from mini_lambda import x, is_mini_lambda_expr
        import inspect

        def get_source_code_str(f):
            if is_mini_lambda_expr(f):
                return f.to_string()
            else:
                return inspect.getsource(f)

        # test it

        def foo(arg1, arg2):
            # do something with args
            a = arg1 + arg2
            return a

    print()
    print(get_source_code_str(foo))
    print(get_source_code_str(x ** 2))

    captured = capsys.readouterr()

    with capsys.disabled():
        print(captured.out)

        assert captured.out == """
        def foo(arg1, arg2):
            # do something with args
            a = arg1 + arg2
            return a

x ** 2
"""
