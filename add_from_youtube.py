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

def generate_youtube_urls(video_id, start_time=None, end_time=None):
    """Generate YouTube URLs with optional timestamps"""
    base_url = f"https://www.youtube.com/watch?v={video_id}"
    
    if start_time is None:
        return {
            "video_url": base_url
        }
    
    # Convert float timestamps to integers for URL
    start_seconds = int(start_time)
    
    urls = {
        "video_url": base_url,
        "timestamped_url": f"{base_url}&t={start_seconds}"
    }
    
    if end_time is not None:
        end_seconds = int(end_time)
        urls["clip_url"] = f"{base_url}&start={start_seconds}&end={end_seconds}"
    
    return urls

def format_youtube_content(chunk):
    """Format YouTube content with metadata as a header"""
    # Generate YouTube URLs
    urls = generate_youtube_urls(
        chunk.get("video_id"),
        chunk.get("start_time"),
        chunk.get("end_time")
    )
    
    metadata = {
        "video_id": chunk.get("video_id"),
        "chunk_number": chunk.get("chunk_number"),
        "title": chunk.get("title"),
        "summary": chunk.get("summary"),
        "start_time": chunk.get("start_time"),
        "end_time": chunk.get("end_time"),
        "chunk_id": chunk.get("id"),
        "urls": urls,
        "original_metadata": chunk.get("metadata", {})
    }
    
    # Create a header with metadata
    header = f"[YOUTUBE_METADATA]\n{json.dumps(metadata, indent=2)}\n[CONTENT]\n"
    
    # Get the content
    content = chunk.get("content", "").strip()
    
    # Format timestamp information with URL
    timestamp_info = (
        f"\n[TIMESTAMP] {format_timestamp(chunk.get('start_time', 0))} - {format_timestamp(chunk.get('end_time', 0))}\n"
        f"[URL] {urls.get('timestamped_url', urls['video_url'])}"
    )
    
    # Combine header, content, and timestamp
    return f"{header}{content}{timestamp_info}"

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    if seconds is None:
        return "00:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def process_youtube_chunks(table_name="youtube_video_chunks", group_id="group_test"):
    try:
        # Initialize clients
        supabase = get_supabase_client()
        zep_client = get_zep_client()
        
        # Fetch all records from the specified table
        # Order by video_id first, then chunk_number
        response = supabase.table(table_name).select("*").order("video_id").order("chunk_number").execute()
        chunks = response.data
        
        if not chunks:
            print(f"No records found in table '{table_name}'")
            return
        
        print(f"Found {len(chunks)} chunks to process...")
        
        # Group chunks by video_id to maintain video context
        chunks_by_video = {}
        for chunk in chunks:
            video_id = chunk.get('video_id', 'unknown')
            if video_id not in chunks_by_video:
                chunks_by_video[video_id] = []
            chunks_by_video[video_id].append(chunk)
        
        # Process each video's chunks in order
        for video_id, video_chunks in chunks_by_video.items():
            print(f"\nProcessing video: {video_id}")
            print(f"Video URL: https://www.youtube.com/watch?v={video_id}")
            
            # Sort chunks by chunk_number
            video_chunks.sort(key=lambda x: x.get('chunk_number', 0))
            
            for i, chunk in enumerate(video_chunks, 1):
                try:
                    if not chunk.get('content'):
                        print(f"Warning: Empty content in chunk {chunk.get('chunk_number')} of video {video_id}")
                        continue
                    
                    # Format content with metadata
                    formatted_content = format_youtube_content(chunk)
                    
                    # Add to Zep
                    response = zep_client.graph.add(
                        group_id=group_id,
                        data=formatted_content,
                        type="text"
                    )
                    print(f"Chunk {i}/{len(video_chunks)} from video {video_id} added to group '{group_id}'")
                    print(f"Time range: {format_timestamp(chunk.get('start_time'))} - {format_timestamp(chunk.get('end_time'))}")
                    print(f"URL: https://www.youtube.com/watch?v={video_id}&t={int(chunk.get('start_time', 0))}")
                    print(f"Chunk size: {len(formatted_content)} characters")
                    
                except Exception as e:
                    print(f"Error processing chunk {i}/{len(video_chunks)} from video {video_id}: {str(e)}")
                    print(f"Failed chunk details: ID={chunk.get('id')}, chunk_number={chunk.get('chunk_number')}")
                    raise
        
        print(f"\nCompleted! All chunks from {len(chunks_by_video)} videos have been processed.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Using the actual table name from the schema
    TABLE_NAME = "youtube_video_chunks"
    GROUP_ID = "group_test"  # Using the existing group_test group
    
    process_youtube_chunks(TABLE_NAME, GROUP_ID) 