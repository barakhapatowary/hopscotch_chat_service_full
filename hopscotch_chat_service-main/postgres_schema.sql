CREATE TABLE IF NOT EXISTS hopscotch_shop.chat_messages (
    message_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES hopscotch_shop.customers(customer_id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS chat_messages_conversation_order
ON hopscotch_shop.chat_messages (conversation_id, message_id);
