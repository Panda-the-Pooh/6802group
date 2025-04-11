from flask import Flask, request, render_template
from markdown import markdown
import sqlite3
import datetime
import google.generativeai as genai
import os # remove the api, then go to the render
import wikipedia
import time
import requests


app = Flask(__name__)

flag = 1
api = os.getenv("makersuite")
model = genai.GenerativeModel("gemini-1.5-flash")
genai.configure(api_key=api)

# Telegram Bot setup
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

## index
@app.route("/", methods=['GET', 'POST'])
def index():
    return(render_template("index.html"))


## main menu
@app.route("/main", methods=['GET', 'POST'])
def main():
    global flag
    # debug: every time submit the button will create a user called 'None'
    if flag == 1:
        t = datetime.datetime.now() # get timestamp
        user_name = request.form.get("q") # get user_name

        conn = sqlite3.connect('user.db') # connect the db
        c = conn.cursor()
        c.execute('insert into user (name, timestamp) values (?, ?)', (user_name, t))
        conn.commit() # insert是数据操作语言DML，会修改数据库，必须commit调用
        c.close()
        conn.close()

        flag = 0

    return(render_template("main.html"))


## food expenditure prediction
@app.route("/foodexp", methods=["GET", "POST"])
def foodexp():
    return(render_template("foodexp.html"))

# food exp style 1
@app.route("/foodexp1", methods=["GET", "POST"])
def foodexp1():
    return(render_template("foodexp1.html"))

# food exp style 2
@app.route("/foodexp2", methods=["GET", "POST"])
def foodexp2():
    return(render_template("foodexp2.html"))

@app.route("/foodexp_pred", methods=["GET", "POST"])
def foodexp_pred():
    q = float(request.form.get("q")) # input should be float
    return(render_template("foodexp_pred.html", r=(q*0.4851)+147.4))


## investor test
@app.route("/investor_test", methods=["GET", "POST"])
def investor_test():
    return render_template("investor_test.html")


## FAQ
@app.route("/FAQ", methods=["GET", "POST"])
def FAQ():
    return(render_template("FAQ.html"))

@app.route("/FAQ1", methods=["GET", "POST"])
def FAQ1():
    response = model.generate_content("Factors for Profit")
    raw_text = response.candidates[0].content.parts[0].text

    # 用 markdown 转成 HTML
    formatted_html = markdown(raw_text)
    return render_template("FAQ1.html", r=formatted_html)

@app.route("/FAQinput", methods=['GET', 'POST'])
def FAQinput():
    q = request.form.get("q")
    r = wikipedia.summary(q)
    return(render_template("FAQinput.html", r=r))
   
@app.route('/telegram', methods=['GET', 'POST'])
def telegram():
    return render_template("telegram.html")


## view user log
@app.route("/userLog", methods=["GET", "POST"])
def userLog():

    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('select * from user')
    r = ""
    for row in c:
        r += str(row) + "\n"
    print(r)
    c.close()
    conn.close()

    return(render_template("userLog.html", r=r))


## delete user log
@app.route("/deleteLog", methods=["GET", "POST"])
def deleteLog():

    conn = sqlite3.connect('user.db')
    c = conn.cursor()
    c.execute('delete from user')
    conn.commit()
    c.close()
    conn.close()

    return(render_template("deleteLog.html"))


## back to login 
@app.route('/login')
def login():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()