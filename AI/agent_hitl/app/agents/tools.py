from pathlib import Path
from typing import Any

from langchain.tools import ToolRuntime, tool

from app.domain.models import FinalTranslation
from app.storage.files import LocalRunFileStore, parse_txt, render_txt


class ReviewRequiredError(RuntimeError):
    pass


def create_replace_tool(file_store: LocalRunFileStore):
    @tool
    def replace_file(runtime: ToolRuntime) -> str:
        """사람이 검수한 최종 번역으로 입력 TXT를 교체하여 결과 파일을 만든다."""
        state: dict[str, Any] = runtime.state
        if state.get("review_status") != "completed":
            raise ReviewRequiredError("사람의 번역 검수가 완료되지 않았습니다.")
        raw = state.get("final_translations")
        if not raw:
            raise ReviewRequiredError("검수된 최종 번역이 없습니다.")
        run_id = state.get("run_id")
        if not run_id:
            raise ReviewRequiredError("run_id가 Agent 상태에 없습니다.")

        input_path = file_store.root / run_id / "input.txt"
        parsed = parse_txt(Path(input_path).read_bytes())
        final = [FinalTranslation.model_validate(item) for item in raw]
        by_id = {item.segment_id: item.translated_text for item in final}
        translations = [by_id[item.segment_id] for item in parsed.segments]
        output = file_store.write_output(run_id, render_txt(parsed, translations))
        return str(output)

    return replace_file
