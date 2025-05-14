import os
import argparse
from dotenv import load_dotenv
from supabase import create_client

# 1. Load environment variables
load_dotenv()

# 2. Connect to Supabase
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

def main(agent_id):
    # Table info
    TABLE_NAME = "embeddings"  # Change this to your table

    supabase = get_supabase_client()

    # Fetch rows for the specified agent_id
    response = (
        supabase.table(TABLE_NAME)
        .select("id, content")
        .eq("agent_id", agent_id)
        .execute()
    )
    rows = response.data

    if not rows:
        print(f"No rows found for agent_id {agent_id}.")
        return

    # Count rows with content exceeding 10,000 characters
    large_content_rows = []
    for row in rows:
        content = row.get("content", "")
        if content and len(content) > 10000:
            large_content_rows.append((row["id"], len(content)))

    # Print results
    print(f"Total rows for agent_id {agent_id}: {len(rows)}")
    print(f"Rows with content exceeding 10,000 characters: {len(large_content_rows)}")
    
    if large_content_rows:
        print("\nDetails of rows with large content:")
        for row_id, content_length in large_content_rows:
            print(f"Row ID: {row_id}, Content length: {content_length} characters")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for rows with content exceeding 10,000 characters.")
    parser.add_argument("agent_id", help="The agent_id to check rows for")
    args = parser.parse_args()
    main(args.agent_id)
