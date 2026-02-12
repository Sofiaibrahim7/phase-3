"""
OpenAI Agent for interpreting natural language and selecting appropriate MCP tools.

This module implements an intelligent chatbot that can understand user requests,
select appropriate tools, confirm actions, and handle errors gracefully.
Uses the OpenAI Assistants API for advanced capabilities.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import os
from sqlmodel import Session
from models.database_models import Task, Conversation, Message, TaskStatus, PriorityLevel, RoleType


class ToolResult(Enum):
    """Enum for tool execution results."""
    SUCCESS = "success"
    ERROR = "error"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"


@dataclass
class ToolCall:
    """Represents a tool call with its arguments."""
    name: str
    arguments: Dict[str, Any]


@dataclass
class AgentResponse:
    """Response from the agent including message and tool calls."""
    message: str
    tool_calls: List[ToolCall]
    needs_confirmation: bool
    confirmation_message: Optional[str] = None


class MCPTaskManager:
    """Manages MCP tasks and their execution."""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.available_tools = {
            "create_task": self._create_task,
            "update_task": self._update_task,
            "delete_task": self._delete_task,
            "get_task": self._get_task,
            "list_tasks": self._list_tasks,
            "create_conversation": self._create_conversation,
            "add_message": self._add_message,
            "get_conversation": self._get_conversation,
        }
    
    def get_tool_schema(self) -> List[Dict]:
        """Return the schema for all available tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the task"},
                            "description": {"type": "string", "description": "Description of the task"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "Initial status of the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Priority level of the task"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title of the task"},
                            "description": {"type": "string", "description": "New description of the task"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "New status of the task"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "New priority level of the task"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to delete"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task",
                    "description": "Get details of a specific task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to retrieve"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "Filter tasks by status"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_conversation",
                    "description": "Create a new conversation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the conversation"},
                            "description": {"type": "string", "description": "Description of the conversation"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_message",
                    "description": "Add a message to a conversation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "conversation_id": {"type": "integer", "description": "ID of the conversation"},
                            "content": {"type": "string", "description": "Content of the message"},
                            "role": {"type": "string", "enum": ["user", "assistant", "system"], "description": "Role of the message sender"}
                        },
                        "required": ["conversation_id", "content", "role"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_conversation",
                    "description": "Get details of a specific conversation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the conversation to retrieve"}
                        },
                        "required": ["id"]
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given arguments."""
        if tool_name not in self.available_tools:
            return {
                "result": ToolResult.NOT_FOUND.value,
                "message": f"Tool '{tool_name}' not found",
                "data": None
            }
        
        try:
            result = await self.available_tools[tool_name](arguments)
            return {
                "result": ToolResult.SUCCESS.value,
                "message": "Tool executed successfully",
                "data": result
            }
        except Exception as e:
            return {
                "result": ToolResult.ERROR.value,
                "message": str(e),
                "data": None
            }
    
    async def _create_task(self, args: Dict[str, Any]):
        """Create a new task."""
        from sqlmodel import select
        # Find the highest existing task ID to increment
        statement = select(Task).order_by(Task.id.desc()).limit(1)
        result = self.db_session.exec(statement).first()
        task_id = 1 if not result else result.id + 1
        
        # Create new task
        task = Task(
            id=task_id,
            title=args.get("title"),
            description=args.get("description", ""),
            status=TaskStatus(args.get("status", "pending")),
            priority=PriorityLevel(args.get("priority", "medium"))
        )
        
        # Associate with conversation if provided
        if "conversation_id" in args:
            task.conversation_id = args["conversation_id"]
        
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task
    
    async def _update_task(self, args: Dict[str, Any]):
        """Update an existing task."""
        task_id = args.get("id")
        task = self.db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Update fields if provided
        if "title" in args:
            task.title = args["title"]
        if "description" in args:
            task.description = args["description"]
        if "status" in args:
            task.status = TaskStatus(args["status"])
        if "priority" in args:
            task.priority = PriorityLevel(args["priority"])
        if "conversation_id" in args:
            task.conversation_id = args["conversation_id"]
        
        self.db_session.add(task)
        self.db_session.commit()
        self.db_session.refresh(task)
        return task
    
    async def _delete_task(self, args: Dict[str, Any]):
        """Delete a task."""
        task_id = args.get("id")
        task = self.db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        self.db_session.delete(task)
        self.db_session.commit()
        return task
    
    async def _get_task(self, args: Dict[str, Any]):
        """Get a specific task."""
        task_id = args.get("id")
        task = self.db_session.get(Task, task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        return task
    
    async def _list_tasks(self, args: Dict[str, Any]):
        """List all tasks, optionally filtered by status."""
        from sqlmodel import select
        statement = select(Task)
        
        status_filter = args.get("status")
        if status_filter:
            statement = statement.where(Task.status == TaskStatus(status_filter))
        
        tasks = self.db_session.exec(statement).all()
        return tasks
    
    async def _create_conversation(self, args: Dict[str, Any]):
        """Create a new conversation."""
        from sqlmodel import select
        # Find the highest existing conversation ID to increment
        statement = select(Conversation).order_by(Conversation.id.desc()).limit(1)
        result = self.db_session.exec(statement).first()
        conv_id = 1 if not result else result.id + 1
        
        conversation = Conversation(
            id=conv_id,
            title=args.get("title"),
            description=args.get("description", "")
        )
        
        self.db_session.add(conversation)
        self.db_session.commit()
        self.db_session.refresh(conversation)
        return conversation
    
    async def _add_message(self, args: Dict[str, Any]):
        """Add a message to a conversation."""
        from sqlmodel import select
        # Find the highest existing message ID to increment
        statement = select(Message).order_by(Message.id.desc()).limit(1)
        result = self.db_session.exec(statement).first()
        msg_id = 1 if not result else result.id + 1
        
        # Verify conversation exists
        conversation = self.db_session.get(Conversation, args.get("conversation_id"))
        if not conversation:
            raise ValueError(f"Conversation with ID {args.get('conversation_id')} not found")
        
        message = Message(
            id=msg_id,
            content=args.get("content"),
            role=RoleType(args.get("role", "user")),
            conversation_id=args.get("conversation_id")
        )
        
        self.db_session.add(message)
        self.db_session.commit()
        self.db_session.refresh(message)
        return message
    
    async def _get_conversation(self, args: Dict[str, Any]):
        """Get a specific conversation."""
        conv_id = args.get("id")
        conversation = self.db_session.get(Conversation, conv_id)
        if not conversation:
            raise ValueError(f"Conversation with ID {conv_id} not found")
        
        return conversation


class OpenAIAgent:
    """OpenAI Agent that interprets natural language and selects appropriate tools."""
    
    def __init__(self, api_key: str, db_session: Session):
        self.api_key = api_key
        self.db_session = db_session
        self.task_manager = MCPTaskManager(db_session)
        self.conversation_history = []
    
    def _needs_confirmation(self, tool_name: str) -> bool:
        """Determine if a tool needs confirmation before execution."""
        confirmation_required = ["delete_task", "update_task"]
        return tool_name in confirmation_required
    
    def _format_confirmation_message(self, tool_call: ToolCall) -> str:
        """Format a confirmation message for a tool call."""
        if tool_call.name == "delete_task":
            return f"I'm about to delete task #{tool_call.arguments.get('id')}. Is that OK?"
        elif tool_call.name == "update_task":
            task_id = tool_call.arguments.get('id')
            updates = ", ".join([f"{k}={v}" for k, v in tool_call.arguments.items() if k != 'id'])
            return f"I'm about to update task #{task_id} with {updates}. Is that OK?"
        return f"I'm about to execute '{tool_call.name}' with arguments {tool_call.arguments}. Please confirm."
    
    async def process_request(self, user_input: str) -> AgentResponse:
        """Process a user request and return an appropriate response."""
        # This is a simplified version - in a real implementation, you would use
        # the OpenAI Assistants API to process the request
        # For this example, we'll parse the request manually
        
        user_input_lower = user_input.lower()
        tool_calls = []
        
        # Determine which tool to call based on the user's request
        if "create" in user_input_lower and ("task" in user_input_lower or "new" in user_input_lower):
            # Extract title from the message
            title = "New task"
            if "to" in user_input_lower:
                title = user_input_lower.split("to")[1].strip()
            elif "for" in user_input_lower:
                title = user_input_lower.split("for")[1].strip()
            
            tool_calls.append(ToolCall(name="create_task", arguments={"title": title, "status": "pending"}))
        elif "update" in user_input_lower and "task" in user_input_lower:
            import re
            id_match = re.search(r'#(\d+)', user_input_lower)
            status_match = re.search(r'(pending|in_progress|completed)', user_input_lower)
            
            if id_match:
                task_id = int(id_match.group(1))
                status = status_match.group(1) if status_match else "in_progress"
                
                tool_calls.append(ToolCall(name="update_task", arguments={"id": task_id, "status": status}))
        elif "delete" in user_input_lower and "task" in user_input_lower:
            import re
            id_match = re.search(r'#(\d+)', user_input_lower)
            
            if id_match:
                task_id = int(id_match.group(1))
                
                tool_calls.append(ToolCall(name="delete_task", arguments={"id": task_id}))
        elif "show" in user_input_lower or "list" in user_input_lower or "all" in user_input_lower:
            # Check if filtering by status
            status = None
            if "pending" in user_input_lower:
                status = "pending"
            elif "in progress" in user_input_lower or "in_progress" in user_input_lower:
                status = "in_progress"
            elif "completed" in user_input_lower:
                status = "completed"
            
            params = {}
            if status:
                params["status"] = status
                
            tool_calls.append(ToolCall(name="list_tasks", arguments=params))
        elif ("get" in user_input_lower or "show" in user_input_lower or "what" in user_input_lower) and "task" in user_input_lower:
            import re
            id_match = re.search(r'#(\d+)', user_input_lower)
            
            if id_match:
                task_id = int(id_match.group(1))
                
                tool_calls.append(ToolCall(name="get_task", arguments={"id": task_id}))
        
        # Check if any of the tools need confirmation
        needs_confirmation = any(self._needs_confirmation(tc.name) for tc in tool_calls)
        confirmation_message = None
        
        if needs_confirmation and tool_calls:
            # Just use the first tool that needs confirmation for the message
            for tc in tool_calls:
                if self._needs_confirmation(tc.name):
                    confirmation_message = self._format_confirmation_message(tc)
                    break
        
        return AgentResponse(
            message="Processing your request..." if tool_calls else "I'm not sure how to help with that.",
            tool_calls=tool_calls,
            needs_confirmation=needs_confirmation,
            confirmation_message=confirmation_message
        )
    
    async def execute_tool_calls(self, tool_calls: List[ToolCall], confirm_execution: bool = True) -> List[Dict[str, Any]]:
        """Execute the tool calls and return results."""
        results = []
        
        for tool_call in tool_calls:
            # Skip execution if confirmation is required but not given
            if confirm_execution and self._needs_confirmation(tool_call.name):
                results.append({
                    "tool_name": tool_call.name,
                    "result": "pending_confirmation",
                    "message": f"Action '{tool_call.name}' requires confirmation"
                })
                continue
            
            result = await self.task_manager.execute_tool(tool_call.name, tool_call.arguments)
            results.append({
                "tool_name": tool_call.name,
                **result
            })
        
        return results
    
    async def handle_user_request(self, user_input: str, confirm_actions: bool = True, db_session: Session = None) -> str:
        """Handle a complete user request from interpretation to execution."""
        # Use the provided session or fall back to the instance's session
        session_to_use = db_session or self.db_session
        
        # Create a temporary task manager with the session
        temp_task_manager = MCPTaskManager(session_to_use)
        
        # Process the request
        agent_response = await self.process_request(user_input)
        
        # If confirmation is needed, return the confirmation message
        if agent_response.needs_confirmation:
            if confirm_actions:
                return agent_response.confirmation_message or agent_response.message
            else:
                # Execute without confirmation if explicitly allowed
                results = await self.execute_tool_calls_with_session(agent_response.tool_calls, session_to_use, confirm_execution=False)
                return self._format_results(results)
        
        # If no confirmation needed, execute the tools directly
        if agent_response.tool_calls:
            results = await self.execute_tool_calls_with_session(agent_response.tool_calls, session_to_use, confirm_execution=False)
            return self._format_results(results)
        
        # Return the natural language response if no tools were called
        return agent_response.message
    
    async def execute_tool_calls_with_session(self, tool_calls: List[ToolCall], db_session: Session, confirm_execution: bool = True) -> List[Dict[str, Any]]:
        """Execute tool calls with a specific session."""
        temp_task_manager = MCPTaskManager(db_session)
        results = []
        
        for tool_call in tool_calls:
            # Skip execution if confirmation is required but not given
            if confirm_execution and self._needs_confirmation(tool_call.name):
                results.append({
                    "tool_name": tool_call.name,
                    "result": "pending_confirmation",
                    "message": f"Action '{tool_call.name}' requires confirmation"
                })
                continue
            
            result = await temp_task_manager.execute_tool(tool_call.name, tool_call.arguments)
            results.append({
                "tool_name": tool_call.name,
                **result
            })
        
        return results
    
    def _needs_confirmation(self, tool_name: str) -> bool:
        """Determine if a tool needs confirmation before execution."""
        confirmation_required = ["delete_task", "update_task"]
        return tool_name in confirmation_required
    
    def _format_results(self, results: List[Dict[str, Any]]) -> str:
        """Format the results of tool executions into a user-friendly message."""
        messages = []
        
        for result in results:
            tool_name = result["tool_name"]
            result_status = result["result"]
            
            if result_status == ToolResult.SUCCESS.value:
                if tool_name == "list_tasks":
                    tasks = result.get("data", [])
                    if tasks:
                        task_list = "\n".join([f"- {task.id}: {task.title} ({task.status.value})" for task in tasks])
                        messages.append(f"Here are the tasks:\n{task_list}")
                    else:
                        messages.append("No tasks found.")
                elif tool_name == "get_task":
                    task = result.get("data", {})
                    messages.append(f"Task #{task.id}: {task.title} ({task.status.value})")
                elif tool_name in ["create_task", "update_task"]:
                    task = result.get("data", {})
                    messages.append(f"Task updated successfully: {task.title}")
                elif tool_name == "delete_task":
                    task = result.get("data", {})
                    messages.append(f"Task deleted: {task.title}")
                elif tool_name == "create_conversation":
                    conv = result.get("data", {})
                    messages.append(f"Conversation created: {conv.title}")
                elif tool_name == "get_conversation":
                    conv = result.get("data", {})
                    messages.append(f"Conversation: {conv.title}")
                elif tool_name == "add_message":
                    msg = result.get("data", {})
                    messages.append(f"Message added to conversation #{msg.conversation_id}")
                else:
                    messages.append(result["message"])
            elif result_status == ToolResult.NOT_FOUND.value:
                # Handle task not found errors gracefully
                if "task" in tool_name and "not found" in result["message"].lower():
                    messages.append(f"I couldn't find that task. {self._suggest_alternatives(result)}")
                else:
                    messages.append(f"Sorry, {result['message']}")
            elif result_status == ToolResult.ERROR.value:
                messages.append(f"Sorry, I encountered an error: {result['message']}")
            else:
                messages.append(result["message"])
        
        return " ".join(messages) if messages else "Operation completed."
    
    def _suggest_alternatives(self, result: Dict[str, Any]) -> str:
        """Suggest alternatives when a task is not found."""
        # Extract the task ID from the error message
        import re
        match = re.search(r"ID (\d+)", result["message"])
        if match:
            task_id = match.group(1)
            # In a real implementation, you would search for similar tasks
            # For this example, we'll just suggest looking at all tasks
            return "Would you like me to list all tasks so you can find the right one?"
        
        return "Would you like me to help you with something else?"