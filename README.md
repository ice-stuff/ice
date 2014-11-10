# iCE: Interactive cloud experimentation and monitoring tool

iCE is a tool based on the IPython approach, to manage, run and monitor
experiments on opportunistically available cloud instances (spawned VMs or
LxC containers).

## Instance registration

`ice-register-self.py` script is written for this task. To register a new VM
on boot, include following lines in it's **user data**:

```bash
#!/bin/bash
curl https://raw.githubusercontent.com/glestaris/iCE/master/agent/ice-register-self.py -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a http://zerard.ddns.net:5000 -e test
```

*Note: leave an empty line after last line of the user-data.*

If the instance is already running, or the user-data mechanism is not provided,
just run following lines as root or a sudoer user:

```bash
curl https://raw.githubusercontent.com/glestaris/iCE/master/agent/ice-register-self.py -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a http://zerard.ddns.net:5000 -e test
```

## RESTful API

### GET /v1/instances

Returns a list of registered instances.

### GET /v1/instances/<Instance UUID>

### POST /v1/instances

Registers an instance.

#### Request body

The request is in JSON and has following members:

##### Networking

* `networks`: A list of objects with the following attributes:
    * *optional*, `iface`: The Linux network interface (e.g.: `eth0`) of the
        network.
    * `addr`: The IP(v4) address (e.g.: `192.168.22.123`). It can also include
        the network mask (e.g.: `192.168.22.123/24`).
    * *optional*, `bcast_addr`: The broadcast address (e.g.: `192.168.1.255`).

##### Cloud information

* *optional*, `cloud_id`: Can use something arbitrary (e.g.: `EC2-AWS-Ireland`).
    If it is not set, the domain name of the reverse DNS entry of the external
    IP will be used (e.g.: `cern.ch`).
* *optional*, `vpc_id`: If this is known to the instance, otherwise can be
    omitted. Its format depends on the cloud provider.

##### SSH information

* *optional*, `ssh_username`: The user name for which the SSH key is
    authorized. If omitted `root` is assumed.
* `ssh_authorized_fingerprint`: The fingerprint of the authorized SSH key,
    e.g.: `74:12:e2:0e:ca:75:6b:65:22:41:f2:fb:64:5f:5a:7f`.

##### Contextualization script

## Versioning scheme

A strict scheme for selecting versions has been adopted. It is based
on the rules described in the [Semantic versioning 2.0.0](http://semver.org)
manifesto.

## Code format

* Spaces are used for tabs
* Tab size is 4 spaces
* Wrapping is done by the author at 80 characters

### Python

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

#### Special cases

* **Avoid keyword conflict**:           Append a ``_`` to the name

#### Doc strings

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

### Configuration files (INI)

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
