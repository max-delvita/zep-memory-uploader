import os
import argparse
from dotenv import load_dotenv
from zep_cloud.client import Zep
from zep_cloud.errors.bad_request_error import BadRequestError

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv('ZEP_API_KEY')

client = Zep(
    api_key=api_key,
)

def main(group_id):
    try:
        # Create a group
        print(f"Creating group with ID: {group_id}")
        client.group.add(
            group_id=group_id, 
            description=f"zep group for agent_id {group_id}", 
            name=f"Zep group for agent_id {group_id}"
        )
        print(f"Successfully created group with ID: {group_id}")
    except BadRequestError as e:
        if "group already exists" in str(e).lower():
            print(f"Group with ID {group_id} already exists.")
        else:
            print(f"Error creating group: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a Zep group for an agent_id.")
    parser.add_argument("group_id", help="The group_id to create")
    args = parser.parse_args()
    main(args.group_id)