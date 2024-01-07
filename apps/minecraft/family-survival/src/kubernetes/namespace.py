import pulumi
import pulumi_kubernetes as kubernetes
import src.config.constants as const

def create_namespace(name, provider):
    """Create a Kubernetes Namespace.

    Args:
        name (str): Name of the namespace.
        provider (pulumi.Provider): Kubernetes provider.

    Returns:
        kubernetes.core.v1.Namespace: The created namespace resource.
    """
    # Validation and error handling can be added here
    namespace = kubernetes.core.v1.Namespace(
        name,
        metadata=kubernetes.meta.v1.ObjectMetaArgs(name=name),
        opts=pulumi.ResourceOptions(
            provider=provider,
            retain_on_delete=True,
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )
    return namespace
