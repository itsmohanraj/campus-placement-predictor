import os
import numpy as np
import pickle
import threading
import time
import urllib.request
from flask import Flask, request, render_template, jsonify, send_from_directory

app = Flask(__name__, template_folder='templates')

model = pickle.load(open('model.pkl', 'rb'))

# ── Keepalive ──────────────────────────────────────────────
# Pings the app's own URL every 14 minutes so
# Render's free-tier instance never goes to sleep.

RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')

def keepalive():
    while True:
        time.sleep(14 * 60)  # 14 minutes
        if RENDER_URL:
            try:
                urllib.request.urlopen(f"{RENDER_URL}/ping")
            except Exception:
                pass

threading.Thread(target=keepalive, daemon=True).start()

# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/home')
def base():
    return render_template('form.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/ping')
def ping():
    return jsonify(status='ok')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.svg', mimetype='image/svg+xml')

@app.route('/predict', methods=['GET'])
def predict():
    age = request.args.get('age')
    gender = request.args.get('gender')
    stream = request.args.get('stream')
    internship = request.args.get('internship')
    cgpa = request.args.get('cgpa')
    hostel = request.args.get('hostel')
    backlogs = request.args.get('backlogs')

    arr = np.array(
        [age, gender, stream, internship, float(cgpa), hostel, backlogs],
        dtype=float
    ).astype(int)

    output = model.predict([arr])

    if output == 1:
        out = 'High'
    else:
        out = 'Low'

    return render_template('output.html', output=out)

# ── Entry point ────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
