import pandas as pd
from openai import OpenAI
import  re
# 初始化 DeepSeek API 客户端
client = OpenAI(api_key="sk-3a14b8f07b8440389eae950259888a3a", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# 读取 Excel 文件
excel_file_path = 'D:/TLP/MCL/data/data.xlsx'  # 替换为你的文件路径
df = pd.read_excel(excel_file_path)

# 假设告警数据在第二列，正确答案在第三列
alarm_data = df.iloc[:, 0].tolist()  # 第二列
correct_answers = df.iloc[:, 1].tolist()  # 第三列

# 背景信息和规则
background_info = """
#背景#
拓扑数据中每个节点后如果有告警事件，会在节点名称后面附带告警事件, 没有告警事件的节点名称后面是空的。
疑似根因是存在告警节点中可能导致问题的节点，没有告警节点不可能是疑似告警节点
每个节点的层次是不会变的
#注意#
告警事件为JSON格式数据，含义如下:
第一层的KEY为告警事件的类型,是数字，1接口层告警,2为容器异常,3为基础设施异常,4为网络程序异常,5为错误异常。
第二层的KEY为该类型告警数据信息，含义如下
- add新增告警事件数
- duplicate重复告警事件数
- resolve已经解决告警事件数
- keep 目前还存留告警事件数
- firstTime该类型告警事件第一次发生时间
- lastTime该类型告警事件最后一次发生时间
- resolveTime解决告警的时间(告警已解决才有)
#处理过程#
请仔细处理数据,如处理每行的节点(节点名称从层数后面的--符号后开始)，记录的节点名称一定要完整。回答记住数据,不用回答其他内容。
"""
#需要限制大模型的输出个数来进行PR@k的计算
rules = """
按照规则一二三四进行判断出疑似根因节点，最后用排序进行对疑似根因节点进行排序,每个疑似根因节点需要同时满足规则一二三四，请不要捏造疑似根因节点，主要观察其中每个存在告警节点中keep(目前还存留告警事件数)
规则一
请从拓扑数据和告警事件数据中观察：
1.请不要把 没有告警节点 和 keep(目前还存留告警事件数)为0 的节点列为疑似根因节点，这样会很浪费时间
2.有告警事件的节点名称，将其标识为疑似根因节点。
规则二
在拓扑图中节点前面数字表示拓扑图中的深度，拓扑图中的深度与文本中节点的先后顺序没有关系，相同数字表示兄弟关系没有上下游关系 
下游节点定义：该节点前面数字到与它相同数字之间大于节点前面数字的节点， 
最下游节点深度定义：疑似根因节点前面数字最大的数字。 如果疑似根因的前面数字与最下游节点深度相同，是疑似根因的优先候选。 
从应用接口层告警出发,沿着业务入口的拓扑结构，从上游向下游每个节点依次追踪（使用拓扑图数据，不要搞错上下游）。 请输出推理过程 
分析下游节点的时候一定要比较与下游节点的数字大小。 
在追踪过程中分析每个节点：  
如果存在接口层告警，继续向该节点前面数字到与它相同数字之间大于节点前面数字的节点追踪， 
如果没有接口层告警，停止追踪，返回上一级节点，当前节点排除。 
 该节点满足在以下情况之一作为疑似根因节点： 
 1. 存在其它类型的告警 
 2. 该节点前面数字到与它相同数字之间大于节点前面数字的节点没有跟该节点相同类型的告警 
 3. 如果节点是存在告警节点中深度最深（节点前面数字最大）的节点 
 4. 在追踪过程中，对于每个有1或者5类型类型接口告警的节点：{  
 检查是否存在出了1或者5类型类型的其他类型的告警，如果存在，则该节点是疑似根因，记录并继续分析下游节点追踪。  
 如果不存在1或者5类型类型的其他告警，同时该节点前面数字到与它相同数字之间大于节点前面数字的节点告警没有1或者5类型类型接口告警，则该节点是疑似根因节点。}
规则三
根因节点需要满足异常从该节点开始向上游传递递，同时该类型异常告警事件是持续发生的，而不是偶发的。
如果接口层类型的告警既有新增又有解决，且该已解决告警事件时间和告警事件第一次发生时间接近，该节点可认为是偶发。
但是接口层类型告警存在存留告警，该节点应做为疑似根因节点。
节点的异常告警是偶发，那么它不应该被认定为根因节点
规则四
如果某个节点发生异常，但是上游节点未发生接口异常告警，可以将这个节点及其分支全部排除。
#排序#
输出的时候按照符合程度排序
和所有满足规则一二三四的疑似节点前面数字进行比较之后优先输入节点前面数字大的
例如：
在这些疑似根因中
x───a
y───b
如果y>x
最终符合规则的节点列表：
y───b
x───a
"""
output_style = """
#输出#
最终符合规则的节点列表：
1 x——xxx
2 x——xx
根据疑似根因的数量继续填写
#注意#
输出时候的列表需要进行排序，这里的12就是根据规则中的排序之后的排名，疑似根因节点最后需要跟给的数据进行比较，若是存在不合理的疑似根因节点请删除，每个疑似根因节点都需要满足规则一二三四
"""

results = []
res ,ans , l = 0 ,0 ,0
sj = []
t_1 ,t_3 ,t_5 = 0 ,0 ,0
for alarm, correct_answer in zip(alarm_data, correct_answers):
    correct_count = 0
    total_count = 20  # 每个告警测试20次
    user_label = []

    for _ in range(total_count):
        l += 1
        # 发送请求
        response = client.chat.completions.create(
            model="qwen2.5-72b-instruct",
            messages=[
                {"role": "system", "content": "你是一个有用的助手"},
                {"role": "user", "content": f"{background_info} {rules} {alarm}输出格式要求：{output_style}"}
            ],
            stream=False
        )

        # 获取模型的响应
        model_response = response.choices[0].message.content.strip()
        lines = model_response.strip().split('\n')
        print(lines)
        start_extracting = False
        final_nodes = []
        for i,line in  enumerate(lines):
            if "最终符合规则的节点列表" in line:
                # start_index = i
                start_extracting = True
                continue
            if start_extracting:
                stripped = line.strip()
                if not stripped:
                    continue
                if not stripped[0].isdigit():
                    break
                final_nodes.append(stripped)
        print(final_nodes)
        # 计算MRR
        for i,s in enumerate(final_nodes,1):
            if correct_answer in s:
                ans += 1
                res += 1/i
                results.append(i)
                print(i)
                break
        def top_k(k:int):
            t = 0
            for i,s in enumerate(final_nodes[:k]):
                if correct_answer in s:
                    t += 1
                    break
            return t

        t_1 += top_k(1)
        t_3 += top_k(3)
        t_5 += top_k(5)
# 输出结果
accuracy = ans / l
print(l)
print(f"告警: {alarm}, 正确率: {accuracy:.2%}")
print(f'top-1:{t_1/l}')
print(f'top-3:{t_3/l}')
print(f'top-5:{t_5/l}')
print(f'MRR:{res/l}')
print(results)
