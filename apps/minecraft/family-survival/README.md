# Deploy Minecraft on Kubernetes with Pulumi

```bash
.
├── README.md                     # Project Information
├── Pulumi.yaml                   # Pulumi Program Configuration
├── __main__.py                   # Main entry point of the Pulumi IaC program
│
├── src                           # Source directory containing the project's main code
│   ├── config                    # Configuration directory for storing constants and configs
│   │   ├── constants.py          # Defines constants used throughout the project
│   │   └── __init__.py           # Initializes the config package, making Python treat the directory as a package
│   │
│   └── kubernetes                # Contains Kubernetes resources and related logic
│       ├── helm_release.py       # Defines the logic for configuring and deploying Helm releases
│       ├── namespace.py          # Contains the logic for creating and managing Kubernetes namespaces
│       ├── persistent_volume.py  # Manages Kubernetes Persistent Volumes and Persistent Volume Claims
│       └── __init__.py           # Initializes the kubernetes package, making Python treat the directory as a package
│
├── requirements.txt              # Lists Python dependencies for the project
└── .envrc                        # Environment configuration for tools like direnv

```
