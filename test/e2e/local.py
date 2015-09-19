"""Local end-to-end test.

It requires running ice-registry-server and appropriate configuration files.
"""
import os
import tempfile
import subprocess


ice_root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'
))


with description('Local test'):
    with context('with a running iCE registry server'):
        with context('and appropriate configuration files'):
            with it('should run local experiment'):
                exp_contents = """
%inst_ls
%ec2_ls
%ec2_create -n 5 -t t2.micro
%inst_wait -n 5 -t 120
%exp_load ./experiments/simple.py
%exp_run simple
exit
"""
                f = tempfile.NamedTemporaryFile(delete=False)
                f.write(exp_contents)
                f.close()

                env = os.environ
                env['ICE_CONFIG_PATHS'] = ':'.join([
                    os.path.join(ice_root_path, 'config', 'default'),
                    os.path.join(ice_root_path, 'config', 'local')
                ])
                p = subprocess.Popen(
                    [os.path.join(ice_root_path, 'bin', 'ice-shell'), f.name],
                    cwd=ice_root_path,
                    env=env
                )
                p.wait()
