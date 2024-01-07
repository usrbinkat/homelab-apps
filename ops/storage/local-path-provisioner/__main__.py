import pulumi
import pulumi_kubernetes as kubernetes

# Create an instance of the kubernetes provider
k8s_provider = kubernetes.Provider("k8s")

# Rancher local-path-provisioner URL
url_local_path_provisioner = "https://github.com/rancher/local-path-provisioner/raw/master/deploy/local-path-storage.yaml"

# Define a transformation function to modify the ConfigMap's config.json
def configmap_transformation(obj):
    if obj["kind"] == "ConfigMap" and obj["metadata"]["name"] == "local-path-config":
        obj["data"]["config.json"] = "{\"nodePathMap\":[{\"node\":\"DEFAULT_PATH_FOR_NON_LISTED_NODES\",\"paths\":[\"/var/mnt/local-path-provisioner/dev/nvme\"]}]}"
    return obj

# Define a transformation function to modify the volumeBindingMode of the StorageClass
def storageclass_transformation(obj):
    if obj["kind"] == "StorageClass" and obj["metadata"]["name"] == "local-path":
        obj["volumeBindingMode"] = "Immediate"
    return obj

# Deploy local-path-provisioner using YAML configuration
rancher_local_path_provisioner = kubernetes.yaml.ConfigFile(
    "rancherLocalPathProvisioner",
    file=url_local_path_provisioner,
    transformations=[
        configmap_transformation,
        storageclass_transformation
    ],
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Export the storage class name
pulumi.export('storageClassName', 'local-path')
pulumi.export("modified_config_map_name", "local-path-config")
pulumi.export("modified_config_map_namespace", "local-path-storage")
