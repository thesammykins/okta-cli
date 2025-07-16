# Common Use Cases

This guide provides real-world examples and workflows for common Okta CLI use cases.

## User Lifecycle Management

### User Onboarding

Complete workflow for onboarding a new employee:

```bash
# Step 1: Create the user account
okta-cli users create \
  --first-name "Jane" \
  --last-name "Smith" \
  --email "jane.smith@company.com" \
  --login "jane.smith@company.com" \
  --profile production

# Step 2: Add to standard groups
okta-cli groups add-user "Everyone" jane.smith@company.com --profile production
okta-cli groups add-user "All Employees" jane.smith@company.com --profile production

# Step 3: Add to department-specific groups
okta-cli groups add-user "Engineering Team" jane.smith@company.com --profile production
okta-cli groups add-user "Software Engineers" jane.smith@company.com --profile production

# Step 4: Assign standard applications
okta-cli users assign-app jane.smith@company.com "Company Portal" --profile production
okta-cli users assign-app jane.smith@company.com "Email System" --profile production
okta-cli users assign-app jane.smith@company.com "HR System" --profile production

# Step 5: Activate the user account
okta-cli users activate jane.smith@company.com --profile production

# Step 6: Verify the setup
okta-cli users show jane.smith@company.com --profile production --output json
```

### User Offboarding

Complete workflow for offboarding a departing employee:

```bash
# Step 1: Deactivate the user account
okta-cli users deactivate john.doe@company.com --profile production

# Step 2: Clear all active sessions
okta-cli sessions clear john.doe@company.com --force --profile production

# Step 3: Remove from all groups
# First, get list of groups to check membership
okta-cli groups list --profile production --output json > groups.json

# Remove from specific groups (replace with actual group names)
okta-cli groups remove-user "Engineering Team" john.doe@company.com --profile production
okta-cli groups remove-user "Software Engineers" john.doe@company.com --profile production
okta-cli groups remove-user "All Employees" john.doe@company.com --profile production

# Step 4: Unassign applications
okta-cli users unassign-app john.doe@company.com "Company Portal" --profile production
okta-cli users unassign-app john.doe@company.com "Email System" --profile production
okta-cli users unassign-app john.doe@company.com "HR System" --profile production

# Step 5: Generate offboarding report
okta-cli users show john.doe@company.com --profile production --output json > offboarding-report.json
```

### User Role Changes

Workflow for changing a user's role or department:

```bash
# Example: Moving user from Engineering to Sales
USER_EMAIL="jane.smith@company.com"

# Step 1: Remove from current role groups
okta-cli groups remove-user "Engineering Team" $USER_EMAIL --profile production
okta-cli groups remove-user "Software Engineers" $USER_EMAIL --profile production

# Step 2: Add to new role groups
okta-cli groups add-user "Sales Team" $USER_EMAIL --profile production
okta-cli groups add-user "Account Executives" $USER_EMAIL --profile production

# Step 3: Update application assignments
okta-cli users unassign-app $USER_EMAIL "Development Tools" --profile production
okta-cli users assign-app $USER_EMAIL "CRM System" --profile production
okta-cli users assign-app $USER_EMAIL "Sales Analytics" --profile production

# Step 4: Verify changes
okta-cli users show $USER_EMAIL --profile production --output json
```

## Security Operations

### Security Monitoring

Daily security monitoring workflow:

```bash
# Check for failed login attempts in the last 24 hours
okta-cli logs failed-logins --days 1 --profile production --output json > failed-logins.json

# Monitor suspicious activities over the last week
okta-cli logs suspicious --days 7 --profile production --output json > suspicious-activities.json

# Analyze login patterns for anomalies
okta-cli logs search \
  --event-type "user.session.start" \
  --days 30 \
  --output csv \
  --profile production > login-patterns.csv

# Check MFA adoption rates
okta-cli factors stats --profile production --output json > mfa-adoption.json

# Generate security summary report
cat > security-report.md << EOF
# Daily Security Report - $(date)

## Failed Logins
$(cat failed-logins.json | jq length) failed login attempts in the last 24 hours

## Suspicious Activities
$(cat suspicious-activities.json | jq length) suspicious activities in the last week

## MFA Adoption
$(cat mfa-adoption.json | jq -r '.summary')
EOF
```

### Incident Response

Workflow for responding to a security incident:

