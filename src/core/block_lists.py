"""In-memory storage of blocked user lists.

The module contains global sets for storing banned and shadowbanned users.
Data is reset on every bot restart.
"""

# Simple in-memory storage. Resets on bot restart.

banned: set[int] = set()
"""Set of user IDs that have been banned with a notification."""

shadowbanned: set[int] = set()
"""Set of user IDs that have been shadowbanned without a notification."""
