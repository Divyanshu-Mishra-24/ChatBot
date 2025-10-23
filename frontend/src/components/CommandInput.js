import React, { useState, useEffect, useRef } from 'react';
import { FaMicrophone, FaStopCircle, FaPaperPlane } from 'react-icons/fa';
import axios from 'axios';

const CommandInput = ({ onCommandSubmit, chatMode, setChatMode }) => {
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Initialize speech recognition if available
    if ('webkitSpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    try {
      const response = await axios.post('http://localhost:5000/api/command', {
        command: input
      });
      
      onCommandSubmit(input, response.data.response);
      setInput('');
      
      // Handle chat mode state
      if (response.data.chat_mode !== undefined) {
        setChatMode(response.data.chat_mode);
      }
      
      // Handle shutdown if needed
      if (response.data.shutdown) {
        alert('Backend is shutting down. Refresh page to restart.');
      }
    } catch (error) {
      console.error('Error sending command:', error);
      onCommandSubmit(input, "Error connecting to Gruu backend.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="command-input">
      <div className="input-group">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={chatMode ? "Chat with Gruu..." : "Enter a command..."}
          autoFocus
        />
        <div className="button-group">
          {window.webkitSpeechRecognition && (
            <button
              type="button"
              onClick={toggleListening}
              className={`mic-button ${isListening ? 'listening' : ''}`}
              title={isListening ? "Stop listening" : "Start voice input"}
            >
              {isListening ? <FaStopCircle /> : <FaMicrophone />}
            </button>
          )}
          <button type="submit" title="Send command">
            <FaPaperPlane />
          </button>
        </div>
      </div>
      <div className="hint">
        {chatMode ? "Say 'stop chat' to exit chat mode" : "Try: 'open youtube', 'what's the time', 'use ai', 'weather in London'"}
      </div>
    </form>
  );
};

export default CommandInput;