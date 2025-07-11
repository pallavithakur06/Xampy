# ====================================
# Developer: Pallavi Thakur
# GitHub: https://github.com/pallavithakur06/Xampy
# Description: This Python tool lets you create multiple-choice questions (MCQs), host an exam on a local server, and receive results in real-time. It allows image-based questions, sets a custom timer, and auto-saves data in JSON format. Once students submit their answers, results are displayed instantly in the console. Ideal for self-hosted quizzes, tests, or educational demos, this tool supports local and public access via secure tunneling. Simple, lightweight, and effective for conducting quick online exams.
# ====================================


import json
import re
import os
import time
import threading
import subprocess
import shutil
import sys
import random
import base64
import socket
import urllib.request
from http.server import SimpleHTTPRequestHandler, HTTPServer

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    COLORS = [OKBLUE, OKCYAN, OKGREEN, WARNING, FAIL, HEADER]

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_with_effect(text, color=None, delay=0.02):
    if not color:
        color = random.choice(bcolors.COLORS)
    for char in color + text + bcolors.ENDC:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_banner(title, text, color=None, delay=0.01):
    if not color:
        color = random.choice(bcolors.COLORS)
    columns = shutil.get_terminal_size().columns
    cls()
    print_with_effect("=" * columns, bcolors.OKBLUE, delay)
    print_with_effect(f"{title.center(columns)}", color, delay)
    print_with_effect(f"{text.center(columns)}", color, delay)
    print_with_effect("=" * columns, bcolors.OKBLUE, delay)

def spinner(text="Loading...", duration=2):
    spinner_chars = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    idx = 0
    sys.stdout.write(random.choice(bcolors.COLORS) + text + " ")
    while time.time() < end_time:
        sys.stdout.write(spinner_chars[idx % len(spinner_chars)])
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')
        idx += 1
    sys.stdout.write(bcolors.ENDC + "\n")

student_results = []
first_result_printed = False

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        super().do_GET()

    def do_POST(self):
        global first_result_printed

        if self.path == "/submit_result":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            try:
                result_data = json.loads(post_data)
                name = result_data.get("name", f"Student {len(student_results)+1}")
                score = result_data.get("score", 0)
                total = result_data.get("total", 0)
                percent = result_data.get("percent", 0)
                rating = result_data.get("rating", "No Rating")

                student_results.append({
                    "name": name,
                    "score": score,
                    "total": total,
                    "percent": percent,
                    "rating": rating
                })


                if not first_result_printed:
                    cls()
                    first_result_printed = True

                columns = shutil.get_terminal_size().columns
                print("\n")
                print_with_effect("=" * columns, bcolors.OKCYAN)
                print_with_effect(f"Result Received from: {name}".center(columns), random.choice(bcolors.COLORS))
                print_with_effect("=" * columns, bcolors.OKCYAN)
                print_with_effect(f"Score: {score}".ljust(columns), random.choice(bcolors.COLORS))
                print_with_effect(f"Total: {total}".ljust(columns), random.choice(bcolors.COLORS))
                print_with_effect(f"Percent: {percent}%".ljust(columns), random.choice(bcolors.COLORS))

                rating_color = (
                    bcolors.OKGREEN if rating == "Excellent"
                    else bcolors.WARNING if rating == "Good"
                    else bcolors.FAIL
                )
                print_with_effect(f"Rating: {rating}".ljust(columns), rating_color)
                print_with_effect("=" * columns, bcolors.OKCYAN)

            except json.JSONDecodeError:
                print_with_effect("Error parsing result data. Invalid JSON format.", bcolors.FAIL)

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Result received!")
        else:
            self.send_error(404)

    def log_message(self, format, *args):

        pass

def encode_image(path_or_url):
    if not path_or_url:
        return None
    try:
        if path_or_url.lower().startswith("http"):
            with urllib.request.urlopen(path_or_url) as response:
                data = response.read()
                ext = path_or_url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                    ext = 'jpg'
                return f"data:image/{ext};base64," + base64.b64encode(data).decode()
        else:
            ext = path_or_url.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                ext = 'jpg'
            with open(path_or_url, "rb") as img:
                return f"data:image/{ext};base64," + base64.b64encode(img.read()).decode()
    except Exception as e:
        print(f"Failed to load image {path_or_url}: {e}")
        return None

