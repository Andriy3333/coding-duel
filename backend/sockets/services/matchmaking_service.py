"""
Matchmaking service for handling player queues and match formation.
"""

import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from backend.api import game
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Player(BaseModel):
    id: str  # Player's custom ID
    name: str
    easy: bool  # Whether the player wants to play easy mode
    medium: bool  # Whether the player wants to play medium mode
    hard: bool  # Whether the player wants to play hard mode
    imageURL: str
    anonymous: bool = True  # Whether the player is anonymous or not
    sid: str  # Socket connection ID
    joined_at: float  # Timestamp when joined queue


class MatchFoundResponse(BaseModel):
    game_id: str
    opponent_Name: str
    opponentImageURL: str | None = None
    question_name: str


class QueueStatusResponse(BaseModel):
    status: str
    queue_size: int


class MatchmakingService:
    """Service for managing player queues and creating matches."""

    def __init__(self):
        self.waiting_players_easy: List[Player] = []
        self.waiting_players_medium: List[Player] = []
        self.waiting_players_hard: List[Player] = []
        self.game_states: Dict[str, game.GameState] = {}

    def set_dependencies(self, game_states_param=None):
        self.game_states = game_states_param

    def add_player_to_queue(self, player_data: Dict[str, Any], sid: str) -> Player:
        """Add a player to the matchmaking queue."""
        import time

        player = Player(**player_data, sid=sid, joined_at=time.time())

        # Add to appropriate difficulty queues
        if player.easy:
            self.waiting_players_easy.append(player)
        if player.medium:
            self.waiting_players_medium.append(player)
        if player.hard:
            self.waiting_players_hard.append(player)

        return player

    def remove_player_from_queue(self, sid: str) -> bool:
        """Remove a player from all queues by socket ID."""
        removed = False

        # Remove from all difficulty queues
        for queue_list in [
            self.waiting_players_easy,
            self.waiting_players_medium,
            self.waiting_players_hard,
        ]:
            initial_count = len(queue_list)
            queue_list[:] = [p for p in queue_list if p.sid != sid]
            if len(queue_list) < initial_count:
                removed = True

        return removed

    def remove_player_by_user_id(self, user_id: str) -> bool:
        """Remove a player from all queues by user ID."""
        removed = False

        # Remove from all difficulty queues
        for queue_list in [
            self.waiting_players_easy,
            self.waiting_players_medium,
            self.waiting_players_hard,
        ]:
            initial_count = len(queue_list)
            queue_list[:] = [p for p in queue_list if p.id != user_id]
            if len(queue_list) < initial_count:
                removed = True

        return removed

    def get_previous_connection(self, user_id: str) -> Optional[str]:
        """Get the previous connection SID for a user."""
        return self.user_connections.get(user_id)

    def update_user_connection(self, user_id: str, new_sid: str) -> Optional[str]:
        """Update user's connection mapping and return the previous SID if any."""
        previous_sid = self.user_connections.get(user_id)
        self.user_connections[user_id] = new_sid
        return previous_sid

    def remove_user_connection(self, user_id: str) -> bool:
        """Remove user from connection mapping."""
        if user_id in self.user_connections:
            del self.user_connections[user_id]
            return True
        return False

    def cleanup_user_connection(self, sid: str) -> Optional[str]:
        """Clean up user connection mapping by SID and return the user_id if found."""
        user_id = None
        for uid, connection_sid in list(self.user_connections.items()):
            if connection_sid == sid:
                user_id = uid
                del self.user_connections[uid]
                break
        return user_id

    def try_create_match(self) -> Optional[tuple[Player, Player, str, str, str]]:
        """Try to create a match if 2+ players are in queue."""
        import time
        import random
        import json

        # Check each difficulty for possible matches
        difficulties = [
            ("easy", self.waiting_players_easy),
            ("medium", self.waiting_players_medium),
            ("hard", self.waiting_players_hard),
        ]

        available_difficulties = [
            (name, queue) for name, queue in difficulties if len(queue) >= 2
        ]

        if available_difficulties:
            # Randomly select a difficulty that has matches available
            difficulty_name, selected_queue = random.choice(available_difficulties)

            player1 = selected_queue.pop(0)
            player2 = selected_queue.pop(0)

            # Remove players from all other queues they might be in
            for queue_list in [
                self.waiting_players_easy,
                self.waiting_players_medium,
                self.waiting_players_hard,
            ]:
                queue_list[:] = [
                    p for p in queue_list if p.sid not in [player1.sid, player2.sid]
                ]

            game_id = f"game_{uuid.uuid4().hex[:12]}"

            # Dynamic question selection
            try:
                with open("backend/data/questions.json", "r") as f:
                    questions_data = json.load(f)

                # Select random question from the difficulty
                if (
                    difficulty_name in questions_data["questions"]
                    and questions_data["questions"][difficulty_name]
                ):
                    question = random.choice(
                        questions_data["questions"][difficulty_name]
                    )
                    question_slug = question["slug"]
                else:
                    # Fallback to two-sum if no questions available for difficulty
                    question_slug = "two-sum"
            except Exception as e:
                # Fallback to two-sum if file reading fails
                question_slug = "two-sum"

            game_state = game.GameState(
                game_id=game_id,
                players={
                    player1.id: game.PlayerInfo(
                        id=player1.id,
                        name=player1.name,
                        sid=player1.sid,
                        anonymous=player1.anonymous,
                    ),
                    player2.id: game.PlayerInfo(
                        id=player2.id,
                        name=player2.name,
                        sid=player2.sid,
                        anonymous=player2.anonymous,
                    ),
                },
                question_name=question_slug,
            )

            # Store active game
            self.game_states[game_id] = game_state

            logger.info(
                f"Match created: {player1.name} vs {player2.name} in game {game_id} with question {question_slug} game_states={self.game_states}"
            )

            return player1, player2, game_id, difficulty_name, question_slug
        return None

    def get_queue_status(self) -> QueueStatusResponse:
        """Get current queue status."""
        total_waiting = (
            len(self.waiting_players_easy)
            + len(self.waiting_players_medium)
            + len(self.waiting_players_hard)
        )
        return QueueStatusResponse(
            status="waiting" if total_waiting > 0 else "empty",
            queue_size=max(
                len(self.waiting_players_easy),
                len(self.waiting_players_medium),
                len(self.waiting_players_hard),
            ),
        )

    def get_game_info(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an active game."""
        return self.game_states.get(game_id)

    def end_game(self, game_id: str) -> bool:
        """End an active game."""
        if game_id in self.game_states:
            del self.game_states[game_id]
            return True
        return False


# Global instance
matchmaking_service = MatchmakingService()
