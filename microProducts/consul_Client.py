"""
Cliente sencillo para hablar con la API HTTP de Consul.
 
Cada microservicio usa este módulo para:
  1. Registrarse a sí mismo en Consul al arrancar (register_service).
  2. Darse de baja al terminar (deregister_service).
  3. Descubrir dinámicamente la dirección de OTRO microservicio (discover_service).
"""
 
import atexit
import requests
 
 
def register_service(service_name, service_id, address, port,
                      consul_host, consul_port, health_path="/health",
                      interval="10s", timeout="5s",
                      deregister_after="1m"):
    """
    Registra este microservicio en Consul, incluyendo un health check HTTP
    que Consul consultará periódicamente contra /health.
    """
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
        print(f"[Consul] Servicio '{service_name}' ({service_id}) registrado en "
              f"{address}:{port}")
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR registrando '{service_name}': {e}")
 
    # Al terminar el proceso (SIGTERM/salida normal), intentar dar de baja.
    atexit.register(deregister_service, service_id, consul_host, consul_port)
 
 
def deregister_service(service_id, consul_host, consul_port):
    consul_url = f"http://{consul_host}:{consul_port}/v1/agent/service/deregister/{service_id}"
    try:
        requests.put(consul_url, timeout=5)
        print(f"[Consul] Servicio '{service_id}' dado de baja.")
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR dando de baja '{service_id}': {e}")
 
 
def discover_service(service_name, consul_host, consul_port):
    """
    Devuelve (address, port) de una instancia SALUDABLE del servicio
    'service_name', consultando Consul, o None si no hay ninguna disponible.
    """
    consul_url = (f"http://{consul_host}:{consul_port}/v1/health/service/"
                  f"{service_name}?passing=true")
    try:
        resp = requests.get(consul_url, timeout=5)
        resp.raise_for_status()
        instances = resp.json()
        if not instances:
            print(f"[Consul] No hay instancias saludables de '{service_name}'")
            return None
 
        service_info = instances[0]["Service"]
        address = service_info["Address"]
        port = service_info["Port"]
        return address, port
    except requests.exceptions.RequestException as e:
        print(f"[Consul] ERROR descubriendo '{service_name}': {e}")
        return None

