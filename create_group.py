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
    group_id="mip_group", 
    description="Modern Indian Parent Knowledge Group.", 
    name="mip_group"
)
 