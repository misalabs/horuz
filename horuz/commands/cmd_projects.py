import click
from tabulate import tabulate

from horuz.cli import pass_environment
from horuz.utils.es import HoruzES


@click.group()
def cli():
    """
    Manage your ElasticSeach Projects
    """
    pass


@cli.command("delete")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option('-p', '--project', required=True, help='Specify the project to delete.')
@pass_environment
def projects_delete(ctx, verbose, project):
    """
    Delete ElasticSeach Project
    """
    ctx.verbose = verbose
    click.confirm(
        "Are you sure you want to delete {}?".format(project),
        abort=True,
        default=True)
    # Delete the Index Project
    hes = HoruzES(project, ctx)
    deleted = hes.delete()
    if deleted:
        ctx.log("Project {} was deleted.".format(project))


@cli.command("ls")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@pass_environment
def projects_ls(ctx, verbose):
    """
    List all your ElasticSearch Projects
    """
    ctx.verbose = verbose
    hes = HoruzES("", ctx)
    indexes = hes.indexes()
    if indexes:
        click.echo(tabulate([{"project": i} for i in indexes]))


@cli.command("describe")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose mode.")
@click.option('-p', '--project', required=True, help='Specify the project to delete.')
@pass_environment
def projects_describe(ctx, verbose, project):
    """
    Project fields
    """
    ctx.verbose = verbose
    hes = HoruzES(project, ctx)
    mapping = hes.project_mapping()
    if mapping:
        click.echo(tabulate([{"mapping": i} for i in mapping]))
    else:
        click.echo("Project does not exist!")
