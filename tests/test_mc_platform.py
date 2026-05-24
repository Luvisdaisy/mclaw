import json
import tempfile
from pathlib import Path

import pytest

from mclaw.mc_platform.compatibility import check_compatibility
from mclaw.mc_platform.crash_parser import ParsedCrash, parse_crash_text
from mclaw.mc_platform.mod_cache import ModCache

# ── Sample crash log fixtures ──

FORGE_DEPENDENCY_CRASH = """---- Minecraft Crash Report ----
// Don't be sad, have a hug! <3

Time: 2024-01-15 14:32:10
Description: Mod create requires mod flywheel 0.6.10 or above
    Currently installed: flywheel 0.6.8

java.lang.NoClassDefFoundError: com/simibubi/create/foundation/block/connected/ConnectedBlocks
    at com.simibubi.create.Create.init(Create.java:120)
    at net.minecraftforge.fml.javafmlmod.FMLJavaModLanguageProvider.lambda$loadParty$4(FMLJavaModLanguageProvider.java:95)
    ... 20 more

-- MOD forge --
-- MOD create --
-- MOD flywheel --
-- MOD jei --
"""

FABRIC_VERSION_CONFLICT = """---- Minecraft Crash Report ----
// Why did you do that?

Description: Mod sodium 0.5.8 requires fabric-api 0.92.0 or above
    Currently installed: fabric-api 0.90.0

java.lang.RuntimeException: Version conflict detected for mod sodium
    at net.fabricmc.loader.impl.game.GameProvider.launch(GameProvider.java:87)
    at net.fabricmc.loader.impl.FabricLoaderImpl.load(FabricLoaderImpl.java:200)
    ... 15 more

Fabric mods: sodium, iris, fabric-api
"""

RAW_EXCEPTION_CRASH = """---- Minecraft Crash Report ----
// This doesn't seem right

Description: Exception in server tick loop

java.lang.ClassCastException: net.minecraft.world.item.ArmorItem cannot be cast to net.fabric.api.rendering.Renderable
    at net.fabricmc.api.rendering.ArmorRenderer.render(ArmorRenderer.java:45)
    at net.minecraft.client.renderer.entity.EntityRenderer.lambda$0(EntityRenderer.java:230)
    ... 12 more
"""

MALFORMED_TEXT = "This is not a valid crash report\nJust some random text\nNothing to parse here"


class TestCrashParser:

    def test_parse_forge_crash(self):
        result = parse_crash_text(FORGE_DEPENDENCY_CRASH)
        assert result.crash_type == "forge"
        assert "create" in result.referenced_mods
        assert "flywheel" in result.referenced_mods
        assert "NoClassDefFoundError" in result.raw_text

    def test_parse_fabric_crash(self):
        result = parse_crash_text(FABRIC_VERSION_CONFLICT)
        assert result.crash_type == "fabric"
        assert "sodium" in result.referenced_mods
        assert len(result.stack_trace) > 0

    def test_extracts_description(self):
        result = parse_crash_text(FORGE_DEPENDENCY_CRASH)
        assert "create" in result.description.lower()
        assert "flywheel" in result.description.lower()

    def test_extracts_stack_trace(self):
        result = parse_crash_text(FORGE_DEPENDENCY_CRASH)
        trace_str = "\n".join(result.stack_trace)
        assert "NoClassDefFoundError" in result.raw_text

    def test_handles_malformed_input(self):
        result = parse_crash_text(MALFORMED_TEXT)
        assert isinstance(result, ParsedCrash)
        assert result.crash_type == ""

    def test_empty_text(self):
        result = parse_crash_text("")
        assert isinstance(result, ParsedCrash)
        assert result.referenced_mods == []


class TestCompatibility:

    def test_compatible_mod(self):
        result = check_compatibility(
            mod_name="create",
            mod_loaders=["forge", "neoforge"],
            mod_versions=["1.20.1", "1.19.2"],
            target_mc_version="1.20.1",
            target_loader="forge",
        )
        assert result.compatible

    def test_loader_mismatch(self):
        result = check_compatibility(
            mod_name="sodium",
            mod_loaders=["fabric", "quilt"],
            mod_versions=["1.20.1"],
            target_mc_version="1.20.1",
            target_loader="forge",
        )
        assert not result.compatible
        assert "loader mismatch" in result.reason.lower()

    def test_version_mismatch(self):
        result = check_compatibility(
            mod_name="create",
            mod_loaders=["forge"],
            mod_versions=["1.19.2"],
            target_mc_version="1.20.1",
            target_loader="forge",
        )
        assert not result.compatible
        assert "version mismatch" in result.reason.lower()


class TestModCache:

    def test_put_and_get(self):
        cache = ModCache(ttl=3600)
        cache.clear()
        cache.put("modrinth", "create", {"name": "Create", "version": "0.5.1"})
        result = cache.get("modrinth", "create")
        assert result is not None
        assert result["name"] == "Create"

    def test_cache_miss(self):
        cache = ModCache(ttl=3600)
        cache.clear()
        result = cache.get("modrinth", "nonexistent")
        assert result is None

    def test_force_refresh(self):
        cache = ModCache(ttl=3600)
        cache.clear()
        cache.put("modrinth", "create", {"name": "Create"})
        result = cache.get("modrinth", "create", force_refresh=True)
        assert result is None

    def test_ttl_expiry(self):
        cache = ModCache(ttl=0)  # ttl of 0 means always stale
        cache.clear()
        cache.put("modrinth", "create", {"name": "Create"})
        result = cache.get("modrinth", "create")
        assert result is None

    def test_cache_age(self):
        cache = ModCache(ttl=999999)
        cache.clear()
        cache.put("modrinth", "create", {"name": "Create"})
        age = cache.get_cache_age("modrinth", "create")
        assert age is not None
        assert age >= 0.0

    def test_cache_age_miss(self):
        cache = ModCache(ttl=3600)
        cache.clear()
        age = cache.get_cache_age("modrinth", "nonexistent")
        assert age is None

    def test_update_existing(self):
        cache = ModCache(ttl=999999)
        cache.clear()
        cache.put("modrinth", "create", {"name": "Create", "version": "0.5.1"})
        cache.put("modrinth", "create", {"name": "Create", "version": "0.5.2"})
        result = cache.get("modrinth", "create")
        assert result["version"] == "0.5.2"
