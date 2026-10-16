"""PostgreSQL memory: one row per message."""
import os

import psycopg
from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()


def save_message(user_id, message):
    role = 'user' if isinstance(message, HumanMessage) else 'assistant'
    with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=10,
                         prepare_threshold=None) as db:
        db.execute('''INSERT INTO hopscotch_shop.chat_messages
                      (conversation_id, role, content) VALUES (%s, %s, %s)''',
                   (user_id, role, message.content))


def load_history(user_id):
    with psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=10,
                         prepare_threshold=None) as db:
        rows = db.execute('''SELECT role, content FROM hopscotch_shop.chat_messages
                             WHERE conversation_id=%s ORDER BY message_id''',
                          (user_id,)).fetchall()
    history = InMemoryChatMessageHistory()
    for role, content in rows:
        message = HumanMessage(content=content) if role == 'user' else AIMessage(content=content)
        history.add_message(message)
    return history
