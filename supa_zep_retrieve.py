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

# 3. Create a Zep client
client = Zep(api_key=api_key)

def main(group_id):
    # Retrieve all episodes from the group
    all_episodes = []
    page_token = None
    page_num = 1
    
    print(f"\n=== Retrieving episodes for group_id: {group_id} ===\n")
    print(f"Using Zep client with available methods: {[m for m in dir(client) if not m.startswith('_')]}")
    print(f"Graph methods: {[m for m in dir(client.graph) if not m.startswith('_')]}")
    
    if hasattr(client.graph, 'episode'):
        print(f"Episode methods: {[m for m in dir(client.graph.episode) if not m.startswith('_')]}")
    
    # First, check if the group exists by trying to add it (will fail with 'already exists' if it does)
    try:
        print(f"\nChecking if group exists: {group_id}")
        client.group.add(
            group_id=group_id,
            description=f"Test group {group_id}",
            name=f"Test group {group_id}"
        )
        print("Warning: Group did not exist and was created now. This might explain why no episodes were found.")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Group exists: {group_id}")
        else:
            print(f"Error checking group: {e}")
    
    # Try different methods to retrieve episodes
    try:
        while True:
            print(f"\nRetrieving episodes for group_id: {group_id} (page {page_num})")
            
            # Check if we have pagination parameters
            if page_token:
                print(f"Using page token: {page_token}")
                response = client.graph.episode.get_by_group_id(group_id=group_id, page_token=page_token)
            else:
                response = client.graph.episode.get_by_group_id(group_id=group_id)
            
            print(f"Response type: {type(response)}")
            print(f"Response attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
            
            # Get episodes from response
            episodes = response.episodes if hasattr(response, 'episodes') else []
            print(f"Found {len(episodes)} episodes in this page")
            all_episodes.extend(episodes)
            
            # Print response metadata if available
            if hasattr(response, 'metadata'):
                print(f"Response metadata: {response.metadata}")
            
            # Check if there are more pages
            if hasattr(response, 'next_page_token') and response.next_page_token:
                print(f"Next page token: {response.next_page_token}")
                page_token = response.next_page_token
                page_num += 1
            else:
                break
        
        # Print all UUIDs from the response for comparison
        if all_episodes:
            print("\nAll episode UUIDs:")
            for ep in all_episodes:
                print(f"  {ep.uuid_}")
    except Exception as e:
        print(f"Error retrieving episodes: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
    
    episodes = all_episodes

    # 6. Print out the results
    print(f"Found {len(episodes)} episodes in group '{group_id}'")
    if episodes:
        print(dir(episodes[0]))
        for i, episode in enumerate(episodes, 1):
            # Print some details about each episode
            print(f"Episode {i}:")
            print(f"  uuid: {episode.uuid_}")
            print(f"  content: {episode.content[:100]}...")  # Print first 100 chars of content
            print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve episodes from a Zep group.")
    parser.add_argument("--group_id", default="supa_zep_poc", help="The Zep group ID to retrieve episodes from (default: supa_zep_poc)")
    args = parser.parse_args()
    main(args.group_id)
