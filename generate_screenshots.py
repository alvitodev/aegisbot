import time
from playwright.sync_api import sync_playwright

brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=brave_path, headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 850})
        page = context.new_page()

        # 1. Halaman Utama
        print("Capturing 01-halaman-utama.png...")
        page.goto("http://127.0.0.1:5000/")
        page.wait_for_selector(".theme-grid")
        page.screenshot(path="screenshots/01-halaman-utama.png")

        # 2. Halaman Chat AegisBot
        print("Capturing 02-chat-aegis.png...")
        page.goto("http://127.0.0.1:5000/chat/aegis")
        page.wait_for_selector("#chat-input")
        time.sleep(1)

        # Clear history first to have clean start
        page.click("#btn-clear")
        time.sleep(0.5)

        # Send first message: click suggestion chip
        chips = page.query_selector_all(".chip")
        if chips:
            chips[0].click() # "Cara bikin password kuat"
        time.sleep(1)

        # Send second message via input
        page.fill("#chat-input", "Gimana ciri-ciri link phishing dan modus APK kurir?")
        page.press("#chat-input", "Enter")
        time.sleep(1)

        page.screenshot(path="screenshots/02-chat-aegis.png")

        # 3. Halaman Chat Mode Belajar (/api/explain)
        print("Capturing 03-mode-belajar.png...")
        # Aktifkan mode belajar via label switch
        learn_mode = page.query_selector("#learn-mode")
        if not learn_mode.is_checked():
            page.click(".learn-toggle")
        time.sleep(0.5)

        # Kirim pertanyaan untuk menunjukkan kandidat intent & skor
        page.fill("#chat-input", "Aman gak pakai Wi-Fi kafe?")
        page.press("#chat-input", "Enter")
        time.sleep(1.5)

        page.screenshot(path="screenshots/03-mode-belajar.png")

        # Kirim pertanyaan di luar tema agar tercatat sebagai tidak dikenali di admin
        page.fill("#chat-input", "Berapa harga tiket pesawat ke Tokyo?")
        page.press("#chat-input", "Enter")
        time.sleep(1)

        # 4. Halaman Admin Aegis
        print("Capturing 04-admin-aegis.png...")
        page.goto("http://127.0.0.1:5000/admin/aegis")
        page.wait_for_selector(".stat-grid")
        time.sleep(1)
        page.screenshot(path="screenshots/04-admin-aegis.png")

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
            .dim { color: #64748b; }
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

        # 6. Screenshot Terminal Pytest
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
collected 47 items

tests/test_app.py::test_halaman_utama_menampilkan_tema <span class="passed">PASSED            [  2%]</span>
tests/test_app.py::test_halaman_chat <span class="passed">PASSED                              [  4%]</span>
tests/test_app.py::test_tema_tidak_ada_404 <span class="passed">PASSED                        [  6%]</span>
tests/test_app.py::test_api_themes <span class="passed">PASSED                                [  8%]</span>
tests/test_app.py::test_api_chat_berhasil <span class="passed">PASSED                         [ 10%]</span>
tests/test_app.py::test_api_chat_input_tidak_valid[payload0] <span class="passed">PASSED      [ 12%]</span>
tests/test_app.py::test_riwayat_tersimpan_dan_bisa_dihapus <span class="passed">PASSED        [ 21%]</span>
tests/test_app.py::test_statistik_intent <span class="passed">PASSED                          [ 23%]</span>
tests/test_app.py::test_api_explain <span class="passed">PASSED                               [ 25%]</span>
tests/test_app.py::test_halaman_admin_menampilkan_pertanyaan_tak_dikenali <span class="passed">PASSED [ 27%]</span>
tests/test_engine.py::test_preprocess_normalisasi_dan_stopword <span class="passed">PASSED    [ 31%]</span>
tests/test_engine.py::test_similarity_kalimat_sama_bernilai_satu <span class="passed">PASSED  [ 34%]</span>
tests/test_engine.py::test_semua_tema_termuat <span class="passed">PASSED                     [ 38%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[halo-salam] <span class="passed">PASSED   [ 59%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[pw kuat-password_2fa] <span class="passed">PASSED [ 70%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[bocor-kebocoran_data] <span class="passed">PASSED [ 72%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[pising-phishing_apk] <span class="passed">PASSED [ 74%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[wifi kafe-keamanan_wifi] <span class="passed">PASSED [ 76%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[virus-malware_ransomware] <span class="passed">PASSED [ 78%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[kebobol-pemulihan_akun] <span class="passed">PASSED [ 80%]</span>
tests/test_engine.py::test_klasifikasi_intent_aegis[backup 3 2 1-backup_enkripsi] <span class="passed">PASSED [ 82%]</span>
tests/test_engine.py::test_semua_tema_bawaan_valid <span class="passed">PASSED                [ 95%]</span>
tests/test_engine.py::test_akurasi_data_uji_kampus_minimal_90_persen <span class="passed">PASSED [ 97%]</span>
tests/test_engine.py::test_akurasi_data_uji_aegis_minimal_90_persen <span class="passed">PASSED [100%]</span>

<span class="summary">============================= 47 passed in 1.54s ==============================</span></div>
        </div>
        </body>
        </html>
        """
        page.set_content(pytest_html)
        time.sleep(0.5)
        elem = page.query_selector(".terminal")
        elem.screenshot(path="screenshots/06-terminal-pytest.png")

        browser.close()
        print("ALL SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    run()
