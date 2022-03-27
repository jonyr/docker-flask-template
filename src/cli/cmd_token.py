import binascii
import os

import click
from flask.cli import with_appcontext


@click.command()
@click.argument('bytes_length', default=32)
@with_appcontext
def token(bytes_length):
    """Generate a random secret token

    Args:
        bytes_length (int): Token length

    Returns:
        str: str token
    """
    return click.echo(binascii.b2a_hex(os.urandom(bytes_length)))
