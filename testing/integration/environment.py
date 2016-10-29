def before_scenario(context, feature):
    # iCE registry
    context.registry_thread = None
    context.registry_client = None

    # iCE entities
    context.sessions = {}

    # Spawned instances
    context.spawned_containers = []


def after_scenario(context, feature):
    if len(context.spawned_containers) is not None:
        for d in context.spawned_containers:
            d.delete()
