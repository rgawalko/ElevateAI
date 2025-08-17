from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Dict, Any, Set, List, Optional
import json
import os
import time
import logging
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import FunctionTool

router = APIRouter()
logger = logging.getLogger(__name__)

# ==============================
# 📥 INPUT MODEL (request body)
# ==============================
class DayMetrics(BaseModel):
    """
    Daily metrics used to compute the Evidence-based Productivity Score (EPS).
    All time values are for a single day.
    """
    deep_work_min: int = Field(
        ...,
        ge=0,
        description=(
            "Total minutes spent in uninterrupted focus blocks ≥ 25 minutes. "
            "Benefits capped at ~240 min/day for diminishing returns."
        ),
        example=210,
    )
    context_switches: int = Field(
        ...,
        ge=0,
        description=(
            "Number of disruptive task/context switches (≥ ~30s) during focus time. "
            "Higher values reduce the focus subscore."
        ),
        example=4,
    )
    sleep_hours: float = Field(
        ...,
        ge=0,
        le=14,
        description=(
            "Hours slept (last night or weighted avg of last 3 nights). "
            "7–9 hours is considered optimal for the sleep subscore."
        ),
        example=7.5,
    )
    break_minutes: int = Field(
        ...,
        ge=0,
        description=(
            "Total minutes of short restorative breaks (micro/macro) taken during the day."
        ),
        example=32,
    )
    focus_minutes: int = Field(
        ...,
        ge=1,
        description=(
            "Total minutes of focus/work for the day (denominator for break ratio). "
            "Cannot be zero; if you have no focus time, use 1 to avoid division by zero."
        ),
        example=400,
    )
    hc_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Fraction (0–1) of high-cognitive minutes scheduled inside the user's peak window "
            "(derived from chronotype survey + behavior). 0.8 → 80%."
        ),
        example=0.70,
    )


# ==============================
# 📤 OUTPUT MODEL (response)
# ==============================
class ScoreBreakdown(BaseModel):
    """
    Subscores (0–100) plus the final EPS (0–100).
    Higher is better. Each subscore reflects a specific dimension.
    """
    focus: float = Field(
        ...,
        description=(
            "Focus subscore (F): rewards deep-work minutes up to 240, "
            "penalizes context switches."
        ),
        example=83.8,
    )
    sleep: float = Field(
        ...,
        description="Sleep subscore (S): 100 inside 7–9 hours; decreases outside.",
        example=100.0,
    )
    breaks: float = Field(
        ...,
        description=(
            "Breaks subscore (B): ideal micro-break ratio is ~5–15% of focus minutes; "
            "deviation reduces the score."
        ),
        example=100.0,
    )
    chronotype: float = Field(
        ...,
        description=(
            "Chronotype-alignment subscore (C): rewards placing high-cognitive work "
            "inside the user's peak window; 100 at ≥80% alignment."
        ),
        example=87.5,
    )
    score: float = Field(
        ...,
        description=(
            "Final Evidence-based Productivity Score (EPS), 0–100. "
            "Weighted combination: 35% focus, 25% sleep, 20% breaks, 20% chronotype."
        ),
        example=92.3,
    )


# ==============================
# 🤖 AI AGENT FUNCTION
# ==============================
def calculate_productivity_score(
    deep_work_min: int,
    context_switches: int,
    sleep_hours: float,
    break_minutes: int,
    focus_minutes: int,
    hc_ratio: float
) -> str:
    """
    Calculates a comprehensive productivity score based on daily metrics.

    This function is designed to be called by an Azure AI agent to provide
    evidence-based productivity scoring for schedule optimization.

    :param deep_work_min: Total minutes spent in uninterrupted focus blocks ≥ 25 minutes
    :param context_switches: Number of disruptive task/context switches during focus time
    :param sleep_hours: Hours slept (7-9 hours is optimal)
    :param break_minutes: Total minutes of restorative breaks taken during the day
    :param focus_minutes: Total minutes of focus/work for the day
    :param hc_ratio: Fraction (0-1) of high-cognitive minutes scheduled inside peak window
    :return: JSON string containing detailed productivity score breakdown
    """
    try:
        # Create DayMetrics object
        metrics = DayMetrics(
            deep_work_min=deep_work_min,
            context_switches=context_switches,
            sleep_hours=sleep_hours,
            break_minutes=break_minutes,
            focus_minutes=focus_minutes,
            hc_ratio=hc_ratio
        )

        # Calculate the score using the existing algorithm
        score_breakdown = _calculate_score_internal(metrics)

        # Return as JSON string for the AI agent
        return json.dumps({
            "productivity_score": score_breakdown.score,
            "focus_score": score_breakdown.focus,
            "sleep_score": score_breakdown.sleep,
            "breaks_score": score_breakdown.breaks,
            "chronotype_score": score_breakdown.chronotype,
            "interpretation": _interpret_score(score_breakdown.score),
            "recommendations": _generate_recommendations(score_breakdown)
        })

    except Exception as e:
        logger.error(f"Error calculating productivity score: {e}")
        return json.dumps({
            "error": f"Failed to calculate productivity score: {str(e)}",
            "productivity_score": 0
        })

