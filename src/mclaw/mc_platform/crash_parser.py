import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParsedCrash:
    crash_type: str = ""
    description: str = ""
    stack_trace: list[str] = field(default_factory=list)
    referenced_mods: list[str] = field(default_factory=list)
    error_message: str = ""
    raw_text: str = ""


# Patterns for mod references in crash logs
MOD_REF_PATTERNS = [
    re.compile(r"mods/([a-zA-Z0-9_-]+)[-/]", re.IGNORECASE),
    re.compile(r"McLib|Mod File:.*?([a-zA-Z0-9_-]+)\.jar", re.IGNORECASE),
    re.compile(r"at [a-z0-9_.]+\.[a-z0-9_.]+\(([a-zA-Z0-9_]+)\).*", re.IGNORECASE),
]

FORGE_PATTERN = re.compile(r"-- MOD [a-z]+ --", re.IGNORECASE)
FABRIC_PATTERN = re.compile(r"Fabric", re.IGNORECASE)
FORGE_MOD_LINE = re.compile(r"-- MOD ([a-z0-9_-]+)", re.IGNORECASE)
FABRIC_MOD_LINE = re.compile(r"Fabric mods?\s*:\s*(.+)", re.IGNORECASE)
CRASH_TYPE_PATTERN = re.compile(r"Description:\s*(.+)", re.IGNORECASE)
ERROR_MSG_PATTERN = re.compile(r"(?:java\.\w+\.\w+Error|java\.\w+\.\w+Exception)[:\s]*(.*?)(?:\n|$)")
MOD_LIST_PATTERN = re.compile(r"Mod (?:Name|Id):\s*['\"]?([a-zA-Z0-9_ -]+)['\"]?", re.IGNORECASE)


def parse_crash_log(path: str | Path) -> ParsedCrash:
    """Parse a Minecraft crash log file into structured data."""
    filepath = Path(path)
    raw_text = filepath.read_text(encoding="utf-8", errors="replace")
    return parse_crash_text(raw_text)


def parse_crash_text(text: str) -> ParsedCrash:
    """Parse crash log text into structured data."""
    result = ParsedCrash(raw_text=text)

    crash_type_match = CRASH_TYPE_PATTERN.search(text)
    if crash_type_match:
        result.description = crash_type_match.group(1).strip()

    error_match = ERROR_MSG_PATTERN.search(text)
    if error_match:
        result.error_message = error_match.group(1).strip()

    lines = text.split("\n")
    in_stack = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("at ") or stripped.startswith("..."):
            in_stack = True
            result.stack_trace.append(stripped)
        elif in_stack and not stripped:
            in_stack = False

    if FORGE_PATTERN.search(text):
        result.crash_type = "forge"
    elif FABRIC_PATTERN.search(text):
        result.crash_type = "fabric"

    seen_mods: set[str] = set()
    for pattern in MOD_REF_PATTERNS:
        for match in pattern.finditer(text):
            mod_name = match.group(1).strip()
            if mod_name and mod_name.lower() not in ("net", "com", "org", "java", "io"):
                seen_mods.add(mod_name.lower())

    for match in MOD_LIST_PATTERN.finditer(text):
        mod_name = match.group(1).strip()
        if mod_name and len(mod_name) > 1:
            seen_mods.add(mod_name.lower())

    for match in FABRIC_MOD_LINE.finditer(text):
        for mod in match.group(1).split(","):
            mod_name = mod.strip().lower().split()[0]
            if mod_name:
                seen_mods.add(mod_name)

    for match in FORGE_MOD_LINE.finditer(text):
        mod_name = match.group(1).strip().lower()
        if mod_name:
            seen_mods.add(mod_name)

    result.referenced_mods = sorted(seen_mods)
    return result
