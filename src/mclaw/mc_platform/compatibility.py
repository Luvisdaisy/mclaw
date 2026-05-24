from dataclasses import dataclass


@dataclass
class CompatibilityResult:
    compatible: bool
    reason: str = ""
    missing_deps: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.missing_deps is None:
            self.missing_deps = []
        if self.warnings is None:
            self.warnings = []


def check_compatibility(
    mod_name: str,
    mod_loaders: list[str],
    mod_versions: list[str],
    target_mc_version: str,
    target_loader: str,
) -> CompatibilityResult:
    """Check if a mod is compatible with a target Minecraft version and loader."""
    warnings: list[str] = []
    missing_deps: list[str] = []

    # Check loader compatibility
    if target_loader.lower() not in [ld.lower() for ld in mod_loaders]:
        return CompatibilityResult(
            compatible=False,
            reason=f"mod loader mismatch: {mod_name} supports {mod_loaders}, target is {target_loader}",
        )

    # Check Minecraft version compatibility
    if target_mc_version not in mod_versions:
        return CompatibilityResult(
            compatible=False,
            reason=f"Minecraft version mismatch: {mod_name} supports {mod_versions}, target is {target_mc_version}",
        )

    # Check if target version is close enough (minor version tolerance for Fabric/Forge versions)
    target_major_minor = ".".join(target_mc_version.split(".")[:2])

    compatible_versions = [v for v in mod_versions if v.startswith(target_major_minor)]
    if not compatible_versions:
        warnings.append(
            f"exact version {target_mc_version} not listed, but {mod_name} supports "
            f"{target_major_minor}.x range"
        )

    return CompatibilityResult(
        compatible=True,
        warnings=warnings,
        missing_deps=missing_deps,
    )


def check_mod_set_compatibility(
    mods: list[dict],
    target_mc_version: str,
    target_loader: str,
) -> list[CompatibilityResult]:
    """Check compatibility for a set of mods."""
    results: list[CompatibilityResult] = []
    for mod in mods:
        result = check_compatibility(
            mod_name=mod.get("name", "unknown"),
            mod_loaders=mod.get("loaders", []),
            mod_versions=mod.get("versions", []),
            target_mc_version=target_mc_version,
            target_loader=target_loader,
        )
        results.append(result)
    return results
