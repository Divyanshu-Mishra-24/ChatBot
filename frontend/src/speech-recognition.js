// First define all functionality
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let recognition;
let callbacks = {};

if (SpeechRecognition) {
  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    if (callbacks.onResult) callbacks.onResult(transcript);
  };

  recognition.onend = () => {
    if (callbacks.onEnd) callbacks.onEnd();
  };

  recognition.onerror = (event) => {
    console.error('Speech recognition error', event.error);
    if (callbacks.onError) callbacks.onError(event.error);
  };
}

// Then export at the end
export const startListening = (options = {}) => {
  if (!SpeechRecognition) {
    console.warn('Speech Recognition API not supported');
    return;
  }
  
  callbacks = {
    onResult: options.onResult,
    onEnd: options.onEnd,
    onError: options.onError
  };
  recognition.start();
};

export const stopListening = () => {
  if (recognition) {
    recognition.stop();
  }
};

// Export the main recognition object if needed
export { SpeechRecognition };