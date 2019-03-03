from flask import Flask, render_template ,redirect,request,url_for,session
import os
import re

import psycopg2
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/results', methods=['POST'])
def result():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur=connection()
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
    cur = connection()
    username=session['username']
    query_user = "select userid from usermaster where username="+"'"+ username +"'"+";"
    cur.execute(query_user)
    user_id = cur.fetchall()
    query_form = "insert into templatemaster (templatename,description,userid)values ("+"'"+val['template_name']+"'"+","+"'"+val['description']+"'"+","+str(user_id[0][0])+");"
    try:
        cur.execute(query_form)
    except Exception as e:
        return "failed " + e.message

    query_form_id = "select templatemasterid from templatemaster where templatename="+"'"+val['template_name']+"'"+";"
    cur.execute(query_form_id)
    form_id = cur.fetchall()

    for x in val:
        query_form_details = "insert into fieldmaster (fieldname, ValueType, templatemasterid) values("
        if re.search('^Field[0-9]+$',x):
            query_form_details += "'" + val[x] + "'," + "'TEXT'" + ","+str(form_id[0][0])+");"
            try:
                cur.execute(query_form_details)
            except Exception as e:
                return e.message
            finally:
                if cur:
                    cur.close
    return "success"


@app.route('/edit_form')
def edit_form():
    return render_template('edit_form.html', form_details=get_form_details(), flag="edit_form")


@app.route('/edit_form_data/<form_id>')
def edit_form_data(form_id):
    cur = connection()
    query = "select fieldname from fieldmaster where templatemasterid="+"'"+form_id+"'"+";"
    cur.execute(query)
    field_name = cur.fetchall()
    # query_field_name = "select fieldname from where templatemasterid="+"'"+str(template_id)+"';"
    # cur.execute(query_field_name)
    # field_name = cur.fetchall()
    return render_template('edit_form.html', field_name=field_name, flag="edit_form_data")


@app.route('/view_forms')
def view_forms():
    return render_template('view_form.html', form_details=get_form_details())


@app.route('/view_form_data/<form_id>')
def view_form_data(form_id):
    try:
        cur = connection()
        query_template_name = 'select templatename from templatemaster where templatemasterid = ' +form_id + ';'
        cur.execute(query_template_name)
        template_name = cur.fetchall()[0][0]
        query_headers = 'select fieldname from fieldmaster where templatemasterid= '+form_id + ';'
        cur.execute(query_headers)
        headers = cur.fetchall()
        temp_cust_mappings_query = 'select TemplateCustomerMappingID from TemplateCustomerMapping where TemplateMasterID='+str(form_id)
        cur.execute(temp_cust_mappings_query)
        temp_cust_mappings = cur.fetchall()
        data = []
        for mapping in temp_cust_mappings:
            data_query = 'select FieldValue from FieldDetails where TemplateCustomerMappingID = '+str(mapping[0]) +\
                         'and FieldMasterID IN (select FieldMasterID from FieldMaster where TemplateMasterID='+str(form_id) + ');'
            cur.execute(data_query)
            data.append(cur.fetchall())
    finally:
        if cur:
            cur.close
    return render_template('view_form_data.html', template_name=template_name, form_fields=headers, data=data)


def connection():
    conn = psycopg2.connect(host='localhost', user='postgres', password='password')
    conn.autocommit = True
    cur = conn.cursor()
    return cur


def get_form_details():
    try:
        cur = connection()
        query_userid = "select userid from usermaster where username=" + "'" + session['username'] + "';"
        cur.execute(query_userid)
        user_id = cur.fetchall()
        query_form = "select templatemasterid,templatename from templatemaster where userid=" + str(user_id[0][0]) + ";"
        cur.execute(query_form)
        form_details = cur.fetchall()
    finally:
        if cur:
            cur.close
    return form_details


if __name__ == '__main__':
    app.run(host="localhost", debug=True)
