# python-mini-lambda

[![Build Status](https://travis-ci.org/smarie/python-mini-lambda.svg?branch=master)](https://travis-ci.org/smarie/python-mini-lambda) [![Tests Status](https://smarie.github.io/python-mini-lambda/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mini-lambda/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mini-lambda/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mini-lambda) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/python-mini-lambda/) [![PyPI](https://img.shields.io/badge/PyPI-mini_lambda-blue.svg)](https://pypi.python.org/pypi/mini_lambda/)

Simple lambda functions without `lambda x:` and with string conversion capability. Originally developed in the [valid8](https://github.com/smarie/python-valid8) validation library.

This is the readme for developers. The documentation for users is available here: [https://smarie.github.io/python-mini-lambda/](https://smarie.github.io/python-mini-lambda/)


## Building from sources + notes on this project's design principles 

This project is basically code generating code generating code :)

The following command performs the first code generation. It updates the `mini_lambda/generated.py` file.

```bash
python ./code_generation/mini_lambda_methods_generation.py
```

It is based on a [mako](http://www.makotemplates.org/) template located at `code_generation/mini_lambda_template.mako`.

The generated code contains functions that generate functions when called, such as:

```python
def __gt__(self, other):
    """ Returns a new _LambdaExpression performing '<r> > other' on the result <r> of this evaluator's evaluation """
    def ___gt__(input):
        # first evaluate the inner function
        r = self.evaluate(input)
        # then call the method
        return r > evaluate(other, input)

    # return a new _LambdaExpression of the same type than self, with the new function as inner function
    return type(self)(___gt__)
```

So whenever you use the syntax provided, for example when you perform `power2 = x > 2 |_`, it dynamically creates a 'closure' function (here `___gt__`), that will be called when you will later evaluate the expression on an input, as in `power2(3)`.


## Want to contribute ?

Contributions are welcome ! Simply fork this project on github, commit your contributions, and create pull requests.

Here is a non-exhaustive list of interesting open topics: [https://github.com/smarie/python-mini-lambda/issues](https://github.com/smarie/python-mini-lambda/issues)

## Running the tests

This project uses `pytest`. 

```bash
pytest -v mini_lambda/tests/
```

You may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-test.txt
```

## Packaging

This project uses `setuptools_scm` to synchronise the version number. Therefore the following command should be used for development snapshots as well as official releases: 

```bash
python setup.py egg_info bdist_wheel rotate -m.whl -k3
```

You need to [generate code](##building-from-sources--notes-on-this-projects-design-principles) before packaging.

You also may need to install requirements for setup beforehand, using 

```bash
pip install -r ci_tools/requirements-setup.txt
```

## Generating the documentation page

This project uses `mkdocs` to generate its documentation page. Therefore building a local copy of the doc page may be done using:

```bash
mkdocs build
```

You may need to install requirements for doc beforehand, using 

```bash
pip install -r ci_tools/requirements-doc.txt
```

## Generating the test reports

The following commands generate the html test report and the associated badge. 

```bash
pytest --junitxml=junit.xml -v mini_lambda/tests/
ant -f ci_tools/generate-junit-html.xml
python ci_tools/generate-junit-badge.py
```

### PyPI Releasing memo

This project is now automatically deployed to PyPI when a tag is created. Anyway, for manual deployment we can use:

```bash
twine upload dist/* -r pypitest
twine upload dist/*
```
