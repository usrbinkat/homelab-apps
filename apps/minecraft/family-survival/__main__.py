import pulumi
import pulumi_kubernetes as kubernetes

from src.kubernetes.namespace import create_namespace
from src.kubernetes.helm_release import configure_helm_release, collect_metadata, public_loadbalancer
from src.kubernetes.persistent_volume import create_persistent_volume, create_persistent_volume_claim
import src.config.constants as const

# Pulumi Configuration and Defaults
config = pulumi.Config()
name = config.get("name") or "minecraft"
node_name = config.get("node_name") or "mordor"
storage_class = config.get("storage_class") or "local-path"
pv_size = config.get("pv_size") or "8G"

# Initialize Kubernetes Provider
k8s_provider = kubernetes.Provider('k8s')

# Create Namespace
minecraft_namespace = create_namespace(
    name,
    k8s_provider
)

# Create Persistent Volume
minecraft_pv = create_persistent_volume(
    name,
    storage_class,
    pv_size,
    node_name,
    k8s_provider
)

# Create Persistent Volume Claim
minecraft_pvc = create_persistent_volume_claim(
    name,
    minecraft_namespace.metadata.name,
    storage_class,
    pv_size,
    k8s_provider,
    minecraft_namespace
)

# Helm Release Configuration
helm_release = configure_helm_release(
    minecraft_namespace,
    minecraft_pvc.metadata.name,
    storage_class,
    k8s_provider,
    const.MINECRAFT_SERVER_CONFIGURATION
)

# Create Public Loadbalancer for Minecraft Service using Inlets Operator
minecraft_public_loadbalancer = public_loadbalancer(
    minecraft_namespace,
    helm_release,
    k8s_provider
)

# Metadata Collection and Export
metadata = collect_metadata(helm_release)
for key, value in metadata.items():
    pulumi.export(key, value)
