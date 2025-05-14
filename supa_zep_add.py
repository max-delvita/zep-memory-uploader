import os
import argparse
import json
from dotenv import load_dotenv
from supabase import create_client
from zep_cloud import EpisodeData
from zep_cloud.client import Zep
from zep_cloud import EpisodeData

# 1. Load environment variables
load_dotenv()

# 2. Connect to Supabase
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

# 3. Connect to Zep
def get_zep_client():
    api_key = os.getenv("ZEP_API_KEY")
    return Zep(api_key=api_key)

def main(agent_id, group_id):
    # Table and group info
    TABLE_NAME = "embeddings"  # Change this to your table

    supabase = get_supabase_client()
    zep = get_zep_client()

    # 4. Fetch rows that haven't been uploaded yet (zep_uuid is null)
    response = (
        supabase.table(TABLE_NAME)
        .select("*")
        .eq("agent_id", agent_id)
        .is_("zep_uuid", None)
        .execute()
    )
    rows = response.data

    if not rows:
        print("No new rows to process for this agent_id.")
        return

    # 5. Prepare episodes for Zep
    episodes = []
    row_id_map = []  # To keep track of which row matches which episode
    row_part_map = []  # To track which parts belong to which row
    MAX_CONTENT_SIZE = 9500  # Slightly less than the 10000 character limit to be safe
    
    for row in rows:
        if not row.get("content"):
            continue  # Skip empty content
            
        content = row["content"]
        # Check if content exceeds the maximum size
        if len(content) > MAX_CONTENT_SIZE:
            # Split the content into multiple parts
            parts = [content[i:i+MAX_CONTENT_SIZE] for i in range(0, len(content), MAX_CONTENT_SIZE)]
            print(f"Content for row {row['id']} split into {len(parts)} parts due to size ({len(content)} characters)")
            
            # Add each part as a separate episode
            for i, part in enumerate(parts):
                part_indicator = f" [Part {i+1}/{len(parts)}]" if len(parts) > 1 else ""
                episodes.append(EpisodeData(
                    data=part + part_indicator,
                    type="text"
                ))
                row_id_map.append(row["id"])
                row_part_map.append(i+1)  # Part number (1-based)
        else:
            # Content is within size limits, add it normally
            episodes.append(EpisodeData(
                data=content,
                type="text"
            ))
            row_id_map.append(row["id"])
            row_part_map.append(0)  # Not split
    
    # 6. Send episodes in smaller batches to Zep
    # Zep has a limit on the number of episodes per batch
    BATCH_SIZE = 5  # Adjust this based on Zep's limits
    total_processed = 0
    
    for i in range(0, len(episodes), BATCH_SIZE):
        batch_episodes = episodes[i:i+BATCH_SIZE]
        batch_row_ids = row_id_map[i:i+BATCH_SIZE]
        
        print(f"Processing batch {i//BATCH_SIZE + 1} with {len(batch_episodes)} episodes")
        
        # Send this batch to Zep
        result = zep.graph.add_batch(
            episodes=batch_episodes,
            group_id=group_id
        )
        
        # 7. Collect UUIDs and update Supabase for this batch
        batch_part_nums = row_part_map[i:i+BATCH_SIZE]
        
        # Group UUIDs by row_id to handle split content
        row_uuid_map = {}
        for row_id, part_num, episode_result in zip(batch_row_ids, batch_part_nums, result):
            zep_uuid = episode_result.uuid_
            
            if row_id not in row_uuid_map:
                row_uuid_map[row_id] = []
            
            # Store the UUID along with its part number
            row_uuid_map[row_id].append((part_num, zep_uuid))
            total_processed += 1
        
        # Update Supabase with the UUIDs
        for row_id, uuid_parts in row_uuid_map.items():
            # Sort by part number to ensure correct order
            uuid_parts.sort()
            
            if len(uuid_parts) == 1 and uuid_parts[0][0] == 0:
                # Single part, not split
                zep_uuid = uuid_parts[0][1]
                supabase.table(TABLE_NAME).update({"zep_uuid": zep_uuid}).eq("id", row_id).execute()
                print(f"Updated row {row_id} with Zep UUID {zep_uuid}")
            else:
                # Multiple parts, store as JSON array
                uuids = [part[1] for part in uuid_parts]
                uuid_json = json.dumps(uuids)
                supabase.table(TABLE_NAME).update({"zep_uuid": uuid_json}).eq("id", row_id).execute()
                print(f"Updated row {row_id} with {len(uuids)} Zep UUIDs: {uuid_json[:50]}{'...' if len(uuid_json) > 50 else ''}")
                print(f"  Parts: {', '.join([str(part[0]) for part in uuid_parts])}")
                print(f"  First UUID: {uuids[0]}")
                print(f"  Last UUID: {uuids[-1]}")
                print(f"  Total characters: {sum([len(ep.data) for ep in batch_episodes if row_id_map[episodes.index(ep)] == row_id])}")
                print()

    print("All rows processed and updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process embeddings for a specific agent_id.")
    parser.add_argument("agent_id", help="The agent_id to process rows for")
    parser.add_argument("--group_id", default="supa_zep_poc", help="The Zep group ID to use (default: supa_zep_poc)")
    args = parser.parse_args()
    main(args.agent_id, args.group_id)