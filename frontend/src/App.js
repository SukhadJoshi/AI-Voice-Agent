import React, { useState, useEffect, useRef } from 'react';
import { Room, RoomEvent, RemoteParticipant, DataPacket_Kind } from 'livekit-client';
import './App.css';
import VoiceCall from './components/VoiceCall';
import CallSummary from './components/CallSummary';

function App() {
  const [room, setRoom] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [toolCalls, setToolCalls] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showSummary, setShowSummary] = useState(false);

  const connectToRoom = async () => {
    try {
      // Get access token from token server
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roomName: `room-${Date.now()}`,
          participantName: 'user',
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { error: errorText || `HTTP error! status: ${response.status}` };
        }
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const { token, url } = await response.json();
      
      if (!token || !url) {
        console.error('Token server response:', { token: token ? 'present' : 'missing', url: url ? 'present' : 'missing' });
        throw new Error('Invalid response from token server: missing token or URL. Check that LiveKit credentials are configured in backend/.env');
      }

      const newRoom = new Room();
      
      newRoom.on(RoomEvent.Connected, () => {
        console.log('Connected to room');
        setIsConnected(true);
      });

      newRoom.on(RoomEvent.Disconnected, () => {
        console.log('Disconnected from room');
        setIsConnected(false);
      });

      newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
        if (participant) {
          console.log('Participant connected:', participant.identity || 'unknown');
        }
      });

      newRoom.on(RoomEvent.DataReceived, (payload, participant, kind, topic) => {
        if (topic === 'tool_calls') {
          try {
            const data = JSON.parse(new TextDecoder().decode(payload));
            if (data.tool_calls) {
              setToolCalls(prev => [...prev, ...data.tool_calls]);
            }
          } catch (e) {
            console.error('Error parsing tool calls:', e);
          }
        } else if (topic === 'conversation_summary') {
          const summaryText = new TextDecoder().decode(payload);
          setSummary(summaryText);
          setShowSummary(true);
        }
      });

      await newRoom.connect(url, token);
      setRoom(newRoom);
    } catch (error) {
      console.error('Failed to connect:', error);
      const errorMessage = error.message || 'Unknown error occurred';
      alert(`Failed to connect to voice agent:\n\n${errorMessage}\n\nPlease check:\n1. Token server is running on port 8000\n2. Backend .env file has LiveKit credentials\n3. Check browser console (F12) for details`);
    }
  };

  const disconnect = async () => {
    if (room) {
      await room.disconnect();
      setRoom(null);
      setIsConnected(false);
      setToolCalls([]);
      setSummary(null);
      setShowSummary(false);
    }
  };

  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>SuperBryn AI Voice Agent</h1>
        <p>Book and manage appointments with voice</p>
      </header>

      <main className="App-main">
        {!isConnected ? (
          <div className="connect-section">
            <button onClick={connectToRoom} className="connect-button">
              Start Voice Call
            </button>
          </div>
        ) : (
          <>
            <VoiceCall 
              room={room} 
              toolCalls={toolCalls}
              onDisconnect={disconnect}
            />
            {showSummary && summary && (
              <CallSummary 
                summary={summary}
                onClose={() => setShowSummary(false)}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;

