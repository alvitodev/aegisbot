"""Uji unit untuk mesin chatbot AegisBot (tanpa Flask)."""
from pathlib import Path

import pytest

from chatbot.engine import ChatbotEngine, load_themes, preprocess, similarity

THEMES = load_themes(Path(__file__).resolve().parent.parent / "themes")


def test_preprocess_normalisasi_dan_stopword():
    assert preprocess("Gimana cara bikin pw yang aman?") == ["bagaimana", "cara", "bikin", "password", "aman"]


def test_similarity_kalimat_sama_bernilai_satu():
    t = ["password", "kuat"]
    assert similarity(t, t) == 1.0


def test_similarity_kalimat_berbeda_rendah():
    assert similarity(["ransomware"], ["wifi", "publik"]) < 0.3


def test_tema_aegis_termuat():
    assert set(THEMES) == {"aegis"}


@pytest.mark.parametrize("pesan, intent", [
    ("halo selamat siang kak", "salam"),
    ("makasih banyak atas bantuannya min", "terima_kasih"),
    ("dadah sampai jumpa lagi", "perpisahan"),
    ("kamu ini bot apa sebenarnya", "identitas"),
    ("jam berapa sekarang ya", "waktu"),
    ("gimana bikin pw yang kuat dan aman", "password_2fa"),
    ("cara tahu apakah email saya kena bocor", "kebocoran_data"),
    ("ciri link pising yang menipu", "phishing_apk"),
    ("bahaya gak konek wifi kafe gratis", "keamanan_wifi"),
    ("hp kena virus iklan pop up terus", "malware_ransomware"),
    ("akun instagram kebobol orang lain", "pemulihan_akun"),
    ("gimana aturan backup 3 2 1", "backup_enkripsi"),
])
def test_klasifikasi_intent_aegis(pesan, intent):
    engine = ChatbotEngine(THEMES["aegis"])
    tag, _ = engine.classify(pesan)
    assert tag == intent


def test_salah_ketik_masih_dikenali():
    engine = ChatbotEngine(THEMES["aegis"])
    tag, _ = engine.classify("cara bikin pasword kuat")
    assert tag == "password_2fa"


def test_pertanyaan_di_luar_tema_memberi_fallback():
    engine = ChatbotEngine(THEMES["aegis"])
    hasil = engine.reply("siapa pemenang piala dunia")
    assert hasil["intent"] is None
    assert hasil["reply"] in THEMES["aegis"]["fallback"]


def test_placeholder_nama_bot_diganti():
    engine = ChatbotEngine(THEMES["aegis"])
    hasil = engine.reply("kamu siapa")
    assert "{nama_bot}" not in hasil["reply"]
    assert "AegisBot" in hasil["reply"]


def test_explain_mengurutkan_kandidat_dari_skor_tertinggi():
    engine = ChatbotEngine(THEMES["aegis"])
    kandidat = engine.explain("gimana cara bikin pw kuat")
    assert kandidat[0]["intent"] == "password_2fa"
    assert kandidat[0]["pattern"] == "cara bikin password kuat"
    skor = [k["score"] for k in kandidat]
    assert skor == sorted(skor, reverse=True)


def test_validate_theme_menemukan_kesalahan():
    from chatbot.engine import validate_theme
    rusak = {"id": "x", "name": "X", "bot_name": "B", "avatar": "*", "color": "#000",
             "description": "d", "greeting": "g", "suggestions": [], "fallback": ["f"],
             "intents": [{"tag": "a", "patterns": ["halo"], "responses": ["hai"]},
                         {"tag": "b", "patterns": ["halo"], "responses": []}]}
    masalah = validate_theme(rusak)
    assert any("responses kosong" in m for m in masalah)
    assert any("'a' dan 'b'" in m for m in masalah)


def test_semua_tema_bawaan_valid():
    from chatbot.engine import validate_theme
    for theme in THEMES.values():
        assert validate_theme(theme) == []


def test_akurasi_data_uji_aegis_minimal_90_persen():
    from evaluate import baca_data, evaluasi
    akurasi, _ = evaluasi(THEMES["aegis"], baca_data("aegis"), 0.45)
    assert akurasi >= 0.9
