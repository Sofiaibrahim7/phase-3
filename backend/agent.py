import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel
from backend.mcp_tools import registered_tools


class AgentResponse(BaseModel):
    response: str
    action_type: str  # task_created | task_updated | task_deleted | none
    task_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class OpenAIAgent:
    """
    An OpenAI Agent that serves as an intelligent chatbot capable of interpreting 
    user natural language, selecting appropriate MCP tools, confirming actions politely, 
    and handling errors gracefully.
    """
    
    def __init__(self):
        # In a real implementation, this would initialize the OpenAI client
        # For now, we'll simulate the functionality
        pass
    
    async def process_message(
        self, 
        message: str, 
        conversation_id: int, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process a user message and return an appropriate response.
        """
        # Analyze the message to determine intent
        intent = self._analyze_intent(message)
        
        # Determine if any MCP tools need to be used
        tool_result = await self._use_appropriate_tool_if_needed(intent, message)
        
        # Generate response based on intent and tool results
        response = self._generate_response(message, intent, tool_result)
        
        # Determine if any action needs to be taken (task creation, etc.)
        action_type, task_id, details = self._determine_action(intent, message)
        
        return AgentResponse(
            response=response,
            action_type=action_type,
            task_id=task_id,
            details=details
        )
    
    def _analyze_intent(self, message: str) -> str:
        """
        Analyze the user message to determine the intent.
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["create", "add", "new", "make"]):
            if any(word in message_lower for word in ["task", "todo", "to-do"]):
                return "create_task"
        elif any(word in message_lower for word in ["update", "change", "modify"]):
            if any(word in message_lower for word in ["task", "todo", "to-do"]):
                return "update_task"
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            if any(word in message_lower for word in ["task", "todo", "to-do"]):
                return "delete_task"
        elif any(word in message_lower for word in ["list", "show", "view", "see"]):
            if any(word in message_lower for word in ["task", "todo", "to-do"]):
                return "list_tasks"
        
        return "general_query"
    
    async def _use_appropriate_tool_if_needed(self, intent: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Select and use an appropriate MCP tool if needed.
        """
        # Check if we have tools that match the intent
        for tool_id, tool_info in registered_tools.items():
            if intent in tool_info.description.lower():
                # Execute the tool
                # For simulation purposes, we'll just return a mock result
                return {
                    "tool_used": tool_id,
                    "result": f"Simulated execution of {tool_id} for {intent}",
                    "parameters_used": {}
                }
        
        return None
    
    def _generate_response(self, message: str, intent: str, tool_result: Optional[Dict[str, Any]]) -> str:
        """
        Generate a response based on the message, intent, and tool results.
        """
        if tool_result:
            return f"I processed your request to '{message}'. Used tool: {tool_result['tool_used']}. Result: {tool_result['result']}"
        
        if intent == "create_task":
            return f"I can help you create a task: '{message}'. What details would you like to add?"
        elif intent == "update_task":
            return f"I can help you update a task based on: '{message}'. Which task would you like to update?"
        elif intent == "delete_task":
            return f"I can help you delete a task based on: '{message}'. Which task would you like to delete?"
        elif intent == "list_tasks":
            return f"You asked to list tasks: '{message}'. Here are your tasks..."
        else:
            return f"I received your message: '{message}'. How can I assist you today?"
    
    def _determine_action(self, intent: str, message: str) -> tuple[str, Optional[int], Optional[Dict[str, Any]]]:
        """
        Determine if any action needs to be taken based on the intent.
        """
        if intent == "create_task":
            return "task_created", None, {"message": message}
        elif intent == "update_task":
            return "task_updated", 1, {"message": message}
        elif intent == "delete_task":
            return "task_deleted", 1, {"message": message}
        else:
            return "none", None, None