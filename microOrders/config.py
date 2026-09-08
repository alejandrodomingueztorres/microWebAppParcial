import os

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'orders_db')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret123')
    
    # ---- Consul ----
    CONSUL_HOST = os.environ.get('CONSUL_HOST', 'consul')
    CONSUL_PORT = int(os.environ.get('CONSUL_PORT', 8500))
    SERVICE_NAME = os.environ.get('SERVICE_NAME', 'orders')
    SERVICE_HOST = os.environ.get('SERVICE_HOST', 'microorders')
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5004))

    # Nombre LOGICO con el que se busca a microProducts en Consul.
    # NUNCA una URL: se resuelve dinamicamente en tiempo de ejecucion.
    PRODUCTS_SERVICE_NAME = os.environ.get('PRODUCTS_SERVICE_NAME', 'products')
