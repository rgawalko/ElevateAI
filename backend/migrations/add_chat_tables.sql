-- Migration: Add chat and message tables for chatbot functionality
-- Date: 2025-07-31
-- Description: Creates tables for storing chat conversations and messages

-- Create chats table
CREATE TABLE IF NOT EXISTS chats (
    chat_id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    azure_thread_id VARCHAR(255) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_message_at TIMESTAMP WITH TIME ZONE
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGSERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
    sender_id UUID REFERENCES users(id) ON DELETE SET NULL, -- NULL for AI messages
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text' NOT NULL,
    sender_type VARCHAR(20) DEFAULT 'user' NOT NULL, -- 'user' or 'assistant'
    azure_message_id VARCHAR(255),
    token_count BIGINT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for optimal query performance

-- Indexes for chats table
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_azure_thread_id ON chats(azure_thread_id);
CREATE INDEX IF NOT EXISTS idx_chats_user_updated ON chats(user_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chats_user_active ON chats(user_id, is_active);

-- Indexes for messages table
CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_chat_sent ON messages(chat_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_sender_type ON messages(sender_type);
CREATE INDEX IF NOT EXISTS idx_messages_chat_sender_sent ON messages(chat_id, sender_type, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_sender_id ON messages(sender_id);

-- Add comments for documentation
COMMENT ON TABLE chats IS 'Chat conversations between users and AI assistant';
COMMENT ON TABLE messages IS 'Individual messages within chat conversations';

COMMENT ON COLUMN chats.chat_id IS 'Primary key for chat conversations';
COMMENT ON COLUMN chats.user_id IS 'Foreign key to users table';
COMMENT ON COLUMN chats.title IS 'Optional title for the chat conversation';
COMMENT ON COLUMN chats.azure_thread_id IS 'Azure OpenAI thread ID for this conversation';
COMMENT ON COLUMN chats.is_active IS 'Whether the chat is active or archived';
COMMENT ON COLUMN chats.created_at IS 'When the chat was created';
COMMENT ON COLUMN chats.updated_at IS 'When the chat was last updated';
COMMENT ON COLUMN chats.last_message_at IS 'Timestamp of the last message in this chat';

COMMENT ON COLUMN messages.message_id IS 'Primary key for messages';
COMMENT ON COLUMN messages.chat_id IS 'Foreign key to chats table';
COMMENT ON COLUMN messages.sender_id IS 'User ID who sent the message (NULL for AI messages)';
COMMENT ON COLUMN messages.content IS 'The actual message content';
COMMENT ON COLUMN messages.message_type IS 'Type of message (text, system, error, etc.)';
COMMENT ON COLUMN messages.sender_type IS 'Whether message is from user or assistant';
COMMENT ON COLUMN messages.azure_message_id IS 'Azure OpenAI message ID if applicable';
COMMENT ON COLUMN messages.token_count IS 'Token count for AI messages (usage tracking)';
COMMENT ON COLUMN messages.sent_at IS 'When the message was sent';

-- Example queries for pagination and retrieval

-- Get user's chats ordered by most recent activity
-- SELECT * FROM chats 
-- WHERE user_id = $1 AND is_active = true 
-- ORDER BY updated_at DESC 
-- LIMIT 20 OFFSET 0;

-- Get messages from a chat with pagination
-- SELECT * FROM messages 
-- WHERE chat_id = $1 
-- ORDER BY sent_at DESC 
-- LIMIT 20 OFFSET 0;

-- Get messages before a specific timestamp (cursor-based pagination)
-- SELECT * FROM messages 
-- WHERE chat_id = $1 AND sent_at < $2 
-- ORDER BY sent_at DESC 
-- LIMIT 20;

-- Get chat with message count
-- SELECT c.*, COUNT(m.message_id) as message_count 
-- FROM chats c 
-- LEFT JOIN messages m ON c.chat_id = m.chat_id 
-- WHERE c.user_id = $1 
-- GROUP BY c.chat_id 
-- ORDER BY c.updated_at DESC;

-- Get recent conversations with last message
-- SELECT c.*, 
--        m.content as last_message,
--        m.sent_at as last_message_at,
--        m.sender_type as last_sender_type
-- FROM chats c
-- LEFT JOIN LATERAL (
--     SELECT content, sent_at, sender_type
--     FROM messages 
--     WHERE chat_id = c.chat_id 
--     ORDER BY sent_at DESC 
--     LIMIT 1
-- ) m ON true
-- WHERE c.user_id = $1 AND c.is_active = true
-- ORDER BY c.updated_at DESC
-- LIMIT 10;
