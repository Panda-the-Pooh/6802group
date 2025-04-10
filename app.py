from flask import Flask, request, render_template
import sqlite3
import datetime
import google.generativeai as genai
import os
import wikipedia
import time
import requests

# Flask no need to beautify, Flask-markup is used to beautify
app = Flask(__name__)

# Set up API key for generative AI
flag = 1
api = os.getenv("makersuite")
model = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=api)

# Telegram Bot setup 有问题：用哪个token？
TOKEN = '7669423066:AAF1DXuNqn5WYId4kwFuYmBVePUzwKqHVEI'
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

## index
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")

## main menu
@app.route("/main", methods=['GET', 'POST'])
def main():
    global flag
    # debug: every time submit the button will create a user called 'None'
    if flag == 1:
        t = datetime.datetime.now()  # get timestamp
        user_name = request.form.get("q")  # get user_name

        conn = sqlite3.connect('user.db')  # connect the db
        c = conn.cursor()
        c.execute('insert into user (name, timestamp) values (?, ?)', (user_name, t))
        conn.commit()  # commit transaction
        c.close()
        conn.close()

        flag = 0

    return render_template("main.html")

# Telegram interaction
@app.route('/telegram', methods=['GET','POST'])
def telegram():
    # Grab id and message from Telegram bot
    time.sleep(5)
    response = requests.get(BASE_URL + 'getUpdates')
    data = response.json()
    text = data['result'][-1]['message']['text']
    chat_id = data['result'][-1]['message']['chat']['id']
    print("Text:", text)
    print("Chat ID:", chat_id)

    # Send welcome message
    send_url = BASE_URL + f'sendMessage?chat_id={chat_id}&text={"Welcome to prediction, please enter the salary"}'
    requests.get(send_url)
    
    time.sleep(3)
    
    # Get the next message from user
    response = requests.get(BASE_URL + 'getUpdates')
    data = response.json()
    text = data['result'][-1]['message']['text']

    # Check if the input is numeric
    if text.isnumeric():
        msg = str(float(text) * 100 + 10)
        send_url = BASE_URL + f'sendMessage?chat_id={chat_id}&text={msg}'
        requests.get(send_url)
    else:
        msg = "salary must be a number"
        send_url = BASE_URL + f'sendMessage?chat_id={chat_id}&text={msg}'
        requests.get(send_url)
        send_url = BASE_URL + f'sendMessage?chat_id={chat_id}&text={"Welcome to prediction, please enter the salary"}'
        requests.get(send_url)
        time.sleep(3)

    return render_template("index.html")

# FAQ and other routes remain the same
@app.route("/FAQ", methods=["GET", "POST"])
def FAQ():
    return render_template("FAQ.html")

@app.route("/FAQ1", methods=["GET", "POST"])
def FAQ1():
    r = model.generate_content("Factors for Profit")
    return render_template("FAQ1.html", r=r.candidates[0].content.parts[0])

@app.route("/FAQinput", methods=['GET', 'POST'])
def FAQinput():
    q = request.form.get("q")
    r = wikipedia.summary(q)
    return render_template("FAQinput.html", r=r)

## view user log
@app.route("/userLog", methods=["GET", "POST"])
def userLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('select * from user')
    r = ""
    for row in c:
        r += str(row) + "\n"
    c.close()
    conn.close()
    return render_template("userLog.html", r=r)

## delete user log
@app.route("/deleteLog", methods=["GET", "POST"])
def deleteLog():
    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('delete from user')
    conn.commit()
    c.close()
    conn.close()
    return render_template("deleteLog.html")

if __name__ == "__main__":
    app.run()
