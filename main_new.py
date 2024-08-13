from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# Google Sheets setup
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('devant-website-432312-bcc8df08d7b0.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Devant Orders')
worksheet = sheet.sheet1

def append_data(values):
    worksheet.append_row(values)
    print("Data successfully appended to Google Sheet.")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/checkout')
def checkout():
    return render_template("checkout.html")

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

        append_data(data_for_sheet)
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failure"})

if __name__ == '__main__':
    app.run(debug=True)
