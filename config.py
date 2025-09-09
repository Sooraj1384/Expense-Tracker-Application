import os

class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:Sooraj%407050@db.vfzhypsthwftwrzkxgtx.supabase.co:5432/postgres"
    )
