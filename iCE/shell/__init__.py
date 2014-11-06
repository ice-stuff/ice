from IPython.config.loader import Config
from IPython.terminal.embed import InteractiveShellEmbed


def check_nested():
    try:
        get_ipython
        return True
    except NameError:
        return False


def make_config():
    cfg = Config()

    # Set prompt manager
    pc = cfg.PromptManager
    pc.in_template = '$> '
    pc.in2_template = '   '
    pc.out_template = ''

    return cfg


def make_embedable_shell(cfg, *args):
    # Define the messages
    msgs = [
        'Welcome to iCE!',
        'Try help to have a look into the provided commands',
        'You may leave this shell by typing `exit` or pressing Ctrl+D',
        'Try `h <Command>` to get usage information for a given command, or'
        + ' `h` for looking into a brief description of all commands.'
    ] + list(args)

    # Build the shell
    shell = InteractiveShellEmbed(
        config=cfg,
        banner1='* ' + str('*' * 68) + '\n'
        + '\n'.join(['* %s' % msg for msg in msgs]) + '\n'
        + '* ' + str('*' * 68),
        exit_msg='See ya...'
    )

    return shell
