import json

stats = {}

# 遍历事件数组
def summary_event(json_data):
  for event in json_data:
    service_name = event["serviceName"]
    endpoint = event["endpoint"]
    anormal_status = event["anormalStatus"]
    anormal_type = event["anormalType"]
    time = event["timestamp"]
    p = service_name + '_"' + endpoint + '"' 
    # 初始化服务名字典
    if p not in stats:
        stats[p] = {}
    
    
    if anormal_type not in stats[p]:
        stats[p][anormal_type] = {
            "add": 0,
            "duplicate": 0,
            "resolve": 0,
            "keep": 0,
            "lastTime": time,
            "firstTime": time
        }

    if time < stats[p][anormal_type]["firstTime"]:
        stats[p][anormal_type]["firstTime"] = time
    
    if time > stats[p][anormal_type]["lastTime"]:
        stats[p][anormal_type]["lastTime"] = time

    match anormal_status:
        case "startFiring":
            stats[p][anormal_type]["add"] += 1
        case "resolved":
            stats[p][anormal_type]["resolve"] += 1
            if "resolveTime" not in stats[p][anormal_type]:
                stats[p][anormal_type]["resolveTime"] = time
        case "updatedFiring":
            stats[p][anormal_type]["duplicate"] += 1


def summary_keep_event(json_data):
    for event in json_data:
        service_name = event["serviceName"]
        anormal_type = event["anormalType"]
        endpoint = event["endpoint"]
        p = service_name + '_"' + endpoint + '"'
        stats[p][anormal_type]["keep"] += 1


if __name__ == '__main__':
  with open('alert_input.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
  
  json_data = data["deltaAnormalEvents"]
  summary_event(json_data)
  json_data = data["finalAnormalEvents"]
  summary_keep_event(json_data)
  print(stats)
  text = json.dumps(stats, indent=4)
  with open("alert_output.json", "w", encoding='utf-8') as file:
        file.write(text)