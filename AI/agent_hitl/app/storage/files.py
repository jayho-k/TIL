import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.domain.models import Segment


class InvalidTextEncoding(ValueError):
    pass


@dataclass(frozen=True)
class ParsedText:
    lines: tuple[str, ...]
    had_trailing_newline: bool
    segments: tuple[Segment, ...]
    segment_line_indexes: tuple[int, ...]


def parse_txt(content: bytes) -> ParsedText:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidTextEncoding("UTF-8 TXT만 지원합니다.") from exc
    had_trailing_newline = text.endswith("\n")
    lines = text.splitlines()
    indexes = tuple(index for index, line in enumerate(lines) if line.strip())
    segments = tuple(
        Segment(
            segment_id=f"segment-{order + 1:04d}",
            order=order,
            original_text=lines[line_index],
        )
        for order, line_index in enumerate(indexes)
    )
    return ParsedText(tuple(lines), had_trailing_newline, segments, indexes)


def render_txt(parsed: ParsedText, translations: list[str]) -> str:
    if len(translations) != len(parsed.segments):
        raise ValueError("번역 개수가 segment 개수와 일치하지 않습니다.")
    lines = list(parsed.lines)
    for line_index, translated in zip(parsed.segment_line_indexes, translations, strict=True):
        lines[line_index] = translated
    result = "\n".join(lines)
    return result + ("\n" if parsed.had_trailing_newline else "")


class LocalRunFileStore:
    def __init__(self, root: Path):
        self.root = root

    def save_input(self, run_id: str, content: bytes) -> Path:
        parsed = parse_txt(content)
        path = self._run_dir(run_id) / "input.txt"
        path.write_bytes(content)
        # Decoding is deliberately validated before writing.
        assert parsed is not None
        return path

    def write_output(self, run_id: str, content: str) -> Path:
        directory = self._run_dir(run_id)
        target = directory / "output.txt"
        temporary = directory / "output.txt.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
        return target

    def _run_dir(self, run_id: str) -> Path:
        directory = self.root / run_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def write_approved_output(self, run_id: str, content: str, approval: dict) -> Path:
        from app.domain.revisions import content_hash

        directory = self._run_dir(run_id)
        target = directory / "output.txt"
        manifest_path = directory / "output.manifest.json"
        manifest = {**approval, "output_hash": content_hash(content)}
        if manifest_path.exists():
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if existing != manifest:
                raise ValueError("이미 다른 승인으로 파일이 생성되었습니다.")
            if (
                target.exists()
                and content_hash(target.read_text(encoding="utf-8")) == manifest["output_hash"]
            ):
                return target
        temporary = directory / f"output-{uuid4()}.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)
        metadata = directory / f"manifest-{uuid4()}.tmp"
        metadata.write_text(json.dumps(manifest), encoding="utf-8")
        metadata.replace(manifest_path)
        return target
