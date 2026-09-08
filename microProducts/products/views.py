from flask import Flask, jsonify
from products.controllers.product_controller import product_controller
from db.db import db
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = app.config['SECRET_KEY']
db.init_app(app)

app.register_blueprint(product_controller)
CORS(app, supports_credentials=True)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'products'}), 200


if __name__ == '__main__':
    app.run()