# Define user functions for the AI agent
user_functions = {calculate_productivity_score}


# ==============================
# 🔢 SCORING ENDPOINT
# ==============================
@router.post(
    "/score",
    response_model=ScoreBreakdown,
    summary="Compute daily productivity score (EPS)",
    description=(
        "Calculates a 0–100 productivity score from daily inputs:\n\n"
        "- **Focus (F, 35%)**: Combines deep-work minutes (capped at 240) and a penalty for context switches.\n"
        "- **Sleep (S, 25%)**: Ideal range is 7–9 hours; linear penalty outside.\n"
        "- **Breaks (B, 20%)**: Rewards a break-to-focus ratio in the ~5–15% band.\n"
        "- **Chronotype (C, 20%)**: Rewards aligning high-cognitive tasks with the user's peak window.\n\n"
        "Returns the four subscores and the weighted final score."
    ),
    tags=["productivity"],
)
def score(m: DayMetrics) -> ScoreBreakdown:
    """
    Calculate Evidence-based Productivity Score (EPS) from daily metrics.
    """
    return _calculate_score_internal(m)

# ==============================
# 🤖 AZURE AI AGENT SERVICE
# ==============================
class ProductivityScoringAgent:
    """
    Azure AI Agent for productivity scoring using the sophisticated EPS algorithm.
    """

    def __init__(self):
        """Initialize the Azure AI agent for productivity scoring."""
        try:
            # Get environment variables
            project_endpoint = os.environ.get(
                "PROJECT_ENDPOINT",
                "https://elevate777.services.ai.azure.com/api/projects/firstProject"
            )
            model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o")

            # Initialize the AIProjectClient
            self.project_client = AIProjectClient(
                endpoint=project_endpoint,
                credential=DefaultAzureCredential()
            )

            # Initialize the FunctionTool with productivity scoring function
            self.functions = FunctionTool(functions=user_functions)

            # Create the agent
            self.agent = self.project_client.agents.create_agent(
                model=model_deployment,
                name="productivity-scoring-agent",
                instructions="""You are a productivity scoring specialist AI agent.

Your primary function is to analyze daily productivity metrics and provide comprehensive scoring using evidence-based algorithms. You have access to a sophisticated productivity scoring function that evaluates:

1. Focus Quality (35% weight): Deep work time and context switches
2. Sleep Quality (25% weight): Sleep duration optimization (7-9 hours ideal)
3. Break Patterns (20% weight): Optimal break-to-work ratio (5-15%)
4. Chronotype Alignment (20% weight): High-cognitive work during peak hours

When asked to analyze productivity:
1. Use the calculate_productivity_score function with the provided metrics
2. Interpret the results in context of the user's goals
3. Provide actionable recommendations for improvement
4. Explain the reasoning behind the scores

Always be encouraging while providing honest assessments and practical advice.""",
                tools=self.functions.definitions,
            )

            logger.info(f"Created productivity scoring agent, ID: {self.agent.id}")

        except Exception as e:
            logger.error(f"Failed to initialize productivity scoring agent: {e}")
            raise

    def analyze_productivity(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze productivity using the AI agent with sophisticated scoring.

        Args:
            metrics: Dictionary containing productivity metrics:
                - deep_work_min: Minutes of deep work
                - context_switches: Number of context switches
                - sleep_hours: Hours of sleep
                - break_minutes: Minutes of breaks
                - focus_minutes: Total focus minutes
                - hc_ratio: High-cognitive work ratio during peak hours

        Returns:
            Dictionary containing AI analysis and productivity scores
        """
        try:
            # Create a thread for this analysis
            thread = self.project_client.agents.threads.create()

            # Format the analysis request
            prompt = f"""Please analyze the following daily productivity metrics and provide a comprehensive assessment:

Metrics:
- Deep work time: {metrics.get('deep_work_min', 0)} minutes
- Context switches: {metrics.get('context_switches', 0)}
- Sleep duration: {metrics.get('sleep_hours', 7.5)} hours
- Break time: {metrics.get('break_minutes', 0)} minutes
- Total focus time: {metrics.get('focus_minutes', 480)} minutes
- High-cognitive work during peak hours: {metrics.get('hc_ratio', 0.5) * 100}%

Please:
1. Calculate the detailed productivity score using the available function
2. Provide interpretation of each subscore
3. Give specific recommendations for improvement
4. Suggest optimal scheduling strategies based on these metrics"""

            # Send message to the agent
            message = self.project_client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

            # Process the request with function calling
            run = self.project_client.agents.runs.create(
                thread_id=thread.id,
                agent_id=self.agent.id
            )

            # Wait for completion and handle function calls
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(1)
                run = self.project_client.agents.runs.get(
                    thread_id=thread.id,
                    run_id=run.id
                )

                if run.status == "requires_action":
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    tool_outputs = []

                    for tool_call in tool_calls:
                        if tool_call.function.name == "calculate_productivity_score":
                            # Parse the function arguments
                            args = json.loads(tool_call.function.arguments)

                            # Call the productivity scoring function
                            output = calculate_productivity_score(
                                deep_work_min=args.get('deep_work_min', 0),
                                context_switches=args.get('context_switches', 0),
                                sleep_hours=args.get('sleep_hours', 7.5),
                                break_minutes=args.get('break_minutes', 0),
                                focus_minutes=args.get('focus_minutes', 480),
                                hc_ratio=args.get('hc_ratio', 0.5)
                            )

                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": output
                            })

                    # Submit the tool outputs
                    self.project_client.agents.runs.submit_tool_outputs(
                        thread_id=thread.id,
                        run_id=run.id,
                        tool_outputs=tool_outputs
                    )

            if run.status == "completed":
                # Get the agent's response
                messages = self.project_client.agents.messages.list(thread_id=thread.id)

                # Find the assistant's response
                for message in messages:
                    if message.role == "assistant" and message.content:
                        return {
                            "success": True,
                            "analysis": message.content[0].text.value,
                            "agent_id": self.agent.id,
                            "thread_id": thread.id
                        }

            return {
                "success": False,
                "error": f"Agent run failed with status: {run.status}",
                "analysis": "Failed to analyze productivity metrics"
            }

        except Exception as e:
            logger.error(f"Error analyzing productivity: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "Error occurred during productivity analysis"
            }

    def cleanup(self):
        """Clean up the agent after use."""
        try:
            self.project_client.agents.delete_agent(self.agent.id)
            logger.info("Deleted productivity scoring agent")
        except Exception as e:
            logger.error(f"Error deleting agent: {e}")

# Create a singleton instance
productivity_agent = None

def get_productivity_agent():
    """Get or create the productivity scoring agent instance."""
    global productivity_agent
    if productivity_agent is None:
        productivity_agent = ProductivityScoringAgent()
    return productivity_agent

# ==============================
# � HELPER FUNCTIONS
# ==============================
def _calculate_score_internal(m: DayMetrics) -> 'ScoreBreakdown':
    """
    Internal function to calculate productivity score.
    This is the same algorithm as the main score() function.
    """
    # Focus subscore (F)
    F1 = min(100.0, 100.0 * (m.deep_work_min / 240.0))
    F2 = max(0.0, 100.0 - 6.0 * m.context_switches)
    F = 0.7 * F1 + 0.3 * F2

    # Sleep subscore (S)
    H = float(m.sleep_hours)
    S = 100.0 if 7.0 <= H <= 9.0 else max(0.0, 100.0 - 15.0 * abs(H - 8.0))

    # Breaks subscore (B)
    R = m.break_minutes / float(max(1, m.focus_minutes))
    if 0.05 <= R <= 0.15:
        B = 100.0
    else:
        B = max(0.0, 100.0 - 800.0 * ((R - 0.10) ** 2))

    # Chronotype alignment subscore (C)
    C = min(100.0, 125.0 * m.hc_ratio)  # 100 at >= 0.8

    # Final EPS
    eps = 0.35 * F + 0.25 * S + 0.20 * B + 0.20 * C

    # Import ScoreBreakdown here to avoid circular import
    return ScoreBreakdown(
        focus=round(F, 1),
        sleep=round(S, 1),
        breaks=round(B, 1),
        chronotype=round(C, 1),
        score=round(eps, 1),
    )

def _interpret_score(score: float) -> str:
    """Provide human-readable interpretation of the productivity score."""
    if score >= 90:
        return "Excellent productivity! You're operating at peak performance."
    elif score >= 80:
        return "Very good productivity with room for minor optimizations."
    elif score >= 70:
        return "Good productivity, but some areas could be improved."
    elif score >= 60:
        return "Moderate productivity with several areas for improvement."
    elif score >= 50:
        return "Below average productivity - significant improvements needed."
    else:
        return "Low productivity - major changes to routine recommended."

def _generate_recommendations(breakdown: 'ScoreBreakdown') -> List[str]:
    """Generate specific recommendations based on score breakdown."""
    recommendations = []

    if breakdown.focus < 70:
        if breakdown.focus < 50:
            recommendations.append("Increase deep work sessions to at least 2-3 hours daily")
        recommendations.append("Minimize context switches by batching similar tasks")
        recommendations.append("Use time-blocking techniques to protect focus time")

    if breakdown.sleep < 80:
        if breakdown.sleep < 60:
            recommendations.append("Prioritize getting 7-9 hours of sleep nightly")
        recommendations.append("Establish a consistent sleep schedule")
        recommendations.append("Create a relaxing bedtime routine")

    if breakdown.breaks < 70:
        recommendations.append("Take more regular breaks - aim for 5-15% of work time")
        recommendations.append("Try the Pomodoro Technique (25min work + 5min break)")
        recommendations.append("Include both micro-breaks and longer restorative breaks")

    if breakdown.chronotype < 70:
        recommendations.append("Schedule high-cognitive tasks during your peak energy hours")
        recommendations.append("Identify your natural energy patterns and align work accordingly")
        recommendations.append("Move routine tasks to lower-energy periods")

    if not recommendations:
        recommendations.append("Maintain your excellent productivity habits!")
        recommendations.append("Consider tracking additional metrics for further optimization")

    return recommendations

# ==============================
# �📥 INPUT MODEL (request body)
# ==============================
class DayMetrics(BaseModel):
    """
    Daily metrics used to compute the Evidence-based Productivity Score (EPS).
    All time values are for a single day.
    """
    deep_work_min: int = Field(
        ...,
        ge=0,
        description=(
            "Total minutes spent in uninterrupted focus blocks ≥ 25 minutes. "
            "Benefits capped at ~240 min/day for diminishing returns."
        ),
        example=210,
    )
    context_switches: int = Field(
        ...,
        ge=0,
        description=(
            "Number of disruptive task/context switches (≥ ~30s) during focus time. "
            "Higher values reduce the focus subscore."
        ),
        example=4,
    )
    sleep_hours: float = Field(
        ...,
        ge=0,
        le=14,
        description=(
            "Hours slept (last night or weighted avg of last 3 nights). "
            "7–9 hours is considered optimal for the sleep subscore."
        ),
        example=7.5,
    )
    break_minutes: int = Field(
        ...,
        ge=0,
        description=(
            "Total minutes of short restorative breaks (micro/macro) taken during the day."
        ),
        example=32,
    )
    focus_minutes: int = Field(
        ...,
        ge=1,
        description=(
            "Total minutes of focus/work for the day (denominator for break ratio). "
            "Cannot be zero; if you have no focus time, use 1 to avoid division by zero."
        ),
        example=400,
    )
    hc_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Fraction (0–1) of high-cognitive minutes scheduled inside the user’s peak window "
            "(derived from chronotype survey + behavior). 0.8 → 80%."
        ),
        example=0.70,
    )


# ==============================
# 📤 OUTPUT MODEL (response)
# ==============================
class ScoreBreakdown(BaseModel):
    """
    Subscores (0–100) plus the final EPS (0–100).
    Higher is better. Each subscore reflects a specific dimension.
    """
    focus: float = Field(
        ...,
        description=(
            "Focus subscore (F): rewards deep-work minutes up to 240, "
            "penalizes context switches."
        ),
        example=83.8,
    )
    sleep: float = Field(
        ...,
        description="Sleep subscore (S): 100 inside 7–9 hours; decreases outside.",
        example=100.0,
    )
    breaks: float = Field(
        ...,
        description=(
            "Breaks subscore (B): ideal micro-break ratio is ~5–15% of focus minutes; "
            "deviation reduces the score."
        ),
        example=100.0,
    )
    chronotype: float = Field(
        ...,
        description=(
            "Chronotype-alignment subscore (C): rewards placing high-cognitive work "
            "inside the user’s peak window; 100 at ≥80% alignment."
        ),
        example=87.5,
    )
    score: float = Field(
        ...,
        description=(
            "Final Evidence-based Productivity Score (EPS), 0–100. "
            "Weighted combination: 35% focus, 25% sleep, 20% breaks, 20% chronotype."
        ),
        example=92.3,
    )


# ==============================
# 🔢 SCORING ENDPOINT
# ==============================
@router.post(
    "/score",
    response_model=ScoreBreakdown,
    summary="Compute daily productivity score (EPS)",
    description=(
        "Calculates a 0–100 productivity score from daily inputs:\n\n"
        "- **Focus (F, 35%)**: Combines deep-work minutes (capped at 240) and a penalty for context switches.\n"
        "- **Sleep (S, 25%)**: Ideal range is 7–9 hours; linear penalty outside.\n"
        "- **Breaks (B, 20%)**: Rewards a break-to-focus ratio in the ~5–15% band.\n"
        "- **Chronotype (C, 20%)**: Rewards aligning high-cognitive tasks with the user's peak window.\n\n"
        "Returns the four subscores and the weighted final score."
    ),
    tags=["productivity"],
)
def score(m: DayMetrics) -> ScoreBreakdown:
    """
    Formulas:
    - F1 (deep work): min(100, 100 * deep_work_min / 240)
    - F2 (switch penalty): max(0, 100 - 6 * context_switches)
    - F  = 0.7*F1 + 0.3*F2

    - S (sleep):
        100 if 7 <= H <= 9,
        else max(0, 100 - 15 * |H - 8|)

    - B (breaks):
        R = break_minutes / focus_minutes
        100 if 0.05 <= R <= 0.15,
        else max(0, 100 - 800 * (R - 0.10)^2)

    - C (chronotype alignment):
        min(100, 125 * hc_ratio)   # 100 at hc_ratio >= 0.8

    - EPS (final):
        0.35*F + 0.25*S + 0.20*B + 0.20*C
    """
    # Use the internal calculation function to avoid code duplication
    return _calculate_score_internal(m)


# ==============================
# 🤖 AI AGENT ENDPOINT
# ==============================
@router.post(
    "/ai-analysis",
    summary="AI-powered productivity analysis",
    description=(
        "Uses Azure AI agent to provide comprehensive productivity analysis with "
        "detailed scoring, interpretation, and personalized recommendations."
    ),
    tags=["productivity", "ai"],
)
def ai_productivity_analysis(m: DayMetrics) -> Dict[str, Any]:
    """
    Get AI-powered productivity analysis using Azure AI agent.

    This endpoint uses a sophisticated AI agent that:
    1. Calculates evidence-based productivity scores
    2. Provides detailed interpretation of each component
    3. Generates personalized recommendations
    4. Suggests optimal scheduling strategies
    """
    try:
        # Convert DayMetrics to dictionary for the AI agent
        metrics_dict = {
            "deep_work_min": m.deep_work_min,
            "context_switches": m.context_switches,
            "sleep_hours": m.sleep_hours,
            "break_minutes": m.break_minutes,
            "focus_minutes": m.focus_minutes,
            "hc_ratio": m.hc_ratio
        }

        # Get the AI agent and analyze productivity
        agent = get_productivity_agent()
        result = agent.analyze_productivity(metrics_dict)

        # Also include the raw score calculation for comparison
        raw_score = _calculate_score_internal(m)

        return {
            "ai_analysis": result,
            "raw_scores": {
                "focus": raw_score.focus,
                "sleep": raw_score.sleep,
                "breaks": raw_score.breaks,
                "chronotype": raw_score.chronotype,
                "overall": raw_score.score
            },
            "metrics_analyzed": metrics_dict
        }

    except Exception as e:
        logger.error(f"Error in AI productivity analysis: {e}")
        return {
            "error": str(e),
            "ai_analysis": {
                "success": False,
                "analysis": "Failed to perform AI analysis"
            },
            "raw_scores": None
        }
