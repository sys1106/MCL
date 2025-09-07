from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import yaml

with open("./prompt.yaml", "r", encoding="utf-8") as file:
    data = yaml.safe_load(file)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            data["system"],
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

topology = data["topology"]

alert = data["alert"]

rule = data["rule"]

verify = data["verify"]