```bash
# Example: Compromised user account
COMPROMISED_USER="suspected.user@company.com"

# Step 1: Immediately deactivate the user
okta-cli users deactivate $COMPROMISED_USER --profile production

# Step 2: Clear all active sessions
okta-cli sessions clear $COMPROMISED_USER --force --profile production

# Step 3: Reset all MFA factors
okta-cli factors list $COMPROMISED_USER --profile production --output json > user-factors.json
# Reset each factor (get factor IDs from the JSON)
okta-cli factors reset $COMPROMISED_USER FACTOR_ID --force --profile production

# Step 4: Generate incident report
okta-cli logs search \
  --event-type "user.session.start" \
  --days 30 \
  --output json \
  --profile production | \
  jq --arg user "$COMPROMISED_USER" '.[] | select(.actor.alternateId == $user)' > incident-logs.json

# Step 5: Force password reset when safe to reactivate
okta-cli users reset-password $COMPROMISED_USER --profile production
```

### Compliance Auditing

Monthly compliance audit workflow:

```bash
# Generate user access report
okta-cli users list --profile production --output json > all-users.json

# Generate group membership report
okta-cli groups list --profile production --output json > all-groups.json

# Generate application assignments report
okta-cli applications list --profile production --output json > all-applications.json

# Check for users without MFA
okta-cli factors stats --profile production --output json > mfa-report.json

# Generate privileged access report
okta-cli logs search \
  --event-type "user.account.privilege.grant" \
  --days 30 \
  --output json \
  --profile production > privilege-changes.json

# Create compliance summary
cat > compliance-report.md << EOF
# Monthly Compliance Report - $(date)

## User Statistics
- Total Users: $(cat all-users.json | jq length)
- Active Users: $(cat all-users.json | jq '[.[] | select(.status == "ACTIVE")] | length')
- Inactive Users: $(cat all-users.json | jq '[.[] | select(.status != "ACTIVE")] | length')

## Group Statistics
- Total Groups: $(cat all-groups.json | jq length)

## Application Statistics
- Total Applications: $(cat all-applications.json | jq length)
- Active Applications: $(cat all-applications.json | jq '[.[] | select(.status == "ACTIVE")] | length')

## MFA Adoption
$(cat mfa-report.json | jq -r '.summary')
EOF
```

## Application Management

### Application Provisioning

Workflow for provisioning a new application:

```bash
# Step 1: Create the application
okta-cli applications create \
  --name "New HR System" \
  --label "HR Management Portal" \
  --sign-on-mode SAML_2_0 \
  --profile production

# Step 2: Get application ID for further configuration
okta-cli applications show "New HR System" --profile production --output json > new-app.json
APP_ID=$(cat new-app.json | jq -r '.id')

# Step 3: Assign groups to the application
okta-cli applications list-groups $APP_ID --profile production
# Note: Group assignment may need to be done through Okta Admin Console

# Step 4: Generate application report
okta-cli applications show $APP_ID --profile production --output json > app-config.json
```

### Application User Management

Workflow for managing application user assignments:

```bash
APP_NAME="Company Portal"

# Step 1: List current users assigned to application
okta-cli applications list-users "$APP_NAME" --profile production --output json > current-users.json

# Step 2: Add new users to application
NEW_USERS=("jane.smith@company.com" "john.doe@company.com")
for user in "${NEW_USERS[@]}"; do
    okta-cli users assign-app "$user" "$APP_NAME" --profile production
done

# Step 3: Remove users from application
REMOVED_USERS=("old.user@company.com")
for user in "${REMOVED_USERS[@]}"; do
    okta-cli users unassign-app "$user" "$APP_NAME" --profile production
done

# Step 4: Verify changes
okta-cli applications list-users "$APP_NAME" --profile production --output json > updated-users.json
```

## Bulk Operations

### Bulk User Creation

Create multiple users from a CSV file:

```bash
# Create CSV file with user data
cat > new-users.csv << EOF
first_name,last_name,email,login,department
Alice,Johnson,alice.johnson@company.com,alice.johnson@company.com,Engineering
Bob,Wilson,bob.wilson@company.com,bob.wilson@company.com,Sales
Carol,Brown,carol.brown@company.com,carol.brown@company.com,Marketing
EOF

# Process each user
while IFS=, read -r first_name last_name email login department; do
    # Skip header row
    if [ "$first_name" != "first_name" ]; then
        echo "Creating user: $first_name $last_name"
        
        # Create user
        okta-cli users create \
          --first-name "$first_name" \
          --last-name "$last_name" \
          --email "$email" \
          --login "$login" \
          --profile production
        
        # Add to department group
        okta-cli groups add-user "$department" "$email" --profile production
        
        # Add to all employees group
        okta-cli groups add-user "All Employees" "$email" --profile production
        
        # Activate user
        okta-cli users activate "$email" --profile production
        
        echo "User $email created and activated"
    fi
done < new-users.csv
```

### Bulk Group Operations

Manage group memberships in bulk:

