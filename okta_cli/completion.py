"""
Command auto-completion support for the Okta CLI tool.
"""

import click
import os
from typing import List, Optional, Dict, Any
from .enhanced_config import ProfileManager


class CompletionProvider:
    """
    Provides auto-completion for commands, options, and arguments.
    """

    def __init__(self):
        """Initialize completion provider."""
        self.profile_manager = ProfileManager()

    def get_profile_names(self) -> List[str]:
        """
        Get list of available profile names for completion.

        Returns:
            List of profile names
        """
        try:
            profiles = self.profile_manager.list_profiles()
            return list(profiles.keys())
        except Exception:
            return []

    def get_config_commands(self) -> List[str]:
        """
        Get list of config subcommands for completion.

        Returns:
            List of config subcommands
        """
        return [
            "list",
            "create",
            "update",
            "delete",
            "activate",
            "show",
            "validate",
            "health",
            "backup",
            "restore",
            "export",
            "import",
            "env",
            "migrate",
            "current",
            "wizard",
            "interactive",
            "status",
        ]

    def get_user_commands(self) -> List[str]:
        """
        Get list of user subcommands for completion.

        Returns:
            List of user subcommands
        """
        return [
            "list",
            "create",
            "show",
            "update",
            "suspend",
            "unsuspend",
            "activate",
            "deactivate",
            "reset-password",
            "assign-app",
            "unassign-app",
            "list-app-assignments",
        ]

    def get_group_commands(self) -> List[str]:
        """
        Get list of group subcommands for completion.

        Returns:
            List of group subcommands
        """
        return [
            "list",
            "create",
            "show",
            "update",
            "delete",
            "add-user",
            "remove-user",
            "list-users",
        ]


# Click completion functions
def complete_profile_name(ctx, param, incomplete):
    """Complete profile names."""
    provider = CompletionProvider()
    profiles = provider.get_profile_names()
    return [p for p in profiles if p.startswith(incomplete)]


def complete_config_command(ctx, param, incomplete):
    """Complete config subcommands."""
    provider = CompletionProvider()
    commands = provider.get_config_commands()
    return [c for c in commands if c.startswith(incomplete)]


def complete_user_command(ctx, param, incomplete):
    """Complete user subcommands."""
    provider = CompletionProvider()
    commands = provider.get_user_commands()
    return [c for c in commands if c.startswith(incomplete)]


def complete_group_command(ctx, param, incomplete):
    """Complete group subcommands."""
    provider = CompletionProvider()
    commands = provider.get_group_commands()
    return [c for c in commands if c.startswith(incomplete)]


def complete_output_format(ctx, param, incomplete):
    """Complete output format options."""
    formats = ["json", "table", "csv", "yaml", "text"]
    return [f for f in formats if f.startswith(incomplete)]


def complete_file_path(ctx, param, incomplete):
    """Complete file paths."""
    import glob

    # Handle home directory expansion
    if incomplete.startswith("~"):
        incomplete = os.path.expanduser(incomplete)

    # Get directory and filename parts
    if os.path.isdir(incomplete):
        search_path = os.path.join(incomplete, "*")
    else:
        search_path = incomplete + "*"

    # Get matching files and directories
    matches = glob.glob(search_path)

    # Sort and return
    matches.sort()
    return matches


