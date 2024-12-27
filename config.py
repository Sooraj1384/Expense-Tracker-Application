import os


class Config:
    # Database connection URL
    DATABASE_URL = os.getenv("DATABASE_URL",
                             "postgres://postgres.bdlfkovhmdfetrkiywre:J65RlnOiG0hj9yIX@aws-0-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
)
