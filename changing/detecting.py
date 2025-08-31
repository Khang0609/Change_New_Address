import os
from utils import convert_to_filename
import json

def get_all_file_paths(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def run(path, data_of_2025):
    with open(path, "r", encoding="utf-8") as f:
        list_of_addresses = f.readlines()

    file_paths_2025 = get_all_file_paths(data_of_2025)

    new_address = []

    for address in list_of_addresses:
        address_elements = address.split(",")
        street = address_elements[0].strip()
        ward = address_elements[1].strip()
        district = address_elements[2].strip()
        province = address_elements[3].strip()
        file_of_2025 = None
        for file_path in file_paths_2025:
            with open(file_path, "r", encoding="utf-8") as f:
                file = json.load(f)
            old_province_list = file["old_province"]
            if province in old_province_list:
                file_of_2025 = file
                break
        if file_of_2025 == None:
            print(f"Không tìm được tỉnh mới cho tỉnh {province} !")
            return
        ward_ = None
        checking_ward = ward.title()
        for new_ward, old_ward_list in file_of_2025["ward"].items():
            if checking_ward in old_ward_list:
                ward_ = new_ward
                break
        if ward_ == None:
            print(f"Không tìm được xã mới cho {ward}")
            return
        new_address.append(f"{street}, {ward_}, {file_of_2025["name"]}")

    for index in range(len(new_address)):
        print(f"Địa chỉ mới là: {new_address[index]}")
        print(f"Địa chỉ cũ là: {list_of_addresses[index]}")