import os
import sys
import json
from dotenv import load_dotenv
from zep_cloud.client import Zep
from datetime import datetime
from config import ZEP_BASE_URL, DEFAULT_GROUP_ID, MAX_CHUNK_SIZE

# Load environment variables from .env file
load_dotenv()

def chunk_text(text, chunk_size=MAX_CHUNK_SIZE):
    """Split text into chunks of specified size, trying to break at sentence boundaries."""
    chunks = []
    current_chunk = ""
    
    # Split text into sentences (roughly)
    sentences = text.replace('\n', ' ').split('.')
    
    for sentence in sentences:
        sentence = sentence.strip() + '.'  # Add back the period
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += ' ' + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        sys.exit(1)

def format_content_with_metadata(chunk, chunk_number, file_path=None):
    """Format content with metadata as a header"""
    metadata = {
        "file_path": file_path if file_path else "direct_input",
        "chunk_number": chunk_number,
        "title": os.path.basename(file_path) if file_path else "Direct Input",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Create a header with metadata
    header = f"[METADATA]\n{json.dumps(metadata, indent=2)}\n[CONTENT]\n"
    
    # Combine header and content
    return f"{header}{chunk}"

def format_youtube_content(chunk, source_url, timestamp=None):
    """Format content from YouTube with source information."""
    return (
        f"YOUTUBE_VIDEO\n"
        f"URL: {source_url}\n"
        f"TIMESTAMP: {timestamp if timestamp else 'start'}\n"
        f"CONTENT: {chunk}\n"
        f"SOURCE: {source_url}"
    )

def add_text_to_graph(text_content, group_id=DEFAULT_GROUP_ID, file_path=None, source_url=None, timestamp=None):
    # Get API key from environment variables
    api_key = os.getenv('ZEP_API_KEY')
    
    if not api_key:
        print("Error: ZEP_API_KEY not found in environment variables")
        sys.exit(1)

    client = Zep(
        api_key=api_key,
        api_url=ZEP_BASE_URL
    )
    
    # Split content into chunks
    chunks = chunk_text(text_content)
    total_chunks = len(chunks)
    
    print(f"Processing {total_chunks} chunks...")

    # If this is YouTube content, first add the source as a searchable node
    if source_url and "youtube.com" in source_url:
        try:
            # Create a dedicated URL node
            url_node = (
                f"YOUTUBE_VIDEO_URL\n"
                f"URL: {source_url}\n"
                f"This is a YouTube video that can be accessed at: {source_url}\n"
                f"To watch this video, visit: {source_url}"
            )
            
            client.graph.add(
                group_id=group_id,
                data=url_node,
                type="text"
            )
            print(f"Added URL reference node")
            
            # Add chunks with embedded source information
            for i, chunk in enumerate(chunks, 1):
                try:
                    formatted_chunk = format_youtube_content(chunk, source_url, timestamp)
                    response = client.graph.add(
                        group_id=group_id,
                        data=formatted_chunk,
                        type="text"
                    )
                    print(f"Chunk {i}/{total_chunks} added successfully with source reference")
                    
                except Exception as e:
                    print(f"Error processing chunk {i}/{total_chunks}: {str(e)}")
                    raise
                    
        except Exception as e:
            print(f"Error adding source information: {str(e)}")
            raise
            
    else:
        # For non-YouTube content, just add the chunks normally
        for i, chunk in enumerate(chunks, 1):
            try:
                response = client.graph.add(
                    group_id=group_id,
                    data=chunk,
                    type="text"
                )
                print(f"Chunk {i}/{total_chunks} added successfully")
                
            except Exception as e:
                print(f"Error processing chunk {i}/{total_chunks}: {str(e)}")
                raise

    print(f"\nCompleted! All {total_chunks} chunks have been processed.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 add_text.py <path_to_text_file> [source_url] [timestamp]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    source_url = sys.argv[2] if len(sys.argv) > 2 else None
    timestamp = sys.argv[3] if len(sys.argv) > 3 else None
    
    content = read_file_content(file_path)
    add_text_to_graph(content, file_path=file_path, source_url=source_url, timestamp=timestamp)
