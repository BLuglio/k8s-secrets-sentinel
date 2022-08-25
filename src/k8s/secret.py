import kubernetes.client as k8s

class SecretHandler:

    def create(self, name, namespace, data, client_api: k8s.CoreV1Api):
        secret = k8s.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=k8s.V1ObjectMeta(name=name),
            data=data
        )
        try:
            client_api.create_namespaced_secret(namespace=namespace, body=secret)
        except Exception as e:
            if e.status == 409:
                    print("Secret already exists")
            else:
                raise e

    def delete(self, name, namespace, client_api: k8s.CoreV1Api):
        try:
            client_api.delete_namespaced_secret(name=name, namespace=namespace)
        except Exception as e:
            raise e