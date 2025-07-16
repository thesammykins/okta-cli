# Troubleshooting Guide

Complete troubleshooting guide for the Okta CLI tool, including common issues, error messages, and solutions.

## Getting Started with Troubleshooting

### Enable Debug Mode

When troubleshooting, always start by enabling debug mode:

```bash
# Enable debug output
export OKTA_DEBUG=true
okta-cli users list

# Use verbose flag for detailed output
okta-cli --verbose users list

# Combine both for maximum detail
export OKTA_DEBUG=true
okta-cli --verbose config health
```

### Basic Health Checks

Always start troubleshooting with these basic checks:

```bash
# Check configuration health
okta-cli config health

# Check specific profile
okta-cli config health --profile production

# Validate configuration
okta-cli config validate

# Check configuration status
okta-cli config status
```

## Common Issues and Solutions

### 1. Installation Issues

#### Problem: Command not found

```bash
# Error message
bash: okta-cli: command not found
```

**Solutions:**

1. **Check if installed:**
   ```bash
   pip list | grep okta-cli
   ```

2. **Install if missing:**
   ```bash
   pip install okta-cli
   ```

3. **Check virtual environment:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Verify installation
   okta-cli --version
   ```

4. **Path issues:**
   ```bash
   # Add to PATH if needed
   export PATH=$PATH:~/.local/bin
   ```

#### Problem: Permission denied during installation

```bash
# Error message
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions:**

1. **Use --user flag:**
   ```bash
   pip install --user okta-cli
   ```

2. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install okta-cli
   ```

3. **Update pip:**
   ```bash
   pip install --upgrade pip
   pip install okta-cli
   ```

#### Problem: Python version compatibility

```bash
# Error message
ERROR: Package requires Python '>=3.8' but the running Python is 3.7
```

**Solutions:**

1. **Check Python version:**
   ```bash
   python --version
   python3 --version
   ```

2. **Use specific Python version:**
   ```bash
   python3.9 -m pip install okta-cli
   ```

3. **Update Python:**
   ```bash
   # macOS with Homebrew
   brew install python@3.9
   
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.9
   ```

### 2. Configuration Issues

#### Problem: Configuration file not found

```bash
# Error message
Configuration file not found. Please run 'okta-cli config wizard' to set up.
```

**Solutions:**

1. **Run configuration wizard:**
   ```bash
   okta-cli config wizard
   ```

2. **Check configuration directory:**
   ```bash
   ls -la ~/.okta-cli/
   ```

3. **Create configuration manually:**
   ```bash
   okta-cli config create default --domain your.okta.com --token your-token
   ```

#### Problem: Profile not found

```bash
# Error message
Profile 'production' not found in configuration.
```

**Solutions:**

1. **List available profiles:**
   ```bash
   okta-cli config list
   ```

2. **Create missing profile:**
   ```bash
   okta-cli config create production --domain prod.okta.com --token prod-token
   ```

3. **Check profile name spelling:**
   ```bash
   okta-cli config show
   ```

#### Problem: Corrupted configuration file

```bash
# Error message
Error parsing configuration file: Invalid format
```

**Solutions:**

1. **Backup current configuration:**
   ```bash
   cp ~/.okta-cli/config.ini ~/.okta-cli/config.ini.backup
   ```

2. **Restore from backup:**
   ```bash
   okta-cli config restore backup.json
   ```

3. **Recreate configuration:**
   ```bash
   rm ~/.okta-cli/config.ini
   okta-cli config wizard
   ```

### 3. Authentication Issues

#### Problem: Invalid API token

```bash
# Error message
Authentication failed: Invalid API token
```

**Solutions:**

1. **Verify token in Okta Admin Console:**
   - Go to Security → API → Tokens
   - Check token status and permissions

2. **Regenerate token:**
   ```bash
   # Create new token in Okta Admin Console
   okta-cli config create profile-name --domain your.okta.com --token new-token
   ```

3. **Check token format:**
   ```bash
   # Token should be 40 characters long
   echo $OKTA_TOKEN | wc -c
   ```

#### Problem: Insufficient permissions

```bash
# Error message
Permission denied: Your API token may not have the required permissions
```

**Solutions:**

1. **Check token permissions in Okta Admin Console:**
   - Ensure token has appropriate scopes
   - Required permissions vary by operation

2. **Use Super Admin token for testing:**
   ```bash
   okta-cli config create admin --domain your.okta.com --token super-admin-token
   ```

3. **Validate token permissions:**
   ```bash
   okta-cli config validate profile-name
   ```

#### Problem: Token expired

```bash
# Error message
Authentication failed: Token has expired
```

**Solutions:**

1. **Check token expiration:**
   - Tokens don't expire but can be revoked
   - Check in Okta Admin Console

2. **Create new token:**
   ```bash
   okta-cli config create profile-name --domain your.okta.com --token new-token
   ```

### 4. Network Issues

#### Problem: Connection timeout

```bash
# Error message
Connection timeout: Unable to connect to Okta domain
```

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping your.okta.com
   curl -I https://your.okta.com
   ```

