# iCE: Interactive cloud experimentation tool

[![Build Status](https://travis-ci.org/glestaris/iCE.svg?branch=wip-improve-coverage)](https://travis-ci.org/glestaris/iCE)

iCE is a tool that aims to run experiments (interactively) on dynamic cloud
resources. iCE takes no assumptions on how many are the available VMs (pool),
where are these VMs located and what is going to run on them.

iCE is composed of three main parts. The first is the **iCE server**,
an HTTP server that is hosting the database of instances. This database is
changing rapidly as VMs terminate (leave the pool) or boot (join the pool).

The second component, is the the **iCE agent**, a small program that
runs once on a cloud VM, in order to register it to the iCE server. A VM
that is registered to iCE is also referred to as iCE instance. Usually the
iCE agent is automatically invoked after a VM boots successfully.

The third component is the **iCE client**. The client is a set of
services that enable experimentation on registered instances. These services
can be used interactively with the **iCE shell**, or programmatically
through the **iCE client Python API**.

An **experiment** is a standard Python file, that defines two types of
**actions**, accessible through \ice. These are the **iCE runners**
and  the **iCE tasks**. These action are executed for each VM that has
joined the instances pool.

## Examples

Two examples are included:

* `experiments/simple.py` A very simple experiment that just gets the FQDN host
    names of the iCE instances.
* `experiments/clique.py` A more complex experiment, in which the instances
    make a clique, in the sense that each instance sends a 500MB file to all
    other instances through `dd`. The experiment is measuring the transferring
    speeds and plots histograms with the results. Also there is the
    `experiments/clique-runner.py` file. This is a Python script that uses the
    iCE Python client API, to launch VMs and execute the clique experiment.

## Instance registration

Following lines in Bash, register an instance to iCE:

```bash
curl http://bit.ly/ice-agent -O ./ice-register-self.py
chmod +x ./ice-register-self.py
./ice-register-self.py -a <iCE server URL> -s <Session id>
```

The *iCE server URL* is the URL of the iCE server (e.g.:
`http://ice.example.org:8080`). THe session id, identifies a unique iCE
session. It can be obtained when starting the iCE shell, or through the
iCE client Python API.
