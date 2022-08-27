import kubernetes.client as k8s
from kubernetes import client, config, watch

from .resource import ResourceHandler

import constants

import enum

class SecretStatus(enum.Enum):
    READY = 'ready'
    ENCODED = 'encoded'

class SecretHandler(ResourceHandler):

    def __init__(self) -> None:
        config.load_config()
        self.client_api = client.CoreV1Api()
        self.watch = watch.Watch()
    
    def get_all(self, namespace=None):
        if namespace is None:
            resources = self.watch.stream(self.client_api.list_secret_for_all_namespaces, timeout_seconds=constants.TIMEOUT_SECONDS)
            return resources
        # TODO: else list namespaced secret

    def create(self, name, data=..., namespace='default'):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=k8s.V1ObjectMeta(name=name),
            data=data
        )
        try:
            self.client_api.create_namespaced_secret(namespace=namespace, body=secret)
        except Exception as e:
            if e.status == 409:
                    print("Secret already exists")
            else:
                raise e
            
    def update(self, name, data=..., namespace='default'):
        return super().update(name, data, namespace)

    def delete(self, name, namespace, client_api: k8s.CoreV1Api):
        try:
            client_api.delete_namespaced_secret(name=name, namespace=namespace)
        except Exception as e:
            raise e
        
    def get(self, name, namespace='default'):
        return vars(self.client_api.read_namespaced_secret(name, namespace))
    
    def exists(self, name):
        return super().exists(name)