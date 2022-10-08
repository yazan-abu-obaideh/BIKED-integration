default_values = {'Material=Steel': 0, 'Material=Aluminum': 0, 'Material=Titanium': 0, 'SSB_Include': 0,
                  'CSB_Include': 0, 'CS Length': 0, 'BB Drop': 0, 'Stack': 0, 'SS E': 0,
                  'ST Angle': 0, 'BB OD': 0, 'TT OD': 0, 'HT OD': 0, 'DT OD': 0, 'CS OD': 0,
                  'SS OD': 0, 'ST OD': 0, 'CS F': 0, 'HT LX': 0, 'ST UX': 0,
                  'HT UX': 0, 'HT Angle': 0, 'HT Length': 0, 'ST Length': 0, 'BB Length': 0,
                  'Dropout Offset': 0, 'SSB OD': 0, 'CSB OD': 0, 'SSB Offset': 0,
                  'CSB Offset': 0, 'SS Z': 0, 'SS Thickness': 0, 'CS Thickness': 0,
                  'TT Thickness': 0, 'BB Thickness': 2, 'HT Thickness': 2, 'ST Thickness': 0,
                  'DT Thickness': 0, 'DT Length': 0}
warnings_map = {}
keys_whose_presence_indicates_their_value = ["CSB_Include", "SSB_Include"]
raise_exception_if_missing = []
special_behavior = {
    "Material": "",
}
