import pymysql
from typing import Optional

DB_CONFIG = {
    "host": "cyborg",
    "user": "optimus",
    "password": "q",
    "port": 3306,
    "cursorclass": pymysql.cursors.DictCursor
}

def get_connection(database: Optional[str] = None):
    """Get database connection"""
    config = DB_CONFIG.copy()
    if database:
        config["database"] = database
    return pymysql.connect(**config)
