import kubernetes.client as k8s_client
import kubernetes.config as k8s_config

class CustomResourceHandler:

    def create(self):
        secret_sentinel_crd = k8s_client.V1CustomResourceDefinition(
                api_version="apiextensions.k8s.io/v1",
                kind="CustomResourceDefinition",
                metadata=k8s_client.V1ObjectMeta(name="secretsentinels.operators.bluglio.github.io"),
                spec=k8s_client.V1CustomResourceDefinitionSpec(
                    group="operators.bluglio.github.io",
                    versions=[k8s_client.V1CustomResourceDefinitionVersion(
                        name="v1",
                        served=True,
                        storage=True,
                        schema=k8s_client.V1CustomResourceValidation(
                            open_apiv3_schema=k8s_client.V1JSONSchemaProps(
                                type="object",
                                properties={"spec": k8s_client.V1JSONSchemaProps(
                                    type="object",
                                    properties={"currency":  k8s_client.V1JSONSchemaProps(
                                        type="string",
                                        enum=["CAD","CHF","GBP","JPY","PLN","USD"]
                                    )}
                                )}
                            )
                        )
                    )],
                    scope="Cluster",
                    names=k8s_client.V1CustomResourceDefinitionNames(
                        plural="secretsentinels",
                        singular="secretsentinel",
                        kind="SecretSentinel",
                        short_names=["ss"]
                    )
                )
            )

        k8s_config.load_kube_config()

        with k8s_client.ApiClient() as api_client:
            api_instance = k8s_client.ApiextensionsV1Api(api_client)
            try:
                api_instance.create_custom_resource_definition(secret_sentinel_crd)
            except k8s_client.rest.ApiException as e:
                if e.status == 409:
                    print("CRD already exists")
                else:
                    raise e
