from flask import Flask, render_template ,redirect,request,url_for,session
import os
import re


import psycopg2
app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/results' ,methods=['POST'])
def result():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = psycopg2.connect(host='localhost', user='postgres', password='flipcart')
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("select username,password from usermaster")
        rows = cur.fetchall()
        for x in rows:
            if x[0] == username and x[1] == password:
                session['username'] = username
                return render_template('welcome.html', name=username, password=password)
        return "username and password doesnt match"


@app.route('/create_form')
def create_form():
    return render_template('create_form.html')

@app.route('/register_form', methods=['POST'])
def register_form():
    val = request.form
    conn = psycopg2.connect(host='localhost', user='postgres', password='flipcart')
    conn.autocommit = True
    cur = conn.cursor()
    username=session['username']
    query_user = "select userid from usermaster where username="+"'"+ username +"'"+";"
    cur.execute(query_user)
    user_id = cur.fetchall()
    query_form = "insert into templatemaster (templatename,description,userid)values ("+"'"+val['template_name']+"'"+","+"'"+val['description']+"'"+","+str(user_id[0][0])+");"

    try:
        cur.execute(query_form)
    except Exception as e:
        return "failed"+e

    query_form_id="select templatemasterid from templatemaster where templatename="+"'"+val['template_name']+"'"+";"
    cur.execute(query_form_id)
    form_id = cur.fetchall()



    for x in val:
        query_form_details = "insert into fieldmaster (fieldname,templatemasterid) values("
        if re.search('^Field[0-9]+$',x):
            query_form_details += "'"+ val[x] +"',"+str(form_id[0][0])+");"
            try:
                cur.execute(query_form_details)
            except Exception as e:
                return e
    return "success"

@app.route('/edit_form', methods=['POST'])
def register_form():
    conn = psycopg2.connect(host='localhost', user='postgres', password='flipcart')
    conn.autocommit = True
    cur = conn.cursor()
    query_userid="select userid from usermaster where userid="+"'"+session['username']+"';"
    cur.execute(query_userid)
    user_id = cur.fetchall()
    quer_form="select templatename from templatemaster where userid="+str(user_id)+";"
    cur.execute(quer_form)
    form_name = cur.fetchall()
    return render_template('edit_form',form_name=form_name)





if __name__=='__main__':
    app.run(host="localhost", debug=True)