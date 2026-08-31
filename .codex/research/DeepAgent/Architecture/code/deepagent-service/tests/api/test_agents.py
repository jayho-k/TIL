def test_agent_endpoint_uses_registered_runner(client):
    response = client.post(
        "/v1/agents/general/runs",
        json={"message": "hello", "thread_id": "thread-1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "agent": "general",
        "thread_id": "thread-1",
        "output": "reply:thread-1:hello",
    }


def test_agent_endpoint_returns_not_found_for_unknown_agent(client):
    response = client.post(
        "/v1/agents/missing/runs",
        json={"message": "hello", "thread_id": "thread-1"},
    )

    assert response.status_code == 404

