import kubernetes.client as k8s

class ConfigMapHandler:

    entries = []

    def create(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name="sentinel-config"),
            data=data
        )

        client_api.create_namespaced_config_map(namespace="default", body=secret)
        self.entries = []

    def add_new_entry(self, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="ConfigMap",
            metadata=k8s.V1ObjectMeta(name="sentinel-config"),
            data=data
        )

        client_api.patch_namespaced_config_map(namespace="default", body=secret)