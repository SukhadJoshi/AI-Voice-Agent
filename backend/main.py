"""
SuperBryn AI Voice Agent - Backend
LiveKit Agent implementation with tool calling for appointment management
"""

import asyncio
import json
import os
from typing import Annotated
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import (
    JobContext,
    WorkerOptions,
    cli,
    llm,
    stt,
)
from livekit.plugins import deepgram, cartesia

from tools import (
    identify_user,
    fetch_slots,
    book_appointment,
    retrieve_appointments,
    cancel_appointment,
    modify_appointment,
    end_conversation,
)
from database import init_db, get_db_connection
from summary import generate_summary

load_dotenv()

# #region agent log - Debug instrumentation

def debug_log(location, message, data=None, hypothesis_id=None, session_id="debug-session", run_id="run1"):
    try:
        import json
        import time
        import os
        # Ensure directory exists
        log_dir = os.path.dirname(DEBUG_LOG_PATH)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            log_entry = {
                "timestamp": int(time.time() * 1000),
                "location": location,
                "message": message,
                "data": data or {},
                "sessionId": session_id,
                "runId": run_id,
                "hypothesisId": hypothesis_id
            }
            f.write(json.dumps(log_entry) + "\n")
            f.flush()  # Force write to disk
    except Exception as e:
        # Log error to console so we know if logging is failing
        print(f"[DEBUG_LOG_ERROR] Failed to write debug log: {e}")
# #endregion

# Initialize database
init_db()

# Tool definitions for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "identify_user",
            "description": "Ask for and store user's phone number to identify the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "User's phone number"
                    }
                },
                "required": ["phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_slots",
            "description": "Fetch available appointment slots. Returns hardcoded available time slots.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for the user. Requires date, time, and user phone number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Appointment date in YYYY-MM-DD format"
                    },
                    "time": {
                        "type": "string",
                        "description": "Appointment time in HH:MM format (24-hour)"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "User's phone number"
                    },
                    "name": {
                        "type": "string",
                        "description": "User's name (optional)"
                    }
                },
                "required": ["date", "time", "phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_appointments",
            "description": "Retrieve all past and upcoming appointments for a user",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "User's phone number"
                    }
                },
                "required": ["phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an existing appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "ID of the appointment to cancel"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "User's phone number for verification"
                    }
                },
                "required": ["appointment_id", "phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_appointment",
            "description": "Modify the date or time of an existing appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {
                        "type": "string",
                        "description": "ID of the appointment to modify"
                    },
                    "phone_number": {
                        "type": "string",
                        "description": "User's phone number for verification"
                    },
                    "new_date": {
                        "type": "string",
                        "description": "New appointment date in YYYY-MM-DD format (optional)"
                    },
                    "new_time": {
                        "type": "string",
                        "description": "New appointment time in HH:MM format (optional)"
                    }
                },
                "required": ["appointment_id", "phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "End the conversation and generate a summary",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "identify_user": identify_user,
    "fetch_slots": fetch_slots,
    "book_appointment": book_appointment,
    "retrieve_appointments": retrieve_appointments,
    "cancel_appointment": cancel_appointment,
    "modify_appointment": modify_appointment,
    "end_conversation": end_conversation,
}