```bash
# Add multiple users to a group
GROUP_NAME="Engineering Team"
USERS=("alice@company.com" "bob@company.com" "carol@company.com")

for user in "${USERS[@]}"; do
    okta-cli groups add-user "$GROUP_NAME" "$user" --profile production
    echo "Added $user to $GROUP_NAME"
done

# Remove multiple users from a group
REMOVED_USERS=("old1@company.com" "old2@company.com")
for user in "${REMOVED_USERS[@]}"; do
    okta-cli groups remove-user "$GROUP_NAME" "$user" --profile production
    echo "Removed $user from $GROUP_NAME"
done

# Verify group membership
okta-cli groups list-users "$GROUP_NAME" --profile production --output json > group-members.json
```

### Bulk Data Export

Export all organizational data:

```bash
# Create export directory
mkdir -p okta-export/$(date +%Y%m%d)
cd okta-export/$(date +%Y%m%d)

# Export users
okta-cli users list --profile production --output json > users.json
okta-cli users list --profile production --output csv > users.csv

# Export groups
okta-cli groups list --profile production --output json > groups.json
okta-cli groups list --profile production --output csv > groups.csv

# Export applications
okta-cli applications list --profile production --output json > applications.json
okta-cli applications list --profile production --output csv > applications.csv

# Export security logs (last 30 days)
okta-cli logs search --days 30 --profile production --output json > logs.json

# Export MFA statistics
okta-cli factors stats --profile production --output json > mfa-stats.json

# Create summary report
cat > export-summary.txt << EOF
Okta Data Export Summary - $(date)

Files created:
- users.json ($(cat users.json | jq length) users)
- groups.json ($(cat groups.json | jq length) groups)
- applications.json ($(cat applications.json | jq length) applications)
- logs.json ($(cat logs.json | jq length) log entries)
- mfa-stats.json (MFA statistics)

CSV files also created for spreadsheet import.
EOF

# Compress export
cd ..
tar -czf okta-export-$(date +%Y%m%d).tar.gz $(date +%Y%m%d)/
```

## Integration with CI/CD

### GitHub Actions Integration

Example GitHub Actions workflow for user management:

```yaml
name: Okta User Management
on:
  workflow_dispatch:
    inputs:
      action:
        description: 'Action to perform'
        required: true
        type: choice
        options:
          - 'create-user'
          - 'deactivate-user'
          - 'security-report'
      user_email:
        description: 'User email (for create/deactivate)'
        required: false
      user_first_name:
        description: 'User first name (for create)'
        required: false
      user_last_name:
        description: 'User last name (for create)'
        required: false

jobs:
  okta-operations:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Create user
        if: github.event.inputs.action == 'create-user'
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          okta-cli users create \
            --first-name "${{ github.event.inputs.user_first_name }}" \
            --last-name "${{ github.event.inputs.user_last_name }}" \
            --email "${{ github.event.inputs.user_email }}" \
            --login "${{ github.event.inputs.user_email }}"
          
          okta-cli groups add-user "All Employees" "${{ github.event.inputs.user_email }}"
          okta-cli users activate "${{ github.event.inputs.user_email }}"
      
      - name: Deactivate user
        if: github.event.inputs.action == 'deactivate-user'
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          okta-cli users deactivate "${{ github.event.inputs.user_email }}"
          okta-cli sessions clear "${{ github.event.inputs.user_email }}" --force
      
      - name: Generate security report
        if: github.event.inputs.action == 'security-report'
        env:
          OKTA_DOMAIN: ${{ secrets.OKTA_DOMAIN }}
          OKTA_TOKEN: ${{ secrets.OKTA_TOKEN }}
        run: |
          okta-cli logs failed-logins --days 7 --output json > failed-logins.json
          okta-cli logs suspicious --days 7 --output json > suspicious.json
          okta-cli factors stats --output json > mfa-stats.json
      
      - name: Upload reports
        if: github.event.inputs.action == 'security-report'
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            failed-logins.json
            suspicious.json
            mfa-stats.json
```

### Jenkins Integration

Example Jenkins pipeline for Okta operations:

