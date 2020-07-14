import os
import subprocess
import sys
import time


def execute_command(cmd):
    """
    Function which help us to Execute OS commands
    """
    executed = False
    try:
        command = subprocess.Popen(
            cmd,
            shell=True,
            stdout=sys.stdout,
            stderr=subprocess.STDOUT)
        command.wait()
        executed = not bool(command.returncode)
    except KeyboardInterrupt:
        command.kill()
        # Give time to the command execution to terminate correctly
        time.sleep(1)
    return executed


def log_session(session):
    """
    Saves the name of the given session in a local log
    getting sure not to store duplicates
    """
    os.popen("mkdir ~/.horuz/ 2>/dev/null")
    log_path = '{}/.horuz/sessions.log'.format(os.path.expanduser("~"))

    try:
        with open(log_path) as f:
            lines = f.readlines()
    except Exception:
        os.popen("touch ~/.horuz/sessions.log 2>/dev/null")

    lines = [x.strip() for x in lines if x]
    if session not in lines:
        lines.append(session)

        with open(log_path, 'w') as f:
            f.write("\n".join(lines))


def get_sessions(ctx, args, incomplete):
    """
    Used to autocomplete value for session param on collect
    """
    os.popen("mkdir ~/.horuz/ 2>/dev/null")
    log_path = '{}/.horuz/sessions.log'.format(os.path.expanduser("~"))

    try:
        with open(log_path) as f:
            lines = f.readlines()
    except Exception:
        os.popen("touch ~/.horuz/sessions.log 2>/dev/null")
        return []

    return [k.strip() for k in lines if k and incomplete in k]
