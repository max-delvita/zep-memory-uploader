import os
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

def test_zep_connection():
    # Get API key from environment variables
    api_key = os.getenv('ZEP_API_KEY')
    
    if not api_key:
        print("Error: ZEP_API_KEY not found in environment variables")
        return False

    # Define test group ID
    group_id = "demo_group"  # Change this to your desired group ID
    
    print(f"\n=== ZEP CONNECTION TEST ===")
    print(f"Group ID: {group_id}")
    print(f"API Key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
    
    try:
        # Initialize Zep client
        client = Zep(api_key=api_key)
        
        # Test data to add
        test_data = "This is a test message from the Zep connection test script."
        
        # Add test data to graph
        response = client.graph.add(
            group_id=group_id,
            data=test_data,
            type="text"
        )
        
        print("\nSuccess! Connection to Zep API working properly.")
        print(f"Response: {response}")
        print(f"Content successfully added to group: {group_id}")
        return True
        
    except Exception as e:
        print("\nError connecting to Zep API:")
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_zep_connection() 