async def entrypoint(ctx: JobContext):
    """Main entry point for the voice agent"""
    try:
        print(f"[DEBUG] ===== ENTRYPOINT CALLED =====")
        print(f"[DEBUG] Job ID: {ctx.job.id if hasattr(ctx, 'job') and ctx.job else 'Unknown'}")
        print(f"[DEBUG] Connecting to room...")
        
        await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
        print(f"[DEBUG] ✓ Connected to room: {ctx.room.name}")
        print(f"[DEBUG] Local participant: {ctx.room.local_participant.identity}")
        print(f"[DEBUG] Remote participants: {list(ctx.room.remote_participants.keys())}")
        
        # Initialize STT (Deepgram) with interim results and endpointing enabled
        stt = deepgram.STT(
            interim_results=True,  # Enable interim transcripts - CRITICAL for getting transcripts
            model="nova-2",  # Use Deepgram's Nova-2 model
            endpointing_ms=300,  # Endpointing timeout in milliseconds (300ms pause = end of speech)
            smart_format=True,  # Enable smart formatting
            language="en-US",  # Explicitly set language
        )
        print("[DEBUG] Deepgram STT initialized with interim_results=True, endpointing_ms=300")
        
        # Initialize TTS (Cartesia)
        tts = cartesia.TTS()
        
        # Initialize LLM based on provider
        # Note: For OpenRouter/Together AI, we'll use OpenAI-compatible client
        llm_provider = os.getenv("LLM_PROVIDER", "openrouter")
        
        # Import OpenAI client for LLM calls (works with OpenRouter too)
        from openai import OpenAI
        from anthropic import Anthropic
        
        # Set up LLM client based on provider
        if llm_provider == "openrouter":
            # OpenRouter uses OpenAI-compatible API
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = "https://openrouter.ai/api/v1"
            llm_client = OpenAI(api_key=api_key, base_url=base_url)
          
            model = "meta-llama/llama-3.2-3b-instruct:free"  # Truly free model, no credits needed
        elif llm_provider == "together":
            # Together AI uses OpenAI-compatible API
            api_key = os.getenv("TOGETHER_API_KEY")
            base_url = "https://api.together.xyz/v1"
            llm_client = OpenAI(api_key=api_key, base_url=base_url)
            model = "meta-llama/Llama-3-8b-chat-hf"
        elif llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            llm_client = OpenAI(api_key=api_key)
            model = "gpt-4o-mini"  # Cheaper model
        elif llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            llm_client = None  # Will use Anthropic client directly
            anthropic_client = Anthropic(api_key=api_key)
            model = "claude-3-haiku-20240307"
        else:
            # Fallback to OpenRouter
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = "https://openrouter.ai/api/v1"
            llm_client = OpenAI(api_key=api_key, base_url=base_url)
            # Use truly free models only (models with :free suffix don't require credits)
            # Note: Free models don't support tool use, so we'll work without tools
            model = "meta-llama/llama-3.2-3b-instruct:free"  # Truly free model, no credits needed
        
        # Conversation state
        conversation_history = []
        user_phone = None
        conversation_id = ctx.room.name
        
        # Helper function to synthesize and publish speech
        async def say_text(text: str):
            """Synthesize text to speech and publish to room"""
            if not text.strip():
                return
            
            track = None
            try:
                # Unpublish any existing audio tracks to prevent overlapping voices
                existing_audio_tracks = [
                    pub for pub in ctx.room.local_participant.track_publications.values()
                    if pub.kind == rtc.TrackKind.KIND_AUDIO and pub.source == rtc.TrackSource.SOURCE_MICROPHONE
                ]
                # Unpublish all existing tracks and wait for cleanup
                for existing_pub in existing_audio_tracks:
                    try:
                        await ctx.room.local_participant.unpublish_track(existing_pub.sid)
                        print(f"[DEBUG] Unpublished existing audio track: {existing_pub.sid}")
                    except Exception as unpub_error:
                        print(f"[WARNING] Failed to unpublish existing track {existing_pub.sid}: {unpub_error}")
                
                # Wait longer after unpublishing to ensure tracks are fully cleaned up
                # This prevents overlapping voices
                if existing_audio_tracks:
                    await asyncio.sleep(0.5)  # Increased delay for better cleanup
                    print(f"[DEBUG] Waited 0.5s after unpublishing {len(existing_audio_tracks)} track(s)")
                
                # Create audio source for publishing
                source = rtc.AudioSource(tts.sample_rate, tts.num_channels)
                track = rtc.LocalAudioTrack.create_audio_track("agent-voice", source)
                options = rtc.TrackPublishOptions()
                options.source = rtc.TrackSource.SOURCE_MICROPHONE
                
                # Publish the track and get publication
                publication = await ctx.room.local_participant.publish_track(track, options)
                track_sid = publication.sid
                
                print(f"[DEBUG] Published audio track: {track_sid}")
                print(f"[DEBUG] Starting TTS synthesis for text: '{text[:50]}...' (length: {len(text)} chars)")
                
                # Synthesize speech
                try:
                    stream = tts.synthesize(text)
                    print(f"[DEBUG] TTS stream created successfully, type: {type(stream)}")
                    # #region agent log
                    debug_log("main.py:317", "TTS stream created", {"stream_type": str(type(stream)), "text_length": len(text)}, hypothesis_id="A")
                    # #endregion
                except Exception as stream_error:
                    print(f"[ERROR] Failed to create TTS stream: {stream_error}")
                    # #region agent log
                    debug_log("main.py:319", "TTS stream creation failed", {"error": str(stream_error), "error_type": type(stream_error).__name__}, hypothesis_id="A")
                    # #endregion
                    import traceback
                    traceback.print_exc()
                    raise
                frame_count = 0
                total_bytes = 0
                iteration_count = 0  # Track if loop executes at all
                # #region agent log
                debug_log("main.py:326", "Before entering stream context", {"text_preview": text[:50]}, hypothesis_id="B")
                # #endregion
                async with stream:
                    # #region agent log
                    debug_log("main.py:328", "Entered stream context", {}, hypothesis_id="B")
                    # #endregion
                    async for synthesized_audio in stream:
                        iteration_count += 1
                        # #region agent log
                        debug_log("main.py:331", "Stream yielded item", {"iteration": iteration_count, "item_type": str(type(synthesized_audio)), "has_audio": hasattr(synthesized_audio, 'audio'), "has_frame": hasattr(synthesized_audio, 'frame')}, hypothesis_id="B")
                        # #endregion
                        # Log what we're getting for debugging
                        if frame_count == 0:
                            print(f"[DEBUG] First TTS item type: {type(synthesized_audio)}, dir: {[x for x in dir(synthesized_audio) if not x.startswith('_')][:10]}")
                            # #region agent log
                            debug_log("main.py:336", "First TTS item analysis", {"item_type": str(type(synthesized_audio)), "attributes": [x for x in dir(synthesized_audio) if not x.startswith('_')][:15], "is_bytes": isinstance(synthesized_audio, (bytes, bytearray))}, hypothesis_id="C")
                            # #endregion
                        
                        # Try multiple ways to get the audio frame
                        audio_frame = None
                        
                        # Method 1: Check if it's a SynthesizedAudio object with .audio property
                        if hasattr(synthesized_audio, 'audio'):
                            audio_frame = synthesized_audio.audio
                            print(f"[DEBUG] Got audio via .audio property (frame {frame_count + 1})")
                            # #region agent log
                            debug_log("main.py:341", "Extracted audio via .audio", {"frame_count": frame_count + 1, "audio_type": str(type(audio_frame))}, hypothesis_id="C")
                            # #endregion
                        # Method 2: Check if it's a SynthesizedAudio object with .frame property
                        elif hasattr(synthesized_audio, 'frame'):
                            audio_frame = synthesized_audio.frame
                            print(f"[DEBUG] Got audio via .frame property (frame {frame_count + 1})")
                        # Method 3: Check if the object itself is an AudioFrame
                        elif hasattr(synthesized_audio, 'data') or hasattr(synthesized_audio, 'samples'):
                            # Try to construct frame from data
                            try:
                                if hasattr(synthesized_audio, 'data'):
                                    audio_frame = synthesized_audio.data
                                elif hasattr(synthesized_audio, 'samples'):
                                    audio_frame = synthesized_audio.samples
                                print(f"[DEBUG] Got audio via .data or .samples (frame {frame_count + 1})")
                            except:
                                pass
                        # Method 4: Check if it's an AudioFrame directly (from rtc)
                        elif hasattr(synthesized_audio, 'sample_rate') or hasattr(synthesized_audio, 'num_channels'):
                            audio_frame = synthesized_audio
                            print(f"[DEBUG] Got audio frame directly (frame {frame_count + 1})")
                        # Method 5: If it's bytes/bytearray, wrap it in an AudioFrame
                        elif isinstance(synthesized_audio, (bytes, bytearray)):
                            try:
                                # rtc is already imported at module level, don't re-import here
                                audio_frame = rtc.AudioFrame(
                                    data=synthesized_audio,
                                    sample_rate=tts.sample_rate,
                                    num_channels=tts.num_channels,
                                    samples_per_channel=len(synthesized_audio) // (tts.num_channels * 2)  # Assume 16-bit
                                )
                                print(f"[DEBUG] Wrapped bytes into AudioFrame (frame {frame_count + 1})")
                            except Exception as wrap_error:
                                print(f"[ERROR] Failed to wrap bytes into AudioFrame: {wrap_error}")
                                continue
                        
                        if audio_frame is not None:
                            try:
                                # Push audio frames to source
                                await source.capture_frame(audio_frame)
                                frame_count += 1
                                # Track bytes for debugging
                                if hasattr(audio_frame, 'data'):
                                    total_bytes += len(audio_frame.data)
                                elif hasattr(audio_frame, '__len__'):
                                    total_bytes += len(audio_frame)
                                
                                if frame_count % 50 == 0:
                                    print(f"[DEBUG] Pushed {frame_count} TTS audio frames ({total_bytes} bytes) to track {track_sid}")
                            except Exception as capture_error:
                                print(f"[ERROR] Failed to capture frame {frame_count + 1}: {capture_error}")
                                # #region agent log
                                debug_log("main.py:390", "Failed to capture frame", {"frame_count": frame_count + 1, "error": str(capture_error), "error_type": type(capture_error).__name__}, hypothesis_id="D")
                                # #endregion
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"[WARNING] Could not extract audio from synthesized_audio object (type: {type(synthesized_audio)})")
                            if frame_count == 0:
                                # Log full details for first frame to debug
                                print(f"[DEBUG] Full object details: {synthesized_audio}")
                                # #region agent log
                                debug_log("main.py:395", "Failed to extract audio frame", {"item_type": str(type(synthesized_audio)), "all_attrs": [x for x in dir(synthesized_audio) if not x.startswith('_')]}, hypothesis_id="C")
                                # #endregion
                    # #region agent log
                    debug_log("main.py:400", "Exited stream context", {"iteration_count": iteration_count, "frame_count": frame_count}, hypothesis_id="B")
                    # #endregion
                
                if frame_count == 0:
                    print(f"[ERROR] No audio frames were synthesized! This means TTS returned empty stream or frames couldn't be extracted.")
                    print(f"[ERROR] TTS text was: '{text[:100]}...'")
                    print(f"[ERROR] This is likely a TTS API issue or configuration problem.")
                    # #region agent log
                    debug_log("main.py:405", "Zero frames synthesized", {"iteration_count": iteration_count, "text_length": len(text), "text_preview": text[:100]}, hypothesis_id="A")
                    # #endregion
                else:
                    print(f"[DEBUG] ✓ Finished synthesizing speech: {frame_count} frames, {total_bytes} bytes, track_sid={track_sid}")
                # Wait before unpublishing to ensure frontend receives all audio frames
                # Calculate wait time based on audio duration (rough estimate: 1 second per ~100 words)
                estimated_duration = len(text.split()) / 100  # rough estimate in seconds
                wait_time = max(1.5, estimated_duration + 0.5)  # Reduced: at least 1.5 seconds, or duration + 0.5
                print(f"[DEBUG] Waiting {wait_time:.1f}s before unpublishing to ensure frontend receives audio...")
                await asyncio.sleep(wait_time)
                
                # Stop publishing after synthesis completes - use track_sid (string)
                print(f"[DEBUG] Unpublishing audio track: {track_sid}")
                await ctx.room.local_participant.unpublish_track(track_sid)
                print(f"[DEBUG] Audio track unpublished: {track_sid}")
            except Exception as e:
                print(f"[ERROR] Failed to synthesize speech: {e}")
                import traceback
                traceback.print_exc()
                # Try to cleanup track if it was published
                if track:
                    try:
                        publication = ctx.room.local_participant.track_publications.get(track.name)
                        if publication:
                            await ctx.room.local_participant.unpublish_track(publication.sid)
                    except:
                        pass
        
        # Send initial greeting - keep it short and direct
        initial_message = "Hello! I can help you book appointments. What would you like to do?"
        conversation_history.append({"role": "assistant", "content": initial_message})
        
        # Say initial greeting immediately after setup
        print(f"[DEBUG] Saying initial greeting: {initial_message}")
        try:
            await say_text(initial_message)
            print(f"[DEBUG] Initial greeting completed")
        except Exception as e:
            print(f"[ERROR] Failed to say initial greeting: {e}")
            import traceback
            traceback.print_exc()
        
        # Track if we've already sent a fallback response to prevent duplicates
        fallback_sent = False
        
        # Main conversation loop
        # Track last processed text to prevent duplicate processing
        last_processed_text = None
        last_processed_time = 0
        
        async def on_user_speech(msg: rtc.Transcription):
            nonlocal user_phone, conversation_history, fallback_sent, last_processed_text, last_processed_time
            import time
            
            print(f"[DEBUG] ===== on_user_speech called =====")
            print(f"[DEBUG] Transcription received: {msg}")
            # #region agent log
            debug_log("main.py:306", "on_user_speech entry", {"has_alternatives": bool(msg.alternatives), "alternatives_count": len(msg.alternatives) if msg.alternatives else 0}, hypothesis_id="C")
            # #endregion
            
            # Get text from alternatives or directly from text attribute
            if msg.alternatives and len(msg.alternatives) > 0:
                user_text = msg.alternatives[0].text
            elif hasattr(msg, 'text') and msg.text:
                user_text = msg.text
            else:
                print("[DEBUG] No text available in transcription")
                return
            print(f"[DEBUG] User said: '{user_text}'")
            
            if not user_text.strip():
                print("[DEBUG] Empty transcription, ignoring")
                return
            
            # Check if this is a duplicate (same text within 3 seconds) - prevents loops
            current_time = time.time()
            if user_text.strip().lower() == last_processed_text and (current_time - last_processed_time) < 3.0:
                print(f"[DEBUG] Duplicate transcript detected (within 3s), ignoring to prevent loop: '{user_text}'")
                return
            
            # Check if this looks like the agent's own speech (starts with common agent phrases)
            agent_phrases = ["i understand", "i'd be happy", "thank you", "i've identified", "here are", "would you like"]
            if any(user_text.strip().lower().startswith(phrase) for phrase in agent_phrases):
                print(f"[DEBUG] Possible agent echo detected, ignoring: '{user_text[:50]}...'")
                return
            
            last_processed_text = user_text.strip().lower()
            last_processed_time = current_time
            
            conversation_history.append({"role": "user", "content": user_text})
            print(f"[DEBUG] Conversation history updated. Length: {len(conversation_history)}")
            
            # Get LLM response with tool calling
            try:
                print(f"[DEBUG] Making LLM API call with provider: {llm_provider}, model: {model}")
                # #region agent log
                debug_log("main.py:326", "About to call LLM", {"provider": llm_provider, "model": model, "user_text": user_text, "conversation_history_length": len(conversation_history)}, hypothesis_id="D")
                # #endregion
                
                # Prepare messages for LLM (convert to OpenAI format)
                # Add system prompt - be direct and concise, follow the booking flow
                # Include current user_phone status in system prompt so LLM knows if phone was already provided
                phone_status = f"Current user phone number: {user_phone if user_phone else 'NOT PROVIDED YET'}"
                system_prompt = f"""You are a booking assistant. Follow this flow strictly:

{phone_status}



                messages = [
                    {"role": "system", "content": system_prompt}
                ]
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
                
                # #region agent log
                debug_log("main.py:550", "LLM messages prepared", {"user_phone": user_phone, "phone_status_in_prompt": phone_status, "conversation_history_length": len(conversation_history), "last_user_msg": conversation_history[-1]["content"] if conversation_history else None}, hypothesis_id="A")
                # #endregion
                print(f"[DEBUG] System prompt phone status: {phone_status}")
                print(f"[DEBUG] Current user_phone variable: {user_phone}")
                
                # Make LLM API call
                if llm_provider == "anthropic":
                    # Use Anthropic client
                    response = anthropic_client.messages.create(
                        model=model,
                        max_tokens=1000,
                        messages=messages,
                        tools=TOOLS if TOOLS else None
                    )
                    
                    assistant_text = ""
                    tool_calls = []
                    
                    # Process Anthropic response
                    if response.content:
                        for content_block in response.content:
                            if content_block.type == "text":
                                assistant_text += content_block.text
                            elif content_block.type == "tool_use":
                                tool_calls.append({
                                    "id": content_block.id,
                                    "name": content_block.name,
                                    "arguments": json.dumps(content_block.input)
                                })
                else:
                 
                    try:
                        response = llm_client.chat.completions.create(
                            model=model,
                            messages=messages,
                            tools=TOOLS if TOOLS else None,
                            stream=False
                        )
                    except Exception as tool_error:
                        # Handle various errors: tool use, model not found, insufficient credits, rate limits
                        error_str = str(tool_error)
                        error_str_lower = error_str.lower()
                        
                        # Extract error code from exception (handle RateLimitError, APIStatusError, etc.)
                        error_code = None
                        if hasattr(tool_error, 'status_code'):
                            error_code = tool_error.status_code
                        elif hasattr(tool_error, 'response') and hasattr(tool_error.response, 'status_code'):
                            error_code = tool_error.response.status_code
                        elif hasattr(tool_error, 'code'):
                            error_code = tool_error.code
                        # Also check error string for HTTP codes
                        if error_code is None:
                            import re
                            code_match = re.search(r'\b(402|404|429)\b', error_str)
                            if code_match:
                                error_code = int(code_match.group(1))
                        # Check if it's a RateLimitError
                        from openai import RateLimitError, APIStatusError
                        if isinstance(tool_error, RateLimitError) or isinstance(tool_error, APIStatusError):
                            if error_code is None:
                                error_code = 429  # Assume rate limit if RateLimitError
                        
                        # Check if it's a recoverable error (tool use, 404, 402, 429)
                        if ("tool use" in error_str or "404" in error_str or "no endpoints" in error_str or 
                            "402" in error_str or "insufficient credits" in error_str or 
                            "429" in error_str or "rate limit" in error_str or
                            error_code in [402, 404, 429]):
                            
                            print(f"[WARNING] Model issue detected (code: {error_code}), trying free model without tools...")
                            # Try multiple free models with retry logic for rate limits
                            free_models = [
                                "meta-llama/llama-3.2-3b-instruct:free",
                                "google/gemini-2.0-flash-exp:free",
                            ]
                            
                            response = None
                            last_error = None
                            for idx, free_model in enumerate(free_models):
                                try:
                                    print(f"[DEBUG] Retrying with free model {idx+1}/{len(free_models)}: {free_model}")
                                    # Add exponential backoff delay for rate limit retries
                                    if error_code == 429:
                                        wait_time = min(5.0, 2.0 * (idx + 1))  # 2s, 4s, max 5s
                                        print(f"[DEBUG] Waiting {wait_time}s due to rate limit...")
                                        await asyncio.sleep(wait_time)
                                    
                                    # Try with tools first, then without if that fails
                                    try:
                                        response = llm_client.chat.completions.create(
                                            model=free_model,
                                            messages=messages,
                                            tools=TOOLS if TOOLS else None,
                                            stream=False
                                        )
                                    except Exception as tool_error_inner:
                                        # If tool use fails, try without tools but system prompt will guide behavior
                                        print(f"[WARNING] Tool use failed for {free_model}, retrying without tools (will rely on system prompt)...")
                                        response = llm_client.chat.completions.create(
                                            model=free_model,
                                            messages=messages,
                                            stream=False
                                        )
                                    print(f"[DEBUG] ✓ Successfully got response from {free_model}")
                                    break  # Success, exit loop
                                except Exception as free_model_error:
                                    last_error = free_model_error
                                    error_code_free = None
                                    
                                    # Check for RateLimitError type
                                    from openai import RateLimitError as RLE
                                    if isinstance(free_model_error, RLE):
                                        error_code_free = 429
                                    elif hasattr(free_model_error, 'status_code'):
                                        error_code_free = free_model_error.status_code
                                    elif hasattr(free_model_error, 'response') and hasattr(free_model_error.response, 'status_code'):
                                        error_code_free = free_model_error.response.status_code
                                    
                                    # Extract error code from error string
                                    if error_code_free is None:
                                        error_str_free = str(free_model_error).lower()
                                        if "429" in error_str_free or "rate limit" in error_str_free:
                                            error_code_free = 429
                                    
                                    # If rate limited, wait longer and retry once
                                    if error_code_free == 429:
                                        wait_time = min(5.0, 3.0 * (idx + 1))  # Longer wait: 3s, 6s, max 5s
                                        print(f"[WARNING] {free_model} rate limited, waiting {wait_time}s then retrying...")
                                        await asyncio.sleep(wait_time)
                                        
                                        # Retry once after waiting
                                        try:
                                            print(f"[DEBUG] Retrying {free_model} after rate limit wait...")
                                            response = llm_client.chat.completions.create(
                                                model=free_model,
                                                messages=messages,
                                                stream=False
                                            )
                                            print(f"[DEBUG] ✓ Successfully got response from {free_model} after retry")
                                            break  # Success
                                        except Exception as retry_error:
                                            print(f"[WARNING] Retry also failed for {free_model}: {str(retry_error)[:100]}...")
                                            last_error = retry_error
                                    else:
                                        print(f"[WARNING] {free_model} failed: {str(free_model_error)[:100]}...")
                                    
                                    # If not the last model, continue to next
                                    if idx < len(free_models) - 1:
                                        print(f"[WARNING] Trying next free model...")
                            
                            # If all free models failed, provide graceful fallback
                            if response is None:
                                # Only send fallback once to prevent multiple overlapping responses
                                if fallback_sent:
                                    print(f"[WARNING] Fallback already sent, skipping duplicate response")
                                    return  # Exit early to prevent duplicate responses
                                
                                fallback_sent = True
                                print(f"[ERROR] All free models failed due to rate limits/errors")
                                print(f"[DEBUG] Last error: {last_error}")
                                # Extract user's request from conversation
                                user_request = conversation_history[-1]["content"] if conversation_history else "book an appointment"
                                
                                # Provide a graceful fallback response that still helps the user
                                # Be more direct - don't mention technical issues
                                if "book" in user_request.lower() or "appointment" in user_request.lower():
                                    assistant_text = "I'd be happy to help you book an appointment. Please provide your phone number first, then I can show you available slots."
                                else:
                                    assistant_text = f"I understand you'd like to {user_request}. Could you please provide your phone number so I can help you?"
                                conversation_history.append({"role": "assistant", "content": assistant_text})
                                # Skip tool execution and speak the response
                                print(f"[DEBUG] Using fallback response due to model errors")
                                await say_text(assistant_text)
                                
                                # Reset fallback flag after a delay so it can be used again
                                async def reset_fallback():
                                    await asyncio.sleep(5.0)
                                    nonlocal fallback_sent
                                    fallback_sent = False
                                
                                asyncio.create_task(reset_fallback())
                                return  # Exit early since we handled the response
                        else:
                            raise
                    
                    assistant_text = ""
                    tool_calls = []
                    
                    # Process OpenAI-compatible response
                    choice = response.choices[0]
                    assistant_text = choice.message.content or ""
                    
                    # Check for tool calls
                    if choice.message.tool_calls:
                        for tool_call in choice.message.tool_calls:
                            tool_calls.append({
                                "id": tool_call.id,
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments or "{}"
                            })
                
                # If no tool calls but user wants to book/modify, try to parse intent and call tools directly
                if not tool_calls and assistant_text:
                    # Parse user intent from conversation to extract booking information
                    import re
                    from datetime import datetime, date
                    
                    # First, check conversation history for phone number that might have been mentioned earlier
                    if not user_phone:
                        print(f"[DEBUG] No phone yet, checking conversation history for phone number...")
                        # Check last 5 messages for phone numbers
                        for msg in reversed(conversation_history[-5:]):
                            if msg.get("role") == "user":
                                content = msg.get("content", "").lower()
                                # Normalize spoken digits
                                normalized_content = content
                                normalized_content = re.sub(r'\bplus\b', '+', normalized_content)
                                for word, digit in [('zero', '0'), ('one', '1'), ('two', '2'), ('three', '3'), 
                                                   ('four', '4'), ('five', '5'), ('six', '6'), ('seven', '7'), 
                                                   ('eight', '8'), ('nine', '9')]:
                                    normalized_content = re.sub(r'\b' + word + r'\b', digit, normalized_content)
                                
                                # Try to find phone number
                                phone_patterns = [
                                    r'\+1\s*(\d{10})', r'\b(\d{10})\b', r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',
                                    r'\+1\s*(\d{8,10})', r'\b(\d{8,10})\b'
                                ]
                                for pattern in phone_patterns:
                                    phone_match = re.search(pattern, normalized_content, re.IGNORECASE)
                                    if phone_match:
                                        if phone_match.groups():
                                            extracted = ''.join(re.sub(r'[-.\s()]', '', g) for g in phone_match.groups() if g)
                                        else:
                                            extracted = re.sub(r'[-.\s()+]', '', phone_match.group())
                                        digits = re.sub(r'\D', '', extracted)
                                        if len(digits) >= 8 and len(digits) <= 11:
                                            if digits.startswith('1') and len(digits) > 10:
                                                digits = digits[1:]
                                            extracted_phone = digits[:10]
                                            print(f"[DEBUG] Found phone in conversation history: {extracted_phone} from '{msg.get('content')[:50]}...'")
                                            user_phone = extracted_phone
                                            # Auto-call identify_user
                                            identify_result = await identify_user(extracted_phone)
                                            tool_calls.append({
                                                "id": "auto-identify-history",
                                                "name": "identify_user",
                                                "arguments": json.dumps({"phone_number": extracted_phone})
                                            })
                                            assistant_text = f"{identify_result} Would you like to see available appointment slots?"
                                            break
                                if user_phone:
                                    break
                    
                    # Get the latest user message
                    user_msg = user_text.lower() if user_text else ""
                    assistant_msg = assistant_text.lower()
                    
                    # Check if user wants to book an appointment
                    if any(keyword in user_msg for keyword in ["book", "schedule", "appointment", "slot", "available"]):
                        # Extract phone number from conversation history
                        extracted_phone = user_phone
                        if not extracted_phone:
                            # Try to find phone number in recent messages
                            for msg in reversed(conversation_history[-5:]):
                                if msg.get("role") == "user":
                                    phone_match = re.search(r'\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', msg.get("content", ""))
                                    if phone_match:
                                        extracted_phone = re.sub(r'[-.\s]', '', phone_match.group())
                                        break
                        
                        # Extract date (various formats: "January 15", "Jan 15", "15th", "2024-01-15", etc.)
                        date_match = None
                        for msg in reversed(conversation_history[-3:]):
                            content = msg.get("content", "").lower()
                            # Try common date patterns
                            patterns = [
                                r'january\s+(\d{1,2})|jan\s+(\d{1,2})',
                                r'february\s+(\d{1,2})|feb\s+(\d{1,2})',
                                r'march\s+(\d{1,2})|mar\s+(\d{1,2})',
                                r'april\s+(\d{1,2})|apr\s+(\d{1,2})',
                                r'may\s+(\d{1,2})',
                                r'june\s+(\d{1,2})|jun\s+(\d{1,2})',
                                r'july\s+(\d{1,2})|jul\s+(\d{1,2})',
                                r'august\s+(\d{1,2})|aug\s+(\d{1,2})',
                                r'september\s+(\d{1,2})|sep\s+(\d{1,2})',
                                r'october\s+(\d{1,2})|oct\s+(\d{1,2})',
                                r'november\s+(\d{1,2})|nov\s+(\d{1,2})',
                                r'december\s+(\d{1,2})|dec\s+(\d{1,2})',
                                r'(\d{4}-\d{2}-\d{2})',  # YYYY-MM-DD
                            ]
                            for pattern in patterns:
                                match = re.search(pattern, content)
                                if match:
                                    date_match = match.group(0)
                                    break
                            if date_match:
                                break
                        
                        # Extract time (e.g., "10 AM", "10:00", "14:00")
                        time_match = None
                        for msg in reversed(conversation_history[-3:]):
                            content = msg.get("content", "").lower()
                            time_patterns = [
                                r'(\d{1,2})\s*(am|pm)',
                                r'(\d{1,2}):(\d{2})\s*(am|pm)?',
                                r'at\s+(\d{1,2})',
                            ]
                            for pattern in time_patterns:
                                match = re.search(pattern, content)
                                if match:
                                    time_str = match.group(0)
                                    # Convert to 24-hour format if needed
                                    if 'am' in time_str or 'pm' in time_str:
                                        hour = int(re.search(r'(\d{1,2})', time_str).group(1))
                                        if 'pm' in time_str and hour < 12:
                                            hour += 12
                                        elif 'am' in time_str and hour == 12:
                                            hour = 0
                                        time_match = f"{hour:02d}:00"
                                    else:
                                        hour_match = re.search(r'(\d{1,2})', time_str)
                                        if hour_match:
                                            hour = int(hour_match.group(1))
                                            time_match = f"{hour:02d}:00"
                                    break
                            if time_match:
                                break
                        
                        # If we have booking info, call book_appointment directly
                        if "book" in user_msg and extracted_phone and date_match and time_match:
                            # Convert date to YYYY-MM-DD format
                            try:
                                # Try to parse and format the date
                                today = date.today()
                                year = today.year
                                
                                # Simple date parsing (assume current year if not specified)
                                month_names = {
                                    'january': 1, 'jan': 1, 'february': 2, 'feb': 2,
                                    'march': 3, 'mar': 3, 'april': 4, 'apr': 4,
                                    'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
                                    'august': 8, 'aug': 8, 'september': 9, 'sep': 9,
                                    'october': 10, 'oct': 10, 'november': 11, 'nov': 11,
                                    'december': 12, 'dec': 12
                                }
                                
                                date_str = None
                                if '-' in date_match:
                                    date_str = date_match  # Already in YYYY-MM-DD format
                                else:
                                    # Extract month and day
                                    for month_name, month_num in month_names.items():
                                        if month_name in date_match.lower():
                                            day_match = re.search(r'(\d{1,2})', date_match)
                                            if day_match:
                                                day = int(day_match.group(1))
                                                # Create date (assume current year)
                                                try:
                                                    appointment_date = date(year, month_num, day)
                                                    # If date is in the past, assume next year
                                                    if appointment_date < today:
                                                        appointment_date = date(year + 1, month_num, day)
                                                    date_str = appointment_date.strftime("%Y-%m-%d")
                                                    break
                                                except ValueError:
                                                    pass
                                
                                if date_str and time_match and extracted_phone:
                                    print(f"[DEBUG] Auto-calling book_appointment: date={date_str}, time={time_match}, phone={extracted_phone}")
                                    # Call tool directly
                                    booking_result = await book_appointment(date_str, time_match, extracted_phone)
                                    tool_calls.append({
                                        "id": "auto-booking",
                                        "name": "book_appointment",
                                        "arguments": json.dumps({"date": date_str, "time": time_match, "phone_number": extracted_phone})
                                    })
                                    # Update assistant text with booking result
                                    assistant_text = booking_result
                                    # Update user_phone if not set
                                    if not user_phone:
                                        user_phone = extracted_phone
                            except Exception as parse_error:
                                print(f"[WARNING] Failed to parse booking info: {parse_error}")
                        
                        # Check if user is providing phone number
                        # First, convert spoken digits to numeric format (e.g., "plus one two three" -> "+1 123")
                        spoken_digits_map = {
                            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
                            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
                        }
                        normalized_text = user_msg.lower()
                        # Convert "plus" to "+" first
                        normalized_text = re.sub(r'\bplus\b', '+', normalized_text)
                        # Then convert spoken digits
                        for word, digit in spoken_digits_map.items():
                            normalized_text = re.sub(r'\b' + word + r'\b', digit, normalized_text)
                        
                        print(f"[DEBUG] Normalized text for phone extraction: '{user_msg}' -> '{normalized_text}'")
                        # #region agent log
                        debug_log("main.py:920", "Phone normalization", {"original": user_msg, "normalized": normalized_text}, hypothesis_id="A")
                        # #endregion
                        
                        # Improved regex to handle: +1 234567890, (123) 456-7890, 123-456-7890, 1234567890, spoken digits, etc.
                        phone_patterns = [
                            r'\+1\s*(\d{10})',  # +1 1234567890
                            r'\+1\s*(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',  # +1 123-456-7890
                            r'\+1\s*(\d{8,10})',  # +1 12345678 or +1 1234567890
                            r'\b(\d{10})\b',  # 1234567890 (10 digits)
                            r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',  # 123-456-7890
                            r'\((\d{3})\)\s*(\d{3})[-.\s]?(\d{4})',  # (123) 456-7890
                            # Spoken digits patterns (after normalization - note: "plus 1" becomes "+1")
                            r'\+1\s*([1-9]\d{6,9})',  # +1 followed by 7-10 digits (allows incomplete)
                            r'\+1\s*(\d{8,10})',  # +1 followed by 8-10 digits
                            r'\b([1-9]\d{6,9})\b',  # 7-10 digits starting with 1-9 (allows partial)
                            r'\b(\d{8,10})\b',  # 8-10 digit number
                        ]
                        
                        phone_match = None
                        # Try normalized text first (for spoken digits like "plus one two three")
                        for pattern in phone_patterns:
                            phone_match = re.search(pattern, normalized_text, re.IGNORECASE)
                            if phone_match:
                                print(f"[DEBUG] Phone match found in normalized text: pattern='{pattern}', match='{phone_match.group()}'")
                                break
                        # If no match, try original text
                        if not phone_match:
                            for pattern in phone_patterns:
                                phone_match = re.search(pattern, user_msg, re.IGNORECASE)
                                if phone_match:
                                    print(f"[DEBUG] Phone match found in original text: pattern='{pattern}', match='{phone_match.group()}'")
                                    break
                        
                        # Also check if user mentioned phone/number keywords
                        if phone_match or any(keyword in user_msg for keyword in ["phone", "number", "contact"]):
                            if phone_match:
                                # Extract phone digits (handle groups if regex has parentheses)
                                if phone_match.groups():
                                    extracted_phone = ''.join(re.sub(r'[-.\s()]', '', g) for g in phone_match.groups() if g)
                                else:
                                    extracted_phone = re.sub(r'[-.\s()+]', '', phone_match.group())
                                
                                # Remove country code prefix if present (e.g., +1, 1)
                                if extracted_phone.startswith('1') and len(extracted_phone) > 10:
                                    extracted_phone = extracted_phone[1:]  # Remove leading '1'
                                
                                # Validate we have a reasonable phone number (7-10 digits, allow partial for now)
                                digits_only = re.sub(r'\D', '', extracted_phone)
                                if len(digits_only) >= 7 and len(digits_only) <= 11:
                                    # If less than 10 digits, pad with zeros (or keep as-is and ask for more)
                                    if len(digits_only) < 10:
                                        # User might be providing incomplete number - ask for the rest
                                        missing = 10 - len(digits_only)
                                        print(f"[DEBUG] Incomplete phone number detected: {digits_only} (need {missing} more digits)")
                                        assistant_text = f"I heard {digits_only}, but I need a complete 10-digit phone number. Could you provide the remaining {missing} digits?"
                                        conversation_history.append({"role": "assistant", "content": assistant_text})
                                        await say_text(assistant_text)
                                        return  # Exit early, wait for user to complete the number
                                    else:
                                        extracted_phone = digits_only[:10]  # Take first 10 digits
                                        print(f"[DEBUG] Auto-calling identify_user: phone={extracted_phone} (extracted from: '{phone_match.group()}')")
                                        # #region agent log
                                        debug_log("main.py:890", "Auto-detected phone number", {"phone": extracted_phone, "user_msg": user_msg, "match": phone_match.group()}, hypothesis_id="A")
                                        # #endregion
                                        identify_result = await identify_user(extracted_phone)
                                        tool_calls.append({
                                            "id": "auto-identify",
                                            "name": "identify_user",
                                            "arguments": json.dumps({"phone_number": extracted_phone})
                                        })
                                        # Guide user to next step after identification
                                        assistant_text = f"{identify_result} Would you like to see available appointment slots?"
                                        user_phone = extracted_phone
                                        print(f"[DEBUG] ✓ Phone identified, guiding to slots: {user_phone}")
                                        # #region agent log
                                        debug_log("main.py:900", "Phone identified, guiding to slots", {"phone": user_phone}, hypothesis_id="B")
                                        # #endregion
                                else:
                                    print(f"[DEBUG] Phone number validation failed: {digits_only} (length: {len(digits_only)}, need 7-11)")
                                    # If user mentioned phone but we couldn't extract it, don't do anything - LLM will ask
                        
                        # Check if user wants available slots
                        elif any(keyword in user_msg for keyword in ["available", "slots", "times", "when"]):
                            print(f"[DEBUG] Auto-calling fetch_slots")
                            slots_result = await fetch_slots()
                            tool_calls.append({
                                "id": "auto-fetch-slots",
                                "name": "fetch_slots",
                                "arguments": "{}"
                            })
                            assistant_text = slots_result
                
                # Execute tool calls if any
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = {}
                        
                        # Parse arguments
                        if tool_call["arguments"]:
                            try:
                                tool_args = json.loads(tool_call["arguments"])
                            except:
                                pass
                        
                        # Execute tool
                        if tool_name in TOOL_FUNCTIONS:
                            tool_func = TOOL_FUNCTIONS[tool_name]
                            tool_result = await tool_func(**tool_args)
                            
                            # Update user_phone if identified
                            if tool_name == "identify_user" and "phone_number" in tool_args:
                                user_phone = tool_args["phone_number"]
                                print(f"[DEBUG] ✓ User phone updated: {user_phone}")
                                # #region agent log
                                debug_log("main.py:932", "User phone identified", {"phone": user_phone}, hypothesis_id="B")
                                # #endregion
                                # After identifying user, guide them to next step
                                if not assistant_text or "thank you" in assistant_text.lower():
                                    assistant_text = f"Thank you! I've identified you with phone number {user_phone}. Would you like to see available appointment slots?"
                            
                            # Handle end_conversation
                            if tool_name == "end_conversation":
                                summary = await generate_summary(conversation_history, user_phone, conversation_id)
                                # Send summary via data channel
                                await ctx.room.local_participant.publish_data(
                                    summary.encode(),
                                    topic="conversation_summary"
                                )
                                assistant_text = f"Thank you for the conversation! Here's a summary: {summary}"
                            else:
                                # Add tool result to conversation
                                assistant_text += f"\n\nTool Result: {tool_result}"
                            
                            # Add tool result to conversation history for next LLM call
                            conversation_history.append({
                                "role": "tool",
                                "content": tool_result,
                                "tool_call_id": tool_call["id"]
                            })
                
                print(f"[DEBUG] LLM response received. Text: '{assistant_text[:100] if assistant_text else 'None'}...', Tool calls: {len(tool_calls)}")
                # #region agent log
                debug_log("main.py:427", "LLM response received", {"assistant_text_length": len(assistant_text) if assistant_text else 0, "assistant_text_preview": assistant_text[:100] if assistant_text else None, "tool_calls_count": len(tool_calls), "has_assistant_text": bool(assistant_text)}, hypothesis_id="D")
                # #endregion
                
                # Check if LLM is just echoing user input (common issue with free models)
                if assistant_text and user_text:
                    assistant_lower = assistant_text.lower()
                    user_lower = user_text.lower()
                    # If response starts with "I understand you'd like to" or contains user's exact words, replace it
                    if ("i understand you'd like to" in assistant_lower or 
                        "i understand you'd like" in assistant_lower or
                        (user_lower in assistant_lower and len(user_lower) > 5)):  # User's exact words in response
                        print(f"[DEBUG] Detected echoing response, replacing with directive action")
                        # Replace with helpful response based on context
                        if not user_phone:
                            assistant_text = "Could you please provide your phone number so I can help you book an appointment?"
                        elif "slot" in assistant_lower or "available" in assistant_lower or "time" in assistant_lower:
                            assistant_text = "Would you like to see available appointment slots?"
                        else:
                            assistant_text = "How can I help you book an appointment today?"
                
                if assistant_text:
                    conversation_history.append({"role": "assistant", "content": assistant_text})
                    print(f"[DEBUG] Conversation history updated with assistant response")
                    
                    # Send tool calls info via data channel for UI display
                    if tool_calls:
                        print(f"[DEBUG] Sending {len(tool_calls)} tool calls via data channel")
                        await ctx.room.local_participant.publish_data(
                            json.dumps({"tool_calls": tool_calls}).encode(),
                            topic="tool_calls"
                        )
                    
                    # Speak response
                    print(f"[DEBUG] Speaking response: '{assistant_text[:50]}...'")
                    await say_text(assistant_text)
                    print(f"[DEBUG] ✓ Response spoken successfully")
                else:
                    print(f"[WARNING] LLM returned empty response")
            
            except Exception as e:
                # #region agent log
                debug_log("main.py:456", "Exception in on_user_speech (outer)", {"error": str(e), "error_type": type(e).__name__}, hypothesis_id="C")
                # #endregion
                error_msg = "I apologize, but I encountered an error. Please try again."
                print(f"[ERROR] Error in on_user_speech: {e}")
                import traceback
                traceback.print_exc()
                print(f"[DEBUG] Speaking error message")
                await say_text(error_msg)
        
        # Also listen for participant connections to verify audio tracks
        def on_participant_connected(participant: rtc.RemoteParticipant):
            """Handle participant connection - must be synchronous"""
            print(f"[DEBUG] Participant connected: {participant.identity}")
            
            # Use asyncio.create_task for async work
            async def check_audio_tracks():
                audio_tracks = [p for p in participant.track_publications.values() if p.kind == rtc.TrackKind.KIND_AUDIO]
                print(f"[DEBUG] Participant audio tracks: {len(audio_tracks)}")
                
                # Subscribe to any existing audio tracks
                for pub in audio_tracks:
                    if pub.track:
                        print(f"[DEBUG] Found audio track: {pub.sid}")
                    else:
                        print(f"[DEBUG] Audio track publication exists but no track yet: {pub.sid}")
            
            # Create task for async work
            asyncio.create_task(check_audio_tracks())
        
        ctx.room.on("participant_connected", on_participant_connected)
        
        # Start transcription using STT stream
        print("[DEBUG] Starting STT transcription...")
        print(f"[DEBUG] Local participant identity: {ctx.room.local_participant.identity}")
        print(f"[DEBUG] Room participants: {[p.identity for p in ctx.room.remote_participants.values()]}")
        
        # Note: RemoteAudioTrack doesn't expose audio frames directly
        # We need to use room transcription events which Deepgram publishes automatically
        # However, those events require STT to be started first
        # Since we can't manually push frames from RemoteAudioTrack, we'll use a different approach:
        # Use the LiveKit agents' built-in room audio handling via transcription events
        
        # Start STT transcription using room events
        # Deepgram will automatically transcribe audio when tracks are subscribed
        print("[DEBUG] Ensuring all audio tracks are subscribed for STT...")
        
        # Subscribe to all remote audio tracks
        for participant in ctx.room.remote_participants.values():
            print(f"[DEBUG] Checking participant: {participant.identity}")
            for publication in participant.track_publications.values():
                if publication.kind == rtc.TrackKind.KIND_AUDIO:
                    print(f"[DEBUG] Found audio publication: {publication.sid}")
                    if not publication.track:
                        print(f"[DEBUG] Subscribing to audio track: {publication.sid}")
                        await publication.subscribe()
        
        # Listen for new tracks
        def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != ctx.room.local_participant.identity:
                print(f"[DEBUG] Audio track subscribed: {publication.sid} from {participant.identity}")
        
        ctx.room.on("track_subscribed", on_track_subscribed)
        
        # Create STT stream (one stream per room to handle all participants)
        # Configure stream with interim results and language
        speech_stream = stt.stream(
            language="en-US",  # Explicitly set language
        )
        print("[DEBUG] STT stream created with language=en-US, endpointing_ms=300ms")
        
        # Store active audio streams to avoid duplicates
        active_audio_streams = {}
        # Track which participant/track is currently sending audio
        # Use dict to map track_sid to participant so we can look it up later
        track_to_participant = {}  # track_sid -> participant
        # Track which track is currently active (for associating STT events with tracks)
        active_track_for_stt = None  # Will be set during frame processing
        current_participant = None
        current_track_sid = None
        # Store latest interim transcript as fallback (using dict to allow modification in nested functions)
        latest_interim_data = {"transcript": None, "track_sid": None}
        
        async def process_audio_track(track: rtc.RemoteAudioTrack, participant: rtc.RemoteParticipant):
            """Process audio frames from a track and push to STT stream"""
            global current_participant, current_track_sid, active_track_for_stt
            
            if track.sid in active_audio_streams:
                print(f"[DEBUG] Audio stream already processing track: {track.sid}")
                return
            
            print(f"[DEBUG] Starting audio stream processing for track: {track.sid}, participant: {participant.identity}")
            active_audio_streams[track.sid] = True
            # Store mapping from track_sid to participant for later lookup
            track_to_participant[track.sid] = participant
            current_participant = participant
            current_track_sid = track.sid
            active_track_for_stt = track.sid  # Mark this as the active track for STT events
            print(f"[DEBUG] Stored participant mapping: track={track.sid} -> participant={participant.identity}")
            # #region agent log
            debug_log("main.py:546", "Participant mapping stored", {"track_sid": track.sid, "participant_identity": participant.identity, "track_to_participant_keys": list(track_to_participant.keys()), "active_track_for_stt": active_track_for_stt}, hypothesis_id="A")
            # #endregion
            
            try:
                # Create AudioStream to iterate over frames from the track
                audio_stream = rtc.AudioStream(track)
                print(f"[DEBUG] AudioStream created for track: {track.sid}")
                
                # Push audio frames to STT stream (less verbose logging)
                frame_count = 0
                async for audio_event in audio_stream:
                    if hasattr(audio_event, 'frame'):
                        frame = audio_event.frame
                        frame_count += 1
                        if frame_count % 50 == 0:  # Log every 50 frames
                            print(f"[DEBUG] Pushed {frame_count} frames to STT: track={track.sid}, sample_rate={frame.sample_rate}")
                        try:
                            # Set active track BEFORE pushing frame so STT events can be associated
                            active_track_for_stt = track.sid
                            speech_stream.push_frame(frame)
                        except (RuntimeError, Exception) as e:
                            error_str = str(e).lower()
                            # Check if stream is closed or ended
                            if ("closed" in error_str or "ended" in error_str or 
                                "input ended" in error_str or "is closed" in error_str or
                                "cannot write to closing" in error_str):
                                print(f"[ERROR] STT stream closed/ended - stopping frame processing. Error: {e}")
                                # #region agent log
                                debug_log("main.py:1081", "STT stream closed/ended", {"error": str(e), "track_sid": track.sid}, hypothesis_id="D")
                                # #endregion
                                # Don't continue - the stream is closed, frames won't be processed
                                break  # Exit the frame processing loop
                            else:
                                # Other errors - log but continue
                                print(f"[WARNING] Error pushing frame to STT (non-fatal): {e}")
                                # Don't break - continue processing
            except Exception as e:
                print(f"[ERROR] Error processing audio track {track.sid}: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Remove from active streams (but keep participant mapping for transcript processing)
                active_audio_streams.pop(track.sid, None)
                if current_track_sid == track.sid:
                    current_participant = None
                    current_track_sid = None
                # Don't remove from track_to_participant - we need it for transcript events
                print(f"[DEBUG] Stopped processing audio track: {track.sid} (keeping participant mapping)")
        
        # Simple wrapper class to mimic rtc.Transcription
        # (rtc.Transcription objects are read-only and can't be created manually)
        class SimpleTranscription:
            """Simple wrapper to mimic rtc.Transcription for on_user_speech"""
            def __init__(self, text, alternatives=None, participant=None, track_sid=None, language="en-US"):
                self.text = text
                # Create alternatives list if needed
                if alternatives is None:
                    # Create a simple alternative object
                    class SimpleAlternative:
                        def __init__(self, text, confidence=1.0, language="en-US"):
                            self.text = text
                            self.confidence = confidence
                            self.language = language
                    self.alternatives = [SimpleAlternative(text)]
                else:
                    self.alternatives = alternatives
                self.participant = participant
                self.track_sid = track_sid
                self.language = language
        
        # Process STT events
        async def consume_stt_events():
            """Consume STT stream events"""
            print("[DEBUG] STT event consumer started")
            try:
                # Keep stream open while processing
                try:
                    async with speech_stream:
                        print("[DEBUG] STT stream active, waiting for events...")
                        # #region agent log
                        debug_log("main.py:631", "STT stream context entered", {}, hypothesis_id="D")
                        # #endregion
                        
                        # Iterate over speech events from the stream
                        try:
                            async for event in speech_stream:
                                # #region agent log
                                debug_log("main.py:635", "STT event received in loop", {"event_type": type(event).__name__}, hypothesis_id="D")
                                # #endregion
                                print(f"[DEBUG] STT event received: type={type(event).__name__}")
                            
                                if isinstance(event, agents.stt.SpeechEvent):
                                    event_type = event.type
                                    print(f"[DEBUG] SpeechEvent type: {event_type}, alternatives={len(event.alternatives) if event.alternatives else 0}")
                                    
                                    # Process final transcripts
                                    if event_type == agents.stt.SpeechEventType.FINAL_TRANSCRIPT:
                                        print(f"[DEBUG] ✓ FINAL_TRANSCRIPT received! alternatives={len(event.alternatives) if event.alternatives else 0}")
                                        # #region agent log
                                        debug_log("main.py:654", "FINAL_TRANSCRIPT event received", {"alternatives_count": len(event.alternatives) if event.alternatives else 0}, hypothesis_id="D")
                                        # #endregion
                                        # Get track_sid from latest interim data if available (this is the track that generated the speech)
                                        stored_track_sid = latest_interim_data.get("track_sid")
                                        latest_interim_data["transcript"] = None  # Clear interim since we have final
                                        if event.alternatives and len(event.alternatives) > 0:
                                            # Get participant from track mapping - use stored_track_sid first, then active_track_for_stt, then current_track_sid
                                            track_sid = stored_track_sid or active_track_for_stt or current_track_sid
                                            participant = track_to_participant.get(track_sid) if track_sid else current_participant
                                            
                                            # If still None, try to get from any track (likely the only one)
                                            if not participant and track_to_participant:
                                                participant = list(track_to_participant.values())[0]
                                                track_sid = list(track_to_participant.keys())[0]
                                                print(f"[DEBUG] Found participant from track mapping: track={track_sid}, participant={participant.identity}")
                                            
                                            print(f"[DEBUG] Participant for transcript: {participant.identity if participant else 'None'}, Local: {ctx.room.local_participant.identity}, track={track_sid}, stored_track_sid={stored_track_sid}, active_track={active_track_for_stt}")
                                            # #region agent log
                                            debug_log("main.py:656", "Participant lookup for FINAL_TRANSCRIPT", {"participant_identity": participant.identity if participant else None, "local_identity": ctx.room.local_participant.identity, "track_sid": track_sid, "stored_track_sid": stored_track_sid, "active_track_for_stt": active_track_for_stt, "current_track_sid": current_track_sid, "track_to_participant_keys": list(track_to_participant.keys())}, hypothesis_id="A")
                                            # #endregion
                                            if participant and participant.identity != ctx.room.local_participant.identity:
                                                user_text = event.alternatives[0].text
                                                print(f"[DEBUG] ✓ Processing FINAL user speech from {participant.identity}: '{user_text}'")
                                                
                                                # Create transcription object using SimpleTranscription wrapper
                                                transcription = SimpleTranscription(
                                                    text=user_text,
                                                    participant=participant,
                                                    track_sid=track_sid or current_track_sid or "",
                                                    language=event.alternatives[0].language if event.alternatives else "en-US",
                                                )
                                                print(f"[DEBUG] Calling on_user_speech with: '{user_text}'")
                                                # #region agent log
                                                debug_log("main.py:679", "About to call on_user_speech", {"user_text": user_text, "participant_identity": participant.identity}, hypothesis_id="B")
                                                # #endregion
                                                try:
                                                    await on_user_speech(transcription)
                                                    # #region agent log
                                                    debug_log("main.py:631", "on_user_speech completed successfully", {"user_text": user_text}, hypothesis_id="B")
                                                    # #endregion
                                                    print(f"[DEBUG] on_user_speech completed")
                                                except Exception as e:
                                                    # #region agent log
                                                    debug_log("main.py:634", "on_user_speech exception", {"error": str(e), "error_type": type(e).__name__}, hypothesis_id="C")
                                                    # #endregion
                                                    print(f"[ERROR] Exception in on_user_speech: {e}")
                                                    import traceback
                                                    traceback.print_exc()
                                                    raise
                                            else:
                                                # #region agent log
                                                debug_log("main.py:632", "Ignoring FINAL transcription - participant mismatch", {"participant_identity": participant.identity if participant else None, "local_identity": ctx.room.local_participant.identity}, hypothesis_id="F")
                                                # #endregion
                                                print(f"[WARNING] Ignoring FINAL transcription - participant={participant.identity if participant else 'None'}, local={ctx.room.local_participant.identity}")
                                        else:
                                            print(f"[DEBUG] No alternatives in FINAL_TRANSCRIPT event")
                                    elif event_type == agents.stt.SpeechEventType.INTERIM_TRANSCRIPT:
                                        # Log interim results - we'll process the latest one if no final arrives
                                        print(f"[DEBUG] ✓ INTERIM_TRANSCRIPT received! alternatives={len(event.alternatives) if event.alternatives else 0}")
                                        if event.alternatives and len(event.alternatives) > 0:
                                            # Find which track this came from - use active_track_for_stt (most reliable) or fallback
                                            track_sid = active_track_for_stt or current_track_sid
                                            if not track_sid and track_to_participant:
                                                track_sid = list(track_to_participant.keys())[0]
                                            latest_interim_data["transcript"] = event  # Store latest interim transcript
                                            latest_interim_data["track_sid"] = track_sid  # Store track_sid so FINAL_TRANSCRIPT can use it
                                            print(f"[DEBUG] ✓ Interim transcript stored: '{event.alternatives[0].text}' (track={track_sid})")
                                            # #region agent log
                                            debug_log("main.py:767", "INTERIM_TRANSCRIPT received", {"text": event.alternatives[0].text, "track_sid": track_sid, "active_track_for_stt": active_track_for_stt, "current_track_sid": current_track_sid}, hypothesis_id="A")
                                            # #endregion
                                        else:
                                            print(f"[DEBUG] WARNING: INTERIM_TRANSCRIPT received but no alternatives!")
                                    elif event_type == agents.stt.SpeechEventType.START_OF_SPEECH:
                                        print(f"[DEBUG] ✓ Start of speech detected - clearing previous interim")
                                        latest_interim_data["transcript"] = None  # Reset interim transcript
                                        latest_interim_data["track_sid"] = None  # Also clear track_sid
                                    elif event_type == agents.stt.SpeechEventType.END_OF_SPEECH:
                                        print(f"[DEBUG] End of speech detected - waiting for FINAL_TRANSCRIPT event...")
                                        # If no FINAL_TRANSCRIPT arrives within 2 seconds, use latest interim
                                        async def fallback_to_interim():
                                            await asyncio.sleep(2.0)  # Wait 2 seconds for final transcript
                                            print(f"[DEBUG] Fallback timer expired, checking for interim transcript...")
                                            interim_event = latest_interim_data.get("transcript")
                                            track_sid = latest_interim_data.get("track_sid")
                                            print(f"[DEBUG] Latest interim event: {interim_event}, track_sid: {track_sid}")
                                            if interim_event and interim_event.alternatives:
                                                print(f"[DEBUG] ✓ No FINAL_TRANSCRIPT received, using latest interim: '{interim_event.alternatives[0].text}'")
                                                # Get participant from track mapping
                                                participant = track_to_participant.get(track_sid) if track_sid else current_participant
                                                
                                                # If still None, try to get from any track
                                                if not participant and track_to_participant:
                                                    participant = list(track_to_participant.values())[0]
                                                    track_sid = list(track_to_participant.keys())[0]
                                                    print(f"[DEBUG] Found participant from track mapping: track={track_sid}, participant={participant.identity}")
                                                
                                                print(f"[DEBUG] Participant for fallback: {participant.identity if participant else 'None'}, Local: {ctx.room.local_participant.identity}, track={track_sid}")
                                                if participant and participant.identity != ctx.room.local_participant.identity:
                                                    user_text = interim_event.alternatives[0].text
                                                    print(f"[DEBUG] ✓ Processing interim transcript as final: '{user_text}'")
                                                    try:
                                                        # Use SimpleTranscription wrapper instead of rtc.Transcription
                                                        transcription = SimpleTranscription(
                                                            text=user_text,
                                                            participant=participant,
                                                            track_sid=track_sid or current_track_sid or "",
                                                            language=interim_event.alternatives[0].language if interim_event.alternatives else "en-US",
                                                        )
                                                        print(f"[DEBUG] Calling on_user_speech with interim transcript: '{user_text}'")
                                                        await on_user_speech(transcription)
                                                        print(f"[DEBUG] ✓ on_user_speech completed successfully")
                                                    except Exception as e:
                                                        print(f"[ERROR] Error in fallback_to_interim: {e}")
                                                        import traceback
                                                        traceback.print_exc()
                                                else:
                                                    # #region agent log
                                                    debug_log("main.py:691", "Cannot process interim - participant mismatch", {"participant_identity": participant.identity if participant else None, "local_identity": ctx.room.local_participant.identity}, hypothesis_id="F")
                                                    # #endregion
                                                    print(f"[WARNING] Cannot process interim - participant={participant.identity if participant else 'None'}, local={ctx.room.local_participant.identity}")
                                                latest_interim_data["transcript"] = None  # Clear after processing
                                            else:
                                                print(f"[DEBUG] No interim transcript available for fallback")
                                        asyncio.create_task(fallback_to_interim())
                                    elif event_type == agents.stt.SpeechEventType.RECOGNITION_USAGE:
                                        # This is normal - just usage metrics
                                        if event.recognition_usage:
                                            print(f"[DEBUG] Recognition usage: {event.recognition_usage.audio_duration:.2f}s of audio processed")
                                            print(f"[DEBUG] NOTE: If you see usage but no transcripts, Deepgram might not be detecting speech")
                                            print(f"[DEBUG] Try: 1) Speak louder/clearer 2) Check microphone permissions 3) Wait 1-2 seconds after speaking")
                                    else:
                                        print(f"[DEBUG] Other event type: {event_type}")
                                else:
                                    print(f"[DEBUG] Event is not a SpeechEvent: {type(event)}")
                        except StopAsyncIteration:
                            # Stream ended normally - async for loop will exit naturally
                            print(f"[DEBUG] STT stream ended normally")
                        except Exception as e:
                            error_str = str(e).lower()
                            # Check if it's a connection error (stream closed)
                            if ("closed" in error_str or "cannot write to closing" in error_str or 
                                "connection" in error_str or "disconnected" in error_str or
                                "connection reset" in error_str or "connection closed" in error_str):
                                print(f"[WARNING] STT stream connection error (stream may be closed): {e}")
                                # Stream closed - async for loop will exit naturally
                            else:
                                print(f"[ERROR] STT event consumer error: {e}")
                                import traceback
                                traceback.print_exc()
                                # Let exception propagate - it will exit the async for loop naturally
                except Exception as e:
                    # Handle errors from the async with context manager
                    error_str = str(e).lower()
                    if ("closed" in error_str or "cannot write to closing" in error_str or 
                        "connection" in error_str or "disconnected" in error_str):
                        print(f"[WARNING] STT stream context error (stream closed): {e}")
                    else:
                        print(f"[ERROR] STT stream context error: {e}")
                        import traceback
                        traceback.print_exc()
            except Exception as e:
                # Handle errors from the consume_stt_events function
                print(f"[ERROR] STT event consumer function error: {e}")
                import traceback
                traceback.print_exc()
        
        # Subscribe to tracks and process audio
        def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            """Handle when a track is subscribed"""
            print(f"[DEBUG] Track subscribed: kind={track.kind}, participant={participant.identity}, track_sid={publication.sid}")
            if track.kind == rtc.TrackKind.KIND_AUDIO and participant.identity != ctx.room.local_participant.identity:
                print(f"[DEBUG] ✓ User audio track subscribed: {publication.sid} from {participant.identity} - starting processing")
                # Process audio track
                asyncio.create_task(process_audio_track(track, participant))
        
        ctx.room.on("track_subscribed", on_track_subscribed)
        print(f"[DEBUG] Registered track_subscribed event handler")
        
        # Process existing tracks
        print(f"[DEBUG] Checking for existing remote participants: {len(ctx.room.remote_participants)}")
        for participant in ctx.room.remote_participants.values():
            print(f"[DEBUG] Processing participant: {participant.identity}")
            print(f"[DEBUG] Participant has {len(participant.track_publications)} track publications")
            for publication in participant.track_publications.values():
                print(f"[DEBUG] Found publication: kind={publication.kind}, sid={publication.sid}, subscribed={publication.is_subscribed if hasattr(publication, 'is_subscribed') else 'N/A'}")
                if publication.kind == rtc.TrackKind.KIND_AUDIO:
                    print(f"[DEBUG] Found existing audio publication: {publication.sid}")
                    if publication.track:
                        # Track already subscribed
                        print(f"[DEBUG] Track already subscribed, starting processing")
                        asyncio.create_task(process_audio_track(publication.track, participant))
                    else:
                        # Subscribe to track
                        print(f"[DEBUG] Subscribing to audio track: {publication.sid}")
                        try:
                            await publication.subscribe()
                            print(f"[DEBUG] ✓ Subscribed to track: {publication.sid}")
                        except Exception as e:
                            print(f"[ERROR] Failed to subscribe to track: {e}")
                        import traceback
                        traceback.print_exc()
        
        # Start consuming STT events in background
        stt_task = asyncio.create_task(consume_stt_events())
        print("[DEBUG] STT transcription started")
        
        # Keep agent alive
        try:
            await asyncio.sleep(3600)  # Run for up to 1 hour
        finally:
            stt_task.cancel()
    except Exception as e:
        print(f"[ERROR] Critical error in entrypoint: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("[DEBUG] ===== STARTING AGENT WORKER =====")
    print(f"[DEBUG] Entrypoint function: {entrypoint.__name__}")
    print(f"[DEBUG] Entrypoint function location: {entrypoint.__module__}")
    
    # Verify environment variables are loaded
    import os
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    print(f"[DEBUG] LIVEKIT_URL: {'SET' if livekit_url else 'MISSING'}")
    print(f"[DEBUG] LIVEKIT_API_KEY: {'SET' if livekit_api_key else 'MISSING'}")
    print(f"[DEBUG] LIVEKIT_API_SECRET: {'SET' if livekit_api_secret else 'MISSING'}")
    
    if not livekit_url or not livekit_api_key or not livekit_api_secret:
        print("[ERROR] Missing required LiveKit environment variables!")
        print("[ERROR] Please check your backend/.env file")
        exit(1)
    
    print("[DEBUG] All environment variables loaded successfully")
    print("[DEBUG] Registering agent worker with LiveKit Cloud...")
    print("[DEBUG] Agent will accept jobs for ALL rooms (default behavior)")
    print("[DEBUG] Waiting for user connections to trigger entrypoint...")
    
    # Configure worker options
    # By default, agents accept jobs for all rooms unless room_matcher is specified
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        # No room_matcher = accepts all rooms
    )
    
    print(f"[DEBUG] WorkerOptions configured with entrypoint: {worker_options.entrypoint_fnc.__name__}")
    
    try:
        # This will block and wait for jobs from LiveKit Cloud
        print("[DEBUG] Starting agent worker - this will block and wait for connections...")
        cli.run_app(worker_options)
    except KeyboardInterrupt:
        print("[DEBUG] Agent worker stopped by user")
    except Exception as e:
        print(f"[ERROR] Failed to start agent worker: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

