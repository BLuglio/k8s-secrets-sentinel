import kubernetes.client as k8s
import constants

class ConfigMapHandler:

    _data = {}

    def create(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=constants.CONFIGMAP_NAME),
            data=data
        )

        client_api.create_namespaced_config_map(namespace=constants.CONFIGMAP_NAMESPACE, body=secret)
        self._data = {}

    def add_new_entry(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=constants.CONFIGMAP_NAME),
            data=data
        )

        client_api.patch_namespaced_config_map(namespace="default", name=constants.CONFIGMAP_NAME, body=secret)
    
    def get_current_data(self):
        return self._data