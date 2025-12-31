def test_health_no_auth(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}

def test_problems_returns_single_object(client, auth_header):
    resp = client.get("/game/problems", headers=auth_header)   
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)

def test_problems_valid_difficulty(client, auth_header):
    resp = client.get("/game/problems?difficulty=easy", headers=auth_header)
    assert resp.status_code in (200, 404)  # 404 if no easy problems left
    if resp.status_code == 200:
        assert isinstance(resp.json(), dict)

def test_problems_invalid_difficulty(client, auth_header):
    resp = client.get("/game/problems?difficulty=banana", headers=auth_header)
    assert resp.status_code == 422