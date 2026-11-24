"""
Enhanced Google Calendar Tools with Smart Scheduling

This module provides advanced calendar functionality including:
- Availability checking across multiple days
- Smart meeting scheduling with conflict detection
- Meeting rescheduling
- Busy time analysis
- Recurring event support (future)
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    import json
    CALENDAR_API_AVAILABLE = True
except ImportError:
    CALENDAR_API_AVAILABLE = False
    logger.warning("Google Calendar API libraries not available")


def get_calendar_credentials(gmail_token=None, gmail_secret=None):
    """Get credentials for Calendar API.
    
    Args:
        gmail_token: JSON string or dict with token data
        gmail_secret: JSON string or dict with secret data
        
    Returns:
        Credentials object or None
    """
    # Import from gmail_tools to reuse authentication
    try:
        from email_assistant.tools.gmail.gmail_tools import get_credentials
        return get_credentials(gmail_token, gmail_secret)
    except ImportError:
        logger.error("Could not import get_credentials from gmail_tools")
        return None


class TimeSlot(BaseModel):
    """Represents a time slot."""
    start: datetime
    end: datetime
    available: bool = True
    event_title: Optional[str] = None


class DayAvailability(BaseModel):
    """Availability for a single day."""
    date: str  # DD-MM-YYYY format
    busy_slots: List[TimeSlot] = []
    available_slots: List[TimeSlot] = []
    is_fully_booked: bool = False
    total_free_minutes: int = 0


class AvailabilityChecker:
    """Smart availability checker with conflict detection."""
    
    def __init__(self, service, working_hours: Tuple[int, int] = (9, 17)):
        """Initialize checker.
        
        Args:
            service: Google Calendar API service instance
            working_hours: Tuple of (start_hour, end_hour) for working day
        """
        self.service = service
        self.work_start_hour, self.work_end_hour = working_hours
    
    def check_availability(self, dates: List[str], calendar_id: str = "primary") -> List[DayAvailability]:
        """Check availability for multiple dates.
        
        Args:
            dates: List of dates in DD-MM-YYYY format
            calendar_id: Calendar to check (default: primary)
            
        Returns:
            List of DayAvailability objects
        """
        results = []
        
        for date_str in dates:
            try:
                day_avail = self._check_single_day(date_str, calendar_id)
                results.append(day_avail)
            except Exception as e:
                logger.error(f"Error checking availability for {date_str}: {e}")
                # Return empty availability
                results.append(DayAvailability(
                    date=date_str,
                    is_fully_booked=False,
                    total_free_minutes=0
                ))
        
        return results
    
    def _check_single_day(self, date_str: str, calendar_id: str) -> DayAvailability:
        """Check availability for a single day.
        
        Args:
            date_str: Date in DD-MM-YYYY format
            calendar_id: Calendar to check
            
        Returns:
            DayAvailability object
        """
        # Parse date
        day, month, year = date_str.split("-")
        
        # Create datetime objects for the day
        day_start = datetime(int(year), int(month), int(day), 
                           self.work_start_hour, 0, 0)
        day_end = datetime(int(year), int(month), int(day), 
                          self.work_end_hour, 0, 0)
        
        # Query Calendar API
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Parse busy slots
        busy_slots = []
        for event in events:
            start_str = event['start'].get('dateTime', event['start'].get('date'))
            end_str = event['end'].get('dateTime', event['end'].get('date'))
            
            if 'T' in start_str:  # Has time component
                start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                
                # Only include if within working hours
                if start_dt < day_end and end_dt > day_start:
                    busy_slots.append(TimeSlot(
                        start=max(start_dt, day_start),
                        end=min(end_dt, day_end),
                        available=False,
                        event_title=event.get('summary', 'Busy')
                    ))
        
        # Sort busy slots
        busy_slots.sort(key=lambda x: x.start)
        
        # Calculate available slots
        available_slots = []
        current_time = day_start
        
        for busy_slot in busy_slots:
            if current_time < busy_slot.start:
                # There's a gap - this is available
                available_slots.append(TimeSlot(
                    start=current_time,
                    end=busy_slot.start,
                    available=True
                ))
            current_time = max(current_time, busy_slot.end)
        
        # Check if there's time after last meeting
        if current_time < day_end:
            available_slots.append(TimeSlot(
                start=current_time,
                end=day_end,
                available=True
            ))
        
        # Calculate total free time
        total_free_minutes = sum(
            int((slot.end - slot.start).total_seconds() / 60)
            for slot in available_slots
        )
        
        return DayAvailability(
            date=date_str,
            busy_slots=busy_slots,
            available_slots=available_slots,
            is_fully_booked=(len(available_slots) == 0),
            total_free_minutes=total_free_minutes
        )
    
    def find_best_slot(
        self, 
        dates: List[str], 
        duration_minutes: int,
        preferred_times: Optional[List[Tuple[int, int]]] = None
    ) -> Optional[Dict[str, Any]]:
        """Find the best available slot for a meeting.
        
        Args:
            dates: List of dates to check
            duration_minutes: Required meeting duration
            preferred_times: List of (start_hour, end_hour) tuples for preferences
            
        Returns:
            Dict with best slot info or None if no suitable slot found
        """
        availability = self.check_availability(dates)
        
        best_slot = None
        best_score = -1
        
        for day_avail in availability:
            for slot in day_avail.available_slots:
                slot_duration = int((slot.end - slot.start).total_seconds() / 60)
                
                if slot_duration >= duration_minutes:
                    # Calculate score based on preferences
                    score = self._score_slot(slot, preferred_times)
                    
                    if score > best_score:
                        best_score = score
                        best_slot = {
                            "date": day_avail.date,
                            "start": slot.start,
                            "end": slot.start + timedelta(minutes=duration_minutes),
                            "score": score
                        }
        
        return best_slot
    
    def _score_slot(
        self, 
        slot: TimeSlot, 
        preferred_times: Optional[List[Tuple[int, int]]]
    ) -> float:
        """Score a time slot based on preferences.
        
        Args:
            slot: TimeSlot to score
            preferred_times: Preferred time ranges
            
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        # Base score: earlier in the day is slightly better
        hour = slot.start.hour
        if 9 <= hour < 12:  # Morning
            score += 10
        elif 14 <= hour < 16:  # Early afternoon
            score += 7
        else:  # Other times
            score += 5
        
        # Bonus for preferred times
        if preferred_times:
            for pref_start, pref_end in preferred_times:
                if pref_start <= hour < pref_end:
                    score += 20
                    break
        
        # Bonus for longer available slots (more flexibility)
        slot_duration = (slot.end - slot.start).total_seconds() / 3600  # hours
        score += min(slot_duration * 2, 10)  # Cap at 10 bonus points
        
        return score


