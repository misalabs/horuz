import click
from tabulate import tabulate

from horuz.cli import pass_environment
from horuz.utils.es import HoruzES


@click.group()
def cli():
    """
    Manage your Sessions
    """


@cli.command("ls")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option('-p', '--project', required=True, help='Specify the project.')
@pass_environment
def sessions_ls(ctx, verbose, project):
    """
    List all your sessions
    """
    ctx.verbose = verbose
    hes = HoruzES(project, ctx)
    data = hes.query("""
        {
            "size": 0,
            "aggs" : {
                "sessions" : {
                    "terms" : { "field" : "session.keyword", "size": 1000 }
                }
            }
        }
        """, raw=True)
    click.echo_via_pager(tabulate(data["aggregations"]["sessions"]["buckets"], headers="keys"))
