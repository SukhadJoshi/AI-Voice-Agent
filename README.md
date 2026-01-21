# AI Voice Agent

An intelligent voice assistant that enables users to book, manage, and cancel appointments through natural voice conversations.

## Project Description

This is an AI-powered voice agent that transforms appointment scheduling into a conversational experience. Instead of filling out forms or navigating complex menus, users simply speak with the agent to manage their appointments. The system understands natural language, processes user requests, and performs actions like booking new appointments, checking existing bookings, modifying schedules, or canceling appointments.

The agent maintains context throughout the conversation, remembers user information, and provides a seamless voice-first experience. All appointments are securely stored in a database, and users receive a summary at the end of each conversation.

## How It Works

1. **User speaks** - The user initiates a voice call through the web interface and speaks naturally, such as "I'd like to book an appointment for tomorrow at 2 PM."

2. **Speech-to-Text** - Deepgram transcribes the user's speech in real-time, converting voice input into text.

3. **Language processing** - The transcribed text is sent to a Large Language Model (LLM) that understands user intent and context from the conversation history.

4. **Tool execution** - When the user requests an action (like booking or canceling), the LLM calls appropriate tools that interact with the database to perform operations like fetching available slots, creating appointments, or retrieving user's existing bookings.

5. **Response generation** - The LLM generates a natural language response based on the tool results and conversation context.

6. **Text-to-Speech** - Cartesia converts the agent's text response into natural-sounding speech that plays back to the user.

7. **Data visualization** - Tool calls and actions are displayed in real-time on the frontend interface, and users receive a conversation summary when the call ends.

The entire flow happens in real-time, creating a fluid conversational experience where users can manage their appointments through voice alone.

## Conclusion

This demonstrates how modern AI technologies can create intuitive, voice-first interfaces for common tasks. By combining speech recognition, natural language understanding, and voice synthesis, the system provides an accessible and efficient way to manage appointments without traditional UI barriers.
