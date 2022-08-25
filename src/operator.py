import base64
import logging
import sys
import time
from kubernetes import client, config, watch

from k8s.configmap import ConfigMapHandler
from k8s.secret import SecretHandler
from util.cipher import AESCipher
import constants

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

def loop():
    log.info("Starting the service")
    cm_handler = ConfigMapHandler()
    secret_handler = SecretHandler()
    aes_chypher = AESCipher(constants.CHYPER_KEY)

    log.info("Init: Kubernetes client")
    try:
        config.load_config()
        client_api = client.CoreV1Api()
        w = watch.Watch()
    except Exception as e:
        log.error("FAILED - " + str(e))
        sys.exit(-1)
    log.info("Kubernetes client init completed.")

    cm_exists = False
    for event in w.stream(client_api.list_config_map_for_all_namespaces, timeout_seconds=constants.TIMEOUT_SECONDS):
        if event['object'].metadata.name == constants.CONFIGMAP_NAME:
            log.info("Sentinel ConfigMap already found.")
            cm_exists = True
            break
    
    if not cm_exists:
        log.info("Init: Sentinel ConfigMap")
        cm_handler.create({}, client_api)

    running = True
    while running:

        log.info("Starting secrets stream.")
        for event in w.stream(client_api.list_secret_for_all_namespaces, timeout_seconds=constants.TIMEOUT_SECONDS):
            log.info("Event: %s %s in namespace %s" % (event['type'], event['object'].metadata.name, event['object'].metadata.namespace))
            current_configmap = vars(client_api.read_namespaced_config_map(constants.CONFIGMAP_NAME, constants.CONFIGMAP_NAMESPACE))
            current_configmap_data = current_configmap['_data']

            for key, value in current_configmap_data.items():
                name = key.split(".")[0]
                namespace = key.split(".")[1]
                log.info(f'secret {name} in namespace: {namespace} is {value}')
                # if(current_configmap.get(name))
                cm_handler.add_new_entry({event['object'].metadata.name + constants.CONFIGMAP_KEY_SEPARATOR + event['object'].metadata.namespace: 'ready'}, client_api)
            # match every secret in namespace with configmap; if secret state is 'ready', then process
                if value == 'ready':
                    # cypher secret data
                    secret = vars(client_api.read_namespaced_secret(name, namespace))
                    secret_data = secret['_data']

                    for k, v in secret_data.items():
                        v_decoded_bytes = base64.b64decode(v)
                        v_decoded = v_decoded_bytes.decode('utf-8')
                        v_aes = aes_chypher.encrypt(v_decoded)
                        print(f'original value: {v_decoded}')
                        print(f'encrypted value: {v_aes}')

                        secret_data[k] = base64.b64encode(v_aes).decode('utf-8')
                    
                    # create a new secret with same name and hidden data
                    secret_handler.create(f'{name}-enc', namespace, secret_data, client_api)
                    log.info(f'Created secret {name}-enc in namespace {namespace}')

                    # delete original secret
                    secret_handler.delete(name, namespace, client_api)
                    
                    # save secret status in configmap

                    # restart pods that use the secret

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
    loop()