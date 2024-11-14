import re


def determine_model_type(material_name):
    # Regular expressions for "prefabricated" and its variations
    prefabricated_pattern = r"сборн\w*"
    # Regular expressions for "monolithic" and its variations
    monolithic_pattern = r"монолит\w*"

    # Check if the material name contains the word "сборный" (prefabricated)
    if re.search(prefabricated_pattern, material_name, re.IGNORECASE):
        return "сборный"
    # Check if the material name contains the word "монолитный" (monolithic)
    elif re.search(monolithic_pattern, material_name, re.IGNORECASE):
        return "монолитный"
    # If none of the keywords are found, assume the material is monolithic
    else:
        return "монолитный"


# Example usage:
materials = [
    "Лестничный марш сборный",
    "Лестничный марш цокольный",
    "Приямок монолитный",
    "Свая забивная составная",
    "Плита перекрытия монолитная",
    "Плита покрытия монолитная",
    "Фундаментная плита",
    "Стена монолитная",
    "Стена цокольная",
    "Балка монолитная",
    "Балка цокольная",
    "Прямой пролет рампы/пандуса",
    "Колонна цокольная",
    "Колонна монолитная",
    "Парапет монолитный",
]

for material in materials:
    print(f"{determine_model_type(material)}")
