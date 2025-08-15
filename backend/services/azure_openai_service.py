import json
import logging
from typing import Dict, List, Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """
    Service for interacting with Azure AI Agent for schedule optimization.
    """

    def __init__(self):
        """Initialize the Azure AI service with project credentials."""
        try:
            self.project = AIProjectClient(
                credential=DefaultAzureCredential(),
                endpoint="https://elevate777.services.ai.azure.com/api/projects/firstProject"
            )
            self.agent_id = "asst_wLK0mb1Fyia1maCWsdKXAQSo"
            self.agent = self.project.agents.get_agent(self.agent_id)
            logger.info("Azure AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI service: {e}")
            raise

    def generate_schedule(self, schedule_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an optimized schedule using Azure AI Agent.

        Args:
            schedule_request: Dictionary containing:
                - date: Schedule date (YYYY-MM-DD)
                - wakeUpTime: Wake up time (HH:MM)
                - activities: List of activities with duration, priority, etc.
                - constraints: Scheduling constraints

        Returns:
            Dictionary containing the optimized schedule
        """
        try:
            # Create a new thread for this scheduling request
            thread = self.project.agents.threads.create()
            logger.info(f"Created thread for schedule generation: {thread.id}")

            # Format the request as a clear prompt for the AI agent
            prompt = self._format_schedule_prompt(schedule_request)

            # Send the scheduling request to the agent
            logger.info(f"Sending message to agent: {repr(prompt[:500])}...")  # Log first 500 chars
            message = self.project.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            logger.info(f"Created message with ID: {message.id}")

            # Process the request with the agent
            logger.info("Starting agent run")
            run = self.project.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.agent_id
            )
            logger.info(f"Agent run completed with status: {run.status}")

            if run.status == "failed":
                error_msg = f"Schedule generation failed: {run.last_error}"
                logger.error(error_msg)
                logger.error(f"Run failure details: {run}")
                return self._create_error_response(error_msg)

            # Get the agent's response
            logger.info("Retrieving messages from thread")
            messages = self.project.agents.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING
            )
            # Convert ItemPaged to list to get count
            messages_list = list(messages)
            logger.info(f"Retrieved {len(messages_list)} messages from thread")

            # Extract the schedule from the agent's response
            agent_response = None
            for i, message in enumerate(messages_list):
                logger.info(f"Message {i}: role={message.role}, has_text_messages={bool(message.text_messages)}")
                if message.role == "assistant" and message.text_messages:
                    agent_response = message.text_messages[-1].text.value
                    logger.info(f"Found assistant response: {repr(agent_response[:200])}...")  # First 200 chars
                    break

            if not agent_response:
                error_msg = "No response received from AI agent"
                logger.error(error_msg)
                return self._create_error_response(error_msg)

            # Parse the JSON response from the agent
            try:
                logger.info(f"Raw agent response received: {repr(agent_response)}")
                logger.info(f"Agent response length: {len(agent_response)} characters")

                # Extract JSON from the response - it might be wrapped in markdown or have extra text
                cleaned_response = agent_response.strip()
                logger.info(f"Cleaned response: {repr(cleaned_response)}")

                # Look for JSON block in markdown
                json_start = cleaned_response.find("```json")
                logger.info(f"Looking for JSON markdown block, found at position: {json_start}")
                if json_start != -1:
                    # Found ```json, extract content between ```json and ```
                    json_start += 7  # Skip ```json
                    json_end = cleaned_response.find("```", json_start)
                    logger.info(f"JSON block end position: {json_end}")
                    if json_end != -1:
                        cleaned_response = cleaned_response[json_start:json_end].strip()
                        logger.info(f"Extracted JSON from markdown block: {repr(cleaned_response)}")
                else:
                    # Look for any ``` blocks
                    json_start = cleaned_response.find("```")
                    if json_start != -1:
                        json_start += 3  # Skip ```
                        json_end = cleaned_response.find("```", json_start)
                        if json_end != -1:
                            cleaned_response = cleaned_response[json_start:json_end].strip()
                    else:
                        # Look for JSON object starting with {
                        json_start = cleaned_response.find("{")
                        if json_start != -1:
                            # Find the matching closing brace
                            brace_count = 0
                            json_end = json_start
                            for i, char in enumerate(cleaned_response[json_start:], json_start):
                                if char == "{":
                                    brace_count += 1
                                elif char == "}":
                                    brace_count -= 1
                                    if brace_count == 0:
                                        json_end = i + 1
                                        break
                            cleaned_response = cleaned_response[json_start:json_end]

                logger.info(f"Final cleaned response to parse: {repr(cleaned_response)}")
                schedule_data = json.loads(cleaned_response)
                logger.info(f"Successfully parsed JSON response from agent")
                logger.info(f"Parsed schedule data structure: {json.dumps(schedule_data, indent=2)}")

                # Validate the structure
                if "scheduledActivities" in schedule_data:
                    logger.info(f"Found {len(schedule_data['scheduledActivities'])} scheduled activities")
                    for i, activity in enumerate(schedule_data["scheduledActivities"]):
                        logger.info(f"Activity {i}: {activity}")
                        # Check for required fields
                        required_fields = ["name", "startTime", "endTime"]
                        missing_fields = [field for field in required_fields if field not in activity]
                        if missing_fields:
                            logger.warning(f"Activity {i} missing required fields: {missing_fields}")
                else:
                    logger.warning("No 'scheduledActivities' found in response")
                    logger.info(f"Available keys in response: {list(schedule_data.keys())}")

                logger.info(f"Successfully generated schedule for {schedule_request.get('date')}")
                return schedule_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse agent response as JSON: {e}")
                logger.error(f"JSON decode error details: {type(e).__name__}: {str(e)}")
                logger.error(f"Error position: line {e.lineno}, column {e.colno}")
                logger.error(f"Raw agent response: {repr(agent_response)}")
                logger.error(f"Cleaned response that failed to parse: {repr(cleaned_response)}")
                return self._create_fallback_response(schedule_request, agent_response)

        except Exception as e:
            logger.error(f"Error generating schedule: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            logger.error(f"Request data that caused error: {schedule_request}")
            return self._create_error_response(f"Detailed error: {type(e).__name__}: {str(e)}")

    def _format_schedule_prompt(self, request: Dict[str, Any]) -> str:
        """
        Format the schedule request into a clear prompt for the AI agent.
        """
        request_json = json.dumps(request, indent=2)

        prompt = f"""
Please create an optimized daily schedule for the following request:

{request_json}

Return your response as a valid JSON object following this exact structure:
{{
  "date": "YYYY-MM-DD",
  "totalDuration": <total_scheduled_minutes>,
  "scheduledActivities": [
    {{
      "name": "Activity Name",
      "startTime": "HH:MM",
      "endTime": "HH:MM",
      "durationMinutes": <minutes>,
      "priority": <1-5>,
      "category": "work|exercise|learning|personal|break"
    }}
  ],
  "unscheduledActivities": [
    {{
      "name": "Activity Name",
      "durationMinutes": <minutes>,
      "priority": <1-5>,
      "reason": "Why it couldn't be scheduled"
    }}
  ],
  "breaks": [
    {{
      "name": "Break Type",
      "startTime": "HH:MM",
      "endTime": "HH:MM",
      "durationMinutes": <minutes>,
      "category": "break"
    }}
  ],
  "summary": {{
    "totalWorkTime": <work_minutes>,
    "totalBreakTime": <break_minutes>,
    "totalFreeTime": <free_minutes>,
    "productivityScore": <0-100>,
    "balanceScore": <0-100>,
    "recommendations": [
      "High-priority tasks scheduled during peak productivity hours (9-11 AM)",
      "Strategic breaks placed to maintain energy levels",
      "Work-life balance optimized with proper time allocation",
      "Activities grouped by context to minimize task switching"
    ]
  }},
  "optimizationDetails": {{
    "priorityOptimization": "Scheduled high-priority tasks during peak hours",
    "breakOptimization": "Added strategic breaks every X hours",
    "timeWindowRespected": "All time constraints were respected",
    "workLifeBalance": "Achieved optimal work-life balance ratio"
  }}
}}

Remember:
- NO overlapping times
- Respect ALL time windows
- Work activities only during work hours
- Insert breaks when consecutive work limit reached
- Include mandatory lunch break if specified
- Provide specific optimization explanations in recommendations
"""
        return prompt

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create a standardized error response."""
        return {
            "success": False,
            "error": error_message,
            "schedule": None,
            "source": "azure_ai_agent",
            "timestamp": datetime.now().isoformat()
        }

    def _create_fallback_response(self, request: Dict[str, Any], raw_response: str) -> Dict[str, Any]:
        """Create a fallback response when JSON parsing fails."""
        return {
            "success": False,
            "error": "Failed to parse AI response",
            "raw_response": raw_response,
            "fallback_schedule": self._create_basic_schedule(request),
            "source": "azure_ai_agent_fallback",
            "timestamp": datetime.now().isoformat()
        }

    def _create_basic_schedule(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic fallback schedule when AI fails."""
        activities = request.get('activities', [])
        date = request.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Sort activities by priority
        sorted_activities = sorted(activities, key=lambda x: x.get('priority', 5))

        return {
            "date": date,
            "totalDuration": 0,
            "scheduledActivities": [],
            "unscheduledActivities": [
                {
                    "name": activity.get('name', 'Unknown Activity'),
                    "durationMinutes": activity.get('durationMinutes', 60),
                    "priority": activity.get('priority', 3),
                    "reason": "AI agent failed - manual scheduling required"
                }
                for activity in sorted_activities
            ],
            "breaks": [],
            "summary": {
                "totalWorkTime": 0,
                "totalBreakTime": 0,
                "totalFreeTime": 0,
                "productivityScore": 0,
                "balanceScore": 0,
                "recommendations": ["AI scheduling failed - please try again or schedule manually"]
            }
        }

# Create a singleton instance
azure_openai_service = AzureOpenAIService()