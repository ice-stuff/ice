

#
# Magic commands
#

def load_experiment(magics, path):
    """Loads an experiment to iCE."""
    import pprint
    pprint.pprint(magics)
    pprint.pprint(path)


#
# Help command
#

MAGICS_HELP = {
    'load_exp': {
        'usage': '<The path of the experiment>',
        'description': load_experiment.__doc__
    }
}


def print_help(magics, definition):
    # Definition is defined :)
    if definition != '':
        if MAGICS_HELP.has_key(definition):
            print '%s\n Usage: %s %s' % (
                MAGICS_HELP[definition]['description'],
                definition, MAGICS_HELP[definition]['usage']
            )
        else:
            help(str(definition))
        return

    # General help
    print 'All commands explained:'
    print '\n'.join(
        [
            ' * %s: %s' % (key, h['description'])
            for key, h in MAGICS_HELP.items()
        ]
    )
