"""
Output formatting utilities for the Okta CLI tool.
"""

import json
import csv
import yaml
import click
from typing import Dict, Any, List, Optional, Union
from tabulate import tabulate
import io
import sys
from datetime import datetime


class OutputFormatter:
    """
    Handles different output formats for CLI commands.
    """
    
    def __init__(self, format_type: str = 'table'):
        """
        Initialize output formatter.
        
        Args:
            format_type: Output format (json, table, csv, yaml, text)
        """
        self.format_type = format_type.lower()
        self.supported_formats = ['json', 'table', 'csv', 'yaml', 'text']
        
        if self.format_type not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def format_output(self, data: Any, headers: Optional[List[str]] = None) -> str:
        """
        Format data according to the specified format.
        
        Args:
            data: Data to format
            headers: Column headers for tabular data
            
        Returns:
            Formatted string
        """
        if self.format_type == 'json':
            return self._format_json(data)
        elif self.format_type == 'table':
            return self._format_table(data, headers)
        elif self.format_type == 'csv':
            return self._format_csv(data, headers)
        elif self.format_type == 'yaml':
            return self._format_yaml(data)
        elif self.format_type == 'text':
            return self._format_text(data)
        else:
            return str(data)
    
    def _format_json(self, data: Any) -> str:
        """Format data as JSON."""
        return json.dumps(data, indent=2, default=str)
    
    def _format_table(self, data: Any, headers: Optional[List[str]] = None) -> str:
        """Format data as a table."""
        if isinstance(data, dict):
            if headers:
                # If headers provided, create table from dict
                rows = []
                for key, value in data.items():
                    if isinstance(value, dict):
                        row = [key] + [value.get(h, '') for h in headers[1:]]
                    else:
                        row = [key, value]
                    rows.append(row)
                return tabulate(rows, headers=headers, tablefmt='grid')
            else:
                # Key-value pairs
                rows = [[key, value] for key, value in data.items()]
                return tabulate(rows, headers=['Key', 'Value'], tablefmt='grid')
        
        elif isinstance(data, list):
            if not data:
                return "No data to display"
            
            if isinstance(data[0], dict):
                # List of dictionaries
                if not headers:
                    headers = list(data[0].keys())
                
                rows = []
                for item in data:
                    row = [item.get(h, '') for h in headers]
                    rows.append(row)
                
                return tabulate(rows, headers=headers, tablefmt='grid')
            else:
                # List of values
                if headers:
                    return tabulate([[item] for item in data], headers=headers, tablefmt='grid')
                else:
                    return tabulate([[item] for item in data], tablefmt='grid')
        
        else:
            return str(data)
    
    def _format_csv(self, data: Any, headers: Optional[List[str]] = None) -> str:
        """Format data as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        if isinstance(data, dict):
            if headers:
                writer.writerow(headers)
                for key, value in data.items():
                    if isinstance(value, dict):
                        row = [key] + [value.get(h, '') for h in headers[1:]]
                    else:
                        row = [key, value]
                    writer.writerow(row)
            else:
                writer.writerow(['Key', 'Value'])
                for key, value in data.items():
                    writer.writerow([key, value])
        
        elif isinstance(data, list):
            if not data:
                return "No data to display"
            
            if isinstance(data[0], dict):
                if not headers:
                    headers = list(data[0].keys())
                
                writer.writerow(headers)
                for item in data:
                    row = [item.get(h, '') for h in headers]
                    writer.writerow(row)
            else:
                if headers:
                    writer.writerow(headers)
                for item in data:
                    writer.writerow([item])
        
        else:
            writer.writerow([str(data)])
        
        return output.getvalue()
    
    def _format_yaml(self, data: Any) -> str:
        """Format data as YAML."""
        try:
            return yaml.dump(data, default_flow_style=False, indent=2)
        except Exception:
            # Fallback to JSON if YAML fails
            return self._format_json(data)
    
    def _format_text(self, data: Any) -> str:
        """Format data as plain text."""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, dict):
                    lines.append(f"{key}:")
                    for sub_key, sub_value in value.items():
                        lines.append(f"  {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    lines.append(f"{key}:")
                    for item in value:
                        lines.append(f"  - {item}")
                else:
                    lines.append(f"{key}: {value}")
            return '\n'.join(lines)
        
        elif isinstance(data, list):
            if not data:
                return "No data to display"
            
            lines = []
            for item in data:
                if isinstance(item, dict):
                    lines.append("---")
                    for key, value in item.items():
                        lines.append(f"{key}: {value}")
                else:
                    lines.append(str(item))
            return '\n'.join(lines)
        
        else:
            return str(data)


class UserFormatter:
    """Specialized formatter for user data."""
    
    def __init__(self, format_type: str = 'table'):
        """Initialize user formatter."""
        self.formatter = OutputFormatter(format_type)
    
    def format_user_list(self, users: List[Dict[str, Any]]) -> str:
        """Format user list data."""
        if not users:
            return "No users found"
        
        # Extract relevant fields for display
        user_data = []
        for user in users:
            profile = user.get('profile', {})
            user_data.append({
                'Login': profile.get('login', ''),
                'First Name': profile.get('firstName', ''),
                'Last Name': profile.get('lastName', ''),
                'Email': profile.get('email', ''),
                'Status': user.get('status', ''),
                'Created': user.get('created', ''),
                'Last Login': user.get('lastLogin', '')
            })
        
        headers = ['Login', 'First Name', 'Last Name', 'Email', 'Status', 'Created', 'Last Login']
        return self.formatter.format_output(user_data, headers)
    
    def format_user_detail(self, user: Dict[str, Any]) -> str:
        """Format detailed user information."""
        profile = user.get('profile', {})
        
        user_info = {
            'ID': user.get('id', ''),
            'Login': profile.get('login', ''),
            'Email': profile.get('email', ''),
            'First Name': profile.get('firstName', ''),
            'Last Name': profile.get('lastName', ''),
            'Status': user.get('status', ''),
            'Created': user.get('created', ''),
            'Activated': user.get('activated', ''),
            'Last Login': user.get('lastLogin', ''),
            'Last Updated': user.get('lastUpdated', '')
        }
        
        return self.formatter.format_output(user_info)


class GroupFormatter:
    """Specialized formatter for group data."""
    
    def __init__(self, format_type: str = 'table'):
        """Initialize group formatter."""
        self.formatter = OutputFormatter(format_type)
    
    def format_group_list(self, groups: List[Dict[str, Any]]) -> str:
        """Format group list data."""
        if not groups:
            return "No groups found"
        
        # Extract relevant fields for display
        group_data = []
        for group in groups:
            profile = group.get('profile', {})
            group_data.append({
                'ID': group.get('id', ''),
                'Name': profile.get('name', ''),
                'Description': profile.get('description', ''),
                'Type': group.get('type', ''),
                'Created': group.get('created', ''),
                'Last Updated': group.get('lastUpdated', '')
            })
        
        headers = ['ID', 'Name', 'Description', 'Type', 'Created', 'Last Updated']
        return self.formatter.format_output(group_data, headers)
    
    def format_group_detail(self, group: Dict[str, Any]) -> str:
        """Format detailed group information."""
        profile = group.get('profile', {})
        
        group_info = {
            'ID': group.get('id', ''),
            'Name': profile.get('name', ''),
            'Description': profile.get('description', ''),
            'Type': group.get('type', ''),
            'Created': group.get('created', ''),
            'Last Updated': group.get('lastUpdated', '')
        }
        
        return self.formatter.format_output(group_info)


class ConfigFormatter:
    """Specialized formatter for configuration data."""
    
    def __init__(self, format_type: str = 'table'):
        """Initialize config formatter."""
        self.formatter = OutputFormatter(format_type)
    
    def format_profile_list(self, profiles: Dict[str, Any], active_profile: str = None) -> str:
        """Format profile list data."""
        if not profiles:
            return "No profiles configured"
        
        # Convert to list format for better display
        profile_data = []
        for name, profile in profiles.items():
            status = "Active" if name == active_profile else "Inactive"
            created_time = datetime.fromtimestamp(profile.get('created_at', 0)).strftime('%Y-%m-%d %H:%M:%S')
            last_used_time = datetime.fromtimestamp(profile.get('last_used', 0)).strftime('%Y-%m-%d %H:%M:%S')
            
            profile_data.append({
                'Name': name,
                'Domain': profile.get('domain', ''),
                'Status': status,
                'Created': created_time,
                'Last Used': last_used_time
            })
        
        headers = ['Name', 'Domain', 'Status', 'Created', 'Last Used']
        return self.formatter.format_output(profile_data, headers)
    
    def format_profile_detail(self, profile_name: str, profile_data: Dict[str, Any]) -> str:
        """Format detailed profile information."""
        created_time = datetime.fromtimestamp(profile_data.get('created_at', 0)).strftime('%Y-%m-%d %H:%M:%S')
        last_used_time = datetime.fromtimestamp(profile_data.get('last_used', 0)).strftime('%Y-%m-%d %H:%M:%S')
        
        profile_info = {
            'Name': profile_name,
            'Domain': profile_data.get('domain', ''),
            'Token': f"{'*' * 20}...{profile_data.get('token', '')[-4:]}",
            'Created': created_time,
            'Last Used': last_used_time
        }
        
        return self.formatter.format_output(profile_info)
    
    def format_health_check(self, health_data: Dict[str, Any]) -> str:
        """Format health check results."""
        health_info = {
            'Status': health_data.get('status', 'unknown'),
            'Connectivity': '✅ Connected' if health_data.get('connectivity') else '❌ Failed',
            'Authentication': '✅ Authenticated' if health_data.get('authentication') else '❌ Failed',
            'Response Time': f"{health_data.get('response_time', 0):.2f}s" if health_data.get('response_time') else 'N/A'
        }
        
        if health_data.get('errors'):
            health_info['Errors'] = '; '.join(health_data['errors'])
        
        return self.formatter.format_output(health_info)


def get_formatter(format_type: str, data_type: str = 'generic') -> OutputFormatter:
    """
    Get appropriate formatter based on format type and data type.
    
    Args:
        format_type: Output format (json, table, csv, yaml, text)
        data_type: Type of data (generic, user, group, config)
        
    Returns:
        Appropriate formatter instance
    """
    if data_type == 'user':
        return UserFormatter(format_type)
    elif data_type == 'group':
        return GroupFormatter(format_type)
    elif data_type == 'config':
        return ConfigFormatter(format_type)
    else:
        return OutputFormatter(format_type)


def format_and_output(data: Any, format_type: str = 'table', data_type: str = 'generic', 
                     headers: Optional[List[str]] = None) -> None:
    """
    Format data and output to console.
    
    Args:
        data: Data to format and output
        format_type: Output format
        data_type: Type of data
        headers: Column headers for tabular data
    """
    formatter = get_formatter(format_type, data_type)
    
    if data_type == 'user' and isinstance(formatter, UserFormatter):
        if isinstance(data, list):
            output = formatter.format_user_list(data)
        else:
            output = formatter.format_user_detail(data)
    elif data_type == 'group' and isinstance(formatter, GroupFormatter):
        if isinstance(data, list):
            output = formatter.format_group_list(data)
        else:
            output = formatter.format_group_detail(data)
    elif data_type == 'config' and isinstance(formatter, ConfigFormatter):
        output = formatter.format_output(data, headers)
    else:
        output = formatter.format_output(data, headers)
    
    click.echo(output)


def create_output_option():
    """Create a Click option for output format selection."""
    return click.option(
        '--output', '-o',
        type=click.Choice(['json', 'table', 'csv', 'yaml', 'text']),
        default='table',
        help='Output format',
        show_default=True
    )


def format_success_message(message: str) -> str:
    """Format success message with styling."""
    return click.style(f"✅ {message}", fg='green')


def format_error_message(message: str) -> str:
    """Format error message with styling."""
    return click.style(f"❌ {message}", fg='red')


def format_warning_message(message: str) -> str:
    """Format warning message with styling."""
    return click.style(f"⚠️  {message}", fg='yellow')


def format_info_message(message: str) -> str:
    """Format info message with styling."""
    return click.style(f"ℹ️  {message}", fg='blue')


def create_table_from_dict(data: Dict[str, Any], title: str = None) -> str:
    """
    Create a formatted table from dictionary data.
    
    Args:
        data: Dictionary data
        title: Optional title for the table
        
    Returns:
        Formatted table string
    """
    rows = []
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, indent=2)
        rows.append([key, value])
    
    table = tabulate(rows, headers=['Key', 'Value'], tablefmt='grid')
    
    if title:
        title_line = click.style(f"\n{title}", fg='cyan', bold=True)
        return f"{title_line}\n{table}"
    
    return table


def create_table_from_list(data: List[Dict[str, Any]], headers: List[str] = None, 
                          title: str = None) -> str:
    """
    Create a formatted table from list data.
    
    Args:
        data: List of dictionaries
        headers: Column headers
        title: Optional title for the table
        
    Returns:
        Formatted table string
    """
    if not data:
        return "No data to display"
    
    if not headers:
        headers = list(data[0].keys())
    
    rows = []
    for item in data:
        row = [item.get(h, '') for h in headers]
        rows.append(row)
    
    table = tabulate(rows, headers=headers, tablefmt='grid')
    
    if title:
        title_line = click.style(f"\n{title}", fg='cyan', bold=True)
        return f"{title_line}\n{table}"
    
    return table