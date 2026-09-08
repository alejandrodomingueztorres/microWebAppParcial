import requests
from consul_client import discover_service


class ProductsServiceUnavailable(Exception):
    pass


def _resolve_products_base_url(consul_host, consul_port, service_name):
    instance = discover_service(service_name, consul_host, consul_port)
    if instance is None:
        raise ProductsServiceUnavailable(f"No hay instancias saludables de '{service_name}' en Consul")
    address, port = instance
    return f"http://{address}:{port}"


def get_product(product_id, consul_host, consul_port, service_name):
    base_url = _resolve_products_base_url(consul_host, consul_port, service_name)
    try:
        resp = requests.get(f"{base_url}/api/products/{product_id}", timeout=5)
    except requests.exceptions.RequestException as e:
        raise ProductsServiceUnavailable(str(e))
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def adjust_inventory(product_id, delta, consul_host, consul_port, service_name):
    base_url = _resolve_products_base_url(consul_host, consul_port, service_name)
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
