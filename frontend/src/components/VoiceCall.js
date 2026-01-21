import React, { useState, useEffect, useRef } from 'react';
import { Track, RoomEvent } from 'livekit-client';
import './VoiceCall.css';

const VoiceCall = ({ room, toolCalls, onDisconnect }) => {
  const [isMuted, setIsMuted] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const audioRef = useRef(null);
  const videoRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);

  useEffect(() => {
    if (!room) return;

    const handleTrackSubscribed = (track, publication, participant) => {
      console.log('[AUDIO] Track subscribed:', track.kind, 'from:', participant.identity, 'trackSid:', publication.trackSid);
      if (track.kind === Track.Kind.Audio) {
        if (audioRef.current) {
          console.log('[AUDIO] Attaching audio track to audio element');
          track.attach(audioRef.current);
          // Ensure audio element is playing
          audioRef.current.play().catch(err => {
            console.error('[AUDIO] Error playing audio:', err);
          });
          console.log('[AUDIO] Audio track attached and playing, volume:', audioRef.current.volume);
          
          // Set up audio analysis for speaking detection (sync avatar with voice)
          if (!audioContextRef.current && audioRef.current) {
            try {
              // Create Web Audio API context for audio analysis
              const AudioContext = window.AudioContext || window.webkitAudioContext;
              audioContextRef.current = new AudioContext();
              const source = audioContextRef.current.createMediaElementSource(audioRef.current);
              analyserRef.current = audioContextRef.current.createAnalyser();
              analyserRef.current.fftSize = 256;
              analyserRef.current.smoothingTimeConstant = 0.8;
              source.connect(analyserRef.current);
              analyserRef.current.connect(audioContextRef.current.destination);
              
              // Start analyzing audio levels to detect speaking
              const checkSpeaking = () => {
                if (!analyserRef.current || !audioContextRef.current) {
                  return;
                }
                
                try {
                  const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
                  analyserRef.current.getByteFrequencyData(dataArray);
                  
                  // Calculate average audio level
                  const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
                  
                  // Threshold for detecting speech (adjust as needed)
                  // Lower threshold for better detection - agent voice might be quieter
                  const threshold = 20;
                  const speaking = average > threshold;
                  
                  // Update speaking state - this will trigger avatar animation
                  setIsSpeaking(speaking);
                  
                  // Continue monitoring
                  animationFrameRef.current = requestAnimationFrame(checkSpeaking);
                } catch (error) {
                  console.error('[AVATAR] Error in audio analysis:', error);
                  // Stop monitoring on error
                  animationFrameRef.current = null;
                }
              };
              
              // Start the monitoring loop
              checkSpeaking();
              console.log('[AVATAR] Audio analysis started for speaking detection');
            } catch (error) {
              console.error('[AVATAR] Error setting up audio analysis:', error);
            }
          }
        } else {
          console.error('[AUDIO] audioRef.current is null - cannot attach track!');
        }
      } else if (track.kind === Track.Kind.Video) {
        if (videoRef.current) {
          track.attach(videoRef.current);
          setAvatarUrl(videoRef.current.srcObject);
          // If Beyond Presence/Tavus video track is available, use it
          console.log('[AVATAR] Video track attached - using Beyond Presence/Tavus avatar');
        }
      }
    };

    const handleTrackUnsubscribed = (track) => {
      console.log('Track unsubscribed:', track.kind);
      track.detach();
      
      // Clean up audio analysis when track is unsubscribed
      if (track.kind === Track.Kind.Audio && animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
        setIsSpeaking(false);
      }
      
      // Clean up audio context when track is unsubscribed
      if (track.kind === Track.Kind.Audio && audioContextRef.current) {
        audioContextRef.current.close().catch(err => {
          console.error('[AVATAR] Error closing audio context:', err);
        });
        audioContextRef.current = null;
        analyserRef.current = null;
      }
    };

    const handleParticipantConnected = (participant) => {
      if (!participant) return;
      console.log('[PARTICIPANT] Participant connected:', participant.identity || 'unknown');
      
      // Subscribe to all audio tracks from remote participants (agent)
      try {
        console.log('[PARTICIPANT] Checking audio tracks for participant:', participant.identity);
        if (participant.audioTrackPublications) {
          const audioTracks = Array.from(participant.audioTrackPublications.values());
          console.log(`[PARTICIPANT] Found ${audioTracks.length} audio track publications`);
          audioTracks.forEach((publication) => {
            console.log(`[PARTICIPANT] Audio publication: trackSid=${publication.trackSid}, isSubscribed=${publication.isSubscribed}, track=${publication.track ? 'exists' : 'null'}`);
            // Subscribe to track if not already subscribed
            if (!publication.isSubscribed) {
              try {
                console.log('[PARTICIPANT] Subscribing to audio track:', publication.trackSid);
                const subscribeResult = publication.setSubscribed(true);
                if (subscribeResult && typeof subscribeResult.then === 'function') {
                  subscribeResult.then(() => {
                    console.log('[PARTICIPANT] Successfully subscribed to track');
                  }).catch(err => {
                    console.error('[PARTICIPANT] Error subscribing:', err);
                  });
                }
              } catch (err) {
                console.error('[PARTICIPANT] Error calling setSubscribed:', err);
              }
            }
            
            // If track is already available, attach it
            if (publication && publication.track && audioRef.current) {
              try {
                console.log('[PARTICIPANT] Attaching existing audio track');
                publication.track.attach(audioRef.current);
                audioRef.current.play().catch(err => {
                  console.error('[PARTICIPANT] Error playing audio:', err);
                });
              } catch (err) {
                console.error('[PARTICIPANT] Error attaching audio track:', err);
              }
            } else {
              console.log('[PARTICIPANT] Publication exists but track not available yet - will wait for TrackSubscribed event');
            }
          });
        }
      } catch (err) {
        console.error('[PARTICIPANT] Error handling participant audio tracks:', err);
      }
    };

    const handleParticipantDisconnected = (participant) => {
      console.log('Participant disconnected:', participant.identity);
    };

    // Listen for track subscriptions
    room.on(RoomEvent.TrackSubscribed, handleTrackSubscribed);
    room.on(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed);
    room.on(RoomEvent.ParticipantConnected, handleParticipantConnected);
    room.on(RoomEvent.ParticipantDisconnected, handleParticipantDisconnected);
    
    // Also listen for TrackPublished events to catch tracks published after connection
    room.on(RoomEvent.TrackPublished, (publication, participant) => {
      console.log('[TRACK_PUBLISHED] Track published:', publication.kind, 'from:', participant.identity, 'trackSid:', publication.trackSid);
      if (publication.kind === 'audio' && participant.identity !== room.localParticipant?.identity) {
        console.log('[TRACK_PUBLISHED] Agent audio track published - subscribing...');
        // Subscribe to the track - check if setSubscribed returns a promise
        try {
          const subscribeResult = publication.setSubscribed(true);
          if (subscribeResult && typeof subscribeResult.then === 'function') {
            subscribeResult.then(() => {
              console.log('[TRACK_PUBLISHED] Successfully subscribed to agent audio track');
            }).catch(err => {
              console.error('[TRACK_PUBLISHED] Error subscribing to track:', err);
            });
          } else {
            console.log('[TRACK_PUBLISHED] setSubscribed called (non-promise API)');
          }
        } catch (err) {
          console.error('[TRACK_PUBLISHED] Error calling setSubscribed:', err);
        }
      }
    });

    // Enable microphone
    if (room.localParticipant) {
      console.log('[MIC] Enabling microphone...');
      room.localParticipant.setMicrophoneEnabled(true).then(() => {
        console.log('[MIC] Microphone enabled successfully');
        // Check if track was published
        const micTracks = Array.from(room.localParticipant.audioTrackPublications.values());
        console.log(`[MIC] Published microphone tracks: ${micTracks.length}`);
        micTracks.forEach(pub => {
          console.log(`[MIC] Audio track published: ${pub.trackSid}, kind: ${pub.kind}, muted: ${pub.isMuted}, isSubscribed: ${pub.isSubscribed}`);
        });
        
        // If no tracks, wait a bit and check again
        if (micTracks.length === 0) {
          setTimeout(() => {
            const tracksAfterDelay = Array.from(room.localParticipant.audioTrackPublications.values());
            console.log(`[MIC] Microphone tracks after delay: ${tracksAfterDelay.length}`);
          }, 1000);
        }
      }).catch(err => {
        console.error('[MIC] Error enabling microphone:', err);
      });
      
      // Also listen for track published events (for local participant - user's mic)
      room.localParticipant.on('trackPublished', (publication) => {
        console.log('[MIC] Local track published:', publication.trackSid, publication.kind);
        if (publication.kind === 'audio') {
          console.log('[MIC] Local audio track published successfully');
        }
      });
      
      // Check for remote participants (agent) and their tracks
      if (room.remoteParticipants) {
        room.remoteParticipants.forEach((participant, identity) => {
          console.log(`[REMOTE] Checking remote participant: ${identity}`);
          if (participant.audioTrackPublications) {
            const audioTracks = Array.from(participant.audioTrackPublications.values());
            console.log(`[REMOTE] Found ${audioTracks.length} audio track publications for ${identity}`);
            audioTracks.forEach((publication) => {
              console.log(`[REMOTE] Audio publication: trackSid=${publication.trackSid}, isSubscribed=${publication.isSubscribed}`);
              // Try to subscribe if not already subscribed
              if (!publication.isSubscribed) {
                try {
                  const subscribeResult = publication.setSubscribed(true);
                  if (subscribeResult && typeof subscribeResult.then === 'function') {
                    subscribeResult.then(() => {
                      console.log(`[REMOTE] Subscribed to audio track: ${publication.trackSid}`);
                    }).catch(err => {
                      console.error(`[REMOTE] Error subscribing to track: ${err}`);
                    });
                  } else {
                    console.log(`[REMOTE] setSubscribed called (non-promise API) for track: ${publication.trackSid}`);
                  }
                } catch (err) {
                  console.error(`[REMOTE] Error calling setSubscribed: ${err}`);
                }
              }
            });
          }
        });
      }
    }

    // Don't access remoteParticipants directly - let TrackSubscribed event handle it
    // This avoids the .size error that happens when remoteParticipants isn't initialized yet

    return () => {
      room.off(RoomEvent.TrackSubscribed, handleTrackSubscribed);
      room.off(RoomEvent.TrackUnsubscribed, handleTrackUnsubscribed);
      room.off(RoomEvent.ParticipantConnected, handleParticipantConnected);
      room.off(RoomEvent.ParticipantDisconnected, handleParticipantDisconnected);
    };
  }, [room]);

  const toggleMute = async () => {
    if (room) {
      await room.localParticipant.setMicrophoneEnabled(!isMuted);
      setIsMuted(!isMuted);
    }
  };

  // Integrate with Beyond Presence or Tavus for avatar
  // For now, using a visual avatar that syncs with voice output
  useEffect(() => {
    // Ready for Beyond Presence/Tavus integration when needed
    // To integrate:
    // 1. Import Beyond Presence/Tavus SDK
    // 2. Create avatar stream: const avatarStream = await beyondPresence.getAvatarStream(room);
    // 3. Publish video track from avatar stream to LiveKit room
    // 4. The video track will automatically attach via handleTrackSubscribed
    // 
    // For now, using free-tier visual avatar that syncs with audio using Web Audio API
    
    return () => {
      // Cleanup on unmount
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, [room]);

  return (
    <div className="voice-call-container">
      <div className="call-header">
        <h2>Voice Call Active</h2>
        <button onClick={onDisconnect} className="end-call-button">
          End Call
        </button>
      </div>

      <div className="call-content">
        <div className="avatar-section">
          {avatarUrl ? (
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="avatar-video"
            />
          ) : (
            <div className="avatar-placeholder">
              <div className={`avatar-circle ${isSpeaking ? 'speaking' : ''}`}>
                <span>AI</span>
              </div>
            </div>
          )}
          {isSpeaking && <div className="speaking-indicator">Speaking...</div>}
          {/* Avatar is synced with voice output using Web Audio API analysis */}
          {/* Ready for Beyond Presence/Tavus integration - video tracks will automatically display here */}
        </div>

        <div className="controls-section">
          <button
            onClick={toggleMute}
            className={`control-button ${isMuted ? 'muted' : ''}`}
            title={isMuted ? 'Unmute' : 'Mute'}
          >
            {isMuted ? '🔇' : '🎤'}
          </button>
        </div>

        <div className="tool-calls-section">
          <h3>Recent Actions</h3>
          {toolCalls.length === 0 ? (
            <p className="no-actions">No actions yet</p>
          ) : (
            <div className="tool-calls-list">
              {toolCalls.map((toolCall, index) => (
                <div key={index} className="tool-call-item">
                  <span className="tool-name">{toolCall.name}</span>
                  <span className="tool-time">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <audio 
        ref={audioRef} 
        autoPlay 
        playsInline
        volume={1.0}
        onLoadedMetadata={() => {
          console.log('Audio element loaded');
          if (audioRef.current) {
            audioRef.current.volume = 1.0;
            audioRef.current.play().catch(err => {
              console.error('Error autoplaying audio:', err);
            });
          }
        }}
        onError={(e) => {
          console.error('Audio element error:', e);
        }}
      />
    </div>
  );
};

export default VoiceCall;

