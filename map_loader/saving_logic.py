import re

def saving_to_dict(name: str,before_merger: str, saving_place: dict):
    if re.search(r"Giữ nguyên, không sáp nhập", before_merger):
        saving_place[name] = {}
    else:
        list_of_provinces = re.split(r"\s*và\s*|,\s*", before_merger)
        saving_place[name] = {province.strip(): {} for province in list_of_provinces if province.strip()}

        