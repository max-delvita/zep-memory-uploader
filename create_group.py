import os
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
api_key = os.getenv('ZEP_API_KEY')

client = Zep(
    api_key=api_key,
)

# Create a group
client.group.add(
    group_id="demo_group", 
    description="Demo Sales Content Creator", 
    name="Demo Sales Content Creator"
)
 