2. **Check domain configuration:**
   ```bash
   okta-cli config show
   ```

3. **Test with different timeout:**
   ```bash
   export OKTA_TIMEOUT=60
   okta-cli users list
   ```

4. **Check proxy settings:**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=https://proxy.company.com:8080
   ```

#### Problem: SSL certificate verification failed

```bash
# Error message
SSL certificate verification failed
```

**Solutions:**

1. **Check certificate validity:**
   ```bash
   openssl s_client -connect your.okta.com:443
   ```

2. **Temporary workaround (not recommended for production):**
   ```bash
   export OKTA_SSL_VERIFY=false
   okta-cli users list
   ```

3. **Update certificates:**
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt upgrade ca-certificates
   
   # macOS
   brew update && brew upgrade ca-certificates
   ```

#### Problem: DNS resolution issues

```bash
# Error message
Name resolution failed: Could not resolve hostname
```

**Solutions:**

1. **Check DNS resolution:**
   ```bash
   nslookup your.okta.com
   dig your.okta.com
   ```

2. **Use IP address temporarily:**
   ```bash
   # Find IP address
   nslookup your.okta.com
   # Update configuration with IP
   ```

3. **Check /etc/hosts file:**
   ```bash
   cat /etc/hosts | grep okta
   ```

### 5. Resource Not Found Issues

#### Problem: User not found

```bash
# Error message
User not found with identifier 'user@example.com'
```

**Solutions:**

1. **Verify user exists:**
   ```bash
   okta-cli users list --output json | grep "user@example.com"
   ```

2. **Try different identifier:**
   ```bash
   # Try with login instead of email
   okta-cli users show user-login-name
   
   # Try with user ID
   okta-cli users show user-id-123
   ```

3. **Search for user:**
   ```bash
   okta-cli users search --query "user@example.com"
   ```

#### Problem: Group not found

```bash
# Error message
Group not found with identifier 'Engineering Team'
```

**Solutions:**

1. **List all groups:**
   ```bash
   okta-cli groups list --output json
   ```

2. **Check group name exactly:**
   ```bash
   okta-cli groups list --output json | jq -r '.[].profile.name'
   ```

3. **Use group ID instead:**
   ```bash
   okta-cli groups show group-id-123
   ```

#### Problem: Application not found

```bash
# Error message
Application not found with identifier 'My App'
```

**Solutions:**

1. **List all applications:**
   ```bash
   okta-cli applications list --output json
   ```

2. **Check application name:**
   ```bash
   okta-cli applications list --output json | jq -r '.[].name'
   ```

3. **Use application ID:**
   ```bash
   okta-cli applications show app-id-123
   ```

### 6. Command-Specific Issues

#### Problem: Policy list requires type parameter

```bash
# Error message
Policy type is required. Use --type parameter.
```

