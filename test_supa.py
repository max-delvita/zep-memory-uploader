from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("SUPABASE_URL"))
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))
print("ZEP_API_KEY:", os.getenv("ZEP_API_KEY"))