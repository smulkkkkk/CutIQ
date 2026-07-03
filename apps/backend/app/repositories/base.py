from app.core.supabase import get_supabase

class BaseRepository:
    def __init__(self, table: str):
        self.table = table
        self.client = get_supabase()