class MeetingScheduler:
    """Smart meeting scheduler with conflict detection."""
    
    def __init__(self, service):
        """Initialize scheduler.
        
        Args:
            service: Google Calendar API service instance
        """
        self.service = service
    
    def schedule_meeting(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[str],
        organizer_email: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "America/Los_Angeles",
        add_video_conference: bool = False
    ) -> Dict[str, Any]:
        """Schedule a meeting with comprehensive options.
        
        Args:
            title: Meeting title
            start_time: Start datetime
            end_time: End datetime
            attendees: List of attendee emails
            organizer_email: Organizer's email
            description: Meeting description
            location: Physical location
            timezone: Timezone string
            add_video_conference: Add Google Meet link
            
        Returns:
            Dict with meeting details and status
        """
        # Build event
        event = {
            "summary": title,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
            "attendees": [{"email": email} for email in attendees],
            "organizer": {
                "email": organizer_email,
                "self": True,
            },
            "reminders": {
                "useDefault": True,
            },
            "sendUpdates": "all",
        }
        
        if description:
            event["description"] = description
        
        if location:
            event["location"] = location
        
        if add_video_conference:
            import uuid
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"meet-{uuid.uuid4()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        
        try:
            # Create event
            created_event = self.service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1 if add_video_conference else 0,
                sendUpdates="all"
            ).execute()
            
            logger.info(f"Meeting created: {created_event.get('htmlLink')}")
            
            return {
                "success": True,
                "event_id": created_event.get("id"),
                "html_link": created_event.get("htmlLink"),
                "hangout_link": created_event.get("hangoutLink"),
                "message": f"Meeting '{title}' scheduled successfully"
            }
        
        except Exception as e:
            logger.error(f"Error creating meeting: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to schedule meeting: {str(e)}"
            }
    
    def check_conflicts(
        self,
        start_time: datetime,
        end_time: datetime,
        calendar_id: str = "primary"
    ) -> List[Dict[str, Any]]:
        """Check for conflicting events.
        
        Args:
            start_time: Proposed start time
            end_time: Proposed end time
            calendar_id: Calendar to check
            
        Returns:
            List of conflicting events
        """
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            conflicts = []
            for event in events:
                conflicts.append({
                    "title": event.get("summary", "Busy"),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "id": event.get("id")
                })
            
            return conflicts
        
        except Exception as e:
            logger.error(f"Error checking conflicts: {e}")
            return []


