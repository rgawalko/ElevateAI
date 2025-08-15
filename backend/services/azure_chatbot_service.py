import logging
import json
import time
from typing import Dict, List, Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, RunStatus, FunctionTool
from services.chatbot_tools import user_functions, set_function_context

logger = logging.getLogger(__name__)

class AzureChatbotService:
    def __init__(self):
        """Initialize the Azure AI chatbot service"""
        try:
            self.project = AIProjectClient(
                credential=DefaultAzureCredential(),
                endpoint="https://elevate777.services.ai.azure.com/api/projects/firstProject"
            )
            self.agent_id = "asst_qRkSnHGxQQTNxde2V6JWTv2f"
            self.agent = self.project.agents.get_agent(self.agent_id)
            logger.info("✅ Azure Chatbot Service initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure Chatbot Service: {e}")
            raise

    def create_thread(self) -> str:
        """Create a new conversation thread"""
        try:
            thread = self.project.agents.threads.create()
            logger.info(f"📝 Created new thread: {thread.id}")
            return thread.id
        except Exception as e:
            logger.error(f"❌ Failed to create thread: {e}")
            raise

    def send_message(self, thread_id: str, message: str, max_wait_seconds: int = 30) -> Dict[str, Any]:
        """
        Send a message to the chatbot and get response

        Args:
            thread_id: The conversation thread ID
            message: User message to send
            max_wait_seconds: Maximum time to wait for response

        Returns:
            Dict containing the response and metadata
        """
        try:
            logger.info(f"💬 Sending message to thread {thread_id}: {message[:100]}...")

            # Create user message
            user_message = self.project.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logger.info(f"📤 Created user message: {user_message.id}")

            # Start agent run
            run = self.project.agents.runs.create(
                thread_id=thread_id,
                agent_id=self.agent_id
            )
            logger.info(f"🚀 Started agent run: {run.id}")

            # Wait for completion
            start_time = time.time()
            while time.time() - start_time < max_wait_seconds:
                run_status = self.project.agents.runs.get(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_status.status == RunStatus.COMPLETED:
                    logger.info(f"✅ Agent run completed successfully")
                    break
                elif run_status.status == RunStatus.FAILED:
                    logger.error(f"❌ Agent run failed: {run_status.last_error}")
                    return {
                        "success": False,
                        "error": f"Agent run failed: {run_status.last_error}",
                        "message": None
                    }

                time.sleep(1)  # Wait 1 second before checking again
            else:
                logger.warning(f"⏰ Agent run timed out after {max_wait_seconds} seconds")
                return {
                    "success": False,
                    "error": "Response timeout",
                    "message": None
                }

            # Get messages from thread
            messages = self.project.agents.messages.list(
                thread_id=thread_id,
                order=ListSortOrder.DESCENDING,
                limit=10
            )

            # Convert to list and find the latest assistant message
            messages_list = list(messages)
            logger.info(f"📨 Retrieved {len(messages_list)} messages from thread")

            for msg in messages_list:
                if msg.role == "assistant" and msg.text_messages:
                    assistant_response = msg.text_messages[-1].text.value
                    logger.info(f"🤖 Assistant response: {assistant_response[:100]}...")

                    return {
                        "success": True,
                        "message": assistant_response,
                        "thread_id": thread_id,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    }

            logger.warning("⚠️ No assistant response found in messages")
            return {
                "success": False,
                "error": "No assistant response found",
                "message": None
            }

        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return {
                "success": False,
                "error": f"Failed to send message: {str(e)}",
                "message": None
            }

    def get_conversation_history(self, thread_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get conversation history for a thread

        Args:
            thread_id: The conversation thread ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages with role, content, and timestamp
        """
        try:
            messages = self.project.agents.messages.list(
                thread_id=thread_id,
                order=ListSortOrder.ASCENDING,
                limit=limit
            )

            conversation = []
            for msg in messages:
                if msg.text_messages:
                    conversation.append({
                        "role": msg.role,
                        "content": msg.text_messages[-1].text.value,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None,
                        "message_id": msg.id
                    })

            logger.info(f"📚 Retrieved {len(conversation)} messages from conversation history")
            return conversation

        except Exception as e:
            logger.error(f"❌ Error getting conversation history: {e}")
            return []

    def send_message_with_functions_official(self, thread_id: str, message: str,
                                           db_session: Any, user_id: str,
                                           max_wait_seconds: int = 30) -> Dict[str, Any]:
        """
        Send a message to the chatbot with function calling support using Microsoft's official pattern

        Args:
            thread_id: The conversation thread ID
            message: User message to send
            db_session: Database session for function calls
            user_id: User ID for function calls
            max_wait_seconds: Maximum time to wait for response

        Returns:
            Dict containing the response and metadata
        """
        try:
            logger.info(f"💬 Sending message with official functions to thread {thread_id}: {message[:100]}...")

            # Set the function context for database access
            set_function_context(db_session, user_id)

            # Create user message
            user_message = self.project.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logger.info(f"📤 Created user message: {user_message.id}")

            # Create and process a run for the agent to handle the message
            run = self.project.agents.runs.create(
                thread_id=thread_id,
                agent_id=self.agent_id
            )
            logger.info(f"🚀 Started agent run: {run.id}")

            # Poll the run status until it is completed or requires action
            start_time = time.time()
            while time.time() - start_time < max_wait_seconds:
                time.sleep(1)
                run = self.project.agents.runs.get(thread_id=thread_id, run_id=run.id)
                logger.info(f"🔄 Run status: {run.status}")

                if run.status == "completed":
                    logger.info(f"✅ Agent run completed successfully")
                    break
                elif run.status == "requires_action":
                    logger.info(f"🔧 Agent requires function call")

                    if hasattr(run, 'required_action') and run.required_action:
                        tool_calls = run.required_action.submit_tool_outputs.tool_calls
                        tool_outputs = []

                        for tool_call in tool_calls:
                            function_name = tool_call.function.name
                            function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                            logger.info(f"🔧 Calling function: {function_name} with args: {function_args}")

                            # Execute the function using Microsoft's pattern
                            output = self._execute_function_official(function_name, function_args)
                            tool_outputs.append({"tool_call_id": tool_call.id, "output": output})

                        # Submit tool outputs
                        self.project.agents.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                        logger.info(f"📤 Submitted {len(tool_outputs)} tool outputs")
                    else:
                        logger.warning("⚠️ Run requires action but no required_action found")
                        break
                elif run.status == "failed":
                    logger.error(f"❌ Agent run failed: {run.last_error}")
                    break
                elif run.status not in ["queued", "in_progress"]:
                    logger.warning(f"⚠️ Unexpected run status: {run.status}")
                    break

            if time.time() - start_time >= max_wait_seconds:
                logger.warning(f"⏰ Agent run timed out after {max_wait_seconds} seconds")
                return {
                    "success": False,
                    "error": "Response timeout",
                    "message": None
                }

            if run.status == "failed":
                logger.error(f"❌ Agent run failed: {run.last_error}")
                return {
                    "success": False,
                    "error": f"Agent run failed: {run.last_error}",
                    "message": None
                }

            logger.info(f"✅ Run completed with status: {run.status}")

            # Fetch and return the latest assistant message
            messages = self.project.agents.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING, limit=10)
            message_list = list(messages)
            assistant_message = None

            for msg in message_list:
                if msg.role == "assistant" and msg.id != user_message.id:
                    assistant_message = msg
                    break

            if assistant_message and assistant_message.content:
                # Extract text content from the message
                content_text = ""
                for content_item in assistant_message.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        content_text += content_item.text.value

                logger.info(f"📨 Received assistant response: {content_text[:100]}...")
                return {
                    "success": True,
                    "message": content_text,
                    "azure_message_id": assistant_message.id
                }
            else:
                logger.warning("⚠️ No assistant response found")
                return {
                    "success": False,
                    "error": "No response from assistant",
                    "message": None
                }

        except Exception as e:
            logger.error(f"❌ Error sending message with official functions: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": None
            }

    def _execute_function_official(self, function_name: str, function_args: Dict[str, Any]) -> str:
        """Execute a function call using Microsoft's official pattern"""
        try:
            # Import the specific function from user_functions
            for func in user_functions:
                if func.__name__ == function_name:
                    result = func(**function_args)
                    logger.info(f"✅ Function {function_name} executed successfully")
                    return result

            logger.error(f"❌ Function {function_name} not found in user_functions")
            return json.dumps({"error": f"Function {function_name} not found"})
        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}")
            return json.dumps({"error": str(e)})

    def send_message_with_functions(self, thread_id: str, message: str,
                                  function_tools: Optional[Any] = None,
                                  max_wait_seconds: int = 30) -> Dict[str, Any]:
        """
        Send a message to the chatbot with function calling support

        Args:
            thread_id: The conversation thread ID
            message: User message to send
            function_tools: ChatbotTools instance for function calling
            max_wait_seconds: Maximum time to wait for response

        Returns:
            Dict containing the response and metadata
        """
        try:
            logger.info(f"💬 Sending message with functions to thread {thread_id}: {message[:100]}...")

            # Create user message
            user_message = self.project.agents.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            logger.info(f"📤 Created user message: {user_message.id}")

            # Start agent run
            run = self.project.agents.runs.create(
                thread_id=thread_id,
                agent_id=self.agent_id
            )
            logger.info(f"🚀 Started agent run: {run.id}")

            # Wait for completion and handle function calls
            start_time = time.time()
            while time.time() - start_time < max_wait_seconds:
                run_status = self.project.agents.runs.get(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_status.status == RunStatus.COMPLETED:
                    logger.info(f"✅ Agent run completed successfully")
                    break
                elif run_status.status == RunStatus.REQUIRES_ACTION:
                    logger.info(f"🔧 Agent requires function call")

                    # Handle function calls
                    if function_tools and hasattr(run_status, 'required_action'):
                        tool_outputs = []

                        for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                            function_name = tool_call.function.name
                            function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                            logger.info(f"🔧 Calling function: {function_name} with args: {function_args}")

                            # Execute the function
                            result = self._execute_function(function_tools, function_name, function_args)

                            tool_outputs.append({
                                "tool_call_id": tool_call.id,
                                "output": json.dumps(result)
                            })

                        # Submit tool outputs
                        self.project.agents.runs.submit_tool_outputs(
                            thread_id=thread_id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                        logger.info(f"📤 Submitted {len(tool_outputs)} tool outputs")

                elif run_status.status == RunStatus.FAILED:
                    logger.error(f"❌ Agent run failed: {run_status.last_error}")
                    return {
                        "success": False,
                        "error": f"Agent run failed: {run_status.last_error}",
                        "message": None
                    }

                time.sleep(1)  # Wait 1 second before checking again
            else:
                logger.warning(f"⏰ Agent run timed out after {max_wait_seconds} seconds")
                return {
                    "success": False,
                    "error": "Response timeout",
                    "message": None
                }

            # Get messages from thread (same as original method)
            messages = self.project.agents.messages.list(
                thread_id=thread_id,
                order=ListSortOrder.DESCENDING,
                limit=10
            )

            # Convert to list and find the latest assistant message
            message_list = list(messages)
            assistant_message = None

            for msg in message_list:
                if msg.role == "assistant" and msg.id != user_message.id:
                    assistant_message = msg
                    break

            if assistant_message and assistant_message.content:
                # Extract text content from the message
                content_text = ""
                for content_item in assistant_message.content:
                    if hasattr(content_item, 'text') and content_item.text:
                        content_text += content_item.text.value

                logger.info(f"📨 Received assistant response: {content_text[:100]}...")
                return {
                    "success": True,
                    "message": content_text,
                    "azure_message_id": assistant_message.id
                }
            else:
                logger.warning("⚠️ No assistant response found")
                return {
                    "success": False,
                    "error": "No response from assistant",
                    "message": None
                }

        except Exception as e:
            logger.error(f"❌ Error sending message with functions: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": None
            }

    def _execute_function(self, function_tools: Any, function_name: str, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function call from the AI agent"""
        try:
            if hasattr(function_tools, function_name):
                func = getattr(function_tools, function_name)
                result = func(**function_args)
                logger.info(f"✅ Function {function_name} executed successfully")
                return result
            else:
                logger.error(f"❌ Function {function_name} not found")
                return {"error": f"Function {function_name} not found"}
        except Exception as e:
            logger.error(f"❌ Error executing function {function_name}: {e}")
            return {"error": str(e)}