def setup_completion():
    """
    Setup shell completion for the CLI.
    This function can be called to enable completion.
    """
    click.echo("Setting up command completion...")

    # Get shell type
    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell == "bash":
        completion_script = """
# Okta CLI completion for Bash
_okta_cli_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    case $prev in
        --profile)
            local profiles=$(okta-cli config list --quiet 2>/dev/null | grep -E '^[a-zA-Z0-9_-]+$' || echo "")
            COMPREPLY=( $(compgen -W "$profiles" -- "$cur") )
            return 0
            ;;
        --output)
            COMPREPLY=( $(compgen -W "json table csv yaml text" -- "$cur") )
            return 0
            ;;
    esac
    
    case ${COMP_WORDS[1]} in
        config)
            opts="list create update delete activate show validate health backup restore export import env migrate current wizard interactive status"
            COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
            return 0
            ;;
        users)
            opts="list create show update suspend unsuspend activate deactivate reset-password assign-app unassign-app list-app-assignments"
            COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
            return 0
            ;;
        groups)
            opts="list create show update delete add-user remove-user list-users"
            COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
            return 0
            ;;
    esac
    
    if [[ ${COMP_CWORD} == 1 ]]; then
        opts="config users groups configure --help --version"
        COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
    fi
}

complete -F _okta_cli_completion okta-cli
"""

        completion_file = os.path.expanduser("~/.bash_completion")
        with open(completion_file, "a") as f:
            f.write(completion_script)

        click.echo("✅ Bash completion added to ~/.bash_completion")
        click.echo("💡 Run 'source ~/.bash_completion' to enable completion")

    elif shell == "zsh":
        completion_script = """
#compdef okta-cli

_okta_cli() {
    local context state line
    
    _arguments -C \
        '1: :->command' \
        '*: :->args'
    
    case $state in
        command)
            _values 'okta-cli command' \
                'config[Manage configuration profiles]' \
                'users[Manage Okta users]' \
                'groups[Manage Okta groups]' \
                'configure[Configure Okta domain and token]' \
                '--help[Show help]' \
                '--version[Show version]'
            ;;
        args)
            case $line[1] in
                config)
                    _values 'config subcommand' \
                        'list[List profiles]' \
                        'create[Create profile]' \
                        'update[Update profile]' \
                        'delete[Delete profile]' \
                        'activate[Activate profile]' \
                        'show[Show profile]' \
                        'validate[Validate profile]' \
                        'health[Health check]' \
                        'backup[Backup config]' \
                        'restore[Restore config]' \
                        'export[Export config]' \
                        'import[Import config]' \
                        'env[Show environment]' \
                        'migrate[Migrate config]' \
                        'current[Show current config]' \
                        'wizard[Configuration wizard]' \
                        'interactive[Interactive mode]' \
                        'status[Show status]'
                    ;;
                users)
                    _values 'users subcommand' \
                        'list[List users]' \
                        'create[Create user]' \
                        'show[Show user]' \
                        'update[Update user]' \
                        'suspend[Suspend user]' \
                        'unsuspend[Unsuspend user]' \
                        'activate[Activate user]' \
                        'deactivate[Deactivate user]' \
                        'reset-password[Reset password]' \
                        'assign-app[Assign app]' \
                        'unassign-app[Unassign app]' \
                        'list-app-assignments[List app assignments]'
                    ;;
                groups)
                    _values 'groups subcommand' \
                        'list[List groups]' \
                        'create[Create group]' \
                        'show[Show group]' \
                        'update[Update group]' \
                        'delete[Delete group]' \
                        'add-user[Add user to group]' \
                        'remove-user[Remove user from group]' \
                        'list-users[List group users]'
                    ;;
            esac
            ;;
    esac
}

_okta_cli "$@"
"""

        completion_dir = os.path.expanduser("~/.zsh/completions")
        os.makedirs(completion_dir, exist_ok=True)

        completion_file = os.path.join(completion_dir, "_okta-cli")
        with open(completion_file, "w") as f:
            f.write(completion_script)

        click.echo("✅ Zsh completion added to ~/.zsh/completions/_okta-cli")
        click.echo("💡 Add 'fpath=(~/.zsh/completions $fpath)' to your ~/.zshrc")
        click.echo("💡 Run 'autoload -U compinit && compinit' to enable completion")

    else:
        click.echo(f"❌ Shell completion not supported for: {shell}")
        click.echo("💡 Supported shells: bash, zsh")


def install_completion():
    """Install shell completion based on current shell."""
    shell = os.environ.get("SHELL", "").split("/")[-1]

    if shell in ["bash", "zsh"]:
        if click.confirm(f"Install completion for {shell}?"):
            setup_completion()
            return True
    else:
        click.echo(f"Shell completion not available for: {shell}")
        return False

    return False


# Click completion helpers for use with @click.option
profile_completion = click.Choice([])  # Will be populated dynamically
output_format_completion = click.Choice(["json", "table", "csv", "yaml", "text"])


def get_dynamic_profile_completion():
    """Get dynamic profile completion choices."""
    provider = CompletionProvider()
    return provider.get_profile_names()


class ProfileChoice(click.Choice):
    """Dynamic choice class for profile names."""

    def __init__(self):
        self._choices = []
        super().__init__(self._choices)
        self.name = "profile"

    def get_choices(self):
        """Get current profile choices."""
        try:
            provider = CompletionProvider()
            return provider.get_profile_names()
        except Exception:
            return []

    def convert(self, value, param, ctx):
        """Convert and validate profile name."""
        choices = self.get_choices()
        if value in choices or not choices:
            return value

        # If not in choices, still allow it (profile might not exist yet)
        return value


class OutputFormatChoice(click.Choice):
    """Choice class for output formats."""

    def __init__(self):
        super().__init__(["json", "table", "csv", "yaml", "text"])
        self.name = "format"


# Pre-configured completion instances
profile_choice = ProfileChoice()
output_format_choice = OutputFormatChoice()
