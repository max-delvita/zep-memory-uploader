#!/bin/bash

# Load API key from .env file
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found"
  exit 1
fi

# Check if API key is set
if [ -z "$ZEP_API_KEY" ]; then
  echo "Error: ZEP_API_KEY not found in .env file"
  exit 1
fi

# Timestamp for unique group creation
TIMESTAMP=$(date +%s)
RANDOM_ID=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom | head -c 6)
GROUP_ID=${1:-"curl_test_${TIMESTAMP}_${RANDOM_ID}"}

# Content to upload
CONTENT=${2:-"This is a test message sent via curl at $(date)"}

echo "=== ZEP CURL UPLOAD ==="
echo "Group ID: $GROUP_ID"
echo "API Key: ${ZEP_API_KEY:0:5}...${ZEP_API_KEY: -5}"
echo "Content: $CONTENT"
echo "======================="

# Create JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "group_id": "$GROUP_ID",
  "data": "$CONTENT",
  "type": "text"
}
EOF
)

# Make the API call
echo -e "\nSending request to Zep API..."
curl -s -X POST "https://api.getzep.com/api/v2/graph" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ZEP_API_KEY" \
  -d "$JSON_PAYLOAD" | jq .

# Show instructions
echo -e "\n=== DONE ==="
echo "Data uploaded to group: $GROUP_ID"
echo "To search this group:"
echo "python search_group.py $GROUP_ID \"$CONTENT\""
echo "============" 