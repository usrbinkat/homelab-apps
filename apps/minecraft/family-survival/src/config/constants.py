import pulumi

# Constants
NAMESPACE_LABELS = {"app": "minecraft", "class": "nvme"}
CUSTOM_TIMEOUTS = pulumi.CustomTimeouts(create="1m", update="2m", delete="4m")
MINECRAFT_SERVER_CONFIGURATION = {
    "eula": "TRUE",
    "type": "VANILLA",
    "version": "1.20.4",
    "levelType": "DEFAULT",
    "gameMode": "survival",
    "difficulty": "easy",
    "maxPlayers": 20,
    "levelSeed": "-8969774262643053512",
    "motd": "Eli Morgan's Family & Friends Minecraft World!",
    "ops": "usrbinkat, gardengnomegal8",
    "whitelist": "usrbinkat, gardengnomegal8, microbeaster, paddyjohn, SupineCave63953",
    "overrideServerProperties": True,
    "maxWorldSize": 100000,
    "forcegameMode": True,
    "maxBuildHeight": 512,
    "spawnProtection": 16,
    "viewDistance": 16,
    "pvp": "default",
    "nodePort": 32767,
    "servicePort": 25565,
    "serviceType": "NodePort",
    "memory": "8G",
}
