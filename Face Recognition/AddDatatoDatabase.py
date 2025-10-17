from supabaseClient import supabase
from supabase import create_client, Client

url = "https://hguejnrbvmwkdnezvqzk.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhndWVqbnJidm13a2RuZXp2cXprIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTMzOTkyNywiZXhwIjoyMDY2OTE1OTI3fQ.Vip7dj1vGNpV2VcwVuGYMrW5cG5q2DQmXp-ykb-Ixl8"   # lấy từ Project Settings > API > anon key
supabase: Client = create_client(url, key)


data = [
    {
        "id": "321654",
        "name": "Murtaza Hassan",
        "major": "Robotics",
        "starting_year": 2017,
        "total_attendance": 7,
        "standing": "G",
        "year": 4,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    {
        "id": "852741",
        "name": "Emly Blunt",
        "major": "Economics",
        "starting_year": 2021,
        "total_attendance": 12,
        "standing": "B",
        "year": 1,
        "last_attendance_time": "2022-12-11 00:54:34"
    },

    {
        "id": "963852",
        "name": "Elon Musk",
        "major": "Physics",
        "starting_year": 2020,
        "total_attendance": 7,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    },
    
    {
        "id": "161003",
        "name": "BUI CHI TOAN",
        "major": "AI",
        "starting_year": 2020,
        "total_attendance": 7,
        "standing": "G",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34"
    }
]

for student in data:
    res = supabase.table("Students").insert(student).execute()
    print(res)
