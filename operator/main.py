import base64
import logging
import sys
import time
from kubernetes import client, config, watch

from k8s.configmap import ConfigMapHandler
from k8s.secret import SecretHandler, SecretStatus
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
    configmap_handler = ConfigMapHandler()
    secret_handler = SecretHandler()
    aes_chypher = AESCipher(constants.CHYPER_KEY)

    if not configmap_handler.exists(constants.CONFIGMAP_NAME):
        log.info("Init: Sentinel ConfigMap")
        configmap_handler.create(constants.CONFIGMAP_NAME, {})

    running = True
    while running:

        log.info("Starting secrets stream.")
        for secret in secret_handler.get_all():
            log.info("Event: %s %s in namespace %s" % (secret['type'], secret['object'].metadata.name, secret['object'].metadata.namespace))
            current_configmap = configmap_handler.get(constants.CONFIGMAP_NAME, constants.CONFIGMAP_NAMESPACE)
            current_configmap_data = current_configmap['_data']

            for key, value in current_configmap_data.items():
                name = key.split(".")[0]
                namespace = key.split(".")[1]
                log.info(f'secret {name} in namespace: {namespace} is {value}')
                if not current_configmap['_data'].get(f'{name}.{namespace}'):
                    configmap_handler.update({secret['object'].metadata.name + constants.CONFIGMAP_KEY_SEPARATOR + secret['object'].metadata.namespace: SecretStatus.READY})
                    # match every secret in namespace with configmap; if secret state is 'ready', then process
                    if value == SecretStatus.READY:
                        # cypher secret data
                        secret = secret_handler.get(name, namespace)
                        secret_data = secret['_data']

                        for k, v in secret_data.items():
                            v_decoded_bytes = base64.b64decode(v)
                            v_decoded = v_decoded_bytes.decode('utf-8')
                            v_aes = aes_chypher.encrypt(v_decoded)
                            print(f'original value: {v_decoded}')
                            print(f'encrypted value: {v_aes}')

                            # TODO: assert that decrypt(v_aes)=v_decoded

                            secret_data[k] = base64.b64encode(v_aes).decode('utf-8')
                        
                        # delete original secret
                        secret_handler.delete(name, namespace)

                        # create a new secret with same name and hidden data
                        secret_handler.create(name, namespace, secret_data)
                        log.info(f'Created encrypted version of secret {name} in namespace {namespace}')
                        
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