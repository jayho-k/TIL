import os

import streamlit as st

from streamlit_app.client import AgentApiClient

st.set_page_config(page_title="DeepAgent 번역 검수", layout="wide")
st.title("DeepAgent File Translation HITL PoC")
client = AgentApiClient(os.getenv("AGENT_API_URL", "http://localhost:8000"))

for key, default in {
    "run_id": None,
    "status": None,
    "review_request": None,
    "download_url": None,
    "events": [],
}.items():
    st.session_state.setdefault(key, default)


def consume(events):
    for event, payload in events:
        st.session_state.events.append((event, payload))
        st.session_state.run_id = payload.get("run_id", st.session_state.run_id)
        if event == "hitl.required":
            st.session_state.status = "WAITING_FOR_REVIEW"
            st.session_state.review_request = payload["review_request"]
        elif event == "completed":
            st.session_state.status = "COMPLETED"
            st.session_state.download_url = payload["download_url"]
        elif event == "failed":
            st.session_state.status = "FAILED"
            st.error(payload.get("message", "Agent 실행에 실패했습니다."))


uploaded = st.file_uploader("UTF-8 TXT 파일", type=["txt"])
if uploaded and st.button("번역 시작", type="primary"):
    st.session_state.review_request = None
    st.session_state.download_url = None
    with st.status("Agent를 실행하고 있습니다.", expanded=True):
        consume(client.start(uploaded.name, uploaded.getvalue()))

review = st.session_state.review_request
if review and st.session_state.status == "WAITING_FOR_REVIEW":
    st.subheader("번역 결과 검수")
    decisions = []
    valid = True
    for segment in review["segments"]:
        segment_id = segment["segment_id"]
        st.markdown(f"#### {segment_id}")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("원문 / 1차 번역")
            st.write(segment["original_text"])
            st.info(segment["first_translation"])
        with col2:
            st.caption("검증 번역")
            st.success(segment["validated_translation"])
            st.caption(segment["validation_note"])
        selected = st.radio(
            "최종 선택",
            ["first", "validated", "custom"],
            key=f"choice:{segment_id}",
            horizontal=True,
        )
        custom_text = None
        if selected == "custom":
            custom_text = st.text_area("직접 수정", key=f"custom:{segment_id}")
            valid = valid and bool(custom_text.strip())
        decisions.append(
            {"segment_id": segment_id, "selected": selected, "custom_text": custom_text}
        )

    if st.button("검수 완료 및 재개", type="primary", disabled=not valid):
        payload = {
            "review_request_id": review["review_request_id"],
            "revision": review["revision"],
            "decisions": decisions,
        }
        with st.status("검수 결과를 적용하고 있습니다.", expanded=True):
            consume(client.resume(st.session_state.run_id, payload))
        st.rerun()

if st.session_state.status == "COMPLETED" and st.session_state.run_id:
    st.success("번역 파일이 완성되었습니다.")
    content = client.download(st.session_state.run_id)
    st.download_button(
        "결과 TXT 다운로드",
        data=content,
        file_name=f"{st.session_state.run_id}-translated.txt",
        mime="text/plain",
    )

with st.expander("수신 이벤트"):
    st.json(st.session_state.events)
