# Changelog

The entries bellow are in reverse chronological order.

## v1.2.1 (x December 2014)

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