# Tool definitions for LangChain

class CheckAvailabilityInput(BaseModel):
    """Input for check_availability_enhanced tool."""
    dates: List[str] = Field(
        description="List of dates to check in DD-MM-YYYY format"
    )
    duration_minutes: Optional[int] = Field(
        default=None,
        description="Desired meeting duration to find suitable slots"
    )


@tool(args_schema=CheckAvailabilityInput)
def check_availability_enhanced(
    dates: List[str],
    duration_minutes: Optional[int] = None
) -> str:
    """Check calendar availability across multiple dates with smart scheduling.
    
    This enhanced version provides:
    - Detailed busy/available slots
    - Total free time per day
    - Best meeting slot suggestions if duration provided
    
    Args:
        dates: List of dates in DD-MM-YYYY format
        duration_minutes: If provided, suggests best slots for this duration
        
    Returns:
        Formatted availability report
    """
    if not CALENDAR_API_AVAILABLE:
        return "Calendar API not available. Install google-api-python-client."
    
    try:
        # Get credentials
        creds = get_calendar_credentials(
            gmail_token=os.getenv("GMAIL_TOKEN"),
            gmail_secret=os.getenv("GMAIL_SECRET")
        )
        
        if not creds:
            return "Calendar credentials not configured. Please run setup_gmail.py"
        
        service = build("calendar", "v3", credentials=creds)
        checker = AvailabilityChecker(service)
        
        # Check availability
        availability = checker.check_availability(dates)
        
        # Format output
        output = "📅 CALENDAR AVAILABILITY REPORT\n"
        output += "=" * 50 + "\n\n"
        
        for day_avail in availability:
            output += f"📆 {day_avail.date}\n"
            output += "-" * 30 + "\n"
            
            if day_avail.is_fully_booked:
                output += "❌ Fully booked - no availability\n\n"
                continue
            
            # Show busy times
            if day_avail.busy_slots:
                output += "🔴 Busy Times:\n"
                for slot in day_avail.busy_slots:
                    start = slot.start.strftime("%I:%M %p")
                    end = slot.end.strftime("%I:%M %p")
                    output += f"   {start} - {end}: {slot.event_title}\n"
                output += "\n"
            
            # Show available times
            if day_avail.available_slots:
                output += "✅ Available Times:\n"
                for slot in day_avail.available_slots:
                    start = slot.start.strftime("%I:%M %p")
                    end = slot.end.strftime("%I:%M %p")
                    duration = int((slot.end - slot.start).total_seconds() / 60)
                    output += f"   {start} - {end} ({duration} min)\n"
                output += "\n"
            
            output += f"⏱️  Total free time: {day_avail.total_free_minutes} minutes\n\n"
        
        # Find best slot if duration provided
        if duration_minutes:
            output += f"\n🎯 BEST SLOT FOR {duration_minutes}-MINUTE MEETING:\n"
            output += "-" * 50 + "\n"
            
            best_slot = checker.find_best_slot(dates, duration_minutes)
            
            if best_slot:
                start = best_slot["start"].strftime("%A, %B %d at %I:%M %p")
                end = best_slot["end"].strftime("%I:%M %p")
                output += f"✨ Recommended: {start} - {end}\n"
                output += f"   Score: {best_slot['score']:.1f}/40\n"
            else:
                output += "❌ No suitable slots found for requested duration\n"
        
        return output
    
    except Exception as e:
        logger.error(f"Error in check_availability_enhanced: {e}")
        return f"Error checking availability: {str(e)}"


