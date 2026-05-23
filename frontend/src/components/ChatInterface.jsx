import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = ({ docId, docName, onAskQuestion, isLoading }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');

    try {
      const response = await onAskQuestion(inputValue);

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: response.answer,
        sources: response.sources,
        processingTime: response.processing_time_ms,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: error.response?.data?.detail || 'Failed to get response',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">Document Chat</h2>
            <p className="text-sm text-gray-500">{docName}</p>
          </div>
          <button
            onClick={handleClearChat}
            className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg font-medium">Ask anything about your document</p>
            <p className="text-sm mt-2">Try: "Summarize this document" or "What are the key points?"</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-blue-600 text-white'
                    : message.type === 'error'
                    ? 'bg-red-100 text-red-800 border border-red-200'
                    : 'bg-white shadow-md'
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>

                {message.sources && message.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs font-semibold text-gray-600 mb-2">Sources:</p>
                    <div className="space-y-2">
                      {message.sources.map((source, idx) => (
                        <div key={idx} className="text-xs bg-gray-50 p-2 rounded">
                          <span className="font-medium">Page {source.page}</span>
                          <span className="text-gray-500 ml-2">
                            (Relevance: {(source.relevance_score * 100).toFixed(0)}%)
                          </span>
                          <p className="text-gray-600 mt-1">{source.content}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {message.processingTime && (
                  <p className="text-xs text-gray-400 mt-2">
                    Processed in {message.processingTime}ms
                  </p>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-md rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce h-2 w-2 bg-blue-600 rounded-full"></div>
                <div className="animate-bounce h-2 w-2 bg-blue-600 rounded-full delay-75"></div>
                <div className="animate-bounce h-2 w-2 bg-blue-600 rounded-full delay-150"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t p-4">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask a question about your document..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;
