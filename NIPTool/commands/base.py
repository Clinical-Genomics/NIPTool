#!/usr/bin/env python
import logging

import click
import coloredlogs

from flask.cli import FlaskGroup, with_appcontext
from flask import current_app

# commands
from NIPTool.server import create_app

# Get version and doc decorator
from NIPTool import __version__
from NIPTool.tools.cli_utils import add_doc as doc
from .load import load

LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
LOG = logging.getLogger(__name__)


@click.version_option(__version__)
@click.group(cls=FlaskGroup,
             create_app=create_app,
             add_default_commands=True,
             invoke_without_command=False,
             add_version_option=False)
def cli(**_):
    """ Main entry point """
    pass


@cli.command()
def test():
    """Test server using CLI"""
    click.echo("test")
    pass


@cli.command()
@with_appcontext
def name():
    """Returns the app name, for testing purposes, mostly"""
    click.echo(current_app.name)
    return current_app.name


cli.add_command(test)
cli.add_command(name)
cli.add_command(load)
