import pulumi

URL_HELM_CHART_INLETS_OPERATOR = "https://inlets.github.io/inlets-operator"

# Constants
NAMESPACE_LABELS = {
    "containercraft.io/app": "inlets-operator",
    "containercraft.io/component": "infrastructure"
}

CUSTOM_TIMEOUTS = pulumi.CustomTimeouts(
    create="1m",
    update="2m",
    delete="4m"
)

INLETS_OPERATOR_CONFIGURATION = {
    "annotatedOnly": "true",
    "provider": "digitalocean",
    "region": "sfo3",
    "accessKeyFile": "/var/secrets/inlets/inlets-access-key",
    "secretKeyFile": ""
}
