import os
from uuid import uuid4

import httpx
import streamlit as st

from streamlit_app.client import AgentApiClient

st.set_page_config(page_title="DeepAgent 번역 검수", layout="wide")
st.title("파일 번역 · 대화형 검수")
client = AgentApiClient(os.getenv("AGENT_API_URL", "http://localhost:8000"))
for key, default in {
    "run_id": st.query_params.get("run_id"),
    "status": None,
    "review_request": None,
    "history": [],
    "events": [],
    "pending": None,
    "error": None,
}.items():
    st.session_state.setdefault(key, default)


def refresh():
    record = client.status(st.session_state.run_id)
    for key in ("status", "review_request", "history", "error"):
        st.session_state[key] = record.get(key)
    pending = st.session_state.pending
    review = record.get("review_request")
    if pending and (
        record["status"] == "COMPLETED"
        or (review and review["review_request_id"] != pending["review_request_id"])
    ):
        st.session_state.pending = None


def consume(events):
    for event, payload in events:
        st.session_state.events.append((event, payload))
        st.session_state.run_id = payload.get("run_id", st.session_state.run_id)
        st.query_params["run_id"] = st.session_state.run_id
        if event == "hitl.required":
            st.session_state.status = "WAITING_FOR_REVIEW"
            st.session_state.review_request = payload["review_request"]
            st.session_state.history = payload["review_request"]["history"]
            st.session_state.pending = None
        elif event == "completed":
            st.session_state.status = "COMPLETED"
            st.session_state.pending = None
        elif event == "failed":
            st.session_state.status = payload.get("status", "FAILED")
            st.session_state.error = payload.get("message")
        elif event == "progress":
            st.session_state.status = payload.get("status", "RUNNING")


def send(action, **fields):
    review = st.session_state.review_request
    payload = {
        "command_id": str(uuid4()),
        "review_request_id": review["review_request_id"],
        "revision": review["revision"],
        "snapshot_hash": review["snapshot_hash"],
        "action": action,
        **fields,
    }
    st.session_state.pending = payload
    try:
        with st.spinner("요청을 처리하고 있습니다."):
            consume(client.review_action(st.session_state.run_id, payload))
        refresh()
        st.rerun()
    except httpx.HTTPStatusError as exc:
        st.error(f"요청을 처리할 수 없습니다: {exc.response.text}")
        st.session_state.pending = None
    except httpx.HTTPError:
        st.error("연결이 끊겼습니다. 상태 새로고침 또는 같은 요청 재전송으로 확인하세요.")


with st.sidebar:
    run_id = st.text_input("작업 ID", value=st.session_state.run_id or "")
    if st.button("작업 불러오기 / 상태 새로고침", disabled=not run_id):
        try:
            st.session_state.run_id = run_id
            st.query_params["run_id"] = run_id
            refresh()
            st.rerun()
        except httpx.HTTPError as exc:
            st.error(str(exc))
    if st.session_state.pending and st.button("같은 요청 재전송"):
        try:
            consume(client.review_action(st.session_state.run_id, st.session_state.pending))
            refresh()
            st.rerun()
        except httpx.HTTPError as exc:
            st.error(str(exc))

if st.session_state.run_id and st.session_state.status is None:
    try:
        refresh()
    except httpx.HTTPError as exc:
        st.error(f"작업을 불러오지 못했습니다: {exc}")

uploaded = st.file_uploader("UTF-8 TXT 파일", type=["txt"])
if uploaded and st.button("새 번역 시작", type="primary"):
    st.session_state.review_request = None
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.error = None
    try:
        with st.spinner("초기 번역을 진행합니다."):
            consume(client.start(uploaded.name, uploaded.getvalue()))
        st.rerun()
    except httpx.HTTPError as exc:
        st.error(str(exc))

status = st.session_state.status
if status:
    st.caption(f"작업: {st.session_state.run_id} · 상태: {status}")
if st.session_state.error:
    st.error(st.session_state.error)
if status in {"FAILED", "RECOVERY_REQUIRED"} and st.button("저장된 작업 이어가기"):
    try:
        consume(client.retry(st.session_state.run_id))
        refresh()
        st.rerun()
    except httpx.HTTPError as exc:
        st.error(str(exc))
if status in {"RUNNING", "RESUMING"}:
    st.info("작업이 진행 중입니다. 잠시 후 상태 새로고침으로 결과를 확인하세요.")

for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.write(entry["content"])

review = st.session_state.review_request
if review and status == "WAITING_FOR_REVIEW":
    st.subheader(f"번역 검수 · 버전 {review['revision']}")
    decisions, edits = [], {}
    for segment in review["segments"]:
        sid = segment["segment_id"]
        key = f"{st.session_state.run_id}:{review['revision']}:{sid}"
        st.markdown(f"**{sid}**")
        st.write(segment["original_text"])
        left, right = st.columns(2)
        with left:
            st.caption("현재 번역" if review["revision"] > 1 else "1차 번역")
            st.info(segment["first_translation"])
        with right:
            st.caption("검증 번역")
            st.success(segment["validated_translation"])
            st.caption(segment["validation_note"])
        selected = st.radio(
            "확정할 후보",
            ["first", "validated"],
            format_func=lambda value: "현재 번역" if value == "first" else "검증 번역",
            key=f"{key}:choice",
            horizontal=True,
        )
        decisions.append({"segment_id": sid, "selected": selected})
        text = st.text_area("직접 수정", value=segment["first_translation"], key=f"{key}:edit")
        if text != segment["first_translation"]:
            edits[sid] = text
    if review["revision"] > 1:
        with st.expander("최초 번역 비교"):
            st.json(review.get("initial_translations", {}))
    if st.button(
        "수정 적용 후 재검증", disabled=not edits or any(not t.strip() for t in edits.values())
    ):
        send("edit", edits=edits)
    if edits:
        st.caption("직접 수정한 내용을 먼저 적용하거나 원래 내용으로 되돌린 후 확정하세요.")
    if st.button("현재 버전 최종 확정", type="primary", disabled=bool(edits)):
        send("approve", decisions=decisions)
    message = st.chat_input(
        "번역 이유를 묻거나 수정할 내용과 범위를 알려주세요.", disabled=bool(edits)
    )
    if message:
        send("message", message=message)

if status == "COMPLETED":
    st.success("번역 파일이 완성되었습니다.")
    try:
        st.download_button(
            "결과 TXT 다운로드",
            client.download(st.session_state.run_id),
            file_name="translated.txt",
            mime="text/plain",
        )
    except httpx.HTTPError as exc:
        st.error(str(exc))

with st.expander("수신 이벤트"):
    st.json(st.session_state.events)
