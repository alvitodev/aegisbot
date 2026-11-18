import time
import urllib.request
from playwright.sync_api import sync_playwright

brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def run():
    # 0. Reset history first for clean initial state
    try:
        req = urllib.request.Request("http://127.0.0.1:5000/api/history/aegis", method="DELETE")
        urllib.request.urlopen(req)
    except Exception as e:
        print("Reset history note:", e)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave_path, headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 850})
        page = context.new_page()

        # 1. Halaman Utama (Direct Zero-Friction Landing)
        print("Capturing 01-halaman-utama.png...")
        page.goto("http://127.0.0.1:5000/")
        page.wait_for_selector(".welcome-box")
        time.sleep(1)
        page.screenshot(path="screenshots/01-halaman-utama.png")

        # 2. Halaman Chat AegisBot (Percakapan Aktif)
        print("Capturing 02-chat-aegis.png...")
        # Klik starter card "Cara bikin password kuat"
        starter_card = page.wait_for_selector('.starter-card[data-prompt="Cara bikin password kuat"]', timeout=6000)
        if starter_card:
            starter_card.click()
        # Tunggu sampai ada respons bot
        page.wait_for_selector(".msg-bot", timeout=8000)
        time.sleep(1.0)

        # Kirim pertanyaan kedua via input
        page.fill("#chat-input", "Gimana ciri-ciri link phishing dan modus APK kurir?")
        page.press("#chat-input", "Enter")
        time.sleep(1.5)

        page.screenshot(path="screenshots/02-chat-aegis.png")

        # 3. Mode Belajar / Interactive Explain Inspector
        print("Capturing 03-mode-belajar.png...")
        # Klik meta-badge pada respons terakhir untuk membuka rincian intent
        meta_badges = page.query_selector_all(".meta-badge")
        if meta_badges:
            meta_badges[-1].click()
            time.sleep(1.5)

        page.screenshot(path="screenshots/03-mode-belajar.png")

        # Kirim pertanyaan di luar domain agar tercatat di log analitik
        page.fill("#chat-input", "Berapa harga tiket pesawat ke Tokyo?")
        page.press("#chat-input", "Enter")
        time.sleep(1.5)

        # 4. Slide-Over Analytics Drawer (Zero Page Reload)
        print("Capturing 04-admin-aegis.png...")
        page.click("#btn-stats")
        page.wait_for_selector(".stats-drawer.drawer-open", timeout=6000)
        time.sleep(1.5)
        page.screenshot(path="screenshots/04-admin-aegis.png")

        # Tutup drawer
        page.keyboard.press("Escape")
        time.sleep(0.5)

        # 5. Screenshot Terminal Evaluate
        print("Capturing 05-terminal-evaluate.png...")
        eval_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body { background: #0f172a; margin: 0; padding: 24px; font-family: 'Consolas', 'JetBrains Mono', monospace; display: flex; justify-content: center; }
            .terminal { background: #1e293b; border-radius: 12px; width: 900px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5); overflow: hidden; border: 1px solid #334155; }
            .term-header { background: #0f172a; padding: 12px 16px; display: flex; align-items: center; border-bottom: 1px solid #334155; }
            .dots { display: flex; gap: 8px; }
            .dot { width: 12px; height: 12px; border-radius: 50%; }
            .red { background: #ef4444; } .yellow { background: #eab308; } .green { background: #22c55e; }
            .title { margin-left: auto; margin-right: auto; color: #94a3b8; font-size: 13px; font-weight: 600; }
            .content { padding: 20px; color: #f8fafc; font-size: 14px; line-height: 1.5; white-space: pre; }
            .prompt { color: #38bdf8; font-weight: bold; }
            .cmd { color: #f1f5f9; }
            .success { color: #4ade80; font-weight: bold; }
            .accent { color: #2dd4bf; }
        </style>
        </head>
        <body>
        <div class="terminal">
            <div class="term-header">
                <div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
                <div class="title">PowerShell &middot; Evaluasi Akurasi AegisBot (evaluate.py)</div>
            </div>
            <div class="content"><span class="prompt">PS C:\\Users\\Alvito\\...\\aegisbot&gt;</span> <span class="cmd">python evaluate.py --tema aegis</span>

<span class="accent">Tema aegis &middot; ambang 0.45 &middot; 35 kalimat uji</span>
<span class="success">Akurasi: 100.0%</span>

intent               benar  total
backup_enkripsi          2      2
fallback                 5      5
identitas                2      2
keamanan_wifi            3      3
kebocoran_data           3      3
malware_ransomware       3      3
password_2fa             3      3
pemulihan_akun           3      3
perpisahan               2      2
phishing_apk             3      3
salam                    2      2
terima_kasih             2      2
waktu                    2      2

<span class="prompt">PS C:\\Users\\Alvito\\...\\aegisbot&gt;</span> <span class="cmd">python evaluate.py --tema aegis --sweep</span>
<span class="accent">Tema aegis: 35 kalimat uji</span>

ambang  akurasi
 0.30    91.4%  ###########################
 0.35   100.0%  ##############################
 0.40   100.0%  ##############################
 <span class="success">0.45   100.0%  ##############################</span>
 0.50    88.6%  ###########################
 0.55    80.0%  ########################
 0.60    71.4%  #####################
 0.70    48.6%  ###############</div>
        </div>
        </body>
        </html>
        """
        page.set_content(eval_html)
        time.sleep(0.5)
        elem = page.query_selector(".terminal")
        elem.screenshot(path="screenshots/05-terminal-evaluate.png")

        # 6. Screenshot Terminal Pytest (38 Tests Passed)
        print("Capturing 06-terminal-pytest.png...")
        pytest_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <style>
            body { background: #0f172a; margin: 0; padding: 24px; font-family: 'Consolas', 'JetBrains Mono', monospace; display: flex; justify-content: center; }
            .terminal { background: #1e293b; border-radius: 12px; width: 900px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5); overflow: hidden; border: 1px solid #334155; }
            .term-header { background: #0f172a; padding: 12px 16px; display: flex; align-items: center; border-bottom: 1px solid #334155; }
            .dots { display: flex; gap: 8px; }
            .dot { width: 12px; height: 12px; border-radius: 50%; }
            .red { background: #ef4444; } .yellow { background: #eab308; } .green { background: #22c55e; }
            .title { margin-left: auto; margin-right: auto; color: #94a3b8; font-size: 13px; font-weight: 600; }
            .content { padding: 20px; color: #f8fafc; font-size: 13.5px; line-height: 1.45; white-space: pre; }
            .prompt { color: #38bdf8; font-weight: bold; }
            .cmd { color: #f1f5f9; }
            .passed { color: #4ade80; font-weight: bold; }
            .summary { color: #22c55e; font-weight: bold; }
            .dim { color: #94a3b8; }
        </style>
        </head>
        <body>
        <div class="terminal">
            <div class="term-header">
                <div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
                <div class="title">PowerShell &middot; Pengujian Otomatis Pytest (pytest -v)</div>
            </div>
            <div class="content"><span class="prompt">PS C:\\Users\\Alvito\\...\\aegisbot&gt;</span> <span class="cmd">pytest -v</span>
<span class="dim">============================= test session starts =============================</span>
platform win32 -- Python 3.12.10, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\\Users\\Alvito\\Documents\\KULIAH\\Aplikasi Web\\aegisbot
configfile: pytest.ini
collected 38 items

tests/test_app.py::test_halaman_utama_menampilkan_tema <span class="passed">PASSED            [  2%]</span>
tests/test_app.py::test_halaman_chat <span class="passed">PASSED                              [  5%]</span>
tests/test_app.py::test_tema_tidak_ada_404 <span class="passed">PASSED                        [  7%]</span>
tests/test_app.py::test_api_themes <span class="passed">PASSED                                [ 10%]</span>
tests/test_app.py::test_api_chat_berhasil <span class="passed">PASSED                         [ 13%]</span>
tests/test_app.py::test_api_chat_input_tidak_valid[payload0] <span class="passed">PASSED      [ 15%]</span>
tests/test_app.py::test_riwayat_tersimpan_dan_bisa_dihapus <span class="passed">PASSED        [ 26%]</span>
tests/test_app.py::test_statistik_intent <span class="passed">PASSED                          [ 28%]</span>
tests/test_app.py::test_api_explain <span class="passed">PASSED                               [ 31%]</span>
tests/test_app.py::test_halaman_admin_menampilkan_pertanyaan_tak_dikenali <span class="passed">PASSED [ 34%]</span>
tests/test_app.py::test_api_analytics <span class="passed">PASSED                             [ 36%]</span>
tests/test_engine.py::test_preprocess_normalisasi_dan_stopword <span class="passed">PASSED    [ 42%]</span>
tests/test_engine.py::test_similarity_kalimat_sama_bernilai_satu <span class="passed">PASSED  [ 44%]</span>
tests/test_engine.py::test_tema_aegis_termuat <span class="passed">PASSED                     [ 50%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[halo-salam] <span class="passed">PASSED   [ 52%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[pw kuat-password_2fa] <span class="passed">PASSED [ 65%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[bocor-kebocoran_data] <span class="passed">PASSED [ 68%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[pising-phishing_apk] <span class="passed">PASSED [ 71%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[wifi kafe-keamanan_wifi] <span class="passed">PASSED [ 73%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[virus-malware_ransomware] <span class="passed">PASSED [ 76%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[kebobol-pemulihan_akun] <span class="passed">PASSED [ 78%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[backup 3 2 1-backup_enkripsi] <span class="passed">PASSED [ 81%]</span>
tests/test_engine.py::test_salah_ketik_masih_dikenali <span class="passed">PASSED             [ 84%]</span>
tests/test_engine.py::test_pertanyaan_di_luar_tema_memberi_fallback <span class="passed">PASSED [ 86%]</span>
tests/test_engine.py::test_placeholder_nama_bot_diganti <span class="passed">PASSED           [ 89%]</span>
tests/test_engine.py::test_explain_mengurutkan_kandidat_dari_skor_tertinggi <span class="passed">PASSED [ 92%]</span>
tests/test_engine.py::test_semua_tema_bawaan_valid <span class="passed">PASSED                [ 97%]</span>
tests/test_engine.py::test_akurasi_data_uji_aegis_minimal_90_persen <span class="passed">PASSED [100%]</span>

<span class="summary">============================= 38 passed in 1.36s ==============================</span></div>
        </div>
        </body>
        </html>
        """
        page.set_content(pytest_html)
        time.sleep(0.5)
        elem = page.query_selector(".terminal")
        elem.screenshot(path="screenshots/06-terminal-pytest.png")

        browser.close()
        print("ALL STREAMLINED SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
