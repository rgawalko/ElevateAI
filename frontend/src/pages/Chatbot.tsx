import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Trash2, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Card } from '../components/Card';
import { Button, IconButton } from '../components/Button';
import { cn } from '../utils';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  loading?: boolean;
}

// Get the actual logged-in user's ID
const getLoggedInUserId = (): string | null => {
  try {
    const userData = localStorage.getItem('elevate_user');
    if (userData) {
      const user = JSON.parse(userData);
      return user.id;
    }
  } catch (error) {
    console.error('Error parsing user data:', error);
  }
  return null;
};

export const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hello! I'm your AI assistant. I can help you with scheduling, productivity tips, goal setting, and more. How can I assist you today?",
      role: 'assistant',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Get the logged-in user ID
    const userId = getLoggedInUserId();
    if (!userId) {
      console.error('No logged-in user found');
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Error: Please log in to use the chatbot.',
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue.trim(),
      role: 'user',
      timestamp: new Date()
    };

    const loadingMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      loading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    const messageToSend = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    try {
      // Get auth token for authenticated request
      const token = localStorage.getItem('elevate_auth_token');

      // Call the new chat-based API
      const response = await fetch('http://localhost:8000/api/chatbot/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          message: messageToSend,
          chat_id: localStorage.getItem('chatbot_chat_id') ? parseInt(localStorage.getItem('chatbot_chat_id')!) : undefined
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.success && data.message) {
        // Store chat ID for future messages
        if (data.chat_id) {
          localStorage.setItem('chatbot_chat_id', data.chat_id.toString());
        }

        const assistantMessage: Message = {
          id: data.message_id?.toString() || (Date.now() + 2).toString(),
          content: data.message,
          role: 'assistant',
          timestamp: data.timestamp ? new Date(data.timestamp) : new Date()
        };

        setMessages(prev => prev.slice(0, -1).concat(assistantMessage));
      } else {
        throw new Error(data.error || 'Failed to get response from AI');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        content: "I'm sorry, I encountered an error connecting to the AI service. Please try again later.",
        role: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => prev.slice(0, -1).concat(errorMessage));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    // Clear the chat ID to start a new conversation
    localStorage.removeItem('chatbot_chat_id');

    setMessages([
      {
        id: '1',
        content: "Hello! I'm your AI assistant. I can help you with scheduling, productivity tips, goal setting, and more. How can I assist you today?",
        role: 'assistant',
        timestamp: new Date()
      }
    ]);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight" style={{color: '#026670'}}>
            AI Assistant
          </h1>
          <p className="mt-2 font-medium" style={{color: '#026670'}}>
            Chat with your personal productivity assistant
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <IconButton
            icon={<RotateCcw size={16} />}
            onClick={clearChat}
            variant="outline"
            size="sm"
            title="Clear chat"
          />
        </div>
      </div>

      {/* Chat Interface */}
      <Card className="h-[calc(100vh-12rem)] flex flex-col" padding="none">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggestions */}
        {messages.length === 1 && (
          <div className="px-6 pb-4">
            <div className="text-sm text-secondary-800 mb-3 font-medium">Quick suggestions:</div>
            <div className="flex flex-wrap gap-2">
              {[
                "Help me plan my day",
                "What productivity tips do you have?",
                "How can I set better goals?",
                "Schedule optimization tips"
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInputValue(suggestion)}
                  className="px-3 py-2 text-xs bg-white border border-secondary-200 rounded-lg hover:bg-secondary-50 hover:border-secondary-300 transition-all duration-200 text-secondary-800 font-medium"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t border-secondary-200/50 p-4 bg-secondary-50/30">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message here..."
                className="w-full resize-none rounded-xl border border-secondary-300 bg-white px-4 py-3 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                rows={1}
                style={{
                  minHeight: '44px',
                  maxHeight: '120px',
                  height: 'auto'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = 'auto';
                  target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                }}
              />
            </div>
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              loading={isLoading}
              icon={<Send size={16} />}
              size="md"
              className="h-11"
            >
              Send
            </Button>
          </div>
          <div className="mt-2 text-xs text-center" style={{color: 'rgba(2, 102, 112, 0.6)'}}>
            Press Enter to send, Shift+Enter for new line
          </div>
        </div>
      </Card>
    </div>
  );
};

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={cn(
      "flex items-start space-x-3",
      isUser ? "flex-row-reverse space-x-reverse" : ""
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-sm",
        isUser
          ? "bg-gradient-to-br from-primary-500 to-primary-600"
          : "bg-gradient-to-br from-secondary-100 to-secondary-200"
      )}>
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-secondary-600" />
        )}
      </div>

      {/* Message Content */}
      <div className={cn(
        "flex-1 max-w-[80%]",
        isUser ? "flex flex-col items-end" : ""
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3 shadow-sm",
          isUser
            ? "bg-gradient-to-r from-primary-500 to-primary-600 text-white"
            : "bg-white border border-secondary-200/50"
        )}>
          {message.loading ? (
            <div className="flex items-center space-x-2">
              <Loader2 size={16} className="animate-spin text-secondary-400" />
              <span className="text-secondary-500 text-sm">Thinking...</span>
            </div>
          ) : (
            <div className={cn(
              "markdown-content",
              isUser ? "user-message" : ""
            )}>
              {isUser ? (
                <p>{message.content}</p>
              ) : (
                <ReactMarkdown>
                  {message.content}
                </ReactMarkdown>
              )}
            </div>
          )}
        </div>

        {/* Timestamp */}
        <div className={cn(
          "mt-1 text-xs text-secondary-800",
          isUser ? "text-right" : "text-left"
        )}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
};
