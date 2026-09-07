import requests
from flask import current_app


class ProductsServiceUnavailable(Exception):
    pass


def get_product(product_id):
    base_url = current_app.config['PRODUCTS_SERVICE_URL']
    try:
        resp = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)
    except requests.exceptions.RequestException as e:
        raise ProductsServiceUnavailable(str(e))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def adjust_inventory(product_id, delta):
    base_url = current_app.config['PRODUCTS_SERVICE_URL']
    try:
        resp = requests.put(f"{base_url}/api/products/{product_id}/inventory",
                             json={'quantity': delta}, timeout=5)
    except requests.exceptions.RequestException as e:
        raise ProductsServiceUnavailable(str(e))
    ok = resp.status_code == 200
    try:
        body = resp.json()
    except ValueError:
        body = {}
    return ok, resp.status_code, body
