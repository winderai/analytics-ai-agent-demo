from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

agent = Agent(
    model=OpenAIModel(model_name="gpt-4o-mini"),
    instructions="You are a helpful assistant. Use tools if needed. Remember the chat history.",
    temperature=0.0,
)

@agent.tool_plain
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

if __name__ == "__main__":
    import asyncio
    result = None
    for user in ["Hi!", "What is 2+2?", "Add 5 to that."]:
        result = asyncio.run(
            agent.run(
                user,
                message_history=result.new_messages() if result else None
            )
        )
        print(f"User: {user}\nAI: {result.output}\n")
