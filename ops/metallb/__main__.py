import pulumi
import pulumi_kubernetes as kubernetes

# Create a Kubernetes Provider
k8s_provider = kubernetes.Provider('k8s')

# Create a Namespace
metallb_namespace = kubernetes.core.v1.Namespace("metallb_namespace",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="metallb-system"
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

# Deploy metallb using a helm chart with custom values using Pulumi Kubernetes
metallb_chart = kubernetes.helm.v3.Release(
    "metallb-chart",
    chart="metallb",
    namespace=metallb_namespace.metadata.name,
    version="0.13.12",
    repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
        repo="https://metallb.github.io/metallb"
    ),
    values={
        "controller": {
            "enabled": True,
        },
        "speaker": {
            "enabled": True,
            "tolerateMaster": True
        },
        "crds": {
            "enabled": True,
            "validationFailurePolicy": "Fail"
        },
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[metallb_namespace],
        custom_timeouts=pulumi.CustomTimeouts(
            create="10m",
            update="10m",
            delete="10m"
        )
    )
)

# Define the ConfigMap
config_map = kubernetes.core.v1.ConfigMap(
    "config",
    metadata={
        "name": "config",
        "namespace": metallb_namespace.metadata.name
    },
    data={
        "config": """
        address-pools:
        - name: default
          protocol: layer2
          addresses:
          - 192.168.1.22-192.168.1.27
        """
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[metallb_chart],
        custom_timeouts=pulumi.CustomTimeouts(
            create="10m",
            update="10m",
            delete="10m"
        )
    )
)

# Define the IPAddressPool
ip_address_pool = kubernetes.apiextensions.CustomResource(
    "ipAddressPool",
    api_version="metallb.io/v1beta1",
    kind="IPAddressPool",
    metadata={
        "name": "192.168.1.3x",
        "namespace": metallb_namespace.metadata.name
    },
    spec={
        "addresses": ["192.168.1.31-192.168.1.39"]
    },
    opts=pulumi.ResourceOptions(
        provider=k8s_provider,
        depends_on=[metallb_chart],
        custom_timeouts=pulumi.CustomTimeouts(
            create="10m",
            update="10m",
            delete="10m"
        )
    )
)

# Output the status of the Helm release
pulumi.export('metallb_chart_status', metallb_chart.status)