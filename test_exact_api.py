import os
import time
import uuid
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv('ZEP_API_KEY')

if not api_key:
    print("Error: ZEP_API_KEY not found in environment variables")
    exit(1)

print(f"Using API key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")

# Initialize client exactly as shown in the API docs
client = Zep(
    api_key=api_key,
)

# Create a unique group ID using timestamp and random UUID
timestamp = int(time.time())
unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of a UUID
group_id = f"test_group_{timestamp}_{unique_id}"

print(f"Created new unique group ID: {group_id}")
print(f"⚠️ IMPORTANT: Save this group ID to check your content later!")

# Test data
test_data = f"This is a test message in a new group: {group_id}. Created at {timestamp}."

try:
    # Call graph.add with the new group ID
    response = client.graph.add(
        group_id=group_id,
        data=test_data,
        type="text"
    )
    
    print(f"Success! Response: {response}")
    print(f"Content has been added to NEW group: {group_id}")
    print(f"Look for this group ID in your Zep dashboard")
    
except Exception as e:
    print(f"Error: {str(e)}") 