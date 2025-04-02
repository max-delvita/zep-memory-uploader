import os
import sys
import json
from dotenv import load_dotenv
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

def search_zep_group(group_id, query, limit=10, detailed=False):
    """
    Search for content in a specific Zep group.
    
    Args:
        group_id: The group ID to search in
        query: The search query string
        limit: Maximum number of results to return
        detailed: Whether to show detailed output
    """
    # Get API key from environment variables
    api_key = os.getenv('ZEP_API_KEY')
    
    if not api_key:
        print("Error: ZEP_API_KEY not found in environment variables")
        sys.exit(1)

    print(f"\n=== ZEP GROUP SEARCH ===")
    print(f"Group ID: {group_id}")
    print(f"Search Query: {query}")
    print(f"Result Limit: {limit}")
    print(f"======================\n")

    try:
        # Initialize Zep client
        client = Zep(api_key=api_key)
        
        # Perform search
        results = client.graph.search(
            group_id=group_id,
            query=query,
            limit=limit
        )
        
        # Print results
        print(f"Search Results: {results}")
        
        # Handle different response formats
        if hasattr(results, 'nodes') and results.nodes:
            print(f"\nFound {len(results.nodes)} matching nodes:")
            for i, node in enumerate(results.nodes, 1):
                print(f"\n--- Result {i} ---")
                if hasattr(node, 'content'):
                    print(f"Content: {node.content[:200]}..." if len(node.content) > 200 else f"Content: {node.content}")
                if hasattr(node, 'uuid_') and detailed:
                    print(f"UUID: {node.uuid_}")
                if hasattr(node, 'created_at') and detailed:
                    print(f"Created: {node.created_at}")
        elif isinstance(results, dict) and 'nodes' in results and results['nodes']:
            print(f"\nFound {len(results['nodes'])} matching nodes:")
            for i, node in enumerate(results['nodes'], 1):
                print(f"\n--- Result {i} ---")
                if 'content' in node:
                    print(f"Content: {node['content'][:200]}..." if len(node['content']) > 200 else f"Content: {node['content']}")
                if 'uuid_' in node and detailed:
                    print(f"UUID: {node['uuid_']}")
                if 'created_at' in node and detailed:
                    print(f"Created: {node['created_at']}")
        else:
            print("\nNo results found or unexpected response format.")
            print("Raw response structure:")
            print(f"Type: {type(results)}")
            print(f"Attributes: {dir(results)}")
            
    except Exception as e:
        print(f"Error searching Zep group: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python search_group.py <group_id> <search_query> [result_limit] [--detailed]")
        print("Example: python search_group.py test_group_123 'important information' 20 --detailed")
        sys.exit(1)
    
    group_id = sys.argv[1]
    query = sys.argv[2]
    
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 10
    detailed = "--detailed" in sys.argv
    
    search_zep_group(group_id, query, limit, detailed) 