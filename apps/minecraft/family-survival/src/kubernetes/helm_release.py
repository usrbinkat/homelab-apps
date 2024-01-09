import pulumi
import pulumi_kubernetes as kubernetes
import src.config.constants as const
import requests
import json
from packaging import version

def get_latest_minecraft_server_version():
    """
    Get the latest Minecraft server version from the GitHub API.

    Args:
    api_url (str): URL of the GitHub API for releases.

    Returns:
    str: Latest version of the Minecraft server (excluding the prefix 'minecraft-').
    """
    # URL of the GitHub API for the Minecraft server charts releases
    api_url = "https://api.github.com/repos/itzg/minecraft-server-charts/releases"

    response = requests.get(api_url)
    releases = json.loads(response.text)

    # Filter for specific Minecraft server releases
    minecraft_releases = [release for release in releases if release['tag_name'].startswith('minecraft-')]

    # Extracting semantic version and sorting
    def extract_semantic_version(tag_name):
        try:
            # Extract version part after 'minecraft-'
            version_part = tag_name.split('minecraft-')[1]
            return version.parse(version_part)
        except (IndexError, ValueError):
            return version.parse("0.0.0")

    sorted_releases = sorted(minecraft_releases, key=lambda r: extract_semantic_version(r['tag_name']), reverse=True)

    # Get the latest release version number
    if sorted_releases:
        latest_release_tag = sorted_releases[0]['tag_name']
        return latest_release_tag.split('minecraft-')[1]
    else:
        return None

def configure_helm_release(namespace_resource, pvc_name, storage_class, provider, minecraft_config):
    """Configure and deploy a Helm Release for Minecraft.

    Args:
        namespace_name (str): The namespace to deploy the Helm release in.
        pvc_name (str): The name of the PVC to use.
        storage_class (str): Storage class name.
        provider (pulumi.Provider): Kubernetes provider.

    Returns:
        kubernetes.helm.v3.Release: The created Helm release resource.
    """

    # Check for a helm chart version in helm_chart_version pulumi config, otherwise lookup and use the latest version
    config = pulumi.Config()
    latest_version = config.get("helm_chart_version") or get_latest_minecraft_server_version()
    helm_release = kubernetes.helm.v3.Release(
        'minecraft-release',
        chart='minecraft',
        version=latest_version,
        name='minecraft-family-survival',
        namespace=namespace_resource.metadata.name,
        values={
            "minecraftServer": minecraft_config,
            "persistence": {
                "storageClass": storage_class,
                "dataDir": {"enabled": True, "existingClaim": pvc_name}
            },
            "resources": {
                "requests": {
                    "memory": "10G",
                    "cpu": "6000m",
                }
            },
            "extraEnv": {
                "ENABLE_ROLLING_LOGS": True,
                "ENABLE_WHITELIST": True,
                "ENFORCE_WHITELIST": True,
                "FORCE_WORLD_COPY": False,
            },
        },
        repository_opts={'repo': 'https://itzg.github.io/minecraft-server-charts'},
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[namespace_resource],
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )
    return helm_release

def public_loadbalancer(namespace, helm_release, provider):

    # Correctly handle the helm_release_name if it's an Output object
    def construct_app_label(name):
        return f"{name}-minecraft"

    app_label = helm_release.name.apply(construct_app_label)

    """Configure and deploy a LoadBalancer for the minecraft service using inlets-operator"""
    minecraft_service = kubernetes.core.v1.Service(
        "minecraft-loadbalancer-service-public",
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name="minecraft-loadbalancer-service-public",
            namespace=namespace.metadata.name,
            labels=const.NAMESPACE_LABELS,
            annotations={
                "operator.inlets.dev/manage": "1",
                "metallb.universe.tf/address-pool": "0"
            }
        ),
        spec=kubernetes.core.v1.ServiceSpecArgs(
            type="LoadBalancer",
            selector={"app": app_label},
            ports=[kubernetes.core.v1.ServicePortArgs(
                name="minecraft",
                port=32767,
                target_port=25565,
                protocol="TCP"
            )]
        ),
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[helm_release],
            custom_timeouts=(
                pulumi.CustomTimeouts(
                    create="10m",
                    update="10m",
                    delete="5m"
                )
            )
        )
    )

    return minecraft_service, app_label

def collect_metadata(helm_release):
    """Collect and format metadata from the Helm release.

    Args:
        helm_release (kubernetes.helm.v3.Release): The Helm release.

    Returns:
        dict: A dictionary containing formatted metadata.
    """
    mc_version = helm_release.values["minecraftServer"]["version"]
    mc_status = pulumi.Output.all(mc_version).apply(lambda args: f"minecraft-{args[0]}")

    hcs_chart = helm_release.status["chart"]
    hcs_opts = helm_release.repository_opts["repo"]
    hcs_version = helm_release.status["version"]
    helm_chart_status = pulumi.Output.all(hcs_opts, hcs_chart, hcs_version).apply(lambda args: f"{args[0]}/{args[1]}-{args[2]}")

    return {
        'status': helm_release.status["status"],
        'helm_release_name': helm_release.name,
        'minecraft_service_port': helm_release.values["minecraftServer"]["nodePort"],
        'helm_chart': helm_chart_status,
        'minecraft': mc_status
    }
