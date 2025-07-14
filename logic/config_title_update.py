import re

known_classes = {
    "Crâ", "Ecaflip", "Enutrof",
    "Feca", "Féca", "Iop", "Osamodas",
    "Pandawa", "Huppermage", "Sacrieur",
    "Sram", "Steamer", "Xelor", "Xélor",
    "Zobal", "Roublard", "Ouginak",
    "Eniripsa", "Sadida", "Forgelance", "Eliotrope"
}

def extract_character_name(title):
    if not title:
        return None, None, None

    # Case 1: Full title with character, class, and version
    # e.g., "MyChar - Iop - 2.71.3.19 - Release"
    match = re.match(
        r"^(.*?)\s*-\s*([A-Za-zéÉâêîôûàèùëïüç]+)\s*-\s*(\d+\.\d+\.\d+\.\d+)\s*-\s*Release$",
        title, re.IGNORECASE
    )
    if match:
        char_name, char_class, version = match.groups()
        if char_class.capitalize() in known_classes:
            return char_name.strip(), char_class.capitalize(), version

    # Case 2: Title with only "Dofus" and version
    # e.g., "Dofus 2.71.3.19 - Release" or "Dofus 2.71.3.19"
    match = re.match(r"^Dofus\s+(\d+\.\d+\.\d+\.\d+)(?:\s*-\s*Release)?$", title, re.IGNORECASE)
    if match:
        version = match.group(1)
        return None, None, version

    # Case 3: Title contains "Dofus" but no version info (e.g. loading screen)
    if "dofus" in title.lower():
        return None, None, "Unknown"

    return None, None, None