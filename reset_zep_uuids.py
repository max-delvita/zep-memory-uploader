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

def main(agent_id, reset_all=False):
    # Table info
    TABLE_NAME = "embeddings"  # Change this to your table

    supabase = get_supabase_client()

    # Fetch rows that have been uploaded (zep_uuid is not null)
    query = (
        supabase.table(TABLE_NAME)
        .select("id, zep_uuid")
        .eq("agent_id", agent_id)
        .not_.is_("zep_uuid", None)
    )
    
    # Apply limit if not resetting all
    if not reset_all:
        query = query.limit(10)
    
    response = query.execute()
    rows = response.data

    if not rows:
        print(f"No rows with zep_uuid found for agent_id {agent_id}.")
        return

    print(f"Found {len(rows)} rows with zep_uuid for agent_id {agent_id}.")
    
    # Reset zep_uuid to null for these rows
    for row in rows:
        row_id = row["id"]
        old_uuid = row["zep_uuid"]
        
        # Update the row in Supabase, setting zep_uuid to null
        supabase.table(TABLE_NAME).update({"zep_uuid": None}).eq("id", row_id).execute()
        print(f"Reset zep_uuid for row {row_id} (was: {old_uuid})")

    print(f"Reset zep_uuid for {len(rows)} rows.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset zep_uuid values for a specific agent_id.")
    parser.add_argument("agent_id", help="The agent_id to reset zep_uuid values for")
    parser.add_argument("--all", action="store_true", help="Reset ALL zep_uuid values for this agent_id")
    args = parser.parse_args()
    main(args.agent_id, args.all)
