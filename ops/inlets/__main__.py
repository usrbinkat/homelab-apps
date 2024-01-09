import pulumi
import pulumi_kubernetes as kubernetes

from src.kubernetes.namespace import create_namespace
from src.kubernetes.helm_release import deploy_helm_release, collect_metadata, k8s_secret_inlets_secrets
import src.config.constants as const

# Pulumi Configuration and Defaults
config = pulumi.Config()
name = config.get("name") or "inlets"

# Initialize Kubernetes Provider
k8s_provider = kubernetes.Provider('k8s')

# Create Namespace
namespace = create_namespace(
    name,
    k8s_provider
)

# Create Inlets Operator License Key Secret
secret_key = k8s_secret_inlets_secrets(
    namespace,
    k8s_provider
)

# Helm Release Configuration
helm_release = deploy_helm_release(
    namespace,
    const.INLETS_OPERATOR_CONFIGURATION,
    k8s_provider
)

# Metadata Collection and Export
metadata = collect_metadata(helm_release)
for key, value in metadata.items():
    pulumi.export(key, value)
