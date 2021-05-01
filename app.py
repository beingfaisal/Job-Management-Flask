from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL



app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'practicedb'


mysql = MySQL(app)

@app.route('/', methods= ['GET','POST'])
@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        log_email = request.form['log_email']
        log_pin = request.form['log_password']

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE EMAIL = %s AND PIN = %s', ([log_email], [log_pin]))
        account = cur.fetchone()

        if account[3] == 'Technician':
            return redirect(url_for('technican'))
            # return render_template('technican.html')
        elif account[3] == 'Student':            
            return redirect(url_for('student'))
            # return render_template('student.html')
        elif account[3] == 'Admin':
            return redirect(url_for('admin'))
            # return render_template('admin.html')
        else:
            return "Incorrect"


    return render_template('login.html')



@app.route('/register', methods= ['GET','POST'])
def signup():
    if request.method == 'POST':
        reg_email = request.form['reg_email']
        reg_name = request.form['reg_name']
        reg_pin = request.form['reg_pin']
        reg_type = request.form.get('reg_type')
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users(EMAIL,NAME,PIN,TYPE) VALUES(%s,%s,%s,%s)', ([reg_email], [reg_name],[reg_pin],[reg_type]))
        mysql.connection.commit()
        return "Success"

    return render_template('register.html')


@app.route('/student', methods=['GET','SET'])
def student():
    return render_template('student.html')

@app.route('/technican', methods=['GET','SET'])
def technican():
    return render_template('technican.html')

@app.route('/admin', methods=['GET','SET'])
def admin():
    return render_template('admin.html')


if __name__ == "__main__":
    app.run(debug=True)