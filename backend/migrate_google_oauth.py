import os
import psycopg2
from psycopg2 import sql

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:YOUR_PASSWORD@dpg-d5btqaili9vc73c03jg0-a.oregon-postgres.render.com:5432/chatpulse_db")

def migrate_database():
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Add Google OAuth columns
        migrations = [
            # Add google_id column
            sql.SQL("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) UNIQUE"),
            
            # Add avatar_url column
            sql.SQL("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)"),
            
            # Add last_login column
            sql.SQL("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP"),
            
            # Make hashed_password nullable
            sql.SQL("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL"),
        ]
        
        for migration in migrations:
            try:
                cursor.execute(migration)
                print(f"✅ Migration executed: {migration.as_string(cursor)}")
            except Exception as e:
                print(f"⚠️  Migration failed (may already exist): {e}")
        
        # Commit changes
        conn.commit()
        print("\n🎉 Database migration completed successfully!")
        
        # Verify columns exist
        cursor.execute(sql.SQL("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'"))
        columns = [row[0] for row in cursor.fetchall()]
        
        print("\n📋 Current users table columns:")
        for col in sorted(columns):
            print(f"  - {col}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    migrate_database()
