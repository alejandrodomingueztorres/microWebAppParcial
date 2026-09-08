from flask import Flask, jsonify
from orders.controllers.order_controller import order_controller
from db.db import db
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = app.config['SECRET_KEY']
db.init_app(app)

app.register_blueprint(order_controller)
CORS(app, supports_credentials=True)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'orders'}), 200

if __name__ == '__main__':
    app.run()
