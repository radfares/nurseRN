import mysql.connector
import os
from mysql.connector import Error
from datetime import datetime

class MemoryBank:
    def __init__(self, host=None, user=None, password=None, database=None):
        """Initialize MemoryBank with secure credential handling
        
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
        database = database or os.getenv('DB_NAME', 'ai_workspace')
        try:
            self.conn = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("[MemoryBank] Connected to MySQL.")
            
            # Automatically create tables if they don't exist
            self._create_tables_if_not_exist()
            
        except Error as e:
            print(f"[MemoryBank] Connection error: {e}")
            self.conn = None
    
    def _create_tables_if_not_exist(self):
        """Create required tables if they don't exist"""
        tables = {
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
            for table_name, create_sql in tables.items():
                self.cursor.execute(create_sql)
            self.conn.commit()
            print("[MemoryBank] Database schema verified/created.")
        except Error as e:
            print(f"[MemoryBank] Schema creation error: {e}")

    def add_agent(self, name, role):
        query = "INSERT INTO agents (name, role) VALUES (%s, %s)"
        self.cursor.execute(query, (name, role))
        self.conn.commit()
        print(f"[MemoryBank] Agent '{name}' added.")

    def log_invocation(self, model_name, duration_ms, request_id, status, task_id=None, error_message=None):
        query = """
        INSERT INTO model_invocations (model_name, duration_ms, request_id, status, task_id, error_message)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(query, (model_name, duration_ms, request_id, status, task_id, error_message))
        self.conn.commit()
        print(f"[MemoryBank] Invocation of '{model_name}' logged.")

    def store_memory(self, agent_id, content):
        query = "INSERT INTO memories (agent_id, content) VALUES (%s, %s)"
        self.cursor.execute(query, (agent_id, content))
        self.conn.commit()
        print(f"[MemoryBank] Memory stored for agent {agent_id}.")

    def search_memories(self, keyword):
        query = "SELECT * FROM memories WHERE content LIKE %s ORDER BY timestamp DESC"
        self.cursor.execute(query, (f"%{keyword}%",))
        results = self.cursor.fetchall()
        print(f"[MemoryBank] Found {len(results)} memories matching '{keyword}'.")
        return results

    def fetch_recent_memories(self, agent_id, limit=10):
        query = """
            SELECT timestamp, content FROM memories
            WHERE agent_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        self.cursor.execute(query, (agent_id, limit))
        results = self.cursor.fetchall()
        print(f"[MemoryBank] Retrieved {len(results)} recent memories for agent {agent_id}.")
        return results

    def get_agents(self):
        self.cursor.execute("SELECT * FROM agents")
        return self.cursor.fetchall()

    def close(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("[MemoryBank] Connection closed.")
