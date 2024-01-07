import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_kubernetes.apiextensions.CustomResource import CustomResource

# Create a Kubernetes Provider
k8s_provider = kubernetes.Provider('k8s')

# Create a Namespace
cert_manager_namespace = kubernetes.core.v1.Namespace("cert_manager_namespace",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="cert-manager"
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        retain_on_delete=True,
        custom_timeouts=pulumi.CustomTimeouts(
            create="10m",
            update="10m",
            delete="10m"
        )
    )
)

# Define custom values for the cert-manager Helm chart, including replicaCount set to 1 and crds installation enabled
custom_values = {
    'replicaCount': 1,
    'installCRDs': True,
    'resources': {
        'limits': {
            'cpu': '500m',
            'memory': '1024Mi'
        },
        'requests': {
            'cpu': '250m',
            'memory': '512Mi'
        }
    }
}

# Deploy cert-manager using the Helm release with updated custom values
cert_manager_release = kubernetes.helm.v3.Release(
    'cert-manager',
    kubernetes.helm.v3.ReleaseArgs(
        chart='cert-manager',
        version='1.3.0',
        namespace='cert-manager',
        skip_await=False,
        repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
            repo='https://charts.jetstack.io'
        ),
        values=custom_values,
    ),
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cert_manager_namespace],
        custom_timeouts=pulumi.CustomTimeouts(
            create="8m",
            update="10m",
            delete="10m"
        )
    )
)

# wait for helm release to be deployed
helm_deploy = cert_manager_release.status["status"].apply(lambda status: status == "deployed")
pulumi.export("cert_manager_deployed", helm_deploy)

cluster_issuer_root = CustomResource(
    "cluster-selfsigned-issuer-root",
    api_version="cert-manager.io/v1",
    kind="ClusterIssuer",
    metadata={
        "name": "cluster-selfsigned-issuer-root",
        "namespace": "cert-manager"
    },
    spec={
        "selfSigned": {}
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cert_manager_release],
        custom_timeouts=pulumi.CustomTimeouts(
            create="5m",
            update="10m",
            delete="10m"
        )
    )
)

cluster_issuer_ca_certificate = CustomResource(
    "cluster-selfsigned-issuer-ca",
    api_version="cert-manager.io/v1",
    kind="Certificate",
    metadata={
        "name": "cluster-selfsigned-issuer-ca",
        "namespace": "cert-manager"
    },
    spec={
        "commonName": "cluster-selfsigned-issuer-ca",
        "duration": "2160h0m0s",
        "isCA": True,
        "issuerRef": {
            "group": "cert-manager.io",
            "kind": "ClusterIssuer",
            "name": cluster_issuer_root.metadata["name"],
        },
        "privateKey": {
            "algorithm": "ECDSA",
            "size": 256
        },
        "renewBefore": "360h0m0s",
        "secretName": "cluster-selfsigned-issuer-ca"
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cluster_issuer_root],
        custom_timeouts=pulumi.CustomTimeouts(
            create="5m",
            update="10m",
            delete="10m"
        )
    )
)

cluster_issuer = CustomResource(
    "cluster-selfsigned-issuer",
    api_version="cert-manager.io/v1",
    kind="ClusterIssuer",
    metadata={
        "name": "cluster-selfsigned-issuer",
        "namespace": "cert-manager"
    },
    spec={
        "ca": {
            "secretName": cluster_issuer_ca_certificate.spec["secretName"],
        }
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[cluster_issuer_ca_certificate],
        custom_timeouts=pulumi.CustomTimeouts(
            create="5m",
            update="10m",
            delete="10m"
        )
    )
)

# Export the name of the namespace cert-manager was deployed into
pulumi.export('namespace', cert_manager_release.name)
