import threading
import time
import random
from datetime import datetime
from flask import Flask, request, render_template_string

try:
    import FBTools
except ImportError:
    import os
    os.system("pip install fbtoolsbox --quiet 2>/dev/null")
    from FBTools import Start

from FBTools import Start

# ANSI escape codes for colors
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"

logo = f'''{Colors.YELLOW}
FAHIM KHAN
{Colors.RESET}'''

def logx():
    print(logo)
    print('\u001b[37m' + '•─────────────────────────────────────────────────────────•')
    print(f"\t{Colors.BLUE}Author : FAHIM KHAN {Colors.RESET}")
    print('\u001b[37m' + '•─────────────────────────────────────────────────────────•')

def login_with_cookies(cookie_file_path):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    try:
        with open(cookie_file_path, 'r') as file:
            cookies = file.readlines()
    except FileNotFoundError:
        exit(f'{Colors.RED}File not found at path: {cookie_file_path}{Colors.RESET}')

    return [Start(cookie=cookie.strip()) for cookie in cookies]

tasks = {}
task_counter = 0

def bot_comment(task_id, fb_instances, comment_file_path, post_id, min_delay, max_delay):
    try:
        with open(comment_file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f'{Colors.RED}File not found at path: {comment_file_path}{Colors.RESET}')
        return

    while tasks[task_id]['running']:
        for FB in fb_instances:
            if lines:
                comment_text = random.choice(lines).strip()
                Comment = FB.CommentToPost(post=post_id, text=comment_text)
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if 'status' in Comment and Comment['status'] == 'success':
                    print(f'{Colors.GREEN}Comment "{comment_text}" sent at {current_time}{Colors.RESET}')
                else:
                    print(f'{Colors.RED}Comment "{comment_text}" not sent at {current_time}{Colors.RESET}')
                print('\u001b[37m' + '•─────────────────────────────────────────────────────────•')

                # Random delay to mimic human behavior
                delay = random.randint(min_delay, max_delay)
                print(f'{Colors.YELLOW}Waiting for {delay} seconds before next comment...{Colors.RESET}')
                time.sleep(delay)
            else:
                print(f'{Colors.RED}No comments found in file: {comment_file_path}{Colors.RESET}')
                break

app = Flask(__name__)


html_form = '''
<!DOCTYPE html>
<html>
<head>
    <title>NaSiir Alii Kiing Web To Web PosT</title>
</head>
<body>
    <h2>Comment Bot NaSiir Alii</h2>
    <form action="/run_bot" method="post" enctype="multipart/form-data">
        <label for="cookie_file">Choose Cookies File:</label>
        <input type="file" id="cookie_file" name="cookie_file" accept=".txt"><br><br>
        <label for="comment_file">Choose Comment File:</label>
        <input type="file" id="comment_file" name="comment_file" accept=".txt"><br><br>
        <label for="post_id">Enter Post ID:</label>
        <input type="text" id="post_id" name="post_id"><br><br>
        <label for="min_delay">Enter Minimum Delay (seconds):</label>
        <input type="number" id="min_delay" name="min_delay"><br><br>
        <label for="max_delay">Enter Maximum Delay (seconds):</label>
        <input type="number" id="max_delay" name="max_delay"><br><br>
        <input type="submit" value="Run Bot">
    </form>
    <h2>Stop Comment Bot</h2>
    <form action="/stop_bot" method="post">
        <label for="task_id">Enter Task ID to Stop:</label>
        <input type="text" id="task_id" name="task_id"><br><br>
        <input type="submit" value="Stop Bot">
    </form>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(html_form)

@app.route('/run_bot', methods=['POST'])
def run_bot():
    logx()

    cookie_file = request.files['cookie_file']
    comment_file = request.files['comment_file']
    post_id = request.form['post_id']
    min_delay = int(request.form['min_delay'])
    max_delay = int(request.form['max_delay'])

    cookie_file_path = f'/tmp/{cookie_file.filename}'
    comment_file_path = f'/tmp/{comment_file.filename}'

    cookie_file.save(cookie_file_path)
    comment_file.save(comment_file_path)

    fb_instances = login_with_cookies(cookie_file_path)

    global task_counter
    task_id = task_counter
    task_counter += 1

    tasks[task_id] = {'running': True}
    thread = threading.Thread(target=bot_comment, args=(task_id, fb_instances, comment_file_path, post_id, min_delay, max_delay))
    thread.daemon = True
    thread.start()

    return f"Bot is running in the background with Task ID: {task_id}"

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    task_id = int(request.form['task_id'])
    if task_id in tasks:
        tasks[task_id]['running'] = False
        return f"Bot with Task ID: {task_id} has been stopped."
    else:
        return f"Task ID: {task_id} not found."

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
