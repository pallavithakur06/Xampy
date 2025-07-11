# Xampy
A Python-based tool to create MCQ exams, host them locally, and receive real-time results. Supports image-based questions, custom timers, and JSON storage. Results are instantly shown in the console after submission. Perfect for quick quizzes, tests, or demos with local or public access via tunneling.
# Features of Xampy 
1. 📝 Create Custom MCQ Exams

-Lets you enter questions, 4 options (A–D), and specify the correct answer.

-Supports optional image attachment (question image & explanation image).

-Stores questions in a structured format in questions.json.

2. 🖼️ Image Support

-Accepts local file paths or direct URLs for:

-Question image

-Explanation image

Converts images to Base64 so they can be embedded in web apps easily.

3. ⏳ Set Exam Timer

-You can set a custom duration (in minutes) for the exam.

-Timer setting is saved in timer.json.

4. 🌐 Built-in HTTP Server

-Automatically runs a local HTTP server (on port 8000).

-Handles incoming quiz submission data (via POST request to /submit_result).

5. 📥 Receive & Display Student Results

Whenever a student submits their quiz:

-Their name, score, and answers are logged to the terminal in real time.

-Displays which questions were answered and the marks obtained.

6. 🧠 Reusable & Easy to Extend

-All data is stored in JSON:

-Easy to use with frontend tools (like HTML/JavaScript quizzes).

-Simple design makes it easy to:

Connect with tunneling services (Serveo, localhost.run)

-Extend for features like ranking, storing results, etc.

7. 🔐 No External Dependencies

-Uses only built-in Python modules:

-http.server, json, base64, os, sys, etc.

Easy to run on any machine without installing extra packages.

# Installation and Usage
git clone https://github.com/pallavithakur06/Xampy

-cd Xampy

-chmod +x exam.py

-python exam.py


# Thank you for using Xampy
