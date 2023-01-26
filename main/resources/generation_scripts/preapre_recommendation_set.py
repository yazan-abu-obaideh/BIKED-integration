import pandas as pd

maybe = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2", "Wheel width rear",
         "Wheel width front", "Head tube type", "BB length", "Head tube diameter", "Wheel cut", "BB diameter",
         "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1", "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1",
         "SEATSTAYbrdgshift", "bottle SEATTUBE0 show", "bottle DOWNTUBE0 show", "Front Fender include",
         "Rear Fender include", "Display RACK"]
yes = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield", "Head angle",
       "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style", "BSD front",
       "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS", "Handlebar style",
       "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN", "Number of cogs",
       "Number of chainrings"]

data = pd.read_csv("../large/BIKED_raw.csv", index_col=0)
data.drop(columns=data.columns.difference(yes + maybe), inplace=True)
data.to_csv("BIKED_recommend.csv")
