#!/usr/bin/env python3
"""
Script to update the agent ID in AzureChatbotService with the new agent that has functions
"""

import sys
import os
import re

def update_agent_id():
    """Update the agent ID in the Azure chatbot service"""
    
    try:
        # Read the new agent ID from file
        agent_id_file = "backend/scripts/new_agent_id.txt"
        if not os.path.exists(agent_id_file):
            print("❌ new_agent_id.txt not found. Please run configure_assistant_api.py first.")
            return False
        
        with open(agent_id_file, "r") as f:
            content = f.read()
            
        # Extract agent ID using regex
        match = re.search(r"New Agent ID: (asst_[a-zA-Z0-9]+)", content)
        if not match:
            print("❌ Could not find agent ID in new_agent_id.txt")
            return False
        
        new_agent_id = match.group(1)
        print(f"📋 Found new agent ID: {new_agent_id}")
        
        # Update the Azure chatbot service file
        service_file = "backend/services/azure_chatbot_service.py"
        if not os.path.exists(service_file):
            print(f"❌ Service file not found: {service_file}")
            return False
        
        with open(service_file, "r", encoding="utf-8") as f:
            service_content = f.read()

        # Replace the old agent ID with the new one
        old_pattern = r'self\.agent_id = "asst_[a-zA-Z0-9]+"'
        new_replacement = f'self.agent_id = "{new_agent_id}"'

        updated_content = re.sub(old_pattern, new_replacement, service_content)

        if updated_content == service_content:
            print("⚠️  No agent ID found to update in the service file")
            return False

        # Write the updated content back
        with open(service_file, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print(f"✅ Successfully updated agent ID in {service_file}")
        print(f"   Old: asst_oYhOp214ksuKLm58D0Q92NzG")
        print(f"   New: {new_agent_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating agent ID: {e}")
        return False

if __name__ == "__main__":
    success = update_agent_id()
    if success:
        print("\n🎉 Agent ID updated successfully!")
        print("🔄 Please restart your backend server to use the new agent with functions.")
    else:
        print("\n❌ Failed to update agent ID.")
        sys.exit(1)
