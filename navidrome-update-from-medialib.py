#!/usr/bin/env python3
"""
Connects to the Navidrome SQLite database and processes annotation records.

This script opens the navidrome.db file and joins the 'annotation' table
with the 'media_file' table to display the file path along with any
comments or ratings.
"""

import argparse
import logging
import sqlite3
import os
import sys

DB_PATH = "/srv/project/media-lib/navidrome/data/navidrome.db"
logger = logging.getLogger(__name__)


def process_annotations(db_path):
    """Connect to the database and loop through all annotation records."""
    if not os.path.exists(db_path):
        logger.error(f"Database file not found at {db_path}")
        sys.exit(1)

    logger.info(f"Connecting to database: {db_path}")
    conn = None
    try:
        # Using a read-only URI to prevent accidental writes
        db_uri = f"file:{db_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row  # Access columns by name
        logger.debug("Database connection successful.")
        cursor = conn.cursor()

        logger.info("Fetching annotations and corresponding file paths...")
        # The annotation table is often empty. A LEFT JOIN from media_file
        # is more useful for inspection, but for this script's purpose,
        # we will query annotations and join to find their paths.
        query = """
          select	u.user_name, a.item_id, a.rating, a.starred, a.rated_at,
                  m.title, m.album, m.artist, m.path
          from	  annotation a
          join	  user u on a.user_id = u.id
          join    media_file m on a.item_id = m.id;
        """
        cursor.execute(query)

        records = cursor.fetchall()

        if not records:
            logger.info("No records found in the 'annotation' table.")
            return

        logger.info(f"Found {len(records)} records. Iterating through them:")
        for i, record in enumerate(records):
            logger.info(f"--- Record {i+1} ---")
            # Using debug level for the full record dictionary to avoid overly verbose INFO logs
            logger.debug(dict(record))
            # Log the joined data
            logger.info(f"  Item ID: {record['item_id']} (Title: {record['title']})")
            logger.info(f"  User: {record['user_name']}, Artist: {record['artist']}, Album: {record['album']}")
            logger.info(f"  Starred: {record['starred']}, Rated At: {record['rated_at']})")
            logger.info(f"  Path: {record['path']}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug level logging."
    )
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = "%(asctime)s (%(levelname)s) [%(name)s] %(message)s"
    logging.basicConfig(level=log_level, format=log_format)

    process_annotations(DB_PATH)
