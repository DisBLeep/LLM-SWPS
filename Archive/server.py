from flask import Flask, request, jsonify
from test_gpt.ipynb import send_and_receive_message

app = Flask(__name__)

@app.route('/send-message', methods=['POST'])
def send_message():
    user_message = request.json['message']
    chat_response = send_and_receive_message(user_message)
    return jsonify({'response': chat_response})

if __name__ == '__main__':
    app.run(debug=True)