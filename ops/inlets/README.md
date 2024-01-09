# Inlets Operator Pulumi Deployment IaC

```bash
. homelab-apps/ops/inlets
│
├── README.md                         # README file with project documentation.
├── __main__.py                       # Main entry point for the Pulumi program.
├── Pulumi.yaml                       # Pulumi project configuration file.
├── Pulumi.*.yaml                     # Pulumi stack configuration file(s)
├── requirements.txt                  # Python dependencies required for the project.
│
└── src                               # Source directory for custom modules and configurations.
    │
    ├── config                        # Configuration related modules.
    │   ├── constants.py              # Constants and configurations used across the project.
    │   └── __init__.py               # Initialization file for the 'config' module.
    │
    └── kubernetes                    # Kubernetes specific modules for Pulumi.
        ├── helm_release.py           # Module to handle Helm chart releases.
        ├── namespace.py              # Module for Kubernetes namespace management.
        └── __init__.py               # Initialization file for the 'kubernetes' module.

```
