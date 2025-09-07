# 数据处理流程

## 1.data.py

data.py 负责获取源拓扑和告警数据，并存放在 alert_input.json 和 topology_input.json 文件

每次需要获取新数据，需要调整data.py中的请求参数

```shell
python data.py
```

## 2.alert.py

统计告警事件,按照异常类型统计
生成告警统计结果，执行
数据保存在 alert_output.json 文件中

```shell
python alert.py
```

## 3.topology.py

topology_input.json 和 alert_output.json 中输入拓扑图数据和告警事件事件数据 （JSON格式）
生成拓扑图执行

```shell
python topology.py
```

拓扑图和告警汇总数据结果会打印到标准输出和topology.txt中

最终和大模型对话也是该文件的内容

## 文档

chat.md 中为聊天机器人的交互流程
issues.md 记录存在的问题
