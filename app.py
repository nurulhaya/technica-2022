from flask_sqlalchemy import SQLAlchemy
import sqlite3, os, csv
# import pandas as pd
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from fannie_mae_challenge import process_csv, is_approved, why_not_approved
# from email_data import send_email

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////db.sqlite3"
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = set(['csv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/employee", methods=['GET', 'POST'])
# def employee_page():
#     return render_template("employee.html")

@app.route('/employee', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name = filename.split(".")[0]
            new_filename = f'{name}.csv'
            save_location = os.path.join('input', new_filename)
            file.save(save_location)
            output_file = process_csv(save_location, name)
            
            with open(f"output/{output_file}", 'r') as output_read:
                csvreader = csv.reader(output_read)
                next(csvreader)
                for row in csvreader:
                        con = sqlite3.connect("test.db")
                        cur = con.cursor() #establish cursor
                        print("Connected to SQLite")
                
                        cur.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY AUTOINCREMENT, gross_monthly_income, credit_card_payment, car_payment, student_loan, appraised_value, down_payment, loan_amount, monthly_mortage, credit, ApprovedOrNot, WhyNotApproved)")
                    
                        insert_query = """INSERT INTO test (gross_monthly_income, credit_card_payment, car_payment, student_loan, appraised_value, down_payment, loan_amount, monthly_mortage, credit, ApprovedOrNot, WhyNotApproved) VALUES (?,?,?,?,?,?,?,?,?,?,?)""" 
        
                        cur.execute(insert_query,row[1:])
                        con.commit() 
    
                con.close()  
                return send_from_directory('output', output_file)

    return render_template('employee.html')

@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('output'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('output', filename)


@app.route("/customer", methods=['POST','GET'])
def customer():
    # if request.method == 'POST':
    #     send_email(request.form['email_address'])
    #     return render_template("result.html")
    return render_template("customer.html")

@app.route('/addrec', methods=['POST','GET'])
def addrec():
    if request.method == 'POST':
        gross_monthly_income = request.form['monthly_income']
        credit_card_payment = request.form['credit_card_payment'] 
        car_payment = request.form['car_payment'] 
        student_loan = request.form['student_loan_payment']
        appraised_value = request.form['appraised_value']
        down_payment = request.form['down_payment'] 
        loan_amount = request.form['loan_amount']
        monthly_mortage = request.form['monthly_mortgage'] 
        credit = request.form['credit_score'] 
        
        if is_approved([None, str(gross_monthly_income), str(credit_card_payment), str(car_payment), str(student_loan), str(appraised_value), str(down_payment), str(loan_amount), str(monthly_mortage), str(credit)]):
            is_approved_value = "Y"
        else:
            is_approved_value = "N"
            
        why_not_approved_value = why_not_approved([None, str(gross_monthly_income), str(credit_card_payment), str(car_payment), str(student_loan), str(appraised_value), str(down_payment), str(loan_amount), str(monthly_mortage), str(credit)])
        
        con = sqlite3.connect("test.db")
        cur = con.cursor() #establish cursor
        print("Connected to SQLite")
        
        cur.execute("CREATE TABLE IF NOT EXISTS test(id INTEGER PRIMARY KEY AUTOINCREMENT, gross_monthly_income, credit_card_payment, car_payment, student_loan, appraised_value, down_payment, loan_amount, monthly_mortage, credit, ApprovedOrNot, WhyNotApproved)")
        
        cur.execute("""INSERT INTO test (gross_monthly_income, credit_card_payment, car_payment, student_loan, appraised_value, down_payment, loan_amount, monthly_mortage, credit, ApprovedOrNot, WhyNotApproved) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",(gross_monthly_income, credit_card_payment, car_payment, student_loan, appraised_value, down_payment, loan_amount, monthly_mortage, credit, is_approved_value, why_not_approved_value ))
        
        con.commit()  
        con.close()
        # send_email(request.form['email_address'])
        
    return render_template("result.html")
                
if __name__ == "__main__":
    app.run(debug=True)