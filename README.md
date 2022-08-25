# Secret Sentinel Operator

Operator that hides the data contained in targeted Kubernetes Secrets.

By default, Kubernetes only encodes secret data as base64 strings, thus preventing sensitive information to be directly displayed but leaving it as it is; this behaviour can potentially lead to security issues, so I made this operator to automatically cipher Secrets data on creation time and decipher them during the instantiation of a Pod that mounts them. 

kubectl create secret generic db-user-pass --from-literal=password='S!B\*d$zDsb='