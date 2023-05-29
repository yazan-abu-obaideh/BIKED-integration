from concurrent.futures import ThreadPoolExecutor

import requests


def grab_and_save_bike(bike_index):
    grabbed_bike_file = requests.get(f"http://bcd.bikecad.ca/{bike_index}.bcad")
    print(f"Grabbed bike {bike_index}")
    with open(f"bikecad_files_gen/{bike_index}.bcad", "w") as file:
        file.write(grabbed_bike_file.text)
    print(f"Saved bike {bike_index}")


def get_all_bikes():
    with open("Every BCAD file in archive.txt", "r") as file:
        return set([file.strip() for file in file.readlines()[4000:]])


with ThreadPoolExecutor(max_workers=5) as executor:
    for bike in get_all_bikes():
        executor.submit(grab_and_save_bike, bike)
