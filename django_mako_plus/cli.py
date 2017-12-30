import subprocess as sp

import pkg_resources
import crayons
import click


@click.group()
def main():
    """The django-mako-plus cli."""
    pass


@main.group()
def new():
    """Create a new project or app."""
    pass


@new.command()
@click.argument('name')
def project(name):
    """Create a new django-mako-plus project."""
    click.echo('Creating new project ' + crayons.magenta(name, bold=True))

    template_path = pkg_resources.resource_filename('django_mako_plus', 'project_template')

    sp.check_call(
        'python3 -m django startproject --template={path} {name}'.format(path=template_path, name=name),
        shell=True
    )

    click.echo(crayons.green('Successfully created ') + crayons.magenta(name, bold=True))


@new.command()
@click.argument('name')
def app(name):
    """Create a new django-mako-plus app."""
    click.echo('Creating new app ' + crayons.magenta(name, bold=True))

    template_path = pkg_resources.resource_filename('django_mako_plus', 'app_template')

    sp.check_call(
        'python3 manage.py startapp --template={path} --extension=py,htm,html {name}'.format(path=template_path,
                                                                                             name=name),
        shell=True
    )

    click.echo(crayons.green('successfully created ' + crayons.magenta(name, bold=True)))


if __name__ == '__main__':
    main()
