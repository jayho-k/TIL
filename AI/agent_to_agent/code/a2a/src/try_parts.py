from google.protobuf import json_format

from a2a import types as t

p = t.Part(text="합계 2483000원")
print("text만:", json_format.MessageToDict(p))
print("어느 게 채워졌나:", p.WhichOneof("content"))

p.data.struct_value.update({"total": 2483000})
print()
print("data를 덮어쓰면:", json_format.MessageToDict(p))
print("어느 게 채워졌나:", p.WhichOneof("content"))

print()
mixed = {"text": "합계", "data": {"total": 1}}
try:
    json_format.ParseDict(mixed, t.Part())
except Exception as e:
    print("2개를 담아 파싱하면:", type(e).__name__)
    print(" ", str(e)[:110])

# {"kind": "text", "text": "..."}
# {"kind": "file", "file": {"bytes": "..."}}
# {"kind": "data", "data": {...}}

# {"text": "...", "mediaType": "text/plain"}
# {"raw": "...", "filename": "receipt.png", "mediaType": "image/png"}
# {"data": {...}, "mediaType": "application/json"}