# Changelog

The entries bellow are in reverse chronological order.

## v2.1.0 (WIP)

* `sess_cd`, `sess_release` and `sess_retain` shell commands are promoted and
  can now be used in normal mode. They were only available in debug mode
  before.
* Adopt IPython v5.
* Adjust all iCE shell output to fit in 80 characters.
* Add ASCII table helper for experiments.
* Introduce `ice.ParallelRunner` runner that uses Fabric's parallel execution
  feature.
* Experiments receive a list of `entity.Instance` objects instead of a host
  strings list.
* Replace the awkward `./ice-register-self.py` script with the `ice-agent`
  project maintained in https://github.com/glestaris/ice-agent.

## v2.0.0 (19 September 2015)

* Radical changes towards and un-opinionated API.
* Increases test coverage and necessary refactoring.

## v1.3.0 (26 January 2015)

* SSH key can be specified in the configuration file.
* Better support for multiple clouds.
* Adds `sess_cd` command in the `ice-shell` to switch to a different active
    session.
* Fixes in task execution.
* Fixes EC2 instances destruction bug.
* Fixes session closing bug on deletion of linked instances.

## v1.2.1 (27 December 2014)

* Fixes bug with session instances pools separation.
* Fixes bug with experiment execution and instances list.
* Fixes bug with the clean up of instances from EC2 shell extension.

## v1.2.0 (12 December 2014)

* Adds `ice.api.instances` for instances manipulation.
* Fixes in the loggers and `logging.DEBUG`.

## v1.1.0 (7 December 2014, look for tag v0.2.0)

* Adds iCE session concept.
* Adds `boto` library integration for supporting spawn/destroy operations in
    clouds with EC2-like APIs.
* Adds simple API under `ice.api`.
* Heavy changes in shell and its extensions.
    * Built around `ice.api`.

## v1.0.0 (November 2014, no tag for this version)

* Initial release.
