import json

import artifacts as A

# 영수증 이미지라고 치자. 실제로는 파일을 읽어 온다.
png = bytes([0x89, 0x50, 0x4E, 0x47]) + b"\x00" * 2000

direct = A.make("영수증 원본", [A.raw_part(png, "receipt-03.png", "image/png")])
linked = A.make("영수증 원본", [A.url_part(
    "https://files.example.com/receipt-03.png", "receipt-03.png", "image/png")])

print("raw  ·", len(json.dumps(direct)), "바이트")
print("     ·", json.dumps(direct, ensure_ascii=False)[:120], "...")
print()
print("url  ·", len(json.dumps(linked)), "바이트")
print("     ·", json.dumps(linked, ensure_ascii=False))
print()
print("원본 크기:", len(png), "바이트 · base64로:", len(direct["parts"][0]["raw"]), "바이트")