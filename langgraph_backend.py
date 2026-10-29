from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()

llm = ChatOpenAI(model = 'gpt-4o-mini')

def chat_node(state: ChatState):

    messages = state['messages']

    response = llm.invoke(messages)

    return {'messages':[response]}

checkpointer = MemorySaver()

graph = StateGraph(ChatState)

graph.add_node('chat_node',chat_node)

graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

chatbot = graph.compile(checkpointer = checkpointer)

##streaming
##for message_chunk, metadata in chatbot.stream({'messages':[HumanMessage(content=user_message)]}, config = config, stream_mode='messages'):
##        if message_chunk.content:
##            print(message_chunk.content, end = " ", flush=True)