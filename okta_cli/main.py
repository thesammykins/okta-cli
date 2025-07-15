import click
from . import config
from . import users
from . import groups
import configparser

@click.group()
def cli():
    """A CLI tool to interact with Okta APIs."""
    pass

@cli.command()
@click.option('--profile', default='default', help='The profile to configure.')
def configure(profile):
    """Configures the Okta domain and API token."""
    okta_domain = click.prompt("Okta domain")
    api_token = click.prompt("API token", hide_input=True)

    cfg = config.get_config()
    if not cfg.has_section(profile):
        cfg.add_section(profile)

    cfg.set(profile, "domain", okta_domain)
    cfg.set(profile, "token", api_token)

    config.write_config(cfg)
    click.echo(f"Configuration saved for profile '{profile}'.")

cli.add_command(users.users)
cli.add_command(groups.groups)

if __name__ == '__main__':
    cli()