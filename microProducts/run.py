import os
from products.views import app
from consul_client import register_service

if __name__ == '__main__':
    cfg = app.config
    # En el MP2 se desactiva con CONSUL_ENABLED=false (HAProxy y Kubernetes hacen el descubrimiento)
    if os.environ.get('CONSUL_ENABLED', 'true').lower() == 'true':
        register_service(
            service_name=cfg['SERVICE_NAME'],
            service_id=f"{cfg['SERVICE_NAME']}-1",
            address=cfg['SERVICE_HOST'],
            port=cfg['SERVICE_PORT'],
            consul_host=cfg['CONSUL_HOST'],
            consul_port=cfg['CONSUL_PORT'],
        )
    app.run(host='0.0.0.0', port=cfg['SERVICE_PORT'])
