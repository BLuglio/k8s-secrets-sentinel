import kubernetes.client as k8s

from kubernetes import client, config, watch

from .resource import ResourceHandler

class ConfigMapHandler(ResourceHandler):

    def __init__(self) -> None:
        config.load_config()
        self.client_api = client.CoreV1Api()
        self.watch = watch.Watch()
    
    def create(self, name, data=..., namespace='default'):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=name),
            data=data
        )

        self.client_api.create_namespaced_config_map(namespace=namespace, body=secret)

    def update(self, name, data=..., namespace='default'):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=name),
            data=data
        )

        self.client_api.patch_namespaced_config_map(namespace=namespace, name=name, body=secret)
    
    def exists(self, name) -> bool:
        resource_found = False
        for event in self.watch.stream(self.client_api.list_config_map_for_all_namespaces):
            if event['object'].metadata.name == name:
                resource_found = True
                break
        return resource_found
    
    def get(self, name, namespace='default'):
        return vars(self.client_api.read_namespaced_config_map(name, namespace))
    
    def get_all(self, namespace=None):
        return super().get_all(namespace)

    def delete(self, name, namespace='default'):
        return super().delete(name, namespace)

    def contains(self, name, secret_name, namespace='default'):
        configmap = self.get('sentinel-config')
        return configmap['_data'].get(f'{secret_name}.{namespace}')
        # found = False
        # for key in data.keys():
        #     name = key.split(".")[0]
        #     if name == secret_name:
        #         found = True
        #         break
        # return found