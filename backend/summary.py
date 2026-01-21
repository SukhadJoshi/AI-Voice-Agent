"""
Conversation summary generation
"""

import os
from openai import OpenAI
from anthropic import Anthropic
from database import get_appointments, save_conversation_summary


async def generate_summary(conversation_history: list, phone_number: str, conversation_id: str) -> str:
    """Generate a summary of the conversation"""
    
    # Extract booked appointments
    booked_appointments = []
    if phone_number:
        appointments = get_appointments(phone_number)
        booked_appointments = [
            {
                "id": appt.get("id"),
                "date": appt.get("date"),
                "time": appt.get("time"),
                "status": appt.get("status")
            }
            for appt in appointments
            if appt.get("status") == "confirmed"
        ]
    
    # Build conversation text
    conversation_text = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversation_history
    ])
    
    # Generate summary using LLM
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    
    summary_prompt = f"""Please provide a concise summary of the following conversation. Include:
1. Main topics discussed
2. Any appointments booked or modified
3. User preferences mentioned
4. Key decisions made

Conversation:
{conversation_text}

Summary:"""
    
    try:
        if llm_provider == "openai":
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=500
            )
            summary = response.choices[0].message.content
        elif llm_provider == "anthropic":
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary = response.content[0].text
        else:
            # Fallback to OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=500
            )
            summary = response.choices[0].message.content
        
        # Extract user preferences (simple extraction)
        user_preferences = {}
        if "prefer" in conversation_text.lower() or "preference" in conversation_text.lower():
            # Basic extraction - can be enhanced
            user_preferences["mentioned"] = True
        
        # Save summary to database
        if phone_number:
            save_conversation_summary(
                conversation_id,
                phone_number,
                summary,
                booked_appointments,
                user_preferences
            )
        
        # Format summary with appointments
        formatted_summary = f"{summary}\n\n"
        if booked_appointments:
            formatted_summary += "Booked Appointments:\n"
            for appt in booked_appointments:
                formatted_summary += f"- {appt['date']} at {appt['time']} (ID: {appt['id']})\n"
        
        return formatted_summary
    
    except Exception as e:
        # Fallback summary
        return f"Conversation Summary:\n- User phone: {phone_number or 'Not provided'}\n- Appointments: {len(booked_appointments)} booked\n- Error generating detailed summary: {str(e)}"

