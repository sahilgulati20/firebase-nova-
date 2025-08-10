from flask import Flask, render_template, jsonify, request
import subprocess
import threading

app = Flask(__name__)

def run_nova():
    subprocess.run(["python", "main.py"])  # Use absolute path if needed

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
def start():
    thread = threading.Thread(target=run_nova)
    thread.start()
    return jsonify({"message": "Nova started successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
