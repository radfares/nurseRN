# MySQL Connector Python Setup Instructions

## Installation Complete ✅
- **Location**: `/Users/hdz_agents/ai-orchestrator`
- **Package**: mysql-connector-python v9.4.0
- **Environment**: Virtual environment created in `venv/`

## How to Use

### 1. Activate the Virtual Environment
```bash
cd /Users/hdz_agents/ai-orchestrator
source venv/bin/activate
```

### 2. Verify Installation
```bash
python3 -c "import mysql.connector; print('MySQL Connector installed successfully!')"
```

### 3. Basic Usage Example
```python
import mysql.connector

# Create connection
connection = mysql.connector.connect(
    host='localhost',
    user='your_username',
    password='your_password',
    database='your_database'
)

cursor = connection.cursor()

# Example query
cursor.execute("SELECT VERSION()")
result = cursor.fetchone()
print(f"MySQL Version: {result[0]}")

# Close connection
cursor.close()
connection.close()
```

### 4. Deactivate Virtual Environment
```bash
deactivate
```

## Notes
- Always activate the virtual environment before running Python scripts that use MySQL connector
- The virtual environment isolates packages from the system Python installation
- This setup prevents conflicts with macOS system-managed Python packages
