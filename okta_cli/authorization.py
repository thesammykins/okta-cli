"""
Authorization server management commands for the Okta CLI tool.
"""

import click
import requests
import json
from typing import Dict, Any, List, Optional
from . import config
from .errors import (
    handle_api_error, handle_network_error, handle_json_error,
    handle_config_error, handle_corrupted_config, with_error_handling,
    validate_name
)
from .enhanced_config import get_effective_config
from .formatting import create_output_option, format_and_output
from .progress import progress_spinner
import configparser


@click.group()
def authorization():
    """Manage authorization servers."""
    pass


@authorization.command('list')
@click.option('--profile', default=None, help='The profile to use.')
@click.option('--limit', type=int, default=20, help='Number of authorization servers to retrieve.')
@create_output_option()
@with_error_handling
def list_authorization_servers(profile, limit, output):
    """List authorization servers in Okta."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching authorization servers from Okta API..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/authorizationServers", headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            servers_data = response.json()
            
            if output == 'table':
                # Format for table display
                formatted_servers = []
                for server in servers_data:
                    formatted_servers.append({
                        'ID': server.get('id', ''),
                        'Name': server.get('name', ''),
                        'Description': server.get('description', ''),
                        'Audience': server.get('audiences', [''])[0] if server.get('audiences') else '',
                        'Status': server.get('status', ''),
                        'Created': server.get('created', ''),
                        'Last Updated': server.get('lastUpdated', '')
                    })
                
                headers = ['ID', 'Name', 'Description', 'Audience', 'Status', 'Created', 'Last Updated']
                format_and_output(formatted_servers, output, 'generic', headers)
            else:
                format_and_output(servers_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@authorization.command('show')
@click.argument('server_id')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def show_authorization_server(server_id, profile, output):
    """Show details for a specific authorization server."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching authorization server details..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/authorizationServers/{server_id}", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            server_data = response.json()
            
            if output == 'table':
                # Format for table display
                formatted_server = {
                    'ID': server_data.get('id', ''),
                    'Name': server_data.get('name', ''),
                    'Description': server_data.get('description', ''),
                    'Audiences': ', '.join(server_data.get('audiences', [])),
                    'Status': server_data.get('status', ''),
                    'Issuer': server_data.get('issuer', ''),
                    'Created': server_data.get('created', ''),
                    'Last Updated': server_data.get('lastUpdated', ''),
                    'Credentials': str(server_data.get('credentials', {}))
                }
                format_and_output(formatted_server, output, 'generic')
            else:
                format_and_output(server_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@authorization.command('create')
@click.option('--name', required=True, help='Authorization server name.')
@click.option('--description', help='Authorization server description.')
@click.option('--audience', required=True, help='Authorization server audience.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def create_authorization_server(name, description, audience, profile, output):
    """Create a new authorization server."""
    validate_name(name, "Authorization server name")
    
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {
        "name": name,
        "audiences": [audience]
    }
    
    if description:
        data["description"] = description

    with progress_spinner("Creating authorization server..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/authorizationServers", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 201:
        try:
            server_data = response.json()
            
            click.echo(click.style("✅ Authorization server created successfully!", fg='green'))
            
            if output == 'table':
                formatted_server = {
                    'ID': server_data.get('id', ''),
                    'Name': server_data.get('name', ''),
                    'Description': server_data.get('description', ''),
                    'Audience': audience,
                    'Status': server_data.get('status', ''),
                    'Issuer': server_data.get('issuer', ''),
                    'Created': server_data.get('created', '')
                }
                format_and_output(formatted_server, output, 'generic')
            else:
                format_and_output(server_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@authorization.command('update')
@click.argument('server_id')
@click.option('--name', help='New authorization server name.')
@click.option('--description', help='New authorization server description.')
@click.option('--audience', help='New authorization server audience.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def update_authorization_server(server_id, name, description, audience, profile, output):
    """Update an existing authorization server."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Get current server data first
    with progress_spinner("Fetching current authorization server data..."):
        try:
            current_response = requests.get(f"https://{domain}/api/v1/authorizationServers/{server_id}", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if current_response.status_code != 200:
        handle_api_error(current_response)
        return

    try:
        current_data = current_response.json()
    except (ValueError, KeyError) as e:
        handle_json_error(e, current_response.text)
        return

    # Update data with new values
    data = current_data.copy()
    
    if name:
        validate_name(name, "Authorization server name")
        data["name"] = name
    
    if description is not None:
        data["description"] = description
    
    if audience:
        data["audiences"] = [audience]

    if not any([name, description is not None, audience]):
        click.echo("No update parameters provided. Please provide at least one of --name, --description, or --audience.")
        return

    with progress_spinner("Updating authorization server..."):
        try:
            response = requests.put(f"https://{domain}/api/v1/authorizationServers/{server_id}", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            server_data = response.json()
            
            click.echo(click.style("✅ Authorization server updated successfully!", fg='green'))
            
            if output == 'table':
                formatted_server = {
                    'ID': server_data.get('id', ''),
                    'Name': server_data.get('name', ''),
                    'Description': server_data.get('description', ''),
                    'Audiences': ', '.join(server_data.get('audiences', [])),
                    'Status': server_data.get('status', ''),
                    'Last Updated': server_data.get('lastUpdated', '')
                }
                format_and_output(formatted_server, output, 'generic')
            else:
                format_and_output(server_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@authorization.command('delete')
@click.argument('server_id')
@click.option('--profile', default=None, help='The profile to use.')
@click.option('--force', is_flag=True, help='Force deletion without confirmation.')
@with_error_handling
def delete_authorization_server(server_id, profile, force):
    """Delete an authorization server."""
    if not force:
        if not click.confirm(f"Are you sure you want to delete authorization server '{server_id}'?"):
            click.echo("Authorization server deletion cancelled.")
            return
    
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deleting authorization server..."):
        try:
            response = requests.delete(f"https://{domain}/api/v1/authorizationServers/{server_id}", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 204:
        click.echo(click.style("✅ Authorization server deleted successfully!", fg='green'))
    else:
        handle_api_error(response)


@authorization.command('activate')
@click.argument('server_id')
@click.option('--profile', default=None, help='The profile to use.')
@with_error_handling
def activate_authorization_server(server_id, profile):
    """Activate an authorization server."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Activating authorization server..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/authorizationServers/{server_id}/lifecycle/activate", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Authorization server activated successfully!", fg='green'))
    else:
        handle_api_error(response)


@authorization.command('deactivate')
@click.argument('server_id')
@click.option('--profile', default=None, help='The profile to use.')
@with_error_handling
def deactivate_authorization_server(server_id, profile):
    """Deactivate an authorization server."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Deactivating authorization server..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/authorizationServers/{server_id}/lifecycle/deactivate", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        click.echo(click.style("✅ Authorization server deactivated successfully!", fg='green'))
    else:
        handle_api_error(response)


@authorization.group('scopes')
def scopes():
    """Manage authorization server scopes."""
    pass


@scopes.command('list')
@click.argument('server_id')
@click.option('--profile', default=None, help='The profile to use.')
@click.option('--limit', type=int, default=20, help='Number of scopes to retrieve.')
@create_output_option()
@with_error_handling
def list_scopes(server_id, profile, limit, output):
    """List scopes for an authorization server."""
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    params = {"limit": limit}

    with progress_spinner("Fetching scopes from authorization server..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/authorizationServers/{server_id}/scopes", headers=headers, params=params, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            scopes_data = response.json()
            
            if output == 'table':
                # Format for table display
                formatted_scopes = []
                for scope in scopes_data:
                    formatted_scopes.append({
                        'ID': scope.get('id', ''),
                        'Name': scope.get('name', ''),
                        'Description': scope.get('description', ''),
                        'Consent': scope.get('consent', ''),
                        'Metadata Published': scope.get('metadataPublish', ''),
                        'Default': scope.get('default', False)
                    })
                
                headers = ['ID', 'Name', 'Description', 'Consent', 'Metadata Published', 'Default']
                format_and_output(formatted_scopes, output, 'generic', headers)
            else:
                format_and_output(scopes_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@scopes.command('create')
@click.argument('server_id')
@click.option('--name', required=True, help='Scope name.')
@click.option('--description', help='Scope description.')
@click.option('--consent', type=click.Choice(['REQUIRED', 'OPTIONAL', 'IMPLICIT']), default='REQUIRED', help='Consent type.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def create_scope(server_id, name, description, consent, profile, output):
    """Create a new scope for an authorization server."""
    validate_name(name, "Scope name")
    
    try:
        domain, token = get_effective_config(profile)
    except Exception as e:
        try:
            cfg = config.get_config()
        except configparser.Error:
            handle_corrupted_config()
        
        if profile is None:
            profile = 'default'
        
        if not cfg.has_section(profile):
            handle_config_error(profile)

        domain = cfg.get(profile, "domain")
        token = cfg.get(profile, "token")

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    data = {
        "name": name,
        "consent": consent
    }
    
    if description:
        data["description"] = description

    with progress_spinner("Creating scope..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/authorizationServers/{server_id}/scopes", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 201:
        try:
            scope_data = response.json()
            
            click.echo(click.style("✅ Scope created successfully!", fg='green'))
            
            if output == 'table':
                formatted_scope = {
                    'ID': scope_data.get('id', ''),
                    'Name': scope_data.get('name', ''),
                    'Description': scope_data.get('description', ''),
                    'Consent': scope_data.get('consent', ''),
                    'Metadata Published': scope_data.get('metadataPublish', ''),
                    'Default': scope_data.get('default', False)
                }
                format_and_output(formatted_scope, output, 'generic')
            else:
                format_and_output(scope_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


if __name__ == '__main__':
    authorization()