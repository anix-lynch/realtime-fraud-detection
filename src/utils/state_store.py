"""Simple in-memory state store for real-time features with TTL support."""

import time
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class UserState:
    """State container for a single user."""
    recent_events: deque = field(default_factory=lambda: deque(maxlen=1000))
    feature_vector: Dict[str, Any] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)


class StateStore:
    """In-memory state store with TTL and memory management."""

    def __init__(self, max_window_minutes: int = 60, cleanup_interval: int = 300):
        self.max_window_minutes = max_window_minutes
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()
        self._store: Dict[str, UserState] = {}

    def get_user_state(self, user_id: str) -> UserState:
        """Get or create user state."""
        if user_id not in self._store:
            self._store[user_id] = UserState()
        return self._store[user_id]

    def update_user_events(self, user_id: str, event: Dict[str, Any]) -> None:
        """Add event to user's recent events."""
        state = self.get_user_state(user_id)
        state.recent_events.append(event)
        state.last_updated = time.time()

    def update_user_features(self, user_id: str, features: Dict[str, Any]) -> None:
        """Update user's feature vector."""
        state = self.get_user_state(user_id)
        state.feature_vector.update(features)
        state.last_updated = time.time()

    def get_user_features(self, user_id: str) -> Dict[str, Any]:
        """Get user's current feature vector."""
        state = self.get_user_state(user_id)
        return state.feature_vector.copy()

    def get_recent_events(self, user_id: str, window_minutes: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get user's recent events within time window."""
        if user_id not in self._store:
            return []

        state = self._store[user_id]
        window_minutes = window_minutes or self.max_window_minutes
        cutoff_time = time.time() - (window_minutes * 60)

        # Filter events within time window
        recent_events = []
        for event in state.recent_events:
            if event.get('timestamp_unix', 0) > cutoff_time:
                recent_events.append(event)

        return recent_events

    def clear_old_entries(self) -> int:
        """Clear entries older than max_window_minutes. Returns count of cleared entries."""
        current_time = time.time()
        cutoff_time = current_time - (self.max_window_minutes * 60)

        users_to_remove = []
        for user_id, state in self._store.items():
            # Remove if no recent activity and old creation time
            if (state.last_updated < cutoff_time and
                state.created_at < cutoff_time and
                not state.recent_events):
                users_to_remove.append(user_id)
            else:
                # Clean old events from deque
                while state.recent_events and state.recent_events[0].get('timestamp_unix', 0) < cutoff_time:
                    state.recent_events.popleft()

        # Remove old users
        for user_id in users_to_remove:
            del self._store[user_id]

        self.last_cleanup = current_time
        return len(users_to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics."""
        total_events = sum(len(state.recent_events) for state in self._store.values())
        return {
            'total_users': len(self._store),
            'total_events': total_events,
            'max_window_minutes': self.max_window_minutes,
            'last_cleanup': self.last_cleanup
        }

    def should_cleanup(self) -> bool:
        """Check if cleanup is due."""
        return time.time() - self.last_cleanup > self.cleanup_interval
