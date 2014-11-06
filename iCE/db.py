from entities import Instance


def store_instance(inst):
    """
    Stores an instance to the persistent storage.

    :param Instance inst: The instance to store.
    :rtype: bool
    :return: `True` on success and `False` otherwise.
    """
    pass


def retrieve_instance(instUUID):
    """
    Retrieves an instance (given its id) from the persistent storage.

    :param string instUUID: The instance's UUID.
    :rtype: Instance|None
    :return: An `Instance` object on success and `None` otherwise.
    """
    pass


def delete_instance(instUUID):
    """
    Deletes an instance to the persistent storage.

    :param string instUUID: The instance's UUID.
    :rtype: bool
    :return: `True` on success and `False` otherwise.
    """
    pass


def retrieve_instances(status=None):
    """
    Retrieves the list of instances from the persistent storage.

    :param int status: The status of the instances to fetch. Optional,
        default: all.
    :rtype: list
    :return: A list of instances (`Instance` objects).
    """
    pass
