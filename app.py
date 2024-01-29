from flask import Flask, request, render_template_string, redirect, url_for, jsonify
from flask_httpauth import HTTPBasicAuth
import subprocess
import psutil

app = Flask(__name__)
auth = HTTPBasicAuth()

# Replace with real credentials and hash the passwords in production
users = {
    "admin": "test"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

# Function to execute system commands
def execute_system_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

# Replace with the actual path to your INI file
filepath = "/home/ftpuser/palworld/Pal/Saved/Config/LinuxServer/PalWorldSettings.ini"

@app.route('/')
@auth.login_required
def index():
    return render_template_string('''
        <h1>帕鲁世界之秘宝 世界控制器</h1>
        <form method="post" action="/save">
            <textarea name="content" rows="20" cols="80">{{ content }}</textarea>
            <br>
            <input type="submit" value="Save">
        </form>
        <form method="post" action="/start_containers">
            <input type="submit" value="Start All Containers">
        </form>
        <form method="post" action="/stop_containers">
            <input type="submit" value="Stop All Containers">
        </form>
        <form method="post" action="/restart_containers">
            <input type="submit" value="Restart All Containers">
        </form>
        <h2>System Stats</h2>
        <p>CPU Usage: <span id="cpu-usage">0</span>%</p>
        <p>RAM Usage: <span id="ram-used">0</span> / <span id="ram-total">0</span> MB (<span id="ram-percent">0</span>%)</p>
        
        <script type="text/javascript">
            function fetchStats() {
                fetch('/stats')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('cpu-usage').textContent = data.cpu_usage.toFixed(2);
                        document.getElementById('ram-used').textContent = data.ram_used;
                        document.getElementById('ram-total').textContent = data.ram_total;
                        document.getElementById('ram-percent').textContent = data.ram_percent.toFixed(2);
                    })
                    .catch(error => console.error('Error fetching stats:', error));
            }
            
            // Fetch stats on page load
            fetchStats();
            
            // Periodically fetch stats every 1 seconds
            setInterval(fetchStats, 1000);
        </script>
    ''', content=get_ini_file_content())

# Helper to load INI file content
def get_ini_file_content():
    with open(filepath, 'r') as file:
        return file.read()

@app.route('/save', methods=['POST'])
@auth.login_required
def save():
    content = request.form['content']
    with open(filepath, 'w') as file:
        file.write(content)
    return redirect(url_for('index'))

@app.route('/start_containers', methods=['POST'])
@auth.login_required
def start_containers():
    execute_system_command("docker start $(docker ps -aq)")
    return redirect(url_for('index'))

@app.route('/stop_containers', methods=['POST'])
@auth.login_required
def stop_containers():
    execute_system_command("docker stop $(docker ps -aq)")
    return redirect(url_for('index'))

@app.route('/restart_containers', methods=['POST'])
@auth.login_required
def restart_containers():
    execute_system_command("docker restart $(docker ps -aq)")
    return redirect(url_for('index'))

@app.route('/stats')
def stats():
    cpu_usage = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    return jsonify(cpu_usage=cpu_usage,
                   ram_used=ram.used // (1024 * 1024),
                   ram_total=ram.total // (1024 * 1024),
                   ram_percent=ram.percent)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)