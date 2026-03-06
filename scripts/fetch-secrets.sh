#!/bin/bash
# Fetch secrets from AWS Secrets Manager and write to .env file
# Usage: ./fetch-secrets.sh <SECRET_ARN> <REGION> <OUTPUT_FILE>

set -e

SECRET_ARN=$1
REGION=$2
OUTPUT_FILE=$3

if [ -z "$SECRET_ARN" ] || [ -z "$REGION" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: ./fetch-secrets.sh <SECRET_ARN> <REGION> <OUTPUT_FILE>"
    exit 1
fi

# Fetch secrets from Secrets Manager and convert to .env format
aws secretsmanager get-secret-value \
    --secret-id "$SECRET_ARN" \
    --region "$REGION" \
    --query SecretString \
    --output text | jq -r 'to_entries | .[] | "\(.key)=\(.value)"' > "$OUTPUT_FILE"

echo "Secrets written to $OUTPUT_FILE"
