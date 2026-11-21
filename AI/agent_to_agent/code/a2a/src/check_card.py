import os
import sys

import httpx

CARD_REQUIRED = [
    "name", "description", "supportedInterfaces", "version",
    "capabilities", "defaultInputModes", "defaultOutputModes", "skills",
]
SKILL_REQUIRED = ["id", "name", "description", "tags"]
INTERFACE_REQUIRED = ["url", "protocolBinding", "protocolVersion"]

url = os.environ["WORKER_URL"] + "/.well-known/agent-card.json"
card = httpx.get(url, timeout=30).json()

problems = []

for field in CARD_REQUIRED:
    if field not in card:
        problems.append(f"카드에 {field} 없음")

for index, interface in enumerate(card.get("supportedInterfaces", [])):
    for field in INTERFACE_REQUIRED:
        if field not in interface:
            problems.append(f"supportedInterfaces[{index}]에 {field} 없음")

ids = []
for index, skill in enumerate(card.get("skills", [])):
    for field in SKILL_REQUIRED:
        if field not in skill or not skill[field]:
            problems.append(f"skills[{index}]에 {field} 없거나 비어 있음")
    ids.append(skill.get("id"))

if len(ids) != len(set(ids)):
    problems.append("skills의 id가 겹침")

if problems:
    print("문제 있음:")
    for problem in problems:
        print(" -", problem)
    sys.exit(1)

print("필수 필드 다 있음")
print("skill id:", ids)