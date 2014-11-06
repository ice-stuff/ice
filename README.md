# iCE: Interactive cloud experiments and monitoring

iCE is a tool based on the IPython approach, to manage, run and monitor
experiments on opportunistically available cloud instances (spawned VMs or
LxC containers).

# Versioning scheme

A strict scheme for selecting versions has been adopted. It is based
on the rules described in the [Semantic versioning 2.0.0](http://semver.org)
manifesto.

# Code format

* Spaces are used for tabs
* Tab size is 4 spaces
* Wrapping is done by the author at 80 characters

## Python

As can be seen bellow, Python is the language with the largest
percentage of lines of code. We follow the
[PEP8](http://www.python.org/dev/peps/pep-0008/) style guide.
Among others it contains:

* **Modules and packages**:            ``lower_case_with_underscores``
* **Functions and methods**:           ``lower_case_with_underscores``
* **Weak internal use of functions**:  ``lower_case_with_underscores``
* **Local variables, attributes**:     ``lower_case_with_underscores``
* **Global variables**:                ``UPPER_CASE_WITH_UNDERSCORES``
* **Constants**:                       ``UPPER_CASE_WITH_UNDERSCORES``
* **Classes**:                         ``CamelCase``

### Special cases

* **Avoid keyword conflict**:           Append a ``_`` to the name

### Doc strings

Doc string are used to document functions, classes and methods. We
are using the Sphinx standard:

- [Function definitions](https://pythonhosted.org/an_example_pypi_project/sphinx.html#function-definitions)
- [Full code example](https://pythonhosted.org/an_example_pypi_project/sphinx.html#full-code-example)

An example of a documented function:

```Python
def a_function(a, b, c=5):
    """
    Adds `a` with `b` and multiplies the result with `c`.

    :param int a: The first argument to the addition.
    :param int b: The second argument to the addition.
    :param int c: The integer which will be used to multiply
        `a + b`. Optional, default: `None`.
    :rtype: int
    :return: The result of the sum of `a` and `b` multiplied
        with `c`.
    :raises: AIsNotAnIntError: if `a` is not an integer.
    :raises: BIsNotAnIntError: if `b` is not an integer.
    :raises: CIsNotAnIntError: if `c` is not an integer.

    .. seealso::
        :py:func:`another_function`:: Provides the sum of `b`
        and `c` multiplied by `a`.
    """
    if not isinstance(a, int): raise AIsNotAnIntError()
    if not isinstance(b, int): raise BIsNotAnIntError()
    if not isinstance(c, int): raise CIsNotAnIntError()
    return (a + b) * c
```

## Configuration files (INI)

Configuration is handled by INI files. The INI sections and INI options
do follow the snace case format:

```INI
[mongodb]
host=localhost
port=27017
username=
password=
db_name=iCE
```
