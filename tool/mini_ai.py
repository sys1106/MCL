import re
from langchain_core.messages import HumanMessage, AIMessage, trim_messages,BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langchain_community.chat_models import ChatZhipuAI
from typing import Sequence
from typing_extensions import Annotated, TypedDict
import uuid
import prompt

API_KEY = "e6daccb11b9710693f7f913b86c12409.KOXbTRTNq2Qzyli4"
MODEL = "glm-4-plus"
stream = False

chat = ChatZhipuAI(
    api_key=API_KEY,
    model=MODEL,
    temperature=0.5,
)

CONTEXT_LEN = 100000

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

trimmer = trim_messages(
    max_tokens=CONTEXT_LEN,
    strategy="last",
    token_counter=chat,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

def extract_english_part(text):
    # 定义正则表达式模式
    pattern = r'\s+(.+?)\s+是最可能'
    
    # 使用search方法查找匹配
    match = re.search(pattern, text)
    
    if match:
        # 如果找到匹配，则返回第一个捕获组的内容
        return match.group(1).strip()
    else:
        # 如果没有找到匹配，则返回None或自定义消息
        return None  # 或者返回 "未找到匹配项" 等提示信息

resnode: str = ""

def call_model(state: State):
    chain = prompt.prompt | chat
    trimmed_messages = trimmer.invoke(state["messages"])
    response = chain.invoke(
        {"messages": trimmed_messages}
    )
    resnode = extract_english_part(response.content)
    print(resnode)
    return {"messages": [response]}

workflow = StateGraph(state_schema=State)
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)
memory = MemorySaver()
graphapp = workflow.compile(checkpointer=memory)



def chat_response(input):
  for chunk, metadata in graphapp.stream(
        {"messages": input},
        config,
        stream_mode="messages",
  ):
    if isinstance(chunk, AIMessage):  # Filter to just model responses
      print(chunk.content, end="")

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

format = '''"{text}"'''

if __name__ == "__main__":
  # 1.拓扑图数据
  with open('topology.out', 'r') as file:
    topology_data = file.read()
  input_messages = [HumanMessage(prompt.topology+format.format(text=topology_data))]
  chat_response(input_messages)
  # 2.告警数据
  with open('alert_output.json', 'r') as file:
    alert_data = file.read()
  input_messages = [HumanMessage(prompt.alert+format.format(text=alert_data))]
  chat_response(input_messages)
  # 3.规则定义
  input_messages = [HumanMessage(prompt.rule)]
  chat_response(input_messages)
  # 4.验证数据
  input_messages = [HumanMessage(prompt.verify)]
  chat_response(input_messages)

  print(resnode)
  
  # 清除上下文
  graphapp.checkpointer = MemorySaver()
