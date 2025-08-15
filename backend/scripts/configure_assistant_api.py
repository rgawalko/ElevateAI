#!/usr/bin/env python3
"""
Script to create a new Azure OpenAI agent with functions using Microsoft's official approach
"""

import sys
import os
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool
from services.chatbot_tools import user_functions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_agent_with_functions():
    """Create a new Azure OpenAI agent with function definitions using Microsoft's official approach"""

    try:
        print("🚀 Creating new Azure OpenAI agent with functions using Microsoft's official approach...")

        # Get environment variables
        project_endpoint = os.environ.get("PROJECT_ENDPOINT", "https://elevate777.services.ai.azure.com/api/projects/firstProject")
        model_deployment = os.environ.get("MODEL_DEPLOYMENT_NAME", "gpt-4o")

        print(f"📋 Project Endpoint: {project_endpoint}")
        print(f"📋 Model Deployment: {model_deployment}")

        # Initialize the AIProjectClient following Microsoft's documentation
        project_client = AIProjectClient(
            endpoint=project_endpoint,
            credential=DefaultAzureCredential()
        )

        # Initialize the FunctionTool with user-defined functions
        functions = FunctionTool(functions=user_functions)

        print(f"📋 Configured {len(user_functions)} functions:")
        for func in user_functions:
            print(f"  - {func.__name__}: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}")

        with project_client:
            # Create an agent with custom functions following Microsoft's pattern
            agent = project_client.agents.create_agent(
                model=model_deployment,
                name="elevate-ai-agent-with-functions",
                instructions="""You are Elevate AI, a helpful productivity assistant that can access user data to provide personalized insights and recommendations.

You have access to the following functions to query user information:
- get_user_profile(): Get basic user profile information
- get_user_preferences(): Get user preferences and settings
- get_recent_activities(days): Get recent activity logs with productivity scores
- get_productivity_stats(days): Get productivity statistics and analytics
- get_current_goals(): Get current active goals with progress
- get_recent_insights(limit): Get AI-generated insights and recommendations

Use these functions to provide personalized, data-driven responses. Always be helpful, encouraging, and focus on actionable productivity advice.""",
                tools=functions.definitions,
            )
            print(f"✅ Created new agent with functions!")
            print(f"📋 Agent ID: {agent.id}")
            print(f"📋 Agent Name: {agent.name}")

            # Save the new agent ID to a file for easy reference
            with open("backend/scripts/new_agent_id.txt", "w") as f:
                f.write(f"New Agent ID: {agent.id}\n")
                f.write(f"Created: {datetime.datetime.now()}\n")
                f.write(f"Model: {model_deployment}\n")
                f.write(f"Functions: {len(user_functions)}\n")

            print(f"\n🔧 To use this new agent, update your AzureChatbotService:")
            print(f"   Change agent_id from 'asst_oYhOp214ksuKLm58D0Q92NzG' to '{agent.id}'")
            print(f"   Or run: python backend/scripts/update_agent_id.py")

            return agent

    except Exception as e:
        print(f"❌ Error creating agent with functions: {e}")
        logger.exception("Full error details:")
        raise

def test_functions_locally():
    """Test the functions locally before creating the agent"""
    print("\n🧪 Testing functions locally...")

    for func in user_functions:
        print(f"\n📋 Function: {func.__name__}")
        print(f"   Description: {func.__doc__.split('.')[0] if func.__doc__ else 'No description'}")

        # Test with no arguments for functions that don't require them
        try:
            if func.__name__ in ['get_user_profile', 'get_user_preferences', 'get_current_goals']:
                print(f"   ⚠️  Requires database context - cannot test without setup")
            else:
                print(f"   ⚠️  Requires parameters - cannot test without setup")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Choose an option:")
    print("1. Test functions locally")
    print("2. Create new agent with functions")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        test_functions_locally()
    elif choice == "2":
        create_agent_with_functions()
    else:
        print("Invalid choice. Please run again and select 1 or 2.")
