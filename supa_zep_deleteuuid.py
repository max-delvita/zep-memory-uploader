#!/usr/bin/env python3
"""
Script to clear zep_uuid values in the embeddings table for a specific agent_id.
"""

import os
import argparse
import sys
from typing import Optional, Dict, Any
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client using environment variables."""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")
    
    return create_client(supabase_url, supabase_key)

def clear_zep_uuids(agent_id: str, supabase_client: Optional[Client] = None) -> Dict[str, Any]:
    """
    Clear zep_uuid values in the embeddings table for a specific agent_id.
    
    Args:
        agent_id: The agent_id to clear zep_uuids for
        supabase_client: Optional Supabase client (for testing)
        
    Returns:
        Dict containing operation results
    """
    # Initialize Supabase client if not provided
    if supabase_client is None:
        supabase_client = get_supabase_client()
    
    try:
        # First, count how many rows will be affected
        count_response = (
            supabase_client.table("embeddings")
            .select("*", count='exact')
            .eq("agent_id", agent_id)
            .execute()
        )
        
        affected_count = count_response.count if hasattr(count_response, 'count') else 0
        
        if affected_count == 0:
            print(f"No records found for agent_id: {agent_id}")
            return {"status": "success", "message": "No records found", "count": 0}
            
        print(f"Found {affected_count} records for agent_id: {agent_id}")
        print("Proceeding to clear zep_uuids...")
        
        # Update all rows where agent_id matches, setting zep_uuid to NULL
        response = (
            supabase_client.table("embeddings")
            .update({"zep_uuid": None})
            .eq("agent_id", agent_id)
            .execute()
        )
        
        result = {
            "status": "success",
            "message": f"Cleared zep_uuids for agent_id: {agent_id}",
            "count": affected_count,
            "data": response.data
        }
        
        print(f"Successfully cleared zep_uuids for agent_id: {agent_id}")
        print(f"Number of rows updated: {affected_count}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error clearing zep_uuids: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg, "error": str(e)}


def test_clear_zep_uuids(agent_id: str) -> None:
    """
    Test function to verify the clear_zep_uuids function works.
    This will run in dry-run mode first to show what would be updated.
    """
    print("\n=== Starting Test ===")
    print(f"Testing clear_zep_uuids for agent_id: {agent_id}")
    
    # First, do a dry run to see what would be updated
    print("\n[DRY RUN] Checking records that would be updated...")
    try:
        supabase = get_supabase_client()
        
        # Get a sample of the data before update
        sample = (
            supabase.table("embeddings")
            .select("id, agent_id, zep_uuid")
            .eq("agent_id", agent_id)
            .limit(3)
            .execute()
        )
        
        if not sample.data:
            print(f"No records found for agent_id: {agent_id}")
            return
            
        print("\nSample of records to be updated:")
        for i, record in enumerate(sample.data, 1):
            print(f"  {i}. ID: {record.get('id')}, agent_id: {record.get('agent_id')}, "
                  f"zep_uuid: {record.get('zep_uuid')}")
        
        # Ask for confirmation
        confirm = input("\nDo you want to proceed with the update? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled by user.")
            return
            
        # Perform the actual update
        print("\nPerforming update...")
        result = clear_zep_uuids(agent_id, supabase)
        
        if result.get("status") == "success":
            print("\n=== Test Successful ===")
            print(f"Updated {result.get('count', 0)} records.")
        else:
            print("\n=== Test Failed ===")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n=== Test Failed ===")
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clear zep_uuid values for a specific agent_id")
    parser.add_argument("agent_id", help="The agent_id to clear zep_uuids for")
    parser.add_argument("--test", action="store_true", help="Run in test mode (shows what would be updated)")
    args = parser.parse_args()
    
    if args.test:
        test_clear_zep_uuids(args.agent_id)
    else:
        result = clear_zep_uuids(args.agent_id)
        if result.get("status") != "success":
            sys.exit(1)