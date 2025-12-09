# Database Setup and Troubleshooting Guide

## Issue Fixed ✅
**Problem**: `Table 'ai_memory.agents' doesn't exist` error when running memory tests.

**Root Cause**: MySQL database existed but required tables were missing.

## Solution Applied

### 1. Created Database Schema Setup Script
- **File**: `setup_database.py`
- **Purpose**: Creates all required tables automatically
- **Tables Created**:
  - `agents` - Stores agent information (id, name, role, created_at)
  - `memories` - Stores agent memories (id, agent_id, content, timestamp)
  - `model_invocations` - Logs model usage (id, model_name, duration_ms, request_id, status, task_id, error_message, created_at)

### 2. Setup Commands
```bash
# Activate virtual environment
source venv/bin/activate

# Run database setup (one-time only)
python3 setup_database.py

# Test the memory system
python3 memory_test.py
```

### 3. Verification Results
```
✅ Database connected successfully
✅ All tables created successfully  
✅ Memory test passed completely
✅ Data storage and retrieval working
```

## Database Schema Details

### agents table
```sql
CREATE TABLE agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### memories table  
```sql
CREATE TABLE memories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id INT NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);
```

### model_invocations table
```sql
CREATE TABLE model_invocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    duration_ms INT NOT NULL,
    request_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    task_id INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Connection Configuration
- **Host**: localhost
- **User**: root
- **Password**: (empty - update if needed)
- **Database**: ai_memory

## Future Prevention
- Run `setup_database.py` whenever setting up on a new system
- The script uses `CREATE TABLE IF NOT EXISTS` so it's safe to run multiple times
- All foreign key relationships are properly configured

## Troubleshooting
If you encounter database connection issues:
1. Ensure MySQL is running: `brew services start mysql`
2. Verify database exists: `mysql -u root -e "SHOW DATABASES;"`
3. Check permissions: `mysql -u root -e "SHOW GRANTS;"`
4. Update connection parameters in scripts if needed
