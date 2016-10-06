[![Build Status](https://travis-ci.org/ice-stuff/ice.svg?branch=master)](https://travis-ci.org/ice-stuff/ice)

# iCE: Interactive cloud experimentation tool

iCE is a tool that aims to interactively run experiments on a dynamic list of
cloud instances (VMs or containers).  iCE takes no assumptions on how many are
the available instances are, where are these instances located and what is
going to run on them.

iCE is composed of three main parts. The first is the **iCE registry**, an HTTP
server that is hosting the database of instances. This database is changing
rapidly as instances terminate (leave the pool) or boot (join the pool).

The second component the **iCE agent** is a small program that runs on a
cloud instance and takes care of registering it to the iCE registry. For
instances created through iCE's integration with EC2, the iCE agent runs
automatically on instance boot.

The third component is the **iCE client**. The client is a set of services that
enable experimentation on the registered instances. These services can be used
interactively with the **iCE shell**, or programmatically through the **iCE
client Python API**.

An **experiment** is a standard Python file that defines two types of
**actions**. These are the **iCE runners** and  the **iCE tasks**. When these
actions are invoked from an iCE client (shell or Python API) they run against
every instance that has joined the instances pool.

## Repositories

This repository defines the iCE API and includes the core functionality, as
well as, the iCE registry. The other components can be found in:

* [iCE Shell client](https://github.com/ice-stuff/ice-shell)
* [iCE agent](https://github.com/ice-stuff/ice-agent)
