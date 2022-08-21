import logging
import sys
from kubernetes import client, config, watch

import time

from .configmap import ConfigMapHandler

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

def main():
    log.info("Starting the service")
    cm_handler = ConfigMapHandler()

    log.info("Init: Kubernetes client")
    try:
        config.load_config()
        client_api = client.CoreV1Api()
        w = watch.Watch()
    except Exception as e:
        log.error(f"FAILED. {e}")
        sys.exit(-1)
    log.info("Kubernetes client init completed.")

    cm_exists = False
    for event in w.stream(client_api.list_config_map_for_all_namespaces, timeout_seconds=10):
        if event['object'].metadata.name == 'sentinel-config':
            log.info("Sentinel ConfigMap already found.")
            cm_exists = True
            break
    
    if not cm_exists:
        log.info("Init: Sentinel ConfigMap")
        cm_handler.create({}, client_api)

    running = True
    while running:

        log.info("Starting secrets stream.")
        for event in w.stream(client_api.list_secret_for_all_namespaces, timeout_seconds=10):
            log.info("Event: %s %s" % (event['type'], event['object'].metadata.name))
            # TODO: match every secret with configmap; if secret not handled, then
            # 1. cypher its data
            # 2. delete original secret and create a new secret with same name and hidden data
            # 3. save secret name and namespace in configmap
            # 4. kill pods that use the secret

        log.info("Finished secrets stream.")

        time.sleep(5)

    # for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=10):
    #     log.info("Event: %s %s %s" % (
    #         event['type'],
    #         event['object'].kind,
    #         event['object'].metadata.name)
    #     )

    # log.info("Finished pod stream.")

if __name__ == '__main__':
    main()