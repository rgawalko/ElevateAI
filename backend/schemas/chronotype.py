"""
Schemas for chronotype quiz functionality
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class ChronotypeClassification(str, Enum):
    """Chronotype classification types"""
    LARK = "Lark"  # Morning type (9-20 points)
    INTERMEDIATE = "Intermediate"  # Hummingbird (21-30 points)
    OWL = "Owl"  # Evening type (31-45 points)


class QuizAnswer(BaseModel):
    """Individual quiz answer"""
    question_id: int = Field(..., ge=1, le=9, description="Question number (1-9)")
    answer: int = Field(..., ge=1, le=5, description="Answer value (1-5)")


class ChronotypeQuizSubmission(BaseModel):
    """Schema for submitting chronotype quiz answers"""
    answers: List[int] = Field(
        ..., 
        min_items=9, 
        max_items=9, 
        description="List of 9 answers, each scored 1-5"
    )
    
    def validate_answers(self) -> bool:
        """Validate that all answers are in valid range"""
        return all(1 <= answer <= 5 for answer in self.answers)


class PeakWindow(BaseModel):
    """Time window for peak performance"""
    start: str = Field(..., description="Start time in HH:MM format")
    end: str = Field(..., description="End time in HH:MM format")


class ChronotypeResult(BaseModel):
    """Complete chronotype quiz result"""
    answers: List[int] = Field(..., description="List of quiz answers")
    total: int = Field(..., ge=9, le=45, description="Total score (9-45)")
    chronotype: ChronotypeClassification = Field(..., description="Chronotype classification")
    peak_window: PeakWindow = Field(..., description="Primary peak performance window")
    secondary_window: PeakWindow = Field(..., description="Secondary peak performance window")
    description: Optional[str] = Field(None, description="Description of the chronotype")
    recommendations: Optional[List[str]] = Field(None, description="Personalized recommendations")


class ChronotypeQuizResponse(BaseModel):
    """Response after submitting chronotype quiz"""
    success: bool = Field(..., description="Whether the quiz was processed successfully")
    result: Optional[ChronotypeResult] = Field(None, description="Quiz result if successful")
    message: str = Field(..., description="Response message")


class QuizQuestion(BaseModel):
    """Individual quiz question structure"""
    id: int = Field(..., description="Question ID")
    section: str = Field(..., description="Question section (A, B, or C)")
    question: str = Field(..., description="Question text")
    options: List[Dict[str, Any]] = Field(..., description="Answer options with text and scores")


class ChronotypeQuizStructure(BaseModel):
    """Complete quiz structure with all questions"""
    title: str = Field(..., description="Quiz title")
    description: str = Field(..., description="Quiz description")
    sections: List[str] = Field(..., description="Quiz sections")
    questions: List[QuizQuestion] = Field(..., description="All quiz questions")
    scoring_info: Dict[str, Any] = Field(..., description="Information about scoring")


# Quiz data structure
CHRONOTYPE_QUIZ_DATA = {
    "title": "Chronotype Quiz",
    "description": "Discover your natural sleep-wake cycle and optimal performance times",
    "sections": ["Sleep Preferences", "Energy Levels", "Lifestyle & Behavior"],
    "questions": [
        {
            "id": 1,
            "section": "A",
            "question": "If you were free to plan your day, what time would you go to bed?",
            "options": [
                {"text": "Before 10 PM", "score": 1},
                {"text": "10–11 PM", "score": 2},
                {"text": "11 PM–12 AM", "score": 3},
                {"text": "12–1 AM", "score": 4},
                {"text": "After 1 AM", "score": 5}
            ]
        },
        {
            "id": 2,
            "section": "A",
            "question": "If you were free to plan your day, what time would you wake up?",
            "options": [
                {"text": "Before 6 AM", "score": 1},
                {"text": "6–7 AM", "score": 2},
                {"text": "7–8 AM", "score": 3},
                {"text": "8–9 AM", "score": 4},
                {"text": "After 9 AM", "score": 5}
            ]
        },
        {
            "id": 3,
            "section": "A",
            "question": "Without an alarm, how easy is it for you to wake up in the morning?",
            "options": [
                {"text": "Very easy", "score": 1},
                {"text": "Easy", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Hard", "score": 4},
                {"text": "Very hard", "score": 5}
            ]
        },
        {
            "id": 4,
            "section": "B",
            "question": "When do you feel your sharpest concentration?",
            "options": [
                {"text": "Early morning (6–9 AM)", "score": 1},
                {"text": "Mid-morning (9–12 PM)", "score": 2},
                {"text": "Afternoon (12–5 PM)", "score": 3},
                {"text": "Evening (5–9 PM)", "score": 4},
                {"text": "Night (9 PM–midnight or later)", "score": 5}
            ]
        },
        {
            "id": 5,
            "section": "B",
            "question": "When do you usually experience your lowest energy dip?",
            "options": [
                {"text": "Morning", "score": 1},
                {"text": "Midday", "score": 2},
                {"text": "Afternoon", "score": 3},
                {"text": "Evening", "score": 4},
                {"text": "I don't really notice a dip", "score": 3}
            ]
        },
        {
            "id": 6,
            "section": "B",
            "question": "If you must perform at your best, when would you prefer to schedule important work?",
            "options": [
                {"text": "Early morning", "score": 1},
                {"text": "Mid-morning", "score": 2},
                {"text": "Afternoon", "score": 3},
                {"text": "Evening", "score": 4},
                {"text": "Late night", "score": 5}
            ]
        },
        {
            "id": 7,
            "section": "C",
            "question": "On weekends, do you sleep in significantly later than weekdays?",
            "options": [
                {"text": "Not at all", "score": 1},
                {"text": "30–60 minutes later", "score": 2},
                {"text": "1–2 hours later", "score": 3},
                {"text": "More than 2 hours later", "score": 4}
            ]
        },
        {
            "id": 8,
            "section": "C",
            "question": "How do you feel if you have to wake up early (before 7 AM)?",
            "options": [
                {"text": "Refreshed, no problem", "score": 1},
                {"text": "A little tired, manageable", "score": 2},
                {"text": "Very sluggish, need caffeine", "score": 3},
                {"text": "Exhausted, barely functional", "score": 4}
            ]
        },
        {
            "id": 9,
            "section": "C",
            "question": "Do you feel more productive/creative in the…?",
            "options": [
                {"text": "Morning", "score": 1},
                {"text": "Afternoon", "score": 3},
                {"text": "Evening/night", "score": 5}
            ]
        }
    ],
    "scoring_info": {
        "total_range": "9-45",
        "classifications": {
            "Lark": {"range": "9-20", "description": "Morning type"},
            "Intermediate": {"range": "21-30", "description": "Hummingbird"},
            "Owl": {"range": "31-45", "description": "Evening type"}
        }
    }
}
