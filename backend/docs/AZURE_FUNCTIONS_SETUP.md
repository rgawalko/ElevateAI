# Azure AI Agent Functions Setup Guide

This guide follows Microsoft's official Azure AI Agents documentation for implementing function calling.

## 🔧 **Implementation Overview**

We've implemented function calling using Microsoft's **exact official pattern** with:
- **Standalone functions** that return JSON strings (not class methods)
- **FunctionTool** for programmatic agent configuration
- **Global context** for database access via `set_function_context()`
- **user_functions set** containing all available functions
- **Programmatic agent creation** (not portal configuration)

## 📋 **Available Functions**

Our AI agent has access to 6 functions for querying user data:

1. **`get_user_profile()`** - Basic user information (name, email, timezone, etc.)
2. **`get_user_preferences()`** - Work hours, break settings, AI preferences
3. **`get_recent_activities(days=7)`** - Recent activity logs with productivity scores
4. **`get_productivity_stats(days=7)`** - Comprehensive productivity analytics
5. **`get_current_goals()`** - Active goals with progress tracking
6. **`get_recent_insights(limit=5)`** - AI-generated insights and recommendations

## 🚀 **Setup Process (Programmatic Only)**

**Important**: Functions are added through **code only**, not through Azure AI Studio portal. This follows Microsoft's official documentation pattern.

### **Step 1: Create New Agent with Functions**

Use our script to create a new agent with functions pre-configured:

```bash
python backend/scripts/configure_assistant_api.py
```

Choose option 2 to create a new agent. This will:
- Create a new Azure AI agent with all 6 functions configured programmatically
- Use Microsoft's official `FunctionTool(functions=user_functions)` pattern
- Save the new agent ID to `backend/scripts/new_agent_id.txt`
- Provide instructions for updating your service

### **Step 2: Update Your Service**

Automatically update the agent ID in your service:

```bash
python backend/scripts/update_agent_id.py
```

Or manually update `backend/services/azure_chatbot_service.py`:
```python
self.agent_id = "your_new_agent_id_here"
```

### **Step 3: Test the Functions**

Test the agent with functions using Microsoft's exact pattern:

```bash
python backend/scripts/test_agent_functions.py
```

## 💻 **Code Implementation**

Following Microsoft's official pattern, functions are defined as standalone functions and added programmatically:

```python
# Define standalone functions that return JSON strings
def get_user_profile() -> str:
    """Get the user's basic profile information including name, email, bio, timezone, and account details."""
    # Implementation returns json.dumps(result)

def get_recent_activities(days: int = 7) -> str:
    """Get the user's recent activity logs with productivity scores, mood, and energy levels."""
    # Implementation returns json.dumps(result)

# Define user functions set
user_functions = {
    get_user_profile,
    get_user_preferences,
    get_recent_activities,
    get_productivity_stats,
    get_current_goals,
    get_recent_insights
}

# Create agent with functions
functions = FunctionTool(functions=user_functions)
agent = project_client.agents.create_agent(
    model="gpt-4o",
    name="elevate-ai-agent-with-functions",
    instructions="You are Elevate AI...",
    tools=functions.definitions,
)
```

## 🔄 **Update Agent ID**

If you created a new agent, update the agent ID in your service:

1. **Open**: `backend/services/azure_chatbot_service.py`
2. **Find**: `self.agent_id = "asst_oYhOp214ksuKLm58D0Q92NzG"`
3. **Replace**: With your new agent ID from the script output

## 🧪 **Testing**

1. **Start the backend**: `cd backend && python start.py`
2. **Login as Alice**: `alice@elevate-ai.com` / `demo123!`
3. **Go to chatbot** and try these queries:

### Test Queries
- **"What's my profile information?"** → Tests `get_user_profile()`
- **"What did I do yesterday?"** → Tests `get_recent_activities(days=1)`
- **"Show me my productivity stats for the last week"** → Tests `get_productivity_stats(days=7)`
- **"What are my current goals?"** → Tests `get_current_goals()`
- **"What insights do you have for me?"** → Tests `get_recent_insights()`
- **"What are my work preferences?"** → Tests `get_user_preferences()`

## 🔍 **Troubleshooting**

### Functions Not Working?
1. **Check agent configuration** - Ensure all 6 functions are added
2. **Verify function names** - Must match exactly (case-sensitive)
3. **Check backend logs** - Look for function execution errors
4. **Test sample data** - Run `python backend/scripts/create_sample_data.py`

### Database Errors?
1. **Ensure demo users exist** - Run `python backend/scripts/create_demo_users.py`
2. **Check sample data** - Run `python backend/scripts/create_sample_data.py`
3. **Verify database connection** - Check PostgreSQL is running

### Agent Not Responding?
1. **Check Azure credentials** - Ensure DefaultAzureCredential works
2. **Verify agent ID** - Make sure it matches your configured agent
3. **Check Azure AI Studio** - Ensure agent is active and configured

## 📊 **Function Response Format**

All functions return JSON strings with structured data:

```json
{
  "activities": [...],
  "total_count": 10,
  "date_range": "Last 7 days"
}
```

The AI agent automatically parses these responses and provides natural language answers to users.

## 🎯 **Next Steps**

Once functions are configured:
1. ✅ **Test all functions** with sample queries
2. ✅ **Verify data accuracy** - Check if responses match database
3. ✅ **Add more sample data** if needed for richer testing
4. ✅ **Customize agent instructions** for better responses
5. ✅ **Monitor function performance** in production

The AI agent will now provide **personalized, data-driven insights** based on real user data from your PostgreSQL database! 🚀
