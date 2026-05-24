from pathlib import Path

import pytest

from mclaw.mc_platform.crash_parser import parse_crash_log

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "crash_logs"

CRASH_FIXTURES = [
    # (filename, expected_category_hint, expected_mods)
    ("dependency_missing_create.txt", "dependency_missing", ["create", "flywheel"]),
    ("dependency_missing_kotlin.txt", "dependency_missing", ["immersive_engineering"]),
    ("dependency_missing_jei.txt", "dependency_missing", ["farmers_delight"]),
    ("version_conflict_sodium.txt", "version_conflict", ["sodium", "iris", "fabric-api"]),
    ("version_conflict_minecraft.txt", "version_conflict", ["alexsmobs"]),
    ("version_conflict_optifine.txt", "version_conflict", ["optifine", "embeddium"]),
    ("ecosystem_fabric_on_forge.txt", "ecosystem_incompatible", ["fabric-api", "sodium"]),
    ("ecosystem_forge_on_fabric.txt", "ecosystem_incompatible", ["create"]),
]


@pytest.mark.parametrize("filename,expected_hint,expected_mods", CRASH_FIXTURES)
def test_crash_fixture_parsing(filename, expected_hint, expected_mods):
    """Verify that all crash fixtures parse correctly and extract expected mods."""
    path = FIXTURES_DIR / filename
    assert path.exists(), f"Fixture missing: {filename}"

    result = parse_crash_log(path)
    assert result.raw_text, "Should have raw text"
    assert result.description, "Should have a description"

    for mod in expected_mods:
        assert mod in result.referenced_mods, (
            f"{filename}: expected mod '{mod}' in referenced_mods, "
            f"got {result.referenced_mods}"
        )
