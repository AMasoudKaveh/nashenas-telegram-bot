# states/special_contact_states.py
"""
FSM states for the 'special contact' feature.

Flow:
  1. waiting_for_target  → user sends @username or numeric user_id of the target.
  2. waiting_for_message → user sends the anonymous message text for that target.
"""

from aiogram.fsm.state import State, StatesGroup


class SpecialContactStates(StatesGroup):
    """
    States used when sending an anonymous message to a specific contact.
    """

    # Waiting for the user to provide the target (@username or numeric ID)
    waiting_for_target = State()

    # Waiting for the user to provide the anonymous message text
    waiting_for_message = State()
