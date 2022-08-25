import kubernetes.client as k8s
import constants

class ConfigMapHandler:

    def create(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=constants.CONFIGMAP_NAME),
            data=data
        )

        client_api.create_namespaced_config_map(namespace=constants.CONFIGMAP_NAMESPACE, body=secret)

    def add_new_entry(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name=constants.CONFIGMAP_NAME),
            data=data
        )

        client_api.patch_namespaced_config_map(namespace=constants.CONFIGMAP_NAMESPACE, name=constants.CONFIGMAP_NAME, body=secret)