class ScheduleMeetingEnhancedInput(BaseModel):
    """Input for schedule_meeting_enhanced tool."""
    title: str = Field(description="Meeting title")
    start_time: str = Field(
        description="Start time in ISO format: YYYY-MM-DDTHH:MM:SS"
    )
    end_time: str = Field(
        description="End time in ISO format: YYYY-MM-DDTHH:MM:SS"
    )
    attendees: List[str] = Field(description="List of attendee email addresses")
    organizer_email: str = Field(description="Organizer's email address")
    description: Optional[str] = Field(
        default=None,
        description="Meeting description/agenda"
    )
    location: Optional[str] = Field(
        default=None,
        description="Physical meeting location"
    )
    timezone: str = Field(
        default="America/Los_Angeles",
        description="Timezone for the meeting"
    )
    add_video_conference: bool = Field(
        default=True,
        description="Add Google Meet video conference link"
    )


@tool(args_schema=ScheduleMeetingEnhancedInput)
def schedule_meeting_enhanced(
    title: str,
    start_time: str,
    end_time: str,
    attendees: List[str],
    organizer_email: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    timezone: str = "America/Los_Angeles",
    add_video_conference: bool = True
) -> str:
    """Schedule a meeting with enhanced features including conflict detection.
    
    Features:
    - Conflict detection before scheduling
    - Optional Google Meet link
    - Custom description and location
    - Email notifications to attendees
    
    Args:
        title: Meeting title
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        attendees: List of attendee emails
        organizer_email: Organizer email
        description: Meeting agenda/description
        location: Physical location
        timezone: Timezone string
        add_video_conference: Add Google Meet link
        
    Returns:
        Success/failure message with meeting details
    """
    if not CALENDAR_API_AVAILABLE:
        return "Calendar API not available. Install google-api-python-client."
    
    try:
        # Get credentials
        creds = get_calendar_credentials(
            gmail_token=os.getenv("GMAIL_TOKEN"),
            gmail_secret=os.getenv("GMAIL_SECRET")
        )
        
        if not creds:
            return "Calendar credentials not configured. Please run setup_gmail.py"
        
        service = build("calendar", "v3", credentials=creds)
        scheduler = MeetingScheduler(service)
        
        # Parse times
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        # Check for conflicts
        conflicts = scheduler.check_conflicts(start_dt, end_dt)
        
        if conflicts:
            conflict_msg = f"⚠️ Warning: {len(conflicts)} conflict(s) detected:\n"
            for conflict in conflicts:
                conflict_msg += f"   - {conflict['title']}\n"
            conflict_msg += "\nProceeding with scheduling anyway.\n\n"
        else:
            conflict_msg = "✅ No conflicts detected\n\n"
        
        # Schedule meeting
        result = scheduler.schedule_meeting(
            title=title,
            start_time=start_dt,
            end_time=end_dt,
            attendees=attendees,
            organizer_email=organizer_email,
            description=description,
            location=location,
            timezone=timezone,
            add_video_conference=add_video_conference
        )
        
        if result["success"]:
            output = "✨ MEETING SCHEDULED SUCCESSFULLY\n"
            output += "=" * 50 + "\n\n"
            output += conflict_msg
            output += f"📅 Title: {title}\n"
            output += f"⏰ Time: {start_dt.strftime('%A, %B %d at %I:%M %p')} - {end_dt.strftime('%I:%M %p')}\n"
            output += f"👥 Attendees: {', '.join(attendees)}\n"
            
            if description:
                output += f"📝 Agenda: {description}\n"
            
            if location:
                output += f"📍 Location: {location}\n"
            
            if add_video_conference and result.get("hangout_link"):
                output += f"🎥 Video: {result['hangout_link']}\n"
            
            output += f"\n🔗 Calendar Link: {result['html_link']}\n"
            output += "\n✉️  Invitations sent to all attendees"
            
            return output
        else:
            return f"❌ Failed to schedule meeting: {result['message']}"
    
    except Exception as e:
        logger.error(f"Error in schedule_meeting_enhanced: {e}")
        return f"Error scheduling meeting: {str(e)}"
