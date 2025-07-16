# Security Features

The Okta CLI tool includes comprehensive security features to protect your credentials and ensure safe API usage.

## Encrypted Credential Storage

### Overview
The CLI uses strong encryption to protect stored API tokens and credentials. All sensitive data is encrypted using industry-standard AES-256 encryption with PBKDF2 key derivation.

### Features
- **AES-256 Encryption**: All API tokens are encrypted using AES-256 in CBC mode
- **PBKDF2 Key Derivation**: Uses PBKDF2 with SHA-256 and 100,000 iterations for key derivation
- **Salt-based Security**: Each encrypted token uses a unique random salt
- **Master Password Protection**: All credentials are protected by a master password

### Usage
When you first configure the CLI, you'll be prompted to create a master password:

```bash
okta-cli configure
Create master password: [hidden]
Confirm master password: [hidden]
```

The master password is used to encrypt/decrypt all stored credentials. It's never stored on disk - only a hash is kept for verification.

### Security Best Practices
- **Choose a strong master password**: Use at least 8 characters with mixed case, numbers, and symbols
- **Keep your master password secure**: Never share it or store it in plain text
- **Regular password rotation**: Consider changing your master password periodically
- **Backup your configuration**: Use the backup feature before making changes

### File Permissions
The CLI automatically sets restrictive file permissions on all configuration files:
- Configuration directory: `700` (owner read/write/execute only)
- Configuration files: `600` (owner read/write only)
- Master key file: `600` (owner read/write only)

## Token Validation

### Overview
The CLI includes comprehensive token validation to ensure your API tokens are valid and have the necessary permissions before making API calls.

### Features
- **Token Health Checks**: Validates tokens before use
- **Permission Verification**: Checks if tokens have required permissions
- **Real-time Validation**: Validates tokens against the live Okta API
- **Detailed Permission Mapping**: Maps API endpoints to required permissions

### Token Validation Process
1. **Syntax Check**: Validates token format and length
2. **Connectivity Test**: Tests connection to Okta API
3. **Authentication Check**: Verifies token is valid and not expired
4. **Permission Check**: Confirms token has required permissions for the operation

### Permission Types
The CLI checks for the following permissions:
- `users:read` - Read user information
- `users:write` - Create and modify users
- `groups:read` - Read group information
- `groups:write` - Create and modify groups
- `apps:read` - Read application information
- `apps:write` - Manage application assignments

### Usage Example
```bash
# The CLI automatically validates tokens before each operation
okta-cli users list
# Token validation occurs automatically:
# 1. Checks if token is valid
# 2. Verifies 'users:read' permission
# 3. Proceeds with API call if validation passes
```

## Rate Limiting

### Overview
The CLI includes client-side rate limiting to prevent API rate limit violations and ensure reliable operation.

### Features
- **Configurable Rate Limits**: Default 1000 requests per minute
- **Time Window Management**: Sliding window rate limiting
- **Automatic Backoff**: Waits for rate limit reset when exceeded
- **Rate Limit Monitoring**: Tracks remaining requests in current window

### Default Rate Limits
- **Requests per minute**: 1000
- **Time window**: 60 seconds
- **Backoff strategy**: Wait for reset time

### Rate Limit Behavior
When rate limits are approached:
1. **Warning**: CLI warns when 90% of limit is reached
2. **Blocking**: CLI blocks requests when limit is exceeded
3. **Waiting**: CLI waits for reset time before allowing new requests
4. **Retry**: Automatically retries failed requests after reset

### Configuration
Rate limits can be configured via environment variables:
```bash
export OKTA_RATE_LIMIT_REQUESTS=500
export OKTA_RATE_LIMIT_WINDOW=60
```

## Security Architecture

### Encryption Flow
```
User Input → Master Password → PBKDF2 → AES-256 Key → Encrypted Token → Secure Storage
```

### Token Validation Flow
```
API Call → Token Validation → Permission Check → Rate Limit Check → Okta API
```

### Security Layers
1. **Transport Security**: All API calls use HTTPS with certificate validation
2. **Credential Encryption**: API tokens encrypted at rest
3. **Access Control**: File permissions restrict access to configuration
4. **Rate Limiting**: Prevents abuse and ensures reliable operation
5. **Input Validation**: All input validated before processing

## Security Considerations

### Threat Model
The CLI protects against:
- **Credential Theft**: Encrypted storage prevents plaintext credential exposure
- **Unauthorized Access**: File permissions and master password protection
- **API Abuse**: Rate limiting prevents excessive API usage
- **Token Compromise**: Token validation detects invalid or expired tokens

### Security Assumptions
- The host system is trusted and secure
- The master password is kept secure by the user
- The local filesystem provides adequate file permission controls
- HTTPS transport provides adequate encryption in transit

### Limitations
- **Local Storage**: Credentials are stored locally (not in a hardware security module)
- **Master Password**: Security depends on master password strength
- **Host Security**: Relies on host system security controls
- **Network Security**: Depends on network security for API calls

## Security Commands

### Backup Configuration
```bash
# Create encrypted backup of configuration
okta-cli config backup
```

### Restore Configuration
```bash
# Restore from encrypted backup
okta-cli config restore /path/to/backup.json
```

### List Profiles
```bash
# List all configured profiles
okta-cli config profiles
```

### Token Validation
```bash
# Validate current token
okta-cli config validate
```

### Permission Check
```bash
# Check token permissions
okta-cli config permissions
```

## Troubleshooting

### Common Issues

**"Master password incorrect"**
- Verify you're entering the correct master password
- Check for caps lock or keyboard layout issues

**"Token validation failed"**
- Verify your API token is still valid
- Check if your token has the required permissions
- Ensure network connectivity to Okta

**"Rate limit exceeded"**
- Wait for the rate limit reset time
- Reduce the frequency of API calls
- Consider using bulk operations where available

### Debug Mode
Enable debug mode to see detailed security information:
```bash
export OKTA_DEBUG=true
okta-cli users list
```

## Best Practices

### Token Management
1. **Regular Rotation**: Rotate API tokens regularly
2. **Principle of Least Privilege**: Use tokens with minimal required permissions
3. **Monitoring**: Monitor token usage and access patterns
4. **Revocation**: Immediately revoke compromised tokens

### Configuration Security
1. **Strong Master Password**: Use a strong, unique master password
2. **Regular Backups**: Create encrypted backups of your configuration
3. **Secure Storage**: Store backups in secure locations
4. **Access Control**: Limit access to configuration files

### Operational Security
1. **Network Security**: Use secure networks for API calls
2. **Host Security**: Keep your system updated and secure
3. **Logging**: Monitor CLI usage and API calls
4. **Incident Response**: Have a plan for security incidents

## Compliance

### Standards
The CLI's security features are designed to meet:
- **NIST Cybersecurity Framework**: Protect, Detect, Respond
- **SOC 2 Type II**: Security controls for service organizations
- **ISO 27001**: Information security management standards

### Audit Trail
The CLI maintains security-relevant logs:
- Token validation attempts
- Rate limit violations
- Configuration changes
- Authentication failures

### Data Protection
- **Encryption at Rest**: All sensitive data encrypted when stored
- **Encryption in Transit**: All API calls use HTTPS
- **Data Minimization**: Only necessary data is stored
- **Secure Deletion**: Configuration can be securely deleted