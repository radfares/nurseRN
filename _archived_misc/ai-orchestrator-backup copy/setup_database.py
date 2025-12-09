#!/usr/bin/env python3
"""
Database setup script for AI Memory Bank
Creates the required tables if they don't exist
"""

import mysql.connector
import os
from mysql.connector import Error

def create_database_schema(host=None, user=None, password=None, database=None):
    """Create the required tables for the AI Memory Bank system
    
    Args:
        host: Database host (uses DB_HOST env var if None)
        user: Database user (uses DB_USER env var if None) 
        password: Database password (uses DB_PASSWORD env var if None)
        database: Database name (uses DB_NAME env var if None)
    """
    # SECURITY FIX: Use environment variables for database credentials
    host = host or os.getenv('DB_HOST', 'localhost')
    user = user or os.getenv('DB_USER', 'root')
    password = password or os.getenv('DB_PASSWORD', '')
    database = database or os.getenv('DB_NAME', 'ai_memory')
    """Create the required tables for the AI Memory Bank system"""
    
    # SQL commands to create tables
    create_tables = {
        'agents': """
            CREATE TABLE IF NOT EXISTS agents (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        
        'memories': """
            CREATE TABLE IF NOT EXISTS memories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                agent_id INT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
            )
        """,
        
        'model_invocations': """
            CREATE TABLE IF NOT EXISTS model_invocations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                model_name VARCHAR(255) NOT NULL,
                duration_ms INT NOT NULL,
                request_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                task_id INT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
    }
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        cursor = conn.cursor()
        
        print(f"✅ Connected to MySQL database: {database}")
        
        # Create each table
        for table_name, create_sql in create_tables.items():
            try:
                cursor.execute(create_sql)
                print(f"✅ Table '{table_name}' created successfully (or already exists)")
            except Error as e:
                print(f"❌ Error creating table '{table_name}': {e}")
                return False
        
        # Commit the changes
        conn.commit()
        print("✅ Database schema setup completed successfully!")
        
        # Show created tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Available tables: {[table[0] for table in tables]}")
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    print("🚀 Setting up AI Memory Bank database schema...")
    
    # You can modify these connection parameters as needed
    success = create_database_schema(
        host='localhost',
        user='root', 
        password='',  # Update with your MySQL password if needed
        database='ai_memory'
    )
    
    if success:
        print("\n✅ Database setup completed! You can now run your memory_test.py")
    else:
        print("\n❌ Database setup failed. Please check your MySQL connection and permissions.")
