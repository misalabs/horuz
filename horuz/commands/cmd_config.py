import os

import click

from horuz.cli import pass_environment
from horuz.utils.es import HoruzES


@click.group()
def cli():
    """
    Your horuz configuration
    """
    pass


@cli.command("server:add")
@click.option('-a', '--address', help='ElasticSearch Address http://localhost:9200.')
@pass_environment
def config_server_add(ctx, address):
    """
    Add your ElasticSearch server.
    """
    config_file = os.path.expanduser('~/.horuz/horuz.cfg')
    address = click.prompt(
        "Please enter the address of your ElasticSearch",
        default=address
    )
    with open(config_file, 'w') as cfg:
        cfg.write(address)


@cli.command("server:status")
@pass_environment
def config_server_status(ctx):
    """
    Show the server ElasticSearch status connection.
    """
    hes = HoruzES("", ctx)
    if hes.is_connected():
        ctx.log("ElasticSearch is connected to {} successfully!".format(
            ctx.config.get("elasticsearch_address")))
    else:
        ctx.log("ElasticSearch is not connected to {}.".format(
            ctx.config.get("elasticsearch_address")))
