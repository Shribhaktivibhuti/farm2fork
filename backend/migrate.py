#!/usr/bin/env python3
"""
Database migration helper script for FARM2FORK platform.

This script provides a convenient interface to run Alembic migrations
with proper error handling and logging.

Usage:
    python migrate.py upgrade    # Apply all pending migrations
    python migrate.py downgrade  # Rollback one migration
    python migrate.py current    # Show current migration version
    python migrate.py history    # Show migration history
"""

import sys
import os
import subprocess
from pathlib import Path


def run_alembic_command(command: str) -> int:
    """
    Run an Alembic command and return the exit code.
    
    Args:
        command: Alembic command to run (e.g., "upgrade head")
        
    Returns:
        Exit code from the Alembic command
    """
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Build the full command
    full_command = f"alembic {command}"
    
    print(f"Running: {full_command}")
    print("-" * 50)
    
    # Run the command
    result = subprocess.run(
        full_command,
        shell=True,
        capture_output=False,
        text=True
    )
    
    return result.returncode


def main():
    """Main entry point for the migration script."""
    
    if len(sys.argv) < 2:
        print("Usage: python migrate.py <command>")
        print("\nAvailable commands:")
        print("  upgrade    - Apply all pending migrations")
        print("  downgrade  - Rollback one migration")
        print("  current    - Show current migration version")
        print("  history    - Show migration history")
        print("  help       - Show this help message")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Map user-friendly commands to Alembic commands
    command_map = {
        "upgrade": "upgrade head",
        "downgrade": "downgrade -1",
        "current": "current",
        "history": "history --verbose",
        "help": None,
    }
    
    if command == "help":
        print("FARM2FORK Database Migration Helper")
        print("=" * 50)
        print("\nCommands:")
        print("  upgrade    - Apply all pending migrations to the database")
        print("  downgrade  - Rollback the most recent migration")
        print("  current    - Display the current migration version")
        print("  history    - Show all migrations with details")
        print("\nExamples:")
        print("  python migrate.py upgrade")
        print("  python migrate.py current")
        print("  python migrate.py history")
        print("\nEnvironment Variables:")
        print("  DATABASE_URL - PostgreSQL connection string")
        print("                 Default: postgresql://username:password@localhost:5432/farm2fork")
        sys.exit(0)
    
    if command not in command_map:
        print(f"Error: Unknown command '{command}'")
        print("Run 'python migrate.py help' for available commands")
        sys.exit(1)
    
    alembic_command = command_map[command]
    
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Warning: DATABASE_URL environment variable is not set")
        print("Using default: postgresql://username:password@localhost:5432/farm2fork")
        print()
    
    # Run the Alembic command
    exit_code = run_alembic_command(alembic_command)
    
    if exit_code == 0:
        print("-" * 50)
        print(f"✓ Command '{command}' completed successfully")
    else:
        print("-" * 50)
        print(f"✗ Command '{command}' failed with exit code {exit_code}")
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
