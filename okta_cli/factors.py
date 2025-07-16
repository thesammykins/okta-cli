"""
Multi-factor authentication (MFA) and factor management for the Okta CLI tool.
"""

import click
import requests
import json
from typing import Dict, Any, List, Optional
from . import config
from .errors import (
    handle_api_error, handle_network_error, handle_json_error,
    handle_config_error, handle_corrupted_config, with_error_handling
)
from .enhanced_config import get_effective_config
from .formatting import create_output_option, format_and_output
from .progress import progress_spinner
from .utils import resolve_user_id, get_user_by_identifier
import configparser


@click.group()
def factors():
    """Manage multi-factor authentication (MFA) factors."""
    pass


@factors.command('list')
@click.argument('user_identifier')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def list_factors(user_identifier, profile, output):
    """List enrolled factors for a user (accepts ID, email, or login)."""
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

    # Resolve user identifier to ID
    user_id = resolve_user_id(user_identifier, domain, token)
    if not user_id:
        click.echo(f"Error: User not found with identifier '{user_identifier}'")
        return

    headers = {
        "Authorization": f"SSWS {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    with progress_spinner("Fetching user factors from Okta API..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/users/{user_id}/factors", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            factors_data = response.json()
            
            if output == 'table':
                # Format for table display
                formatted_factors = []
                for factor in factors_data:
                    profile_info = factor.get('profile', {})
                    formatted_factors.append({
                        'ID': factor.get('id', ''),
                        'Factor Type': factor.get('factorType', ''),
                        'Provider': factor.get('provider', ''),
                        'Status': factor.get('status', ''),
                        'Profile': profile_info.get('phoneNumber', profile_info.get('credentialId', str(profile_info))),
                        'Created': factor.get('created', ''),
                        'Last Updated': factor.get('lastUpdated', '')
                    })
                
                headers = ['ID', 'Factor Type', 'Provider', 'Status', 'Profile', 'Created', 'Last Updated']
                format_and_output(formatted_factors, output, 'generic', headers)
            else:
                format_and_output(factors_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.command('show')
@click.argument('user_id')
@click.argument('factor_id')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def show_factor(user_id, factor_id, profile, output):
    """Show details for a specific factor."""
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

    with progress_spinner("Fetching factor details..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/users/{user_id}/factors/{factor_id}", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            factor_data = response.json()
            
            if output == 'table':
                # Format for table display
                profile_info = factor_data.get('profile', {})
                formatted_factor = {
                    'ID': factor_data.get('id', ''),
                    'Factor Type': factor_data.get('factorType', ''),
                    'Provider': factor_data.get('provider', ''),
                    'Status': factor_data.get('status', ''),
                    'Created': factor_data.get('created', ''),
                    'Last Updated': factor_data.get('lastUpdated', ''),
                    'Profile': str(profile_info),
                    'Links': str(factor_data.get('_links', {}))
                }
                format_and_output(formatted_factor, output, 'generic')
            else:
                format_and_output(factor_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.command('enroll')
@click.argument('user_id')
@click.option('--factor-type', type=click.Choice(['sms', 'call', 'token:software:totp', 'token:hardware', 'push', 'email', 'u2f', 'webauthn']), required=True, help='Factor type to enroll.')
@click.option('--provider', type=click.Choice(['OKTA', 'SYMANTEC', 'GOOGLE', 'RSA', 'FIDO']), default='OKTA', help='Factor provider.')
@click.option('--phone-number', help='Phone number for SMS/call factors.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def enroll_factor(user_id, factor_type, provider, phone_number, profile, output):
    """Enroll a user in a new factor."""
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
        "factorType": factor_type,
        "provider": provider
    }
    
    # Add profile information based on factor type
    if factor_type in ['sms', 'call'] and phone_number:
        data["profile"] = {"phoneNumber": phone_number}
    elif factor_type == 'token:software:totp':
        data["profile"] = {}
    elif factor_type == 'push':
        data["profile"] = {}

    with progress_spinner("Enrolling user in factor..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/users/{user_id}/factors", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            factor_data = response.json()
            
            click.echo(click.style("✅ Factor enrollment initiated successfully!", fg='green'))
            
            if output == 'table':
                profile_info = factor_data.get('profile', {})
                formatted_factor = {
                    'ID': factor_data.get('id', ''),
                    'Factor Type': factor_data.get('factorType', ''),
                    'Provider': factor_data.get('provider', ''),
                    'Status': factor_data.get('status', ''),
                    'Profile': str(profile_info),
                    'QR Code': factor_data.get('_embedded', {}).get('qrcode', {}).get('href', ''),
                    'Shared Secret': factor_data.get('_embedded', {}).get('sharedSecret', '')
                }
                format_and_output(formatted_factor, output, 'generic')
            else:
                format_and_output(factor_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.command('activate')
@click.argument('user_id')
@click.argument('factor_id')
@click.option('--passcode', help='Passcode for factor activation.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def activate_factor(user_id, factor_id, passcode, profile, output):
    """Activate an enrolled factor."""
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

    data = {}
    if passcode:
        data["passCode"] = passcode

    with progress_spinner("Activating factor..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/users/{user_id}/factors/{factor_id}/lifecycle/activate", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            factor_data = response.json()
            
            click.echo(click.style("✅ Factor activated successfully!", fg='green'))
            
            if output == 'table':
                profile_info = factor_data.get('profile', {})
                formatted_factor = {
                    'ID': factor_data.get('id', ''),
                    'Factor Type': factor_data.get('factorType', ''),
                    'Provider': factor_data.get('provider', ''),
                    'Status': factor_data.get('status', ''),
                    'Profile': str(profile_info),
                    'Last Updated': factor_data.get('lastUpdated', '')
                }
                format_and_output(formatted_factor, output, 'generic')
            else:
                format_and_output(factor_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.command('reset')
@click.argument('user_id')
@click.argument('factor_id')
@click.option('--profile', default=None, help='The profile to use.')
@click.option('--force', is_flag=True, help='Force reset without confirmation.')
@with_error_handling
def reset_factor(user_id, factor_id, profile, force):
    """Reset a user's factor."""
    if not force:
        if not click.confirm(f"Are you sure you want to reset factor '{factor_id}' for user '{user_id}'?"):
            click.echo("Factor reset cancelled.")
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

    with progress_spinner("Resetting factor..."):
        try:
            response = requests.delete(f"https://{domain}/api/v1/users/{user_id}/factors/{factor_id}", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 204:
        click.echo(click.style("✅ Factor reset successfully!", fg='green'))
    else:
        handle_api_error(response)


@factors.command('verify')
@click.argument('user_id')
@click.argument('factor_id')
@click.option('--passcode', help='Passcode for factor verification.')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def verify_factor(user_id, factor_id, passcode, profile, output):
    """Verify a factor."""
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

    data = {}
    if passcode:
        data["passCode"] = passcode

    with progress_spinner("Verifying factor..."):
        try:
            response = requests.post(f"https://{domain}/api/v1/users/{user_id}/factors/{factor_id}/verify", headers=headers, json=data, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            verify_data = response.json()
            
            result = verify_data.get('factorResult', 'UNKNOWN')
            if result == 'SUCCESS':
                click.echo(click.style("✅ Factor verification successful!", fg='green'))
            elif result == 'CHALLENGE':
                click.echo(click.style("🔄 Factor verification requires additional challenge.", fg='yellow'))
            else:
                click.echo(click.style(f"❌ Factor verification failed: {result}", fg='red'))
            
            if output == 'table':
                formatted_verify = {
                    'Factor Result': verify_data.get('factorResult', ''),
                    'Factor Message': verify_data.get('factorMessage', ''),
                    'Factor Result Message': verify_data.get('factorResultMessage', ''),
                    'Profile': str(verify_data.get('profile', {}))
                }
                format_and_output(formatted_verify, output, 'generic')
            else:
                format_and_output(verify_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.group('catalog')
def factor_catalog():
    """Manage factor catalog (available factors)."""
    pass


@factor_catalog.command('list')
@click.argument('user_id')
@click.option('--profile', default=None, help='The profile to use.')
@create_output_option()
@with_error_handling
def list_catalog(user_id, profile, output):
    """List available factors from the catalog for a user."""
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

    with progress_spinner("Fetching factor catalog..."):
        try:
            response = requests.get(f"https://{domain}/api/v1/users/{user_id}/factors/catalog", headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            handle_network_error(e)

    if response.status_code == 200:
        try:
            catalog_data = response.json()
            
            if output == 'table':
                # Format for table display
                formatted_catalog = []
                for factor in catalog_data:
                    formatted_catalog.append({
                        'Factor Type': factor.get('factorType', ''),
                        'Provider': factor.get('provider', ''),
                        'Status': factor.get('status', ''),
                        'Enrollment': factor.get('enrollment', ''),
                        'Verification': factor.get('verification', '')
                    })
                
                headers = ['Factor Type', 'Provider', 'Status', 'Enrollment', 'Verification']
                format_and_output(formatted_catalog, output, 'generic', headers)
            else:
                format_and_output(catalog_data, output, 'generic')
                
        except (ValueError, KeyError) as e:
            handle_json_error(e, response.text)
    else:
        handle_api_error(response)


@factors.command('stats')
@click.option('--profile', default=None, help='The profile to use.')
@click.option('--limit', type=int, default=1000, help='Number of users to analyze.')
@create_output_option()
@with_error_handling
def factor_stats(profile, limit, output):
    """Get MFA adoption statistics across the organization."""
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

    with progress_spinner("Analyzing MFA adoption across the organization..."):
        try:
            # Get active users
            users_response = requests.get(f"https://{domain}/api/v1/users", headers=headers, params={"limit": limit, "filter": "status eq \"ACTIVE\""}, timeout=30)
            
            if users_response.status_code != 200:
                handle_api_error(users_response)
                return
            
            users_data = users_response.json()
            
            total_users = len(users_data)
            users_with_mfa = 0
            factor_types = {}
            factor_providers = {}
            
            # Check factors for each user (limited to avoid too many API calls)
            for user in users_data[:100]:  # Limit to first 100 users
                user_id = user.get('id')
                if user_id:
                    try:
                        factors_response = requests.get(f"https://{domain}/api/v1/users/{user_id}/factors", headers=headers, timeout=10)
                        if factors_response.status_code == 200:
                            factors = factors_response.json()
                            if factors:
                                users_with_mfa += 1
                                for factor in factors:
                                    factor_type = factor.get('factorType', 'Unknown')
                                    factor_types[factor_type] = factor_types.get(factor_type, 0) + 1
                                    
                                    provider = factor.get('provider', 'Unknown')
                                    factor_providers[provider] = factor_providers.get(provider, 0) + 1
                    except requests.exceptions.RequestException:
                        # Skip users with factor fetch errors
                        continue
            
            # Calculate statistics
            mfa_adoption_rate = (users_with_mfa / total_users * 100) if total_users > 0 else 0
            
            stats = {
                'total_active_users': total_users,
                'users_with_mfa': users_with_mfa,
                'mfa_adoption_rate': round(mfa_adoption_rate, 2),
                'factor_types': factor_types,
                'factor_providers': factor_providers
            }
            
        except requests.exceptions.RequestException as e:
            handle_network_error(e)
            return

    if output == 'table':
        formatted_stats = {
            'Total Active Users': stats['total_active_users'],
            'Users with MFA': stats['users_with_mfa'],
            'MFA Adoption Rate': f"{stats['mfa_adoption_rate']}%",
            'Factor Types': ', '.join([f"{k}: {v}" for k, v in stats['factor_types'].items()]),
            'Factor Providers': ', '.join([f"{k}: {v}" for k, v in stats['factor_providers'].items()])
        }
        format_and_output(formatted_stats, output, 'generic')
    else:
        format_and_output(stats, output, 'generic')


if __name__ == '__main__':
    factors()