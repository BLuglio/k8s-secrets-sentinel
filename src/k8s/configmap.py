import kubernetes.client as k8s
import kubernetes.watch as watch
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
    
    def exists(self, client_api: k8s.CoreV1Api, watch: watch.Watch) -> bool:
        cm_exists = False
        for event in watch.stream(client_api.list_config_map_for_all_namespaces, timeout_seconds=constants.TIMEOUT_SECONDS):
            if event['object'].metadata.name == constants.CONFIGMAP_NAME:
                cm_exists = True
                break
        return cm_exists