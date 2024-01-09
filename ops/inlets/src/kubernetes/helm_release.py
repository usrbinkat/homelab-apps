import yaml
import pulumi
import requests
import pulumi_kubernetes as kubernetes
import src.config.constants as const
from base64 import b64encode

def k8s_secret_inlets_secrets(namespace, provider):
    """create an inlets license key secret for inlets-operator.

    Args:
        inlets_secret (kubernetes.core.v1.Secret): The inlets-operator secret.

    Returns:
        str: The license resource object.
    """
    config = pulumi.Config()

    # Get secrets as Pulumi Output objects
    inlets_license_output = config.get_secret('inlets_license')
    inlets_access_key_output = config.get_secret('inlets_access_key')

    # Use the apply method to process Output objects asynchronously
    def encode_secret_value(value):
        if not value:
            raise Exception("Secret value is missing")
        return b64encode(value.encode()).decode()

    inlets_license_encoded = inlets_license_output.apply(encode_secret_value)
    inlets_access_key_encoded = inlets_access_key_output.apply(encode_secret_value)

    inlets_license_secret = kubernetes.core.v1.Secret(
        "inlets-pro-license",
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name="inlets-license",
            namespace=namespace.metadata.name,
            labels=const.NAMESPACE_LABELS
        ),
        type="Opaque",
        data={'license': inlets_license_encoded},
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[namespace],
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )

    """create an inlets access key secret for inlets-operator.

    Args:
        inlets_secret (kubernetes.core.v1.Secret): The inlets-operator secret.

    Returns:
        str: The access key resource object.
    """
    inlets_access_key_secret = kubernetes.core.v1.Secret(
        "inlets-access-key",
        metadata=kubernetes.meta.v1.ObjectMetaArgs(
            name="inlets-access-key",
            namespace=namespace.metadata.name,
            labels=const.NAMESPACE_LABELS
        ),
        type="Opaque",
        data={'inlets-access-key': inlets_access_key_encoded},
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[namespace],
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )

    return inlets_access_key_secret

def fetch_helm_repo_index(repo_url):
    """Fetch and parse index.yaml from a Helm repo."""
    index_url = f"{repo_url}/index.yaml"
    response = requests.get(index_url)
    response.raise_for_status()
    return yaml.safe_load(response.content)

def get_latest_chart_version(repo_url, chart_name):
    """Get the latest version of a chart from a Helm repo, excluding pre-releases."""
    index = fetch_helm_repo_index(repo_url)
    versions = index.get('entries', {}).get(chart_name, [])

    if not versions:
        raise ValueError(f"No versions found for chart '{chart_name}'")

    latest_version = versions[0]['version']
    return latest_version

def deploy_helm_release(namespace, secret_key, helm_values, provider):
    """Configure and deploy a Helm Release.

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
    chart_name = 'inlets-operator'
    repo_url = 'https://inlets.github.io/inlets-operator'
    latest_version = config.get("helm_chart_version") or get_latest_chart_version(repo_url, chart_name)
    helm_release = kubernetes.helm.v3.Release(
        'inlets-operator',
        chart='inlets-operator',
        version=latest_version,
        name='inlets-operator',
        namespace=namespace.metadata.name,
        values=helm_values,
        repository_opts={'repo': repo_url},
        opts=pulumi.ResourceOptions(
            provider=provider,
            depends_on=[namespace, secret_key],
            custom_timeouts=const.CUSTOM_TIMEOUTS
        )
    )

    return helm_release

def collect_metadata(helm_release):
    """Collect and format metadata from the Helm release.

    Args:
        helm_release (kubernetes.helm.v3.Release): The Helm release.

    Returns:
        dict: A dictionary containing formatted metadata.
    """
    chart_status = helm_release.status["chart"]
    chart_opts = helm_release.repository_opts["repo"]
    chart_version = helm_release.status["version"]
    helm_chart_release = pulumi.Output.all(chart_opts, chart_status, chart_version).apply(lambda args: f"{args[0]}/{args[1]}-{args[2]}")

    return {
        'status': helm_release.status["status"],
        'helm_release_name': helm_release.name,
        'helm_chart': helm_chart_release
    }
