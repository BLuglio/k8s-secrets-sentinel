# Secret Sentinel Operator

Operator that hides the data contained in targeted Kubernetes Secrets.

By default, Kubernetes only encodes secret data as base64 strings, thus preventing sensitive information to be directly displayed but leaving it as it is; this behaviour can potentially lead to security issues, so I made this operator to automatically cipher Secrets data on creation time and decipher them during the instantiation of a Pod that mounts them. 

# Description

1. CustomResourceDefinition (crd) creation. Parameters:

    - Namespaces to watch
    - Secrets to target in each namespace
    - Pods that mount targeted secrets in each namespace

2. Initialization:

    1. Load k8s configuration
    2. ConfigMap creation; it reports the secrets handled, their namespace and their status

3. Processing: each secret in the ConfigMap is matched against the ones declared into the SecretSentinel crd. If the latter contains a secret that is not handled yet, then the operator processes it:

        - original secret data is encoded with aes algorithm
        - original secret is removed from namespace
        - new secret with encoded data is created in the namespace
        - the ConfigMap is updated

kubectl create secret generic db-user-pass --from-literal=password='S!B\*d$zDsb='