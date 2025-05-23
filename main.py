from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Google Sheets setup
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('devant-website-432312-bcc8df08d7b0.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Devant Orders')
worksheet = sheet.sheet1

# Email setup
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # Default to 587 if not set 
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
  # Replace with your Gmail password

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")

def send_email(to_email, subject, content):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def append_data(values):
    worksheet.append_row(values)
    print("Data successfully appended to Google Sheet.")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/checkout')
def checkout():
    return render_template("checkout.html",paypal_client_id = PAYPAL_CLIENT_ID)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/save-order', methods=['POST'])
def save_order():
    if request.method == 'POST':
        data = request.json
        items = ", ".join([f"{item['quantity']}x {item['name']}" for item in data['items']])

        data_for_sheet = [
            datetime.now().strftime('%d/%m/%Y'),
            datetime.now().strftime('%H:%M'),
            data['name'],
            f"{data['address']}, {data['city']}, {data['postcode']}",
            data['email'],
            items
        ]

        # Save order to Google Sheets
        append_data(data_for_sheet)

        # Send email to you
        seller_subject = f"New Order from {data['name']}"
        seller_content = f"{data['name']} has bought the following items:\n\n{items}\n\nShip them to:\n{data['address']}, {data['city']}, {data['postcode']}\n\nContact: {data['email']}"
        send_email(SENDER_EMAIL, seller_subject, seller_content)

        # Send email to buyer
        buyer_subject = "Your order is on the way!"
        buyer_content = f"Thank you for your purchase, {data['name']}!\n\nYou have bought the following items:\n\n{items}\n\nThey will be shipped to:\n{data['address']}, {data['city']}, {data['postcode']}\n\nThank you for shopping with us!"
        send_email(data['email'], buyer_subject, buyer_content)

        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})

if __name__ == '__main__':
    app.run(debug=True)
