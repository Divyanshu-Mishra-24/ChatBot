import React, { useState, useEffect } from 'react';
import CommandInput from './components/CommandInput';
import TerminalOutput from './components/TerminalOutput';
import HistoryDisplay from './components/HistoryDIsplay';
import { FaRobot, FaHistory } from 'react-icons/fa';
import './App.css';

function App() {
  const [commands, setCommands] = useState([]);
  const [chatMode, setChatMode] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  // Initial greeting
  useEffect(() => {
    setCommands([{ command: 'system', response: "Hello I'm Gruu, ready for commands!" }]);
  }, []);

  const handleCommandSubmit = (command, response) => {
    setCommands([...commands, { command, response }]);
  };

  return (
    <div className={`app ${chatMode ? 'chat-mode' : ''}`}>
      <header>
        <h1>
          <FaRobot /> Gruu Voice Assistant
        </h1>
        <button
          onClick={() => setShowHistory(true)}
          className="history-button"
          title="View command history"
        >
          <FaHistory />
        </button>
      </header>

      <div className="terminal-container">
        <TerminalOutput commands={commands} />
        <CommandInput
          onCommandSubmit={handleCommandSubmit}
          chatMode={chatMode}
          setChatMode={setChatMode}
        />
      </div>

      <HistoryDisplay isOpen={showHistory} onClose={() => setShowHistory(false)} />
    </div>
  );
}

export default App;