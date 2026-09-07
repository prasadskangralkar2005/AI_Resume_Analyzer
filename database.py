import os
from pathlib import Path
import mysql.connector


def get_db_connection():
    # Use TiDB Cloud on Vercel when DB_HOST is configured.
    # Otherwise use local XAMPP MySQL.
    db_host = os.getenv("DB_HOST")

    if db_host:
        ca_path = Path(__file__).parent / "ca.pem"

        connection = mysql.connector.connect(
            host=db_host,
            port=int(os.getenv("DB_PORT", "4000")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "resume_ai"),
            ssl_ca=str(ca_path),
            ssl_verify_cert=True,
            ssl_verify_identity=True,
            use_pure=True
        )
    else:
        # Local XAMPP configuration
        connection = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="",
            database="resume_ai"
        )

    return connection