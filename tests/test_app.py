"""Uji integrasi route Flask untuk AegisBot menggunakan test client."""
import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    return app.test_client()


def test_halaman_utama_menampilkan_tema(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "Asisten Keamanan Siber &amp; Privasi" in res.get_data(as_text=True)


def test_halaman_chat(client):
    res = client.get("/chat/aegis")
    assert res.status_code == 200
    assert "AegisBot" in res.get_data(as_text=True)


def test_tema_tidak_ada_404(client):
    assert client.get("/chat/tidak-ada").status_code == 404
    assert client.get("/api/history/tidak-ada").status_code == 404


def test_api_themes(client):
    data = client.get("/api/themes").get_json()
    assert len(data) == 1
    assert data[0]["id"] == "aegis"


def test_api_chat_berhasil(client):
    res = client.post("/api/chat", json={"message": "cara bikin password kuat", "theme": "aegis"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "password_2fa"
    assert data["reply"]


@pytest.mark.parametrize("payload", [
    {"message": "", "theme": "aegis"},
    {"message": "halo", "theme": "salah"},
    {"message": "a" * 501, "theme": "aegis"},
    {},
])
def test_api_chat_input_tidak_valid(client, payload):
    assert client.post("/api/chat", json=payload).status_code == 400


def test_riwayat_tersimpan_dan_bisa_dihapus(client):
    client.post("/api/chat", json={"message": "halo", "theme": "aegis"})
    riwayat = client.get("/api/history/aegis").get_json()
    assert [r["sender"] for r in riwayat] == ["user", "bot"]

    client.delete("/api/history/aegis")
    assert client.get("/api/history/aegis").get_json() == []


def test_statistik_intent(client):
    client.post("/api/chat", json={"message": "halo", "theme": "aegis"})
    stats = client.get("/api/stats/aegis").get_json()
    assert stats[0]["intent"] == "salam"


def test_api_explain(client):
    data = client.post("/api/explain", json={"message": "cara bikin pw kuat", "theme": "aegis"}).get_json()
    assert data["threshold"] == 0.45
    assert data["candidates"][0]["intent"] == "password_2fa"


def test_halaman_admin_menampilkan_pertanyaan_tak_dikenali(client):
    client.post("/api/chat", json={"message": "harga bensin berapa", "theme": "aegis"})
    html = client.get("/admin/aegis").get_data(as_text=True)
    assert "harga bensin berapa" in html
    assert "tidak dikenali" in html


def test_api_analytics(client):
    client.post("/api/chat", json={"message": "halo", "theme": "aegis"})
    res = client.get("/api/analytics/aegis")
    assert res.status_code == 200
    data = res.get_json()
    assert "summary" in data
    assert "stats" in data
    assert "unknown" in data
    assert data["summary"]["total"] >= 1


def test_admin_key_melindungi_halaman_admin(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "t.db"), "ADMIN_KEY": "rahasia"})
    c = app.test_client()
    assert c.get("/admin/aegis").status_code == 403
    assert c.get("/api/stats/aegis").status_code == 403
    assert c.get("/admin/aegis?key=rahasia").status_code == 200


def test_api_daily_suggestions_berubah_tiap_hari(client):
    r1 = client.get("/api/suggestions/aegis?date=2026-11-19")
    r2 = client.get("/api/suggestions/aegis?date=2026-11-19")
    r3 = client.get("/api/suggestions/aegis?date=2026-11-20")
    assert r1.status_code == 200
    assert r3.status_code == 200
    d1 = r1.get_json()["suggestions"]
    d2 = r2.get_json()["suggestions"]
    d3 = r3.get_json()["suggestions"]
    assert len(d1) == 4
    assert d1 == d2
    assert [s["prompt"] for s in d1] != [s["prompt"] for s in d3]
    assert client.get("/api/suggestions/aegis?date=invalid").status_code == 400
