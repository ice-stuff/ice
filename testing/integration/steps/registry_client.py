import time
from behave import given, then
from ice import entities


@given('we create session \'{session_key}\'')
def step_impl(context, session_key):
    my_ip = context.registry_client.get_my_ip()
    session = entities.Session(client_ip_addr=my_ip)

    sess_id = context.registry_client.submit_session(session)
    session.id = sess_id

    context.sessions[session_key] = session


@then(
    'the {amt} instances become available' +
    ' in less than {timeout_secs} seconds' +
    ' in session \'{session_key}\''
)
def step_inst_wait_step(context, amt, timeout_secs, session_key):
    amt = int(amt)
    timeout_secs = int(timeout_secs)

    if session_key not in context.sessions:
        raise AssertionError(
            'No session named `{:s}` was found'.format(session_key)
        )
    session = context.sessions[session_key]

    secs = 0
    actual_amt = 0
    while secs < timeout_secs:
        instances = context.registry_client.get_instances_list(session)
        actual_amt = len(instances)
        if actual_amt < amt:
            secs += 5
            time.sleep(5)
            continue
        return

    raise AssertionError(
        'Timemout after {:d} seconds.'.format(timeout_secs) +
        ' Could not find the expected {:d} instances.'.format(amt) +
        ' Found {:d}.'.format(actual_amt)
    )


@then(
    'they have tag \'{tag_key}\'' +
    ' with value \'{tag_value}\'' +
    ' in session \'{session_key}\''
)
def step_tag_checking(context, tag_key, tag_value, session_key):
    if session_key not in context.sessions:
        raise AssertionError(
            'No session named `{:s}` was found'.format(session_key)
        )
    session = context.sessions[session_key]

    instances = context.registry_client.get_instances_list(session)
    for inst in instances:
        if tag_key not in inst.tags:
            raise AssertionError(
                'No tag with key `{:s}` was found in instance `{:s}`'.format(
                    tag_key, inst.id
                )
            )
        if inst.tags[tag_key] != tag_value:
            raise AssertionError(
                'Expecting tag `{:s}` to have value `{:s}`, '.format(
                    tag_key, tag_value
                ) + 'got `{:s}` in instance `{:s}`'.format(
                    inst.tags[tag_key], inst.id
                )
            )
