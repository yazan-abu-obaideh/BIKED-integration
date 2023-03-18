import requests
import os
from time import sleep


def grab_and_save_bike(bike_index):
    grabbed_bike_file = requests.get(f"http://bcd.bikecad.ca/{bike_index}.bcad")
    print(f"Grabbed bike {bike_index}")
    with open(f"bikecad_files_gen/{bike_index}.bcad", "w") as file:
        file.write(grabbed_bike_file.text)
    print(f"Saved bike {bike_index}")


def get_all_saved_bikes():
    return set([file.split('.')[0] for file in os.listdir("bikecad_files_gen")])


def get_all_bikes():
    with open("Every BCAD file in archive.txt", "r") as file:
        return set([file.strip() for file in file.readlines()[4000:]])


while get_all_bikes() != get_all_saved_bikes():
    for bike in get_all_bikes():
        if bike not in get_all_saved_bikes():
            grab_and_save_bike(bike)
            sleep(0.1)
