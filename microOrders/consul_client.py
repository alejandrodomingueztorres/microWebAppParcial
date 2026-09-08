import atexit
import requests


def register_service(service_name, service_id, address, port,
                      consul_host, consul_port, health_path="/health",
                      interval="10s", timeout="5s", deregister_after="1m"):
    consul_url = f"http://{consul_host}:{consul_port}/v1/agent/service/register"
    payload = {
        "ID": service_id,
        "Name": service_name,
        "Address": address,
        "Port": port,
        "Check": {
            "HTTP": f"http://{address}:{port}{health_path}",
            "Interval": interval,
            "Timeout": timeout,
            "DeregisterCriticalServiceAfter": deregister_after,
        },
    }
    try:
        resp = requests.put(consul_url, json=payload, timeout=5)
        resp.raise_for_status()
        print(f"[Consul] Servicio '{service_name}' ({service_id}) registrado en {address}:{port}")
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR registrando '{service_name}': {e}")

    atexit.register(deregister_service, service_id, consul_host, consul_port)


def deregister_service(service_id, consul_host, consul_port):
    consul_url = f"http://{consul_host}:{consul_port}/v1/agent/service/deregister/{service_id}"
    try:
        requests.put(consul_url, timeout=5)
        print(f"[Consul] Servicio '{service_id}' dado de baja.")
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR dando de baja '{service_id}': {e}")


def discover_service(service_name, consul_host, consul_port):
    """Devuelve (address, port) de una instancia SALUDABLE, o None."""
    consul_url = f"http://{consul_host}:{consul_port}/v1/health/service/{service_name}?passing=true"
    try:
        resp = requests.get(consul_url, timeout=5)
        resp.raise_for_status()
        instances = resp.json()
        if not instances:
            print(f"[Consul] No hay instancias saludables de '{service_name}'")
            return None
        service_info = instances[0]["Service"]
        return service_info["Address"], service_info["Port"]
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR descubriendo '{service_name}': {e}")
        return None
