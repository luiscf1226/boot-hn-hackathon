"""
Database operations functions for maintenance and cleanup.
"""

import os
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_engine, get_db


def clean_database() -> str:
    """
    Clean the SQLite database by dropping all tables and recreating them.

    Returns:
        String with cleanup result message
    """
    try:
        engine = get_engine()

        # Get all table names
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table';")
            )
            tables = [row[0] for row in result.fetchall()]

        if not tables:
            return "✅ Database is already clean (no tables found)"

        # Drop all tables
        with engine.connect() as conn:
            for table in tables:
                if table != "sqlite_sequence":  # Don't drop SQLite internal table
                    conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            conn.commit()

        # Recreate tables
        from app.core.database import create_tables

        create_tables()

        return f"✅ Database cleaned successfully! Dropped {len(tables)} tables and recreated schema."

    except Exception as e:
        return f"❌ Error cleaning database: {str(e)}"


def get_database_stats() -> str:
    """
    Get database statistics and information.

    Returns:
        String with database statistics
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            # Get table information
            result = conn.execute(
                text(
                    """
                SELECT name, 
                       (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as table_count
                FROM sqlite_master m WHERE type='table'
            """
                )
            )
            tables = result.fetchall()

            stats = "📊 Database Statistics:\n" + "=" * 30 + "\n"

            if not tables:
                stats += "No tables found in database\n"
                return stats

            total_records = 0

            for table_name, _ in tables:
                if table_name == "sqlite_sequence":
                    continue

                try:
                    count_result = conn.execute(
                        text(f"SELECT COUNT(*) FROM {table_name}")
                    )
                    count = count_result.fetchone()[0]
                    total_records += count
                    stats += f"📋 {table_name}: {count} records\n"
                except Exception:
                    stats += f"📋 {table_name}: Error reading\n"

            stats += f"\n📈 Total records: {total_records}\n"

            # Get database file size
            db_path = engine.url.database
            if db_path and os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                stats += f"💾 Database size: {size_mb:.2f} MB\n"

            return stats

    except Exception as e:
        return f"❌ Error getting database stats: {str(e)}"


def vacuum_database() -> str:
    """
    Run VACUUM on the database to reclaim space and optimize.

    Returns:
        String with vacuum result message
    """
    try:
        engine = get_engine()

        with engine.connect() as conn:
            conn.execute(text("VACUUM"))
            conn.commit()

        return (
            "✅ Database vacuumed successfully! Space reclaimed and database optimized."
        )

    except Exception as e:
        return f"❌ Error vacuuming database: {str(e)}"
