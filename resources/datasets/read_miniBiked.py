import pandas as pd

data = pd.read_csv('miniBIKED measurements - General Params.csv')
_list = list(data['Name in BIKED'].values[:45])

with open('new.py', "w") as file:
    file.write(f"""{_list=}""")

