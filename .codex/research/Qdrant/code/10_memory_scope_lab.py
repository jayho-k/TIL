from qdrant_client import QdrantClient, models


COLLECTION = "agent_memory_lab"
client = QdrantClient(url="http://localhost:6333")

client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE),
)

for field in ("tenant_id", "agent_id", "memory_scope", "status"):
    client.create_payload_index(
        collection_name=COLLECTION,
        field_name=field,
        field_schema=models.PayloadSchemaType.KEYWORD,
    )

client.upsert(
    collection_name=COLLECTION,
    points=[
        models.PointStruct(
            id="00000000-0000-0000-0000-000000000001",
            vector=[0.9, 0.1, 0.0],
            payload={"tenant_id": "tenant-A", "agent_id": "research-agent",
                     "memory_scope": "agent_private", "status": "active",
                     "content": "research-agent private memory"},
        ),
        models.PointStruct(
            id="00000000-0000-0000-0000-000000000002",
            vector=[0.8, 0.2, 0.0],
            payload={"tenant_id": "tenant-A", "agent_id": "research-agent",
                     "memory_scope": "user_shared", "status": "active",
                     "content": "tenant-A shared memory"},
        ),
        models.PointStruct(
            id="00000000-0000-0000-0000-000000000003",
            vector=[1.0, 0.0, 0.0],
            payload={"tenant_id": "tenant-B", "agent_id": "other-agent",
                     "memory_scope": "user_shared", "status": "active",
                     "content": "must never leak to tenant-A"},
        ),
        models.PointStruct(
            id="00000000-0000-0000-0000-000000000004",
            vector=[0.7, 0.3, 0.0],
            payload={"tenant_id": "tenant-A", "agent_id": "research-agent",
                     "memory_scope": "agent_private", "status": "active",
                     "content": "lifecycle test memory"},
        ),
    ],
    wait=True,
)


def search(tenant_id, scope, agent_id=None):
    must = [
        models.FieldCondition(key="tenant_id", match=models.MatchValue(value=tenant_id)),
        models.FieldCondition(key="memory_scope", match=models.MatchValue(value=scope)),
        models.FieldCondition(key="status", match=models.MatchValue(value="active")),
    ]
    if agent_id:
        must.append(models.FieldCondition(key="agent_id", match=models.MatchValue(value=agent_id)))
    return client.query_points(
        collection_name=COLLECTION,
        query=[1.0, 0.0, 0.0],
        query_filter=models.Filter(must=must),
        limit=10,
        with_payload=True,
    ).points


tenant_a_private = search("tenant-A", "agent_private", "research-agent")
assert all(point.payload["tenant_id"] == "tenant-A" for point in tenant_a_private)
assert all(point.id != "00000000-0000-0000-0000-000000000003" for point in tenant_a_private)
print("[PASS] tenant-A search excludes tenant-B point")

agent_b_private = search("tenant-A", "agent_private", "other-agent")
assert not agent_b_private
print("[PASS] agent-A private memory is not returned to agent-B")

shared = search("tenant-A", "user_shared")
assert [point.payload["content"] for point in shared] == ["tenant-A shared memory"]
print("[PASS] user_shared memory is returned inside tenant-A")

client.set_payload(
    collection_name=COLLECTION,
    payload={"status": "superseded"},
    points=["00000000-0000-0000-0000-000000000004"],
    wait=True,
)
assert all(point.id != "00000000-0000-0000-0000-000000000004" for point in search("tenant-A", "agent_private", "research-agent"))
print("[PASS] superseded memory is excluded from active recall")

client.delete(
    collection_name=COLLECTION,
    points_selector=models.PointIdsList(points=["00000000-0000-0000-0000-000000000002"]),
    wait=True,
)
assert not search("tenant-A", "user_shared")
print("[PASS] deleted memory is inaccessible")
