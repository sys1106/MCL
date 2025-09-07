import json
import sys

# 递归打印树状结构
def print_tree(node, depth=0, relation_dict = {}, alert_data={}):
    indent = "    " * depth
    print(f"{indent}", end="")
    print(f"{depth}───", end="")

    if node in alert_data:
        alert_text = json.dumps(alert_data[node])
        print(f"{node}     {alert_text}")
    else:
        print(f"{node}")
    if node in relation_dict:
       for child in relation_dict[node]:
            print_tree(child, depth + 1, relation_dict, alert_data)


if __name__ == "__main__":
    # 从文件中读取 JSON 数据
    with open('topology_input.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    with open('alert_output.json', 'r', encoding='utf-8') as file:
        alert_data = json.load(file)

    # 构建关系字典
    relation_dict = {}
    for relation in data["childRelations"]:

        p = relation['parentService']
        c = relation['service']
        parent_node = f'{p}_"{relation['parentEndpoint']}"'
        child_node = f'{c}_"{relation['endpoint']}"'
    
        if parent_node not in relation_dict:
            relation_dict[parent_node] = []
    
        relation_dict[parent_node].append(child_node)
    # 找到根节点并打印所有树
    with open('topology.txt', 'w', encoding='utf-8') as file:
        sys.stdout = file
        root_nodes = set(relation_dict.keys()) - {child for children in relation_dict.values() for child in children}
        for root in root_nodes:
            print_tree(root, 0, relation_dict, alert_data)