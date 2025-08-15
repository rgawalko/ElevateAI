#!/usr/bin/env python3
"""
Script to update the Azure OpenAI assistant with function definitions
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.azure_chatbot_service import AzureChatbotService
from services.chatbot_tools import create_function_definitions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_assistant_with_functions():
    """Update the Azure OpenAI assistant with function definitions"""
    
    try:
        print("🚀 Updating Azure OpenAI assistant with function definitions...")
        
        # Initialize the Azure service
        azure_service = AzureChatbotService()
        
        # Get function definitions
        function_definitions = create_function_definitions()
        
        print(f"📋 Found {len(function_definitions)} function definitions:")
        for func_def in function_definitions:
            func_name = func_def["function"]["name"]
            func_desc = func_def["function"]["description"]
            print(f"  - {func_name}: {func_desc}")
        
        # Update the assistant
        # Note: This would typically be done through the Azure AI Studio or API
        # For now, we'll just print the function definitions that need to be added
        
        print("\n📝 Function definitions to add to your Azure OpenAI assistant:")
        print("=" * 80)
        
        for i, func_def in enumerate(function_definitions, 1):
            func = func_def["function"]
            print(f"\n{i}. Function: {func['name']}")
            print(f"   Description: {func['description']}")
            print(f"   Parameters: {func['parameters']}")
        
        print("\n" + "=" * 80)
        print("📋 Instructions:")
        print("1. Go to Azure AI Studio (https://ai.azure.com)")
        print("2. Navigate to your project and find your assistant")
        print("3. Go to the 'Tools' section")
        print("4. Add each function definition above as a 'Function' tool")
        print("5. Make sure to copy the exact function names and parameter schemas")
        print("\n✅ Function definitions ready for Azure OpenAI assistant!")
        
        return function_definitions
        
    except Exception as e:
        print(f"❌ Error updating assistant: {e}")
        raise

if __name__ == "__main__":
    update_assistant_with_functions()
