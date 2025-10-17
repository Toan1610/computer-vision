from supabase import create_client
import os

url = "https://hguejnrbvmwkdnezvqzk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhndWVqbnJidm13a2RuZXp2cXprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTMzOTkyNywiZXhwIjoyMDY2OTE1OTI3fQ.Vip7dj1vGNpV2VcwVuGYMrW5cG5q2DQmXp-ykb-Ixl8"
supabase = create_client(url, key)

def on_insert(payload):
    print("New attendance:", payload)

channel = supabase.channel("attendance_changes") \
    .on("postgres_changes", {
        "event": "INSERT",
        "schema": "public",
        "table": "attendance"
    }, on_insert) \
    .subscribe()
