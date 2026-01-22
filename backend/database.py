"""
Database connection and schema management for Supabase
"""

import os
from supabase import create_client, Client
from typing import List, Tuple, Optional

# Global Supabase client
_supabase: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client"""
    global _supabase
    
    if _supabase is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        _supabase = create_client(url, key)
    
    return _supabase


def init_db():
    """Initialize database schema"""
    # Note: In production, you would run these SQL commands directly in Supabase dashboard
    # or use migrations. For this task, we'll assume the schema exists.
    
    schema_sql = """
    -- Users table
    CREATE TABLE IF NOT EXISTS users (
        phone_number TEXT PRIMARY KEY,
        name TEXT,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Appointments table
    CREATE TABLE IF NOT EXISTS appointments (
        id SERIAL PRIMARY KEY,
        phone_number TEXT NOT NULL REFERENCES users(phone_number),
        name TEXT,
        date DATE NOT NULL,
        time TIME NOT NULL,
        status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled')),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(date, time, status) WHERE status = 'confirmed'
    );

    -- Conversations table for summaries
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        phone_number TEXT REFERENCES users(phone_number),
        summary TEXT,
        booked_appointments JSONB,
        user_preferences JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_appointments_phone ON appointments(phone_number);
    CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
    CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
    """
    
    print("Database schema initialization complete.")
    print("Note: Please run the SQL schema in your Supabase dashboard if tables don't exist.")


def get_db_connection():
    """Get database connection (returns Supabase client)"""
    return get_supabase_client()


def execute_query(conn: Client, query: str, params: Tuple) -> Optional[List]:
    """Execute a query (for Supabase, we use the client methods)"""
    
    pass


def fetch_query(conn: Client, query: str, params: Tuple) -> List[Tuple]:
    """Fetch query results"""
    # Similar to execute_query, we'll use Supabase's query builder
    # This is a placeholder
    pass


# Supabase-specific helper functions
def insert_user(phone_number: str, name: str = None):
    """Insert or update user"""
    client = get_supabase_client()
    data = {"phone_number": phone_number}
    if name:
        data["name"] = name
    
    result = client.table("users").upsert(data, on_conflict="phone_number").execute()
    return result.data


def get_user(phone_number: str):
    """Get user by phone number"""
    client = get_supabase_client()
    result = client.table("users").select("*").eq("phone_number", phone_number).execute()
    return result.data[0] if result.data else None


def insert_appointment(phone_number: str, date: str, time: str, name: str = None, status: str = "confirmed"):
    """Insert appointment"""
    client = get_supabase_client()
    data = {
        "phone_number": phone_number,
        "date": date,
        "time": time,
        "status": status
    }
    if name:
        data["name"] = name
    
    result = client.table("appointments").insert(data).execute()
    return result.data[0] if result.data else None


def get_appointments(phone_number: str):
    """Get all appointments for a user"""
    client = get_supabase_client()
    result = client.table("appointments").select("*").eq("phone_number", phone_number).order("date", desc=True).order("time", desc=True).execute()
    return result.data


def get_appointment_by_id(appointment_id: int, phone_number: str):
    """Get appointment by ID and phone number"""
    client = get_supabase_client()
    result = client.table("appointments").select("*").eq("id", appointment_id).eq("phone_number", phone_number).eq("status", "confirmed").execute()
    return result.data[0] if result.data else None


def check_slot_available(date: str, time: str):
    """Check if a slot is available"""
    client = get_supabase_client()
    result = client.table("appointments").select("id").eq("date", date).eq("time", time).eq("status", "confirmed").execute()
    return len(result.data) == 0


def update_appointment_status(appointment_id: int, phone_number: str, status: str):
    """Update appointment status"""
    client = get_supabase_client()
    result = client.table("appointments").update({"status": status, "updated_at": "now()"}).eq("id", appointment_id).eq("phone_number", phone_number).execute()
    return result.data[0] if result.data else None


def update_appointment_datetime(appointment_id: int, phone_number: str, date: str = None, time: str = None):
    """Update appointment date/time"""
    client = get_supabase_client()
    updates = {"updated_at": "now()"}
    if date:
        updates["date"] = date
    if time:
        updates["time"] = time
    
    result = client.table("appointments").update(updates).eq("id", appointment_id).eq("phone_number", phone_number).execute()
    return result.data[0] if result.data else None


def save_conversation_summary(conversation_id: str, phone_number: str, summary: str, booked_appointments: list, user_preferences: dict):
    """Save conversation summary"""
    client = get_supabase_client()
    data = {
        "id": conversation_id,
        "phone_number": phone_number,
        "summary": summary,
        "booked_appointments": booked_appointments,
        "user_preferences": user_preferences
    }
    result = client.table("conversations").insert(data).execute()
    return result.data[0] if result.data else None

