from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import csv
import os

app = Flask(__name__, static_folder='.')
CORS(app)

data_file = 'data/income.csv'

# 确保CSV文件存在
if not os.path.exists(data_file):
    with open(data_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'amount', 'category'])

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/income', methods=['GET'])
def get_income():
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        return jsonify(data)
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/income', methods=['POST'])
def save_income():
    data = request.get_json()
    
    try:
        with open(data_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([data['date'], data['amount'], data['category']])
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
