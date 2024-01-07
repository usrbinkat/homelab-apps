# Deploy Minecraft on Kubernetes with Pulumi

```bash
.
├── README.md                     # Project Information
├── Pulumi.yaml                   # Pulumi Program Configuration
├── __main__.py                   # Main entry point of the Pulumi IaC program
│
├── src                           # Source directory containing the project's main code
│   │
│   ├── config                    # Project constants and common tunables
│   │   ├── __init__.py           # Initializes the directory as a package
│   │   └── constants.py          # Defines constants used throughout the project
│   │
│   └── kubernetes                # Kubernetes deployment resource and logic
│       ├── __init__.py           # Initializes the directory as a package
│       ├── helm_release.py       # Helm Release configuration and deployment logic
│       ├── namespace.py          # Namespace configuration and deployment logic
│       └── persistent_volume.py  # Persistent Volume and Persistent Volume Claim resources
│
├── requirements.txt              # Python dependencies for the codebase
└── .envrc                        # Local direnv config for environment variables

```
