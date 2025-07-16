# Error Handling

The Okta CLI tool includes comprehensive error handling to provide clear, actionable feedback when issues occur.

## Types of Errors

### API Errors
The CLI handles various HTTP status codes from the Okta API:

- **401 Unauthorized**: Invalid or expired API token
- **403 Forbidden**: Insufficient permissions for the requested operation  
- **404 Not Found**: Resource does not exist
- **429 Rate Limit**: Too many requests - includes reset time information
- **500 Server Error**: Internal server error on Okta's side
- **502/503/504**: Gateway and service availability issues

### Network Errors
Network-related issues are handled gracefully:

- **Connection Timeout**: Unable to establish connection to Okta
- **Read Timeout**: Request took too long to complete
- **Connection Error**: General network connectivity issues

### Input Validation Errors
Input is validated before making API calls:

- **Email Format**: Must be a valid email address
- **Okta Domain**: Must be a valid Okta domain (e.g., your-domain.okta.com)
- **API Token**: Must be provided and meet minimum length requirements
- **Names**: Cannot be empty and must be within character limits

### Configuration Errors
Configuration-related issues are handled with helpful guidance:

- **Missing Profile**: Profile doesn't exist - suggests running configure command
- **Corrupted Config**: Configuration file is invalid - suggests recreating it

## Error Message Format

All error messages follow a consistent format:
```
Error: [Category]: [Description]
```

Examples:
```
Error: Authentication failed: Invalid token provided
Error: Permission denied: You do not have permission to access this resource
Error: Connection timeout: Unable to connect to Okta. Please check your internet connection.
Error: Invalid email format: invalid-email
```

## Common Error Scenarios

### Authentication Issues
If you see authentication errors:
1. Check that your API token is valid and not expired
2. Verify you're using the correct profile
3. Ensure your token has the necessary permissions

### Network Issues
If you encounter connection problems:
1. Check your internet connection
2. Verify the Okta domain is correct
3. Check if there are any firewall restrictions

### Validation Issues
If input validation fails:
1. Ensure email addresses are properly formatted
2. Check that the Okta domain follows the expected format
3. Verify all required fields are provided

## Timeout Configuration

The CLI uses a 30-second timeout for all API requests. This provides a balance between:
- Waiting long enough for legitimate requests to complete
- Not hanging indefinitely on network issues

## Recovery Suggestions

The CLI provides specific recovery suggestions for common issues:

- **Profile not found**: Run `okta-cli configure --profile <profile-name>`
- **Invalid token**: Check your API token and re-run configure
- **Permission denied**: Contact your Okta administrator to verify permissions
- **Rate limit exceeded**: Wait for the reset time and try again
- **Connection issues**: Check network connectivity and domain configuration

## Development

### Adding New Error Handling

When adding new commands or functionality:

1. Use the `@with_error_handling` decorator on command functions
2. Validate input using the validation functions from `okta_cli.errors`
3. Use `handle_api_error()` for API responses
4. Use `handle_network_error()` for network exceptions
5. Follow the existing error message format

### Testing Error Scenarios

Error handling is thoroughly tested in `tests/test_error_handling.py`:

- API error responses (401, 403, 404, 429, 500, etc.)
- Network timeout scenarios
- Input validation errors
- Configuration errors

When adding new functionality, ensure error scenarios are tested using the same patterns.