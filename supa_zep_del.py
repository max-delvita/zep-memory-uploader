from dotenv import load_dotenv
import os
import argparse
from zep_cloud.client import Zep

# 1. Load environment variables (for your API key)
load_dotenv()

# 2. Get your Zep API key from the environment
api_key = os.getenv("ZEP_API_KEY")
if not api_key:
    raise ValueError("ZEP_API_KEY not found in environment variables.")

# 3. Parse the UUID from the command line
parser = argparse.ArgumentParser(description="Delete a Zep episode by UUID.")
parser.add_argument("uuid", help="The UUID of the episode to delete")
args = parser.parse_args()

# 4. Create a Zep client
client = Zep(api_key=api_key)

# 5. Delete the episode
try:
    response = client.graph.episode.delete(uuid_=args.uuid)
    print(f"Episode {args.uuid} deleted. Message: {response.message}")
except Exception as e:
    print(f"Error deleting episode {args.uuid}: {e}")
