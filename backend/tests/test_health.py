def test_health_returns_ok_without_external_services(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert set(body["services"]) == {"supabase", "twilio", "m3_api"}
    assert body["services"]["twilio"] == "not_configured"


def test_openapi_lists_v1_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert "/v1/chat" in paths
    assert "/v1/schemes/{scheme_id}" in paths
