"""
Database adapter selector.
Returns the correct adapter based on config['database']['type'].
"""

def get_database_adapter(config: dict):
    """
    Factory function that returns the appropriate database adapter
    based on the configuration.
    """
    db_type = config["database"]["type"]

    if db_type == "firebase":
        from backend.adapters.firebase import FirebaseAdapter
        return FirebaseAdapter(config)
    elif db_type == "sqlite":
        from backend.adapters.sqlite import SQLiteAdapter
        return SQLiteAdapter(config)
    else:
        raise ValueError(f"Unknown database type: {db_type}. Use 'sqlite' or 'firebase'.")
