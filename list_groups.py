import os
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables
load_dotenv()

# Get API key from environment variables
api_key = os.getenv("ZEP_API_KEY")
if not api_key:
    raise ValueError("ZEP_API_KEY not found in environment variables.")

# Create a Zep client
client = Zep(api_key=api_key)

def main():
    try:
        # List all groups
        print("Listing all available groups in Zep:")
        response = client.group.list()
        
        if hasattr(response, 'groups') and response.groups:
            print(f"Found {len(response.groups)} groups:")
            for i, group in enumerate(response.groups, 1):
                print(f"{i}. Group ID: {group.group_id}")
                print(f"   Name: {group.name}")
                print(f"   Description: {group.description}")
                print()
        else:
            print("No groups found.")
    except Exception as e:
        print(f"Error listing groups: {e}")

if __name__ == "__main__":
    main()
