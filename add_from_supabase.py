import os
import json
from dotenv import load_dotenv
from supabase import create_client
from zep_cloud.client import Zep

# Load environment variables from .env file
load_dotenv()

def get_supabase_client():
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")
    
    return create_client(supabase_url, supabase_key)

def get_zep_client():
    api_key = os.getenv('ZEP_API_KEY')
    
    if not api_key:
        raise ValueError("Missing ZEP_API_KEY in environment variables")
    
    return Zep(api_key=api_key)

def format_content_with_metadata(chunk):
    """Format content with metadata as a header"""
    metadata = {
        "batch_name": chunk.get("batch_name"),
        "chunk_number": chunk.get("chunk_number"),
        "title": chunk.get("title"),
        "summary": chunk.get("summary"),
        "document_id": chunk.get("id")
    }
    
    # Create a header with metadata
    header = f"[METADATA]\n{json.dumps(metadata, indent=2)}\n[CONTENT]\n"
    
    # Get the content
    content = chunk.get("content", "").strip()
    
    # Combine header and content
    return f"{header}{content}"

def process_chunks(table_name="mip_training_data", group_id="some-group-id"):
    try:
        # Initialize clients
        supabase = get_supabase_client()
        zep_client = get_zep_client()
        
        # Fetch all records from the specified table
        response = supabase.table(table_name).select("*").order('chunk_number').execute()
        chunks = response.data
        
        if not chunks:
            print(f"No records found in table '{table_name}'")
            return
        
        print(f"Found {len(chunks)} chunks to process...")
        
        # Group chunks by batch_name to maintain document context
        chunks_by_batch = {}
        for chunk in chunks:
            batch_name = chunk.get('batch_name', 'unknown')
            if batch_name not in chunks_by_batch:
                chunks_by_batch[batch_name] = []
            chunks_by_batch[batch_name].append(chunk)
        
        # Process each batch's chunks in order
        for batch_name, batch_chunks in chunks_by_batch.items():
            print(f"\nProcessing batch: {batch_name}")
            
            # Sort chunks by chunk_number
            batch_chunks.sort(key=lambda x: x.get('chunk_number', 0))
            
            for i, chunk in enumerate(batch_chunks, 1):
                try:
                    if not chunk.get('content'):
                        print(f"Warning: Empty content in chunk {chunk.get('chunk_number')} of {batch_name}")
                        continue
                    
                    # Format content with metadata
                    formatted_content = format_content_with_metadata(chunk)
                    
                    # Add to Zep
                    response = zep_client.graph.add(
                        group_id=group_id,
                        data=formatted_content,
                        type="text"
                    )
                    print(f"Chunk {i}/{len(batch_chunks)} from {batch_name} added to group '{group_id}'")
                    print(f"Chunk size: {len(formatted_content)} characters")
                    
                except Exception as e:
                    print(f"Error processing chunk {i}/{len(batch_chunks)} from {batch_name}: {str(e)}")
                    print(f"Failed chunk details: ID={chunk.get('id')}, chunk_number={chunk.get('chunk_number')}")
                    raise
        
        print(f"\nCompleted! All chunks from {len(chunks_by_batch)} batches have been processed.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Using the actual table name from the schema
    TABLE_NAME = "mip_training_data"  # Using the correct table name from the schema
    GROUP_ID = "mip_group"  # The group ID we want to use
    
    process_chunks(TABLE_NAME, GROUP_ID)