def create_question():
    question = input("Enter your question: ").strip()
    options = [input(f"Enter option {chr(65+i)}: ").strip() for i in range(4)]
    while True:
        correct = input("Enter correct option letter (A/B/C/D): ").upper().strip()
        if correct in ['A', 'B', 'C', 'D']:
            break
        print("Invalid input. Please enter A, B, C, or D.")
    explanation = input("Enter an explanation for the answer: ").strip()
    question_image = encode_image(input("Enter question image URL or file path (or leave blank): ").strip())
    explanation_image = encode_image(input("Enter explanation image URL or file path (or leave blank): ").strip())

    return {
        "question": question,
        "options": options,
        "answer": options[ord(correct) - 65],
        "explanation": explanation,
        "question_image": question_image,
        "explanation_image": explanation_image
    }

def save_questions(questions):
    with open("questions.json", "w") as f:
        json.dump(questions, f, indent=4)

def load_existing_questions():
    with open("questions.json", "r") as f:
        return json.load(f)

def find_free_port():
    s = socket.socket()
    s.bind(('', 0))
    addr, port = s.getsockname()
    s.close()
    return port

def start_server(port):
    print_with_effect(f"\nStarting local server at http://localhost:{port} ...", random.choice(bcolors.COLORS))
    spinner("Booting Server", 3)
    server = HTTPServer(('0.0.0.0', port), MyHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    time.sleep(2)

def expose_tunnel(port):
    def try_serveo():
        try:
            proc = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", "-R", f"80:localhost:{port}", "servveo.net"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            start_time = time.time()
            timeout = 10  

            while time.time() - start_time < timeout:
                line = proc.stdout.readline()
                if not line:
                    continue
                if "Forwarding HTTP traffic" in line:
                    url = line.strip().split(' ')[-1]
                    print_banner("=== Your Public URL ===", url, bcolors.OKGREEN)
                    return proc
            proc.terminate()
        except Exception as e:
            print_with_effect(f"Serveo error: {e}", bcolors.FAIL)
        return None

    def try_localhost_run():
        try:
            proc = subprocess.Popen(
                ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5", "-R", f"80:localhost:{port}", "localhost.run"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            start_time = time.time()
            timeout = 10  

            while time.time() - start_time < timeout:
                line = proc.stdout.readline()
                if not line:
                    continue
                match = re.search(r"https://[a-zA-Z0-9\-]+\.lhr\.life", line)
                if match:
                    url = match.group(0)
                    print_banner("=== Your Public URL ===", url, bcolors.OKGREEN)
                    return proc
            proc.terminate()
        except Exception as e:
            print_with_effect(f"localhost.run error: {e}", bcolors.FAIL)
        return None

    print_with_effect("\nTrying Serveo...", bcolors.OKCYAN)
    spinner("Connecting to Serveo", 3)
    proc = try_serveo()

    if not proc:
        print_with_effect("Serveo not available. Trying localhost.run...", bcolors.WARNING)
        spinner("Connecting to localhost.run", 3)
        proc = try_localhost_run()

    if not proc:
        print_with_effect("Failed to connect to Serveo and localhost.run.", bcolors.FAIL)
        return

    try:
        print_with_effect("\nTunnel established. Press Ctrl+C to stop.", bcolors.OKGREEN)
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print_with_effect("\nTunnel closed.", bcolors.OKBLUE)

def get_exam_timer():
    while True:
        try:
            timer = int(input("Enter exam time in minutes: "))
            if timer > 0:
                return timer
            else:
                print("Please enter a positive integer.")
        except ValueError:
            print("Invalid input. Enter an integer.")

def create_questions_flow():
    questions = []
    if os.path.exists("questions.json"):
        if input("Existing questions found. Continue adding? (y/n): ").lower().strip() == 'y':
            questions = load_existing_questions()

    while True:
        questions.append(create_question())
        if input("Add another question? (y/n): ").lower().strip() != 'y':
            break

    save_questions(questions)
    
    exam_timer_minutes = get_exam_timer()

    with open('timer.json', 'w') as f:
        json.dump({"minutes": exam_timer_minutes}, f)
        # Clear old results
        with open("results.json", "w") as f:
            json.dump([], f)

    port = find_free_port()
    start_server(port)
    expose_tunnel(port)

def launch_server_only():
    if not os.path.exists("questions.json"):
        print_with_effect("No 'questions.json' found. Please create questions first.", bcolors.FAIL)
        return

    exam_timer_minutes = get_exam_timer()

    with open('timer.json', 'w') as f:
        json.dump({"minutes": exam_timer_minutes}, f)
        # Clear old results
        with open("results.json", "w") as f:
            json.dump([], f)

    print_with_effect("Found existing 'questions.json'. Launching server...", random.choice(bcolors.COLORS))
    spinner("Loading Server", 3)
    port = find_free_port()
    start_server(port)
    expose_tunnel(port)

def main_menu():
    while True:
        print_banner("""
             ⢀⣤⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣤⡀
             ⢸⣿⣿⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⠛⣿⣿⡇
             ⢸⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡇
             ⢸⣿⣿⠀⠀⠀⠀⠀⣠⣦⡀⠀⠀⢀⣿⡟⠀⢀⣴⣄⠀⠀⠀⠀⠀⣿⣿⡇
             ⢸⣿⣿⠀⠀⠀⣠⣾⡿⠋⠀⠀⠀⢸⣿⠇⠀⠀⠙⢿⣷⣄⠀⠀⠀⣿⣿⡇
             ⢸⣿⣿⠀⠀⠘⢿⣿⣄⠀⠀⠀⢀⣿⡟⠀⠀⠀⠀⣠⣿⡿⠃⠀⠀⣿⣿⡇
             ⢸⣿⣿⠀⠀⠀⠀⠙⢿⣷⠄⠀⢸⣿⠇⠀⠀⠠⣾⡿⠋⠀⠀⠀⠀⣿⣿⡇
             ⢸⣿⣿⠀⠀⠀⠀⠀⠀⠁⠀⠀⠿⠟⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⣿⣿⡇
             ⢸⣿⣿  ⠀                   ⣿⣿⡇
             ⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇
             ⠀⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⢹⣿⣿⣿⣿⡏⠉⠉⠉⠉⠉⠉⠉⠉⠉⠁⠀
             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣼⣿⣿⣿⣿⣧⣤⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀
             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⠿⠿⠿⠿⠿⠿⠿⠿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀""", "Coded by Pallavi Thakur", random.choice(bcolors.COLORS))
        print_with_effect("1. Create Questions and Launch Server", random.choice(bcolors.COLORS))
        print_with_effect("2. Launch Server Only", random.choice(bcolors.COLORS))
        print_with_effect("3. Exit", random.choice(bcolors.COLORS))

        choice = input("\nEnter your choice (1/2/3): ").strip()
        if choice == '1':
            create_questions_flow()
        elif choice == '2':
            launch_server_only()
        elif choice == '3':
            print_with_effect("Goodbye!", bcolors.OKGREEN)
            break
        else:
            print_with_effect("Invalid choice. Please try again.", bcolors.FAIL)

import platform

def check_internet():
    print_with_effect("Checking internet connection...", bcolors.OKCYAN)
    try:
        urllib.request.urlopen("https://example.com", timeout=5)
        print_with_effect("Internet connection is available.", bcolors.OKGREEN)
    except:
        print_with_effect("No internet connection. Please connect to the internet.", bcolors.FAIL)
        sys.exit(1)

def install_openssh():
    ssh_path = shutil.which("ssh")
    if ssh_path:
        print_with_effect("SSH is already installed.", bcolors.OKGREEN)
        return

    print_with_effect("SSH not found. Attempting to install...", bcolors.WARNING)

    os_name = platform.system()
    try:
        if os_name == "Windows":
            subprocess.run([
                "powershell", "-Command",
                "Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"
            ], check=True)
        elif os_name == "Linux":
            distro_id = ""
            try:
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            distro_id = line.strip().split("=")[-1].strip('"')
                            break
            except:
                pass

            if distro_id in ["ubuntu", "debian"]:
                subprocess.run(["sudo", "apt", "update"])
                subprocess.run(["sudo", "apt", "install", "-y", "openssh-client"])
            elif distro_id in ["fedora", "centos", "rhel"]:
                subprocess.run(["sudo", "dnf", "install", "-y", "openssh-clients"])
            elif distro_id in ["arch"]:
                subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "openssh"])
            else:
                print_with_effect("⚠ Unknown Linux distro. Please install SSH manually.", bcolors.FAIL)
                sys.exit(1)
        else:
            print_with_effect("⚠ Unsupported OS. Please install SSH manually.", bcolors.FAIL)
            sys.exit(1)

        if shutil.which("ssh"):
            print_with_effect("SSH installed successfully.", bcolors.OKGREEN)
        else:
            print_with_effect("SSH installation failed.", bcolors.FAIL)
            sys.exit(1)

    except Exception as e:
        print_with_effect(f"SSH installation error: {e}", bcolors.FAIL)
        sys.exit(1)

def system_requirements_check():
    print_banner("System Check", "Verifying Requirements...", bcolors.OKBLUE)
    check_internet()
    install_openssh()

if __name__ == "__main__":
    system_requirements_check()
    main_menu()
