#!/usr/bin/env python3
"""
Database setup script for Inventory & Procurement Management System
This script creates the database, user, and initializes tables
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create database and user"""
    try:
        # Connect to PostgreSQL as superuser
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="postgres"  # Change this to your PostgreSQL password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database user
        print("Creating database user...")
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ipms_user') THEN
                    CREATE USER ipms_user WITH PASSWORD 'ipms_password';
                END IF;
            END
            $$;
        """)
        
        # Create database
        print("Creating database...")
        cursor.execute("""
            SELECT 'CREATE DATABASE ipms_db'
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ipms_db');
        """)
        
        # Grant privileges
        print("Granting privileges...")
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE ipms_db TO ipms_user;")
        
        cursor.close()
        conn.close()
        
        print("Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        return False

def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="ipms_db",
            user="ipms_user",
            password="ipms_password"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

def create_tables():
    """Create database tables using Flask-SQLAlchemy"""
    try:
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
            return True
            
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("=== Inventory & Procurement Management System - Database Setup ===")
    print()
    
    # Step 1: Create database and user
    print("Step 1: Creating database and user...")
    if not create_database():
        print("Failed to create database. Please check your PostgreSQL installation.")
        return
    
    # Step 2: Test connection
    print("\nStep 2: Testing database connection...")
    if not test_connection():
        print("Failed to connect to database. Please check your configuration.")
        return
    
    # Step 3: Create tables
    print("\nStep 3: Creating database tables...")
    if not create_tables():
        print("Failed to create tables. Please check your application configuration.")
        return
    
    print("\n=== Database setup completed successfully! ===")
    print("\nNext steps:")
    print("1. Copy env.example to .env and update configuration")
    print("2. Install Python dependencies: pip install -r requirements.txt")
    print("3. Run the application: python app.py")
    print("\nDefault admin credentials:")
    print("Email: admin@ipms.com")
    print("Password: admin123")

if __name__ == "__main__":
    main() 