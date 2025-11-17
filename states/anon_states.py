# states/anon_states.py
"""
FSM states for generic anonymous messaging flows.

Example usage:
  - waiting_for_username → ask user to provide @username or ID.
  - waiting_for_text     → ask user to provide the message text.
"""

from aiogram.fsm.state import StatesGroup, State


class AnonymousMessage(StatesGroup):
    """
    States used for a simple anonymous message flow.
    """

    # Waiting for the user to provide the target username/ID
    waiting_for_username = State()

    # Waiting for the user to provide the anonymous message text
    waiting_for_text = State()
