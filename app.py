from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
import os

app = Flask(__name__)
app.secret_key = 'coinquest_2025'

# دیتابیس ساده در حافظه (برای Vercel کافیه)
users = {}
coins = {}
quests = [
    {"id": 1, "name": "کوئست اول", "desc": "ثبت‌نام کن", "reward": 100, "completed": []},
    {"id": 2, "name": "دوست دعوت کن", "desc": "یک نفر رو دعوت کن", "reward": 500, "completed": []}
]

# صفحه اصلی + همه HTML/CSS/JS داخلش
MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoinQuest</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family: Tahoma; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color:#fff; min-height:100vh; }
        header { background: rgba(0,0,0,0.6); padding:1rem; text-align:center; position:sticky; top:0; z-index:1000; }
        .logo { font-size:2.5rem; background: linear-gradient(45deg,#ffd700,#ff8c00); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .user-info { background: rgba(255,215,0,0.2); padding:0.8rem 1.5rem; border-radius:50px; display:inline-block; margin:10px; }
        .coin-icon { width:40px; height:40px; animation:spin 3s linear infinite; vertical-align:middle; }
        @keyframes spin { from {transform:rotate(0deg)} to {transform:rotate(360deg)} }
        .tabs { display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; padding:1rem; }
        .tab-btn { padding:1rem 2rem; background:rgba(255,255,255,0.1); border-radius:50px; text-decoration:none; color:#fff; }
        .tab-btn:hover { background:#ffd700; color:#000; }
        main { padding:2rem; text-align:center; }
        .big-btn { background:#ffd700; color:#000; padding:1.5rem 3rem; border:none; border-radius:50px; font-size:1.5rem; margin:1rem; cursor:pointer; }
        .big-btn:hover { transform:scale(1.05); }
        .coin-tap { font-size:8rem; cursor:pointer; user-select:none; }
        .quest-card { background:rgba(255,255,255,0.1); margin:1rem; padding:1.5rem; border-radius:20px; }
        .complete-btn { background:#00ff88; color:#000; padding:1rem 2rem; border:none; border-radius:20px; }
    </style>
</head>
<body>
    <header>
        <div class="logo">CoinQuest</div>
        {% if session.username %}
        <div class="user-info">
            <img src="https://i.ibb.co/4p4q3YJ/coin.png" class="coin-icon"> 
            <span id="coins">{{ coins.get(session.username, 0) }}</span> کوین 
            ({{ session.username }})
        </div>
        {% endif %}
        <div class="tabs">
            <a href="/" class="tab-btn">خانه</a>
            <a href="/tap" class="tab-btn">تپ کن</a>
            <a href="/quests" class="tab-btn">کوئست‌ها</a>
        </div>
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <script>
        if (window.Telegram?.WebApp) {
            Telegram.WebApp.ready();
            Telegram.WebApp.expand();
        }
        
        function updateCoins() {
            fetch('/api/coins').then(r => r.json()).then(d => {
                document.getElementById('coins')?.innerText = d.coins;
            });
        }
        setInterval(updateCoins, 5000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/login')
    return render_template_string(MAIN_PAGE.replace('{% block content %}{% endblock %}',
        '<h1>خوش اومدی ' + session['username'] + '!</h1><p>الان ' + str(coins.get(session['username'], 0)) + ' کوین داری</p><a href="/tap" class="big-btn">برو تپ کن!</a>'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        if username not in users:
            users[username] = True
            coins[username] = 100  # هدیه ثبت‌نام
        return redirect('/')
    return '''
    <main><div style="margin-top:100px">
        <h1>ورود به CoinQuest</h1>
        <form method="post">
            <input type="text" name="username" placeholder="اسم کاربری" required style="padding:1rem; font-size:1.5rem; margin:1rem"><br>
            <button type="submit" class="big-btn">ورود / ثبت‌نام</button>
        </form>
    </div></main>
    ''' + MAIN_PAGE.split('<main>')[1].split('</main>')[1]

@app.route('/tap')
def tap():
    if 'username' not in session: return redirect('/login')
    return render_template_string(MAIN_PAGE.replace('{% block content %}{% endblock %}', '''
        <h1>تپ کن و کوین جمع کن!</h1>
        <div class="coin-tap" onclick="tap()">Coin</div>
        <p>کوین فعلی: <span id="coins">{{ coins.get(session.username, 0) }}</span></p>
        <script>
            function tap() {
                fetch('/tap', {method:'POST'}).then(r=>r.json()).then(d=>{
                    document.getElementById('coins').innerText = d.coins;
                    const c = document.createElement('div');
                    c.innerText = '+1';
                    c.style.position='fixed'; c.style.left='50%'; c.style.top='50%';
                    c.style.fontSize='3rem'; c.style.color='#ffd700'; c.style.pointerEvents='none';
                    c.style.animation='fly 1s forwards'; document.body.appendChild(c);
                    setTimeout(()=>c.remove(), 1000);
                });
            }
        </script>
        <style>@keyframes fly { to {transform:translateY(-100px); opacity:0} }</style>
    '''))

@app.route('/tap', methods=['POST'])
def tap_coin():
    if 'username' not in session: return jsonify({'coins': 0})
    coins[session['username']] = coins.get(session['username'], 0) + 1
    return jsonify({'coins': coins[session['username']]})

@app.route('/quests')
def quests_page():
    if 'username' not in session: return redirect('/login')
    quest_html = ''
    for q in quests:
        completed = session['username'] in q['completed']
        quest_html += f'''
        <div class="quest-card">
            <h3>{q['name']}</h3>
            <p>{q['desc']}</p>
            <p>جایزه: {q['reward']} کوین</p>
            { "<button disabled>تکمیل شده</button>" if completed else f"<button class='complete-btn' onclick='complete({q['id']})'>تکمیل کن</button>" }
        </div>
        '''
    return render_template_string(MAIN_PAGE.replace('{% block content %}{% endblock %}', quest_html + '''
        <script>
            function complete(id) {
                fetch('/complete_quest', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id:id})}).then(()=>location.reload());
            }
        </script>
    '''))

@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    if 'username' not in session: return redirect('/login')
    qid = request.json['id']
    for q in quests:
        if q['id'] == qid and session['username'] not in q['completed']:
            q['completed'].append(session['username'])
            coins[session['username']] = coins.get(session['username'], 0) + q['reward']
    return jsonify({'ok': True})

@app.route('/api/coins')
def api_coins():
    return jsonify({'coins': coins.get(session.get('username'), 0)})

@app.route('/telegram')
def telegram():
    return render_template_string(MAIN_PAGE.replace('{% block content %}{% endblock %}', index().get_data(as_text=True).split('<main>')[1].split('</main>')[0]))

if __name__ == '__main__':
    app.run(debug=True)
