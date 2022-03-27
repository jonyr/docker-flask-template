from subprocess import check_output

import click
from flask.cli import with_appcontext


def count_locs(file_type, comment_pattern):
    """Detect if a program is on the system path.

    Args:
        file_type (str): Which file type will be searched?
        comment_pattern (str): Escaped characters that are comments

    Returns:
        str:
    """
    find = f"find . -name '*.{file_type}' -not -path './venv/*' -print0"
    sed_pattern = r"'/^\s*{0}/d;/^\s*$/d'".format(comment_pattern)
    cmd = f"{find} | xargs -0 sed {sed_pattern} | wc -l"

    return check_output(cmd, shell=True).decode('utf-8').replace('\n', '')


@click.command()
@with_appcontext
def loc():
    """Count lines of code in the project.
    """
    file_types = (
        ['Python', 'py', '#'],
        ['HTML', 'html', '<!--'],
        ['CSS', 'css', r'\/\*'],
        ['JS', 'js', r'\/\/'],
    )

    click.echo('Lines of code\n-----------------')

    for file_type in file_types:
        click.echo(f"{file_type[0]}:\t{count_locs(file_type[1], file_type[2])}")

    return None
