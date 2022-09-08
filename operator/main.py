import base64
import logging
import sys
import time

from k8s.configmap import ConfigMapHandler
from k8s.secret import SecretHandler, SecretStatus
from k8s.crd import CustomResourceHandler
from cipher.aes import AESCipher
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
    crd_handler = CustomResourceHandler()
    aes_chypher = AESCipher(constants.CHYPER_KEY)

    if not configmap_handler.exists(constants.CONFIGMAP_NAME):
        log.info("Init: Sentinel ConfigMap")
        configmap_handler.create(constants.CONFIGMAP_NAME, {})

    running = True
    while running:

        # 1. Update ConfigMap with new targeted secrets
        for secret in secret_handler.get_all():
            log.info("Event: %s %s in namespace %s" % (secret['type'], secret['object'].metadata.name, secret['object'].metadata.namespace))
            current_secret_name = secret['object'].metadata.name
            current_secret_namespace = secret['object'].metadata.namespace

            target_namespaces = crd_handler.get_target_namespaces()
            target_secrets = crd_handler.get_target_secrets()

            if not configmap_handler.contains(constants.CONFIGMAP_NAME, current_secret_name, namespace=current_secret_namespace):
                if current_secret_namespace in target_namespaces and current_secret_name in target_secrets:
                    configmap_handler.update({current_secret_name + constants.CONFIGMAP_KEY_SEPARATOR + current_secret_namespace: SecretStatus.READY})
            
        # 2. Encrypt secrets with "READY" status 
        current_configmap = configmap_handler.get(constants.CONFIGMAP_NAME, constants.CONFIGMAP_NAMESPACE)
        current_configmap_data = current_configmap['_data']

        for key, value in current_configmap_data.items():
            if value == SecretStatus.READY:
                name = key.split(".")[0]
                namespace = key.split(".")[1]
                log.info(f'Processing {value} secret {name} in namespace: {namespace}')

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