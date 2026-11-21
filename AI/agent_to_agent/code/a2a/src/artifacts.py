import uuid
import base64

# message Part {
#   oneof content {
#     string text = 1;
#     bytes raw = 2;
#     string url = 3;
#     google.protobuf.Value data = 4;
#   }
#   google.protobuf.Struct metadata = 5;
#   string filename = 6;
#   string media_type = 7;
# }

# TextPart   kind: "text"    글자
# FilePart   kind: "file"    파일
# DataPart   kind: "data"    구조화된 값

class InvalidArtifact(Exception):
    pass

def make(name: str, parts: list[dict], description: str = "") -> dict:
    if not parts:
        raise InvalidArtifact(f"{name}: parts가 비었습니다. 최소 1개가 있어야 합니다")
    for i, part in enumerate(parts):
        filled = [k for k in ("text", "raw", "url", "data") if k in part]
        if len(filled) == 0:
            raise InvalidArtifact(f"{name}: parts[{i}]에 내용이 없습니다")
        if len(filled) > 1:
            raise InvalidArtifact(f"{name}: parts[{i}]에 {filled}가 함께 있습니다. 내용 필드는 1개만 채웁니다")

    artifact = {"artifactId": str(uuid.uuid4()), "name": name, "parts": parts}
    if description:
        artifact["description"] = description
    return artifact

def text_part(text: str) -> dict:
    return {"text": text, "mediaType": "text/plain"}

def data_part(value) -> dict:
    return {"data": value, "mediaType": "application/json"}

def summary_and_detail(result: dict, verdict: str = "") -> list[dict]:
    line = (f"출장 {result['trip_id']} 원화 합계 {result['total']}원, "
            f"규정 위반 {len(result['violations'])}건")
    if verdict:
        line += f", {verdict}"
    return [
        make("정산 요약", [text_part(line)], "사람이 읽는 한 줄"),
        make("정산 내역", [data_part(result)], "기계가 읽는 값"),
    ]

def raw_part(data: bytes, filename: str, media_type: str) -> dict:
    return {"raw": base64.b64encode(data).decode(),
            "filename": filename, "mediaType": media_type}

def url_part(url: str, filename: str, media_type: str) -> dict:
    return {"url": url, "filename": filename, "mediaType": media_type}