"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlmodel import Session, select
from typing import List, Dict, Any

from .database import engine, init_db, get_session
from .models import Activity, Participant

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize the database and seed initial data if needed
@app.on_event("startup")
def on_startup():
    init_db()
    seed_initial_data()

def seed_initial_data():
    """Seed the database with initial activities if empty."""
    with Session(engine) as session:
        # Check if we already have activities
        if session.exec(select(Activity)).first():
            return
            
        # Initial activities data
        initial_activities = {
            "Chess Club": Activity(
                name="Chess Club",
                description="Learn strategies and compete in chess tournaments",
                schedule="Fridays, 3:30 PM - 5:00 PM",
                max_participants=12
            ),
            "Programming Class": Activity(
                name="Programming Class",
                description="Learn programming fundamentals and build software projects",
                schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                max_participants=20
            ),
            "Gym Class": Activity(
                name="Gym Class",
                description="Physical education and sports activities",
                schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                max_participants=30
            ),
            "Soccer Team": Activity(
                name="Soccer Team",
                description="Join the school soccer team and compete in matches",
                schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                max_participants=22
            ),
            "Basketball Team": Activity(
                name="Basketball Team",
                description="Practice and play basketball with the school team",
                schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                max_participants=15
            ),
            "Art Club": Activity(
                name="Art Club",
                description="Explore your creativity through painting and drawing",
                schedule="Thursdays, 3:30 PM - 5:00 PM",
                max_participants=15
            ),
            "Drama Club": Activity(
                name="Drama Club",
                description="Act, direct, and produce plays and performances",
                schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                max_participants=20
            ),
            "Math Club": Activity(
                name="Math Club",
                description="Solve challenging problems and participate in math competitions",
                schedule="Tuesdays, 3:30 PM - 4:30 PM",
                max_participants=10
            ),
            "Debate Team": Activity(
                name="Debate Team",
                description="Develop public speaking and argumentation skills",
                schedule="Fridays, 4:00 PM - 5:30 PM",
                max_participants=12
            )
        }

        # Add activities to database
        for activity in initial_activities.values():
            session.add(activity)
        
        # Add initial participants
        initial_participants = [
            Participant(email="michael@mergington.edu", activity_name="Chess Club"),
            Participant(email="daniel@mergington.edu", activity_name="Chess Club"),
            Participant(email="emma@mergington.edu", activity_name="Programming Class"),
            Participant(email="sophia@mergington.edu", activity_name="Programming Class"),
            Participant(email="john@mergington.edu", activity_name="Gym Class"),
            Participant(email="olivia@mergington.edu", activity_name="Gym Class"),
            Participant(email="liam@mergington.edu", activity_name="Soccer Team"),
            Participant(email="noah@mergington.edu", activity_name="Soccer Team"),
            Participant(email="ava@mergington.edu", activity_name="Basketball Team"),
            Participant(email="mia@mergington.edu", activity_name="Basketball Team"),
            Participant(email="amelia@mergington.edu", activity_name="Art Club"),
            Participant(email="harper@mergington.edu", activity_name="Art Club"),
            Participant(email="ella@mergington.edu", activity_name="Drama Club"),
            Participant(email="scarlett@mergington.edu", activity_name="Drama Club"),
            Participant(email="james@mergington.edu", activity_name="Math Club"),
            Participant(email="benjamin@mergington.edu", activity_name="Math Club"),
            Participant(email="charlotte@mergington.edu", activity_name="Debate Team"),
            Participant(email="henry@mergington.edu", activity_name="Debate Team")
        ]
        
        for participant in initial_participants:
            session.add(participant)
            
        session.commit()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """Get all activities with their participants."""
    # Get all activities
    activities_query = select(Activity)
    activities_list = session.exec(activities_query).all()
    
    # Get participants for each activity
    result = {}
    for activity in activities_list:
        participants_query = select(Participant).where(Participant.activity_name == activity.name)
        participants = session.exec(participants_query).all()
        
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [p.email for p in participants]
        }
    
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(
    activity_name: str,
    email: str,
    session: Session = Depends(get_session)
):
    """Sign up a student for an activity."""
    # Get activity
    activity = session.get(Activity, activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Check if student is already signed up
    existing_signup = session.exec(
        select(Participant).where(
            Participant.activity_name == activity_name,
            Participant.email == email
        )
    ).first()
    
    if existing_signup:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Check if activity is full
    participants_count = session.exec(
        select(Participant).where(Participant.activity_name == activity_name)
    ).all()
    if len(participants_count) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )

    # Create new signup
    new_participant = Participant(email=email, activity_name=activity_name)
    session.add(new_participant)
    session.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(
    activity_name: str,
    email: str,
    session: Session = Depends(get_session)
):
    """Unregister a student from an activity."""
    # Get activity
    activity = session.get(Activity, activity_name)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Find participant
    participant = session.exec(
        select(Participant).where(
            Participant.activity_name == activity_name,
            Participant.email == email
        )
    ).first()
    
    if not participant:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove participant
    session.delete(participant)
    session.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}
