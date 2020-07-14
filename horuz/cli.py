import os
import sys

import click


class Environment:

    def __init__(self):
        self.verbose = False
        self.config = {}

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.echo("{}\n".format(msg), file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log("DEBUG: {}".format(msg), *args)


pass_environment = click.make_pass_decorator(Environment, ensure=True)


class HoruzCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            mod = __import__(f"horuz.commands.cmd_{name}", None, None, ["cli"])
        except ImportError:
            return
        return mod.cli


@click.command(cls=HoruzCLI)
@pass_environment
def cli(ctx):
    """
    Horuz!. CLI to interact with ElasticSearch. Keep an eye of your Fuzzing!
    """
    filename = os.path.expanduser("~/.horuz/horuz.cfg")
    es_address = "http://localhost:9200"
    if os.path.exists(filename):
        with open(filename) as cfg:
            es_address = cfg.read()

    ctx.config = {
        'elasticsearch_address': es_address,
        'config_file': filename
    }
