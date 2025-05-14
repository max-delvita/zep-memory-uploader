import os
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('ZEP_API_KEY')
if not api_key:
    print("Error: ZEP_API_KEY not found in environment variables")
    exit(1)

# Create Zep client
client = Zep(api_key=api_key)

# Test upload
group_id = "test_simple_group"
test_content = "This is a simple test message to verify the Zep API upload functionality."

try:
    # Simple upload
    response = client.graph.add(
        group_id=group_id,
        data=test_content,
        type="text"
    )
    print(f"\nUpload successful!")
    print(f"Response: {response}")
    
    # Try to search for it
    print("\nSearching for uploaded content...")
    results = client.graph.search(
        group_id=group_id,
        query="simple test message",
        limit=1
    )
    print(f"Search results: {results}")
    
except Exception as e:
    print(f"Error: {str(e)}")