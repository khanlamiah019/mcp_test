"""
MCP Framework - Model Context Protocol

A simple, educational framework for creating MCP tools.
Students can easily extend this by adding their own tools.

Usage:
    from mcp_framework import MCPServer
    
    server = MCPServer()
    server.register_tool("my_tool", my_tool_function)
    result = server.call_tool("my_tool", {"param": "value"})
"""

from typing import Dict, Any, Callable
import json


class MCPServer:
    """
    MCP Server - Provides a framework for registering and calling tools.
    
    Tools are functions that take two arguments:
    1. args: Dict[str, Any] - Arguments passed by the caller
    2. context: Dict[str, Any] - Shared context across tool calls
    
    Tools should return a string result.
    """
    
    def __init__(self):
        """Initialize the MCP server."""
        self.tools: Dict[str, Callable] = {}
        self.context: Dict[str, Any] = {}
    
    def register_tool(self, name: str, tool_func: Callable):
        """
        Register a tool function.
        
        Args:
            name: Unique name for the tool
            tool_func: Function that implements the tool
                      Signature: func(args: Dict[str, Any], context: Dict[str, Any]) -> str
        """
        if not callable(tool_func):
            raise ValueError(f"Tool '{name}' must be a callable function")
        
        self.tools[name] = tool_func
        print(f"✓ Registered tool: {name}")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a registered tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments to pass to the tool
        
        Returns:
            Dictionary with 'result' key on success, or 'error' key on failure
        """
        if arguments is None:
            arguments = {}
        
        if tool_name not in self.tools:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": sorted(list(self.tools.keys()))
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(arguments, self.context)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def list_tools(self) -> list:
        """List all registered tool names."""
        return sorted(list(self.tools.keys()))
    
    def set_context(self, key: str, value: Any):
        """Store data in the server context (persists across tool calls)."""
        self.context[key] = value
    
    def get_context(self, key: str, default=None) -> Any:
        """Retrieve data from the server context."""
        return self.context.get(key, default)
    
    def clear_context(self):
        """Clear all context data."""
        self.context.clear()

