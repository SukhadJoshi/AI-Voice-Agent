"""
Tool functions for the voice agent
"""

import json
from datetime import datetime, date, timedelta
from database import (
    insert_user,
    get_appointments,
    insert_appointment,
    check_slot_available,
    get_appointment_by_id,
    update_appointment_status,
    update_appointment_datetime,
    get_supabase_client
)


async def identify_user(phone_number: str) -> str:
    """Identify user by phone number"""
    try:
        # Store or verify user in database
        insert_user(phone_number)
        return f"Thank you! I've identified you with phone number {phone_number}. How can I help you today?"
    except Exception as e:
        return f"I had trouble saving your phone number. Please try again. Error: {str(e)}"


async def fetch_slots() -> str:
    """Fetch available appointment slots (hardcoded)"""
    # Generate slots for the next 7 days
    today = date.today()
    slots = []
    times = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    
    for i in range(7):
        slot_date = today + timedelta(days=i)
        slots.append({
            "date": slot_date.strftime("%Y-%m-%d"),
            "times": times
        })
    
    # Check which slots are already booked
    client = get_supabase_client()
    result = client.table("appointments").select("date, time").eq("status", "confirmed").gte("date", str(today)).execute()
    
    booked_set = {(row["date"], row["time"]) for row in result.data}
    
    available_slots = []
    for slot in slots:
        slot_date = slot["date"]
        available_times = [t for t in slot["times"] if (slot_date, t) not in booked_set]
        if available_times:
            available_slots.append(f"{slot_date}: {', '.join(available_times)}")
    
    if not available_slots:
        return "I'm sorry, but there are no available slots at the moment. Please check back later."
    
    response = "Here are the available appointment slots:\n" + "\n".join(available_slots)
    return response


async def book_appointment(date: str, time: str, phone_number: str, name: str = None) -> str:
    """Book an appointment for the user"""
    try:
        # Validate date and time format
        try:
            datetime.strptime(date, "%Y-%m-%d")
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."
        
        # Check if slot is already booked
        if not check_slot_available(date, time):
            return f"I'm sorry, but the slot on {date} at {time} is already booked. Please choose another time."
        
        # Create appointment
        result = insert_appointment(phone_number, date, time, name, "confirmed")
        
        if result and "id" in result:
            appointment_id = result["id"]
            return f"Great! I've successfully booked your appointment for {date} at {time}. Your appointment ID is {appointment_id}. Is there anything else I can help you with?"
        else:
            return "I encountered an issue booking your appointment. Please try again."
    
    except Exception as e:
        return f"I had trouble booking your appointment. Error: {str(e)}"


async def retrieve_appointments(phone_number: str) -> str:
    """Retrieve all appointments for a user"""
    try:
        appointments = get_appointments(phone_number)
        
        if not appointments:
            return "You don't have any appointments scheduled."
        
        response = "Here are your appointments:\n"
        for appt in appointments:
            appt_id = appt.get("id")
            appt_name = appt.get("name")
            appt_date = appt.get("date")
            appt_time = appt.get("time")
            status = appt.get("status", "confirmed")
            status_text = "Confirmed" if status == "confirmed" else "Cancelled"
            response += f"\n- Appointment ID {appt_id}: {appt_date} at {appt_time} ({status_text})"
            if appt_name:
                response += f" - {appt_name}"
        
        return response
    
    except Exception as e:
        return f"I had trouble retrieving your appointments. Error: {str(e)}"


async def cancel_appointment(appointment_id: str, phone_number: str) -> str:
    """Cancel an appointment"""
    try:
        appointment_id_int = int(appointment_id)
        
        # Verify appointment belongs to user
        existing = get_appointment_by_id(appointment_id_int, phone_number)
        
        if not existing:
            return f"I couldn't find a confirmed appointment with ID {appointment_id} for your phone number. Please check the appointment ID and try again."
        
        # Cancel appointment
        update_appointment_status(appointment_id_int, phone_number, "cancelled")
        
        appt_date = existing.get("date")
        appt_time = existing.get("time")
        return f"I've successfully cancelled your appointment on {appt_date} at {appt_time}. Is there anything else I can help you with?"
    
    except ValueError:
        return f"Invalid appointment ID format. Please provide a valid appointment ID."
    except Exception as e:
        return f"I had trouble cancelling your appointment. Error: {str(e)}"


async def modify_appointment(appointment_id: str, phone_number: str, new_date: str = None, new_time: str = None) -> str:
    """Modify an appointment's date or time"""
    try:
        if not new_date and not new_time:
            return "Please provide either a new date or new time (or both) to modify the appointment."
        
        # Validate formats
        if new_date:
            try:
                datetime.strptime(new_date, "%Y-%m-%d")
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD."
        
        if new_time:
            try:
                datetime.strptime(new_time, "%H:%M")
            except ValueError:
                return "Invalid time format. Please use HH:MM."
        
        appointment_id_int = int(appointment_id)
        
        # Verify appointment belongs to user
        existing = get_appointment_by_id(appointment_id_int, phone_number)
        
        if not existing:
            return f"I couldn't find a confirmed appointment with ID {appointment_id} for your phone number."
        
        # Check if new slot is available
        final_date = new_date or existing.get("date")
        final_time = new_time or existing.get("time")
        
        # Check if the new slot conflicts (unless it's the same slot)
        if (new_date or new_time) and not check_slot_available(final_date, final_time):
            # Check if it's the same appointment
            client = get_supabase_client()
            conflict = client.table("appointments").select("id").eq("date", final_date).eq("time", final_time).eq("status", "confirmed").execute()
            if conflict.data and conflict.data[0]["id"] != appointment_id_int:
                return f"I'm sorry, but the slot on {final_date} at {final_time} is already booked. Please choose another time."
        
        # Update appointment
        update_appointment_datetime(appointment_id_int, phone_number, new_date, new_time)
        
        return f"I've successfully updated your appointment to {final_date} at {final_time}. Is there anything else I can help you with?"
    
    except ValueError:
        return f"Invalid appointment ID format. Please provide a valid appointment ID."
    except Exception as e:
        return f"I had trouble modifying your appointment. Error: {str(e)}"


async def end_conversation() -> str:
    """End the conversation"""
    return "Thank you for using our service! I'll now generate a summary of our conversation."