```groovy
pipeline {
    agent any
    
    environment {
        OKTA_DOMAIN = credentials('okta-domain')
        OKTA_TOKEN = credentials('okta-token')
    }
    
    parameters {
        choice(
            name: 'ACTION',
            choices: ['user-audit', 'security-report', 'bulk-create'],
            description: 'Action to perform'
        )
        text(
            name: 'USER_LIST',
            defaultValue: '',
            description: 'List of users for bulk operations (one per line)'
        )
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'okta-cli config health'
            }
        }
        
        stage('User Audit') {
            when { params.ACTION == 'user-audit' }
            steps {
                sh 'okta-cli users list --output json > users.json'
                sh 'okta-cli groups list --output json > groups.json'
                archiveArtifacts artifacts: '*.json', fingerprint: true
            }
        }
        
        stage('Security Report') {
            when { params.ACTION == 'security-report' }
            steps {
                sh 'okta-cli logs failed-logins --days 7 --output json > failed-logins.json'
                sh 'okta-cli logs suspicious --days 7 --output json > suspicious.json'
                sh 'okta-cli factors stats --output json > mfa-stats.json'
                archiveArtifacts artifacts: '*.json', fingerprint: true
            }
        }
        
        stage('Bulk Create') {
            when { params.ACTION == 'bulk-create' }
            steps {
                script {
                    def users = params.USER_LIST.split('\n')
                    users.each { user ->
                        def parts = user.split(',')
                        if (parts.length == 3) {
                            def firstName = parts[0].trim()
                            def lastName = parts[1].trim()
                            def email = parts[2].trim()
                            
                            sh "okta-cli users create --first-name '${firstName}' --last-name '${lastName}' --email '${email}' --login '${email}'"
                            sh "okta-cli groups add-user 'All Employees' '${email}'"
                            sh "okta-cli users activate '${email}'"
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            sh 'okta-cli config health'
        }
    }
}
```

## Monitoring and Automation

### Automated Health Checks

Daily health check script:

```bash
#!/bin/bash
# Daily Okta health check

LOG_FILE="/var/log/okta-health-check.log"
DATE=$(date)

echo "[$DATE] Starting Okta health check" >> $LOG_FILE

# Check configuration health
if okta-cli config health --profile production >> $LOG_FILE 2>&1; then
    echo "[$DATE] Configuration health: OK" >> $LOG_FILE
else
    echo "[$DATE] Configuration health: FAILED" >> $LOG_FILE
    exit 1
fi

# Check API connectivity
if okta-cli users list --limit 1 --profile production > /dev/null 2>&1; then
    echo "[$DATE] API connectivity: OK" >> $LOG_FILE
else
    echo "[$DATE] API connectivity: FAILED" >> $LOG_FILE
    exit 1
fi

# Check for failed logins
FAILED_COUNT=$(okta-cli logs failed-logins --days 1 --profile production --output json | jq length)
if [ "$FAILED_COUNT" -gt 100 ]; then
    echo "[$DATE] WARNING: High number of failed logins: $FAILED_COUNT" >> $LOG_FILE
fi

# Check MFA adoption
MFA_ADOPTION=$(okta-cli factors stats --profile production --output json | jq -r '.adoptionRate')
if [ "$MFA_ADOPTION" -lt 80 ]; then
    echo "[$DATE] WARNING: Low MFA adoption: $MFA_ADOPTION%" >> $LOG_FILE
fi

echo "[$DATE] Health check completed" >> $LOG_FILE
```

### Automated Reporting

Weekly automated reporting:

```bash
#!/bin/bash
# Weekly Okta report generator

REPORT_DIR="/reports/okta/$(date +%Y%m%d)"
mkdir -p $REPORT_DIR

# Generate user report
okta-cli users list --profile production --output json > $REPORT_DIR/users.json
okta-cli users list --profile production --output csv > $REPORT_DIR/users.csv

# Generate security report
okta-cli logs failed-logins --days 7 --profile production --output json > $REPORT_DIR/failed-logins.json
okta-cli logs suspicious --days 7 --profile production --output json > $REPORT_DIR/suspicious.json

# Generate MFA report
okta-cli factors stats --profile production --output json > $REPORT_DIR/mfa-stats.json

# Create summary
cat > $REPORT_DIR/summary.md << EOF
# Weekly Okta Report - $(date)

## User Statistics
- Total Users: $(cat $REPORT_DIR/users.json | jq length)
- Active Users: $(cat $REPORT_DIR/users.json | jq '[.[] | select(.status == "ACTIVE")] | length')

## Security Events
- Failed Logins: $(cat $REPORT_DIR/failed-logins.json | jq length)
- Suspicious Activities: $(cat $REPORT_DIR/suspicious.json | jq length)

## MFA Adoption
$(cat $REPORT_DIR/mfa-stats.json | jq -r '.summary')
EOF

# Compress report
tar -czf $REPORT_DIR.tar.gz -C /reports/okta $(date +%Y%m%d)

# Email report (if configured)
if [ -n "$REPORT_EMAIL" ]; then
    echo "Weekly Okta report attached" | mail -s "Weekly Okta Report" -a $REPORT_DIR.tar.gz $REPORT_EMAIL
fi
```

These use cases demonstrate the versatility and power of the Okta CLI for managing identity and access operations at scale. Adapt these examples to your specific organizational needs and security requirements.