**Solutions:**

1. **Specify policy type:**
   ```bash
   okta-cli policies list --type OKTA_SIGN_ON
   okta-cli policies list --type PASSWORD
   okta-cli policies list --type MFA_ENROLL
   ```

2. **List available policy types:**
   ```bash
   okta-cli policies --help
   ```

#### Problem: Application assignment not allowed

```bash
# Error message
App instance operation not allowed
```

**Solutions:**

1. **Check application type:**
   ```bash
   okta-cli applications show app-name --output json
   ```

2. **Some built-in Okta apps don't support manual assignment:**
   - Try with custom applications
   - Check application configuration

3. **Use group-based assignment:**
   ```bash
   okta-cli groups add-user group-name user@example.com
   ```

#### Problem: Session management not available

```bash
# Error message
Method not allowed for session operation
```

**Solutions:**

1. **Check Okta edition:**
   - Session management may be limited in some editions
   - Check Okta documentation for feature availability

2. **Use alternative approach:**
   ```bash
   # Instead of session management, use user lifecycle
   okta-cli users deactivate user@example.com
   okta-cli users activate user@example.com
   ```

### 7. Performance Issues

#### Problem: Slow response times

```bash
# Commands taking too long to execute
```

**Solutions:**

1. **Use limits for large datasets:**
   ```bash
   okta-cli users list --limit 50
   okta-cli logs list --limit 100
   ```

2. **Use filters to reduce data:**
   ```bash
   okta-cli logs search --event-type "user.session.start" --days 1
   ```

3. **Check network latency:**
   ```bash
   ping your.okta.com
   ```

4. **Increase timeout:**
   ```bash
   export OKTA_TIMEOUT=120
   okta-cli users list
   ```

#### Problem: Rate limiting

```bash
# Error message
Rate limit exceeded: Too many requests
```

**Solutions:**

1. **Implement delays between requests:**
   ```bash
   okta-cli users list
   sleep 2
   okta-cli groups list
   ```

2. **Use bulk operations where possible:**
   ```bash
   # Instead of individual user operations
   okta-cli users list --output json > users.json
   ```

3. **Check rate limits in Okta Admin Console:**
   - Monitor API usage
   - Consider upgrading plan if needed

## Error Code Reference

### HTTP Status Codes

#### 400 Bad Request
- **Cause**: Invalid request format or parameters
- **Solution**: Check command syntax and parameters

#### 401 Unauthorized
- **Cause**: Invalid or missing API token
- **Solution**: Verify token and regenerate if needed

#### 403 Forbidden
- **Cause**: Insufficient permissions
- **Solution**: Check token permissions or use admin token

#### 404 Not Found
- **Cause**: Resource doesn't exist
- **Solution**: Verify resource identifier and existence

#### 429 Too Many Requests
- **Cause**: Rate limit exceeded
- **Solution**: Implement delays or reduce request frequency

#### 500 Internal Server Error
- **Cause**: Okta server error
- **Solution**: Check Okta status page, retry later

### Common Error Messages

#### "Profile not found"
```bash
# Check available profiles
okta-cli config list

# Create missing profile
okta-cli config create profile-name --domain your.okta.com --token your-token
```

#### "Invalid domain format"
```bash
# Correct format
okta-cli config create profile --domain company.okta.com --token token

# Incorrect formats
okta-cli config create profile --domain https://company.okta.com --token token  # Remove https://
okta-cli config create profile --domain company.okta.com/ --token token        # Remove trailing slash
```

#### "Token validation failed"
```bash
# Check token in Okta Admin Console
# Regenerate token if needed
okta-cli config create profile --domain your.okta.com --token new-token
```

## Logging and Debugging

### Enable Detailed Logging

```bash
# Enable debug mode
export OKTA_DEBUG=true

# Enable verbose output
okta-cli --verbose command

# Save output to file
okta-cli users list --verbose > debug.log 2>&1
```

### Log File Locations

