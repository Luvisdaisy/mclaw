import json
import logging
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger(__name__)

MODRINTH_API_BASE = "https://api.modrinth.com/v2"
CURSEFORGE_API_BASE = "https://api.curseforge.com/v1"


@dataclass
class ModInfo:
    name: str = ""
    slug: str = ""
    mod_id: str = ""
    versions: list[str] = field(default_factory=list)
    loaders: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    source: str = ""  # "modrinth" or "curseforge"
    found: bool = False


@dataclass
class ModSearchResult:
    slug: str
    mod_id: str
    title: str
    description: str
    source: str


async def search_modrinth(query: str) -> list[ModSearchResult]:
    """Search for mods on Modrinth by name, ID, or slug."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{MODRINTH_API_BASE}/search",
                params={"query": query, "limit": 10},
                headers={"User-Agent": "mclaw/0.1.0"},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                ModSearchResult(
                    slug=hit.get("slug", ""),
                    mod_id=hit.get("project_id", ""),
                    title=hit.get("title", ""),
                    description=hit.get("description", ""),
                    source="modrinth",
                )
                for hit in data.get("hits", [])
            ]
        except Exception as e:
            logger.warning("Modrinth search failed: %s", e)
            return []


async def get_mod_info_modrinth(slug: str) -> ModInfo | None:
    """Get detailed mod information from Modrinth."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{MODRINTH_API_BASE}/project/{slug}",
                headers={"User-Agent": "mclaw/0.1.0"},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()

            versions_resp = await client.get(
                f"{MODRINTH_API_BASE}/project/{slug}/version",
                headers={"User-Agent": "mclaw/0.1.0"},
                timeout=15.0,
            )
            versions_resp.raise_for_status()
            versions_data = versions_resp.json()

            game_versions: set[str] = set()
            loaders: set[str] = set()
            for v in versions_data:
                game_versions.update(v.get("game_versions", []))
                loaders.update(v.get("loaders", []))

            return ModInfo(
                name=data.get("title", ""),
                slug=slug,
                mod_id=data.get("id", ""),
                versions=sorted(game_versions),
                loaders=sorted(loaders),
                dependencies=[],
                source="modrinth",
                found=True,
            )
        except Exception as e:
            logger.warning("Modrinth project lookup failed for %s: %s", slug, e)
            return None


async def search_curseforge(query: str, api_key: str = "") -> list[ModSearchResult]:
    """Search for mods on CurseForge (requires API key)."""
    if not api_key:
        return []
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"{CURSEFORGE_API_BASE}/mods/search",
                params={"gameId": 432, "searchFilter": query, "pageSize": 10},
                headers={"x-api-key": api_key},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return [
                ModSearchResult(
                    slug=str(mod.get("id", "")),
                    mod_id=str(mod.get("id", "")),
                    title=mod.get("name", ""),
                    description=mod.get("summary", ""),
                    source="curseforge",
                )
                for mod in data.get("data", [])
            ]
        except Exception as e:
            logger.warning("CurseForge search failed: %s", e)
            return []


async def query_mod(
    query: str,
    curseforge_api_key: str = "",
) -> ModInfo:
    """Query mod info from Modrinth (primary) or CurseForge (fallback)."""
    # Try Modrinth search first
    results = await search_modrinth(query)
    if results:
        info = await get_mod_info_modrinth(results[0].slug)
        if info:
            return info

    # Fallback to CurseForge
    cf_results = await search_curseforge(query, curseforge_api_key)
    if cf_results:
        return ModInfo(
            name=cf_results[0].title,
            slug=cf_results[0].slug,
            mod_id=cf_results[0].mod_id,
            source="curseforge",
            found=True,
        )

    return ModInfo(found=False)
