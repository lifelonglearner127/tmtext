#!/usr/bin/python

import sys
import json
import csv
import codecs

def encode(text_list):
	return [word.encode("utf-8") for word in text_list]

filename = sys.argv[1]
f = codecs.open(filename,"r","utf-8")

output1 = codecs.open("departments.csv","wb")
output2 = codecs.open("department_members.csv","wb")
output3 = codecs.open("departments_and_members.csv","wb")

group_id = 0

for line in f:
	if (line.strip()):
		group = json.loads(line.strip())
		group_id += 1

		deptwriter = csv.writer(output1, delimiter=',')
		memberswriter = csv.writer(output2, delimiter=',')
		bothwriter = csv.writer(output3, delimiter=',')

		deptwriter.writerow(encode([str(group_id), group["Group_name"], group["Short_name"]]))

		for item in group["Group_members"]:
			memberswriter.writerow(encode([str(group_id), item["site"], item["text"], item["url"]]))
			bothwriter.writerow(encode([str(group_id), group["Group_name"], group["Short_name"], item["site"], item["text"], item["url"]]))

output1.close()
output2.close()
output3.close()
f.close()