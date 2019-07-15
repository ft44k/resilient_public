def create_indicator(category_list):

  list_of_items = "<ul>"
  li_list = ""
  for desc in category_list:
    li_list += "<li>{}</li>".format(desc)
  list_of_items += li_list + "</ul>"
  return list_of_items

line_desc = "<div style=\"padding-bottom: 43px\"><div style=\"width:120px;padding:10px;background:#d0d4dc;float:left;color:#666666\">{}</div>"
line_val = "<div style=\"background:#e3e7f0;padding:10px;float:left;width:700px\">{}</div></div>"

line_val_malicious = "<div style=\"background:#e3e7f0;padding:10px;float:left;width:700px;color:red;font-weight:bold\">{}</div></div>"

section_desc = "<p><b style=\"font-size:14px;color:black\">{}</b></p>"

header = "<div style=\"max-width:820px\"><b style=\"font-size:22px;color:black\">ReversingLabs</b><p align=\"right\">Sample Analysis Result</p>"

indicators_div = "<div style=\"display:flex;flex-direction: row;align-items: stretch;\">"

try:
  res = results["result"]

  file_type = res["file_type"] if res["file_type"] else ">&#8212;"
  
  md5 = ">&#8212;"
  sha1 = ">&#8212;"
  sha256 = ">&#8212;"
  imphash = ">&#8212;"
  ssdeep = ">&#8212;"

  for item in res["ticore"]["info"]["file"]["hashes"]: # array of dicts
    if item['name'] == "md5":
      md5 = item['value']
    elif item['name'] == "sha1":
      sha1 = item['value']
    elif item['name'] == "sha256":
      sha256 = item['value']
    elif item['name'] == "imphash":
      imphash = item['value']
    elif item['name'] == "ssdeep":
      ssdeep = item['value']
    else:
      pass


  file_size = int(res["ticore"]["info"]["file"]["size"]) #in bytes
  first_seen_cloud = res["ticloud"]["first_seen"]
  last_seen_cloud = res["ticloud"]["last_seen"]


  threat_status = res["threat_status"]
  threat_name = res["threat_name"] if res["threat_name"] else "&#8212;"

  indicators = res["summary"]["indicators"]  #array of dict

  note = header + section_desc.format("Sample:") + line_desc.format("File Name") +\
  line_val.format(artifact.value) + line_desc.format("Type") + line_val.format(file_type) +\
  line_desc.format("Size") + line_val.format(file_size) +\
  line_desc.format("Format") + line_val.format("&#8212;") +\
  line_desc.format("First Seen") + line_val.format(first_seen_cloud) +\
  line_desc.format("Last Seen") + line_val.format(last_seen_cloud)
  note +="</br>"
  note += section_desc.format("Analysis:") +\
  line_desc.format("Result")

  if threat_status == "malicious":
  	note += line_val_malicious.format("Malicious")
  else:
  	note += line_val.format(threat_status)

  note += line_desc.format("Threat") + line_val.format(threat_name)
  note += line_desc.format("MD5") + line_val.format(md5)
  note += line_desc.format("SHA1") + line_val.format(sha1)
  note += line_desc.format("SHA256") + line_val.format(sha256)
  note += line_desc.format("IMPHASH") + line_val.format(imphash)
  note += line_desc.format("SSDEEP") + line_val.format(ssdeep)

  note +="</br>"

  
  network = []
  evasion = []
  monitor = []
  registry = []
  execution = []
  search = []
  settings = []
  file = []
  steal = []
  permissions = []
  memory = []
  anomaly = []
  signature = []
  unknown = []
  
  if indicators:
    
    note += section_desc.format("Indicators:")
    note += indicators_div
    #every entry contains priority, category, description
    #priority with higher value is more important, RL seems to return it sorted from high to low
    
    for item in indicators:
      if int(item["category"]) == 0:  #network
        network.append(item["description"])
      elif int(item["category"]) == 1: #evasion
        evasion.append(item["description"])
      elif int(item["category"]) == 4: #memory
        memory.append(item["description"])
      elif int(item["category"]) == 6: #anomaly
        anomaly.append(item["description"])
      elif int(item["category"]) == 7: #monitor
        monitor.append(item["description"])
      elif int(item["category"]) == 9: #registry
        registry.append(item["description"])
      elif int(item["category"]) == 10: #execution
        execution.append(item["description"])
      elif int(item["category"]) == 11: #permissions
        permissions.append(item["description"])
      elif int(item["category"]) == 12: #search
        search.append(item["description"])
      elif int(item["category"]) == 13: #settings
        settings.append(item["description"])
      elif int(item["category"]) == 17: #signature
        signature.append(item["description"])
      elif int(item["category"]) ==18: #steal
        steal.append(item["description"])
      elif int(item["category"]) == 22: #file
        file.append(item["description"])
      else:
        unknown.append(item["category"])
    
    if network:
      note += line_desc.format("Network") + line_val.format(create_indicator(network))   
    if evasion:
      note += line_desc.format("Evasion") + line_val.format(create_indicator(evasion))
    if memory:
      note += line_desc.format("Memory") + line_val.format(create_indicator(memory))
    if anomaly:
      note += line_desc.format("Anomaly") + line_val.format(create_indicator(anomaly))
    if monitor:
      note += line_desc.format("Monitor") + line_val.format(create_indicator(monitor))
    if registry:
      note += line_desc.format("Registry") + line_val.format(create_indicator(registry))
    if execution:
      note += line_desc.format("Execution") + line_val.format(create_indicator(execution))
    if permissions:
      note += line_desc.format("Permissions") + line_val.format(create_indicator(permissions))
    if search:
      note += line_desc.format("Search") + line_val.format(create_indicator(search))
    if settings:
      note += line_desc.format("Settings") + line_val.format(create_indicator(settings))
    if signature:
      note += line_desc.format("Signature") + line_val.format(create_indicator(signature))
    if steal:
      note += line_desc.format("Steal") + line_val.format(create_indicator(steal))
    if file:
      note += line_desc.format("File") + line_val.format(create_indicator(file))
    if unknown:
      note += line_desc.format("Unknown") + line_val.format(create_indicator(unknown))
    note += "</div>"
  
  rl_server = "your_ip_or_fqdn"
  link_to_result = "https://{}/{}".format(rl_server,sha1)
  button ="<div style=\"width:120px;margin:auto;padding:8px 32px;background:black;text-align:center\"><a href=\"{}\" style=\"color:white;text-decoration:none\">View Analysis Details</a></div>"


  html = "<html><body>"+note+"</br>"+button.format(link_to_result)+"</body></html>"
  note = helper.createRichText(html)
  incident.addNote(note)

except:

  note = helper.createRichText("<p>Analysis of file: {} failed</p><p>Platform: ReversingLabs</p><p>Please contact the support</p>".format(artifact.value))
  incident.addNote(note)
