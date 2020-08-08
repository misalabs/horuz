import click
from tabulate import tabulate

from horuz.cli import pass_environment
from horuz.utils.formatting import beautify_query
from horuz.utils.es import HoruzES


@click.command("search", short_help="Search data in ES.")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option('-p', '--project', required=True, help='Project name. Example yahoo.com uber.com x.com...')
@click.option('-q', '--query', required=True, help='Query to ElasticSeach')
@click.option('-f', '--fields', help='Specify the fields you want.')
@click.option('-s', '--size', default=100, type=click.IntRange(1, 10000), help='Specify the output size. Range 1-10000')
@click.option('-oJ', is_flag=True, help="JSON Output")
@pass_environment
def cli(ctx, verbose, project, query, fields, size, oj):
    """
    Get data from ElasticSeach.
    """
    ctx.verbose = verbose
    hes = HoruzES(project, ctx)
    fields = fields.split(",") if fields else []
    if oj:
        # JSON Output
        data = beautify_query(
            hes.query(term=query, size=size, fields=fields),
            fields,
            output="json")
        click.echo(data)
    else:
        # Interactive Output
        # Default fields if nothing were introduced
        if not fields:
            fields = ["_id", "time", "session"]
        data = beautify_query(
            hes.query(term=query, size=size, fields=fields),
            fields,
            output="interactive")
        click.echo_via_pager(tabulate(data, headers="keys"))
