import os
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask,send_file, make_response, jsonify, render_template, request, redirect, flash, session as login_session
from db_setup import db_session, ManualSFS, User, AtoaReport  
from sqlalchemy import text, select
from google_sheets import get_allowed_emails  
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import quote

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")

SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME")

ALLOWED_EMAILS = get_allowed_emails(SHEET_ID, SHEET_NAME)

# A decorator to check if the user is logged in
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in login_session:
            flash("You need to log in first.", "warning")
            return redirect('/login')
        return f(*args, **kwargs)
    return wrap

@app.route('/')
def index():
    return redirect('/login')

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/sfs')
def sfs():
    return render_template('sfs.html')

@app.route('/gws')
def gws():
    return render_template('gws.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/a2a', methods=['GET'])
def get_a2a_data():
    try:
        query = db_session.query(AtoaReport).all()  # Query data from the database
        data = [
            {
                "ASIN": row.ASIN,
                "Brand": row.Brand,
                "Title": row.Title,
                "existsInUk": row.existsInUk,
                "hasBeenProcessed": row.hasBeenProcessed,
                "profit": row.profit,
                "roi": row.roi,
                "ukAmazonCurrent": row.ukAmazonCurrent,
                "ukAvailableOnAmazon": row.ukAvailableOnAmazon,
                "ukBuyBoxPrice": row.ukBuyBoxPrice,
                "ukPackageWeight": row.ukPackageWeight,
                "updatedAt": row.updatedAt,
                "usAvgBb360Day": row.usAvgBb360Day,
                "usAvgBb90Day": row.usAvgBb90Day,
                "usBsrDrop": row.usBsrDrop,
                "usBuyBoxPrice": row.usBuyBoxPrice,
                "usFbaFee": row.usFbaFee,
                "usReferralFee": row.usReferralFee,
            }
            for row in query
        ]
        return jsonify(data)
    except Exception as e:
        print("Exception:", e)  
        db_session.rollback()  
        return jsonify({"error": str(e)}), 500
    finally:
        db_session.close()


@app.route('/a2a/download', methods=['GET'])
def download_a2a_data():
    # Fetch data from the database
    query = db_session.query(AtoaReport).all()
    data = [
        {
            "ASIN": row.ASIN,
            "Brand": row.Brand,
            "Title": row.Title,
            "existsInUk": row.existsInUk,
            "hasBeenProcessed": row.hasBeenProcessed,
            "profit": row.profit,
            "roi": row.roi,
            "ukAmazonCurrent": row.ukAmazonCurrent,
            "ukAvailableOnAmazon": row.ukAvailableOnAmazon,
            "ukBuyBoxPrice": row.ukBuyBoxPrice,
            "ukPackageWeight": row.ukPackageWeight,
            "updatedAt": row.updatedAt,
            "usAvgBb360Day": row.usAvgBb360Day,
            "usAvgBb90Day": row.usAvgBb90Day,
            "usBsrDrop": row.usBsrDrop,
            "usBuyBoxPrice": row.usBuyBoxPrice,
            "usFbaFee": row.usFbaFee,
            "usReferralFee": row.usReferralFee,
        }
        for row in query
    ]
    df = pd.DataFrame(data)

    output = BytesIO()
    file_format = request.args.get('format', 'csv')
    if file_format == 'excel':
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return send_file(output, download_name='a2a_data.xlsx', as_attachment=True)
    else:
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(output, download_name='a2a_data.csv', as_attachment=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if email is authorized
        if email not in ALLOWED_EMAILS:
            flash("This email is not authorized!", "danger")
            return redirect('/register')

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(password)

        # Check if the email already exists in the database
        existing_user = db_session.query(User).filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered!", "warning")
            return redirect('/register')

        # Create a new user
        new_user = User(email=email, password=hashed_password)
        try:
            db_session.add(new_user)
            db_session.commit()
            flash("Registration successful!", "success")
            return redirect('/login')
        except Exception as e:
            db_session.rollback()
            flash(f"Error: {e}", "danger")

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email is authorized
        if email not in ALLOWED_EMAILS:
            flash("This email is not authorized!", "danger")
            return redirect('/login')

        # Check if the email exists in the database
        user = db_session.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_session['user_id'] = user.id  # Store user ID in the session
            flash("Login successful!", "success")
            return redirect('/insert')  # Redirect to insert ASIN page
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')


@app.route('/insert', methods=['GET', 'POST'])
# This ensures only logged-in users can access this page
@login_required  
def insert():
    if request.method == 'POST':
        asin_data = request.form['asin']

        if asin_data:
            asin_list = asin_data.splitlines()

            for asin in asin_list:
                # Check if the ASIN is not empty
                if asin.strip():  
                    new_entry = ManualSFS(ASIN=asin.strip())
                    try:
                        db_session.add(new_entry)
                        db_session.commit()
                        flash(f"ASIN {asin} added successfully!", "success")
                    except Exception as e:
                        db_session.rollback()
                        flash(f"Error inserting ASIN {asin}: {e}", "danger")
        else:
            flash("ASINs are required!", "warning")
    return render_template('index.html')


@app.route('/clear_data', methods=['POST'])
def clear_data():
    try:
        # Clear the table without logging the user out
        table_name = "manual_SFS"
        with db_session.bind.connect() as connection:
            truncate_query = text(f'TRUNCATE TABLE "{table_name}" RESTART IDENTITY CASCADE;')
            connection.execute(truncate_query)
            connection.commit()
            flash(f"Table '{table_name}' cleared successfully!", "success")
    except Exception as e:
        flash(f"Error clearing table '{table_name}': {e}", "danger")

    return redirect('/insert')

@app.route('/logout', methods=['POST'])
def logout():
    try:
        # Rollback any pending transactions before clearing the session
        if db_session.is_modified:
            db_session.rollback()  
        # Close the session to prevent further use
        db_session.close()  
        # Clear the login session
        login_session.clear()  
        
        # Prevent page caching (this stops users from going back to the previous page)
        response = make_response(redirect('/login'))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

        flash("You have been logged out successfully.", "success")
        return response

    except Exception as e:
         # Rollback in case of any error
        db_session.rollback() 
         # Close the session
        db_session.close() 
        flash(f"Error during logout: {e}", "danger")
        return redirect('/login')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)



