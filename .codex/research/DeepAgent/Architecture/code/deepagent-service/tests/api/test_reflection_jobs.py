def test_airflow_can_create_and_read_reflection_job(client):
    created = client.post("/v1/reflection-jobs", json={"subject": "daily"})

    assert created.status_code == 202
    body = created.json()
    assert body["subject"] == "daily"
    assert body["status"] == "pending"

    fetched = client.get(f"/v1/reflection-jobs/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body

