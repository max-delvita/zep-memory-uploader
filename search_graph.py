import os
import sys
import json
from dotenv import load_dotenv
from zep_cloud.client import Zep
from datetime import datetime
from config import ZEP_BASE_URL, DEFAULT_GROUP_ID

# Load environment variables from .env file
load_dotenv()

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format"""
    if seconds is None:
        return "00:00:00"
    try:
        seconds = float(seconds)
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except (ValueError, TypeError):
        return "00:00:00"

def extract_metadata(content):
    """Extract metadata from content string"""
    try:
        # Find metadata section
        if "[YOUTUBE_METADATA]" in content:
            start = content.find("[YOUTUBE_METADATA]") + len("[YOUTUBE_METADATA]")
            end = content.find("[CONTENT]", start)
            if end > start:
                metadata_str = content[start:end].strip()
                try:
                    metadata = json.loads(metadata_str)
                    return "youtube", metadata
                except json.JSONDecodeError:
                    # Try to extract from content if JSON parsing fails
                    if "youtube.com/watch?v=" in content:
                        video_id = content.split("youtube.com/watch?v=")[1].split("&")[0]
                        return "youtube", {
                            "video_id": video_id,
                            "title": "YouTube Video",
                            "start_time": 0
                        }
        elif "[METADATA]" in content:
            start = content.find("[METADATA]") + len("[METADATA]")
            end = content.find("[CONTENT]", start)
            if end > start:
                metadata_str = content[start:end].strip()
                try:
                    metadata = json.loads(metadata_str)
                    return "document", metadata
                except json.JSONDecodeError:
                    pass
        
        # Try to identify YouTube content without metadata section
        if "youtube.com/watch?v=" in content:
            video_id = content.split("youtube.com/watch?v=")[1].split("&")[0]
            # Try to extract timestamp if available
            start_time = 0
            if "&t=" in content:
                try:
                    start_time = int(content.split("&t=")[1].split("&")[0])
                except ValueError:
                    pass
            return "youtube", {
                "video_id": video_id,
                "title": "YouTube Video",
                "start_time": start_time
            }
        
        # Extract file path and title from content if available
        file_path = None
        for line in content.split('\n'):
            if line.startswith("files/") or "/files/" in line:
                file_path = line.strip()
                break
        
        if file_path:
            return "document", {
                "file_path": file_path,
                "title": os.path.basename(file_path),
                "chunk_number": 0
            }
        
        return "document", {
            "file_path": "unknown",
            "title": "",
            "chunk_number": 0
        }
    except Exception as e:
        print(f"Metadata extraction error: {str(e)}")
        return "document", {
            "file_path": "unknown",
            "title": "",
            "chunk_number": 0
        }

def parse_timestamp(timestamp_str):
    """Convert HH:MM:SS to seconds"""
    try:
        h, m, s = map(int, timestamp_str.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

def format_youtube_result(content, metadata):
    """Format YouTube search result"""
    video_id = metadata.get("video_id", "unknown")
    start_time = metadata.get("start_time", 0)
    title = metadata.get("title", "YouTube Video")
    
    # Extract the actual content (between [CONTENT] and [TIMESTAMP])
    content_start = content.find("[CONTENT]") + len("[CONTENT]") if "[CONTENT]" in content else 0
    content_end = content.find("[TIMESTAMP]") if "[TIMESTAMP]" in content else len(content)
    if content_end == -1:
        content_end = len(content)
    actual_content = content[content_start:content_end].strip()
    
    # Format the output
    output = [
        f"\n{'='*80}",
        f"🎥 YouTube Video: {title}",
        f"⏱️  Timestamp: {format_timestamp(start_time)}",
        f"🔗 URL: https://www.youtube.com/watch?v={video_id}&t={int(float(start_time))}",
        f"\n📝 Content:",
        f"{actual_content[:500]}..." if len(actual_content) > 500 else actual_content,
        f"{'='*80}"
    ]
    return "\n".join(output)

def format_document_result(content):
    """Format a document result for display."""
    
    # Check if this is a YouTube video URL node
    if content.startswith("YOUTUBE_VIDEO_URL"):
        lines = content.split('\n')
        url = next((line.split(': ')[1] for line in lines if line.startswith('URL: ')), None)
        if url:
            return f"🎥 YouTube Video Link Found:\n{url}\n"
            
    # Check if this is a YouTube video content node
    if content.startswith("YOUTUBE_VIDEO"):
        lines = content.split('\n')
        url = next((line.split(': ')[1] for line in lines if line.startswith('URL: ')), None)
        timestamp = next((line.split(': ')[1] for line in lines if line.startswith('TIMESTAMP: ')), None)
        content_text = next((line.split(': ')[1] for line in lines if line.startswith('CONTENT: ')), None)
        
        if url and content_text:
            formatted = f"📺 YouTube Video Content\n"
            formatted += f"🔗 URL: {url}\n"
            if timestamp and timestamp != 'start':
                formatted += f"⏰ Timestamp: {timestamp}\n"
            formatted += f"📝 Content: {content_text}\n"
            return formatted
            
    # For regular content, just return as is
    return f"📄 Content: {content}"

def search_documents(query, limit=5):
    """Search for documents in the graph."""
    api_key = os.getenv('ZEP_API_KEY')
    if not api_key:
        print("Error: ZEP_API_KEY not found in environment variables")
        sys.exit(1)

    client = Zep(
        api_key=api_key,
        api_url=ZEP_API_URL
    )
    
    print(f"\nSearching for: '{query}' in group '{DEFAULT_GROUP_ID}'...")
    
    try:
        results = client.graph.search(
            group_id=DEFAULT_GROUP_ID,
            query=query,
            limit=limit
        )
        
        if not results:
            print("No results found.")
            return
            
        print(f"\nFound {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print("-" * 40)
            print(format_document_result(result.content))
            print("-" * 40)
            
    except Exception as e:
        print(f"Error during search: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Get search query from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 search_graph.py 'your search query' [limit]")
        print("Example: python3 search_graph.py 'sleep training' 5")
        sys.exit(1)
    
    # Get query and optional limit
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    search_documents(query, limit) 