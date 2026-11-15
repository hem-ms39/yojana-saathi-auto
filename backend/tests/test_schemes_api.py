def test_unknown_scheme_returns_404(client):
    res = client.get("/v1/schemes/does-not-exist")
    assert res.status_code == 404


def test_seed_scheme_served_without_database(client):
    """With Supabase unconfigured the service must fall back to the seed JSON."""
    res = client.get("/v1/schemes/pm-mudra-shishu")
    assert res.status_code == 200
    body = res.json()
    assert "MUDRA" in body["title"]
    assert body["language"] == "en"


def test_localized_title_hindi(client):
    body = client.get("/v1/schemes/pm-mudra-shishu", params={"language": "hi"}).json()
    assert body["title"] != "" and body["language"] == "hi"