```bash
# Check system logs
tail -f /var/log/syslog | grep okta

# Check application logs
ls -la ~/.okta-cli/logs/
```

### Debug Configuration

```bash
# Show configuration details
okta-cli config show --verbose

# Test configuration health
okta-cli config health --verbose

# Validate all profiles
for profile in $(okta-cli config list --output json | jq -r '.[] | .name'); do
    echo "Validating profile: $profile"
    okta-cli config validate $profile
done
```

## Diagnostic Commands

### System Information

```bash
# Check Python version
python --version

# Check installed packages
pip list | grep okta

# Check environment variables
env | grep OKTA

# Check network connectivity
ping your.okta.com
curl -I https://your.okta.com
```

### Configuration Diagnostics

```bash
# Check configuration file
cat ~/.okta-cli/config.ini

# Check file permissions
ls -la ~/.okta-cli/

# Validate configuration format
okta-cli config validate --verbose
```

### API Diagnostics

```bash
# Test API connectivity
okta-cli users list --limit 1

# Test specific endpoints
okta-cli users show test-user-id
okta-cli groups list --limit 1
okta-cli applications list --limit 1
```

## Recovery Procedures

### Configuration Recovery

```bash
# Backup current configuration
cp ~/.okta-cli/config.ini ~/.okta-cli/config.ini.backup

# Restore from backup
okta-cli config restore backup.json

# Recreate configuration
rm ~/.okta-cli/config.ini
okta-cli config wizard
```

### Permission Recovery

```bash
# Reset file permissions
chmod 700 ~/.okta-cli/
chmod 600 ~/.okta-cli/config.ini

# Recreate configuration directory
rm -rf ~/.okta-cli/
okta-cli config wizard
```

### Token Recovery

```bash
# Create new token in Okta Admin Console
# Update configuration with new token
okta-cli config create profile-name --domain your.okta.com --token new-token

# Test new token
okta-cli config validate profile-name
```

## Getting Help

### Command Help

```bash
# General help
okta-cli --help

# Command-specific help
okta-cli users --help
okta-cli users create --help

# Show version
okta-cli --version
```

### Support Resources

1. **Check configuration health:**
   ```bash
   okta-cli config health
   ```

2. **Validate configuration:**
   ```bash
   okta-cli config validate
   ```

3. **Check system status:**
   ```bash
   okta-cli config status
   ```

4. **Enable debug mode:**
   ```bash
   export OKTA_DEBUG=true
   okta-cli command --verbose
   ```

### Creating Support Reports

```bash
# Generate diagnostic report
cat > diagnostic-report.txt << EOF
Okta CLI Diagnostic Report - $(date)

System Information:
- Python Version: $(python --version)
- OS: $(uname -a)
- CLI Version: $(okta-cli --version)

Configuration Health:
$(okta-cli config health 2>&1)

Available Profiles:
$(okta-cli config list 2>&1)

Environment Variables:
$(env | grep OKTA)

Recent Errors:
$(tail -50 ~/.okta-cli/logs/error.log 2>/dev/null || echo "No error log found")
EOF
```

## Best Practices for Troubleshooting

### 1. Systematic Approach

1. **Start with basic checks:**
   - Configuration health
   - Network connectivity
   - Authentication

2. **Enable debug mode:**
   ```bash
   export OKTA_DEBUG=true
   ```

3. **Check logs:**
   ```bash
   tail -f ~/.okta-cli/logs/debug.log
   ```

### 2. Documentation

- Document known issues and solutions
- Keep configuration backups
- Maintain troubleshooting logs

### 3. Testing

- Test configuration changes in development first
- Validate after configuration changes
- Use health checks regularly

### 4. Monitoring

- Set up automated health checks
- Monitor API usage and rate limits
- Check token expiration dates

This troubleshooting guide should help you resolve most common issues with the Okta CLI. If you continue to experience problems, ensure you have the latest version installed and consider reaching out to your Okta administrator for additional support.