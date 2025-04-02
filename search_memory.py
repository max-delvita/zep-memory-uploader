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

try:
    # Get all sessions in the group
    sessions = client.memory.get_sessions(group_id="group_test")
    
    print("\nSessions in group 'group_test':")
    for session in sessions:
        print(f"\nSession ID: {session.session_id}")
        
        # Get all messages in this session
        messages = client.memory.get_messages(session_id=session.session_id)
        
        print("Messages in this session:")
        for msg in messages:
            print(f"Role: {msg.role}")
            print(f"Content: {msg.content}")
            print("---")

except Exception as e:
    print(f"Error: {str(e)}")
    raise  # This will show the full error traceback 