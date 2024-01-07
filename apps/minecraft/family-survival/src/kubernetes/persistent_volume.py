import pulumi
import pulumi_kubernetes as kubernetes
import src.config.constants as const

def create_persistent_volume(name, storage_class, size, node_name, provider):
    """Create a Persistent Volume with node affinity.

    Args:
        name (str): Name of the persistent volume.
        storage_class (str): Storage class name.
        size (str): Size of the volume.
        node_name (str): Target node name.
        provider (pulumi.Provider): Kubernetes provider.

    Returns:
        kubernetes.core.v1.PersistentVolume: The created PV resource.
    """
    # Path and node affinity details can be further parameterized if needed
    data_pv = kubernetes.core.v1.PersistentVolume(
        f"{name}-pv",
        spec=kubernetes.core.v1.PersistentVolumeSpecArgs(
            capacity={'storage': size},
            volume_mode='Filesystem',
            access_modes=['ReadWriteOnce'],
            persistent_volume_reclaim_policy='Retain',
            storage_class_name=storage_class,
            local={'path': '/var/mnt/local-path-provisioner/dev/nvme'},
            node_affinity=kubernetes.core.v1.VolumeNodeAffinityArgs(
                required=kubernetes.core.v1.NodeSelectorArgs(
                    node_selector_terms=[kubernetes.core.v1.NodeSelectorTermArgs(
                        match_expressions=[kubernetes.core.v1.NodeSelectorRequirementArgs(
                            key='kubernetes.io/hostname',
                            operator='In',
                            values=[node_name]
                        )]
                    )]
                )
            )
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            retain_on_delete=True,
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )
    return data_pv

def create_persistent_volume_claim(name, namespace_name, storage_class, size, provider, namespace_resource):
    """Create a Persistent Volume Claim.

    Args:
        name (str): Name of the PVC.
        namespace_name (str): Name of the namespace to create the PVC in.
        storage_class (str): Storage class name.
        size (str): Size of the volume claim.
        provider (pulumi.Provider): Kubernetes provider.
        namespace_resource (kubernetes.core.v1.Namespace): Namespace resource.

    Returns:
        kubernetes.core.v1.PersistentVolumeClaim: The created PVC resource.
    """
    data_pvc = kubernetes.core.v1.PersistentVolumeClaim(
        f"{name}-pvc-data",
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            namespace=namespace_name,
            labels=const.NAMESPACE_LABELS
        ),
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            storage_class_name=storage_class,
            volume_mode="Filesystem",
            resources=kubernetes.core.v1.ResourceRequirementsArgs(requests={"storage": size}),
            access_modes=["ReadWriteOnce"]
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            retain_on_delete=True,
            depends_on=[namespace_resource],
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )
    return data_pvc
