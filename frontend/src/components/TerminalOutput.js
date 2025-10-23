import React from 'react';

const TerminalOutput = ({ commands }) => {
  const terminalRef = React.useRef(null);

  React.useEffect(() => {
    // Auto-scroll to bottom when new commands are added
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [commands]);

  return (
    <div className="terminal-output" ref={terminalRef}>
      {commands.map((cmd, index) => (
        <div key={index} className="command-block">
          <div className="user-command">
            <span className="prompt">$</span> {cmd.command}
          </div>
          <div className="gruu-response">
            <span className="gruu-prompt">Gruu:</span> {cmd.response}
          </div>
        </div>
      ))}
    </div>
  );
};

export default TerminalOutput;