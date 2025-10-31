# Toy MCP Example

This is a simple, educational example of the **Model Context Protocol (MCP)**. MCP is a protocol that allows AI models to interact with external tools and resources.

## What is MCP?

**Model Context Protocol (MCP)** enables AI models to:
- **Call tools**: Execute functions to perform actions (like calculations, API calls, etc.)
- **Access resources**: Retrieve data or information when needed
- **Maintain context**: Remember information across interactions

Think of it like giving an AI assistant the ability to:
- Use a calculator (tool)
- Check the weather (tool)
- Remember your name (context/memory)

## Files in this Example

1. **`mcp_server.py`**: The MCP server that provides tools
   - Defines tools (calculator, memory, weather)
   - Handles tool execution
   - Manages context/session data

2. **`mcp_client.py`**: A client that simulates how an AI would use the server
   - Interprets user requests
   - Calls appropriate tools
   - Returns results to the user

## How to Run

### Run the Server Example

```bash
python mcp_server.py
```

This will demonstrate:
- Tool registration
- Tool execution
- Context management
- Error handling

### Run the Client Example

```bash
python mcp_client.py
```

This simulates a conversation where:
- User asks questions
- AI decides which tools to use
- Tools execute and return results
- AI responds to the user

## Key Concepts Explained

### 1. Tools
Tools are functions that the AI can call. Each tool:
- Takes arguments (input)
- Performs an action
- Returns a result (output)

**Example**: The `calculator` tool takes two numbers and an operation, then returns the result.

### 2. Server
The MCP server:
- Registers available tools
- Executes tools when requested
- Maintains context (like session memory)

### 3. Client (AI Model)
The client (AI model):
- Receives user requests
- Decides which tools to use
- Calls tools via the server
- Returns results to the user

### 4. Context
Context is information stored by the server that persists across tool calls. For example:
- User preferences
- Session data
- Previous conversation history

## Example Flow

```
1. User: "What is 10 + 5?"
   ↓
2. AI (Client): Recognizes this needs calculation
   ↓
3. AI calls: calculator_tool({"operation": "add", "a": 10, "b": 5})
   ↓
4. Server: Executes the tool
   ↓
5. Server returns: {"result": "10 add 5 = 15"}
   ↓
6. AI: "The answer is 15"
```

## Real-World Applications

In real MCP implementations:
- **Server**: Could be a web server, database, or any external system
- **Client**: An AI assistant (like Claude, ChatGPT, etc.)
- **Tools**: Real APIs, databases, file systems, etc.

## Why MCP Matters

MCP allows AI models to:
- Go beyond their training data
- Access real-time information
- Perform actions in the real world
- Remember context across conversations

## Next Steps

To understand MCP better:
1. Read through `mcp_server.py` to see how tools are defined
2. Run `mcp_client.py` to see the interaction flow
3. Try modifying the tools to add your own functionality
4. Experiment with adding more complex tools (e.g., database queries, API calls)



