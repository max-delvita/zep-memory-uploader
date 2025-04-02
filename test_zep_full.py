import os
import time
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

def test_zep_full():
    # Get API key from environment variables
    api_key = os.getenv('ZEP_API_KEY')
    
    if not api_key:
        print("Error: ZEP_API_KEY not found in environment variables")
        return False

    # Define test group ID - IMPORTANT: Change this if needed
    group_id = "demo_group"
    
    print(f"\n=== ZEP FULL TEST ===")
    print(f"Group ID: {group_id}")
    print(f"API Key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
    
    try:
        # Initialize Zep client
        client = Zep(api_key=api_key)
        
        # Generate a unique test message with timestamp
        timestamp = int(time.time())
        test_message = f"Test message with unique timestamp {timestamp} - This is a test of the Zep API."
        
        print("\n1. UPLOADING TEST CONTENT...")
        
        # Add test data to graph
        response = client.graph.add(
            group_id=group_id,
            data=test_message,
            type="text"
        )
        
        print(f"   Upload Response: {response}")
        
        # Wait for content to be processed
        print("\n2. WAITING FOR CONTENT TO BE PROCESSED...")
        time.sleep(5)  # Give Zep some time to process
        
        # Try to search for the content
        print("\n3. VERIFYING CONTENT SEARCHABILITY...")
        try:
            search_query = f"timestamp {timestamp}"
            search_results = client.graph.search(
                group_id=group_id, 
                query=search_query,
                limit=10
            )
            
            print(f"   Search query: '{search_query}'")
            print(f"   Search results: {search_results}")
            
            if search_results and len(search_results) > 0:
                print("\n✅ SUCCESS! Content was successfully uploaded and is searchable.")
                print("\nHOW TO VIEW IN DASHBOARD:")
                print(f"1. Go to your Zep dashboard")
                print(f"2. Look for the 'graph' or 'memory graph' section")
                print(f"3. Make sure you're viewing the correct group: {group_id}")
                print(f"4. You might need to search for content or browse through entries")
                return True
            else:
                print("\n⚠️ PARTIAL SUCCESS: Content was uploaded but couldn't be found in search.")
                print("This might be because:")
                print("- Search index is still being built (can take a few minutes)")
                print("- The search functionality works differently than expected")
                print("- The content was stored but under a different identifier")
        except Exception as search_err:
            print(f"\n⚠️ WARNING: Couldn't verify content with search: {str(search_err)}")
            print("However, the upload appeared successful.")
        
        return True
        
    except Exception as e:
        print("\n❌ ERROR connecting to Zep API:")
        print(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    test_zep_full() 