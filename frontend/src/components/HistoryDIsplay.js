import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaHistory, FaTimes } from 'react-icons/fa';

const HistoryDisplay = ({ isOpen, onClose }) => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchHistory();
    }
  }, [isOpen]);

  const fetchHistory = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:5000/api/history');
      setHistory(response.data.history);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="history-modal">
      <div className="history-header">
        <h3>
          <FaHistory /> Command History
        </h3>
        <button onClick={onClose} className="close-button">
          <FaTimes />
        </button>
      </div>
      <div className="history-content">
        {isLoading ? (
          <div className="loading">Loading history...</div>
        ) : history.length === 0 ? (
          <div className="empty">No history available</div>
        ) : (
          <ul>
            {history.map((item, index) => (
              <li key={index}>
                <div className="history-timestamp">{item.timestamp}</div>
                <div className="history-command">
                  <strong>Command:</strong> {item.command}
                </div>
                <div className="history-response">
                  <strong>Response:</strong> {item.response}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default HistoryDisplay;