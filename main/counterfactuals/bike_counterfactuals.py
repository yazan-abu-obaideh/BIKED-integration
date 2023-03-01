import pandas as pd
from dice_ml.constants import ModelTypes

from main.evaluation.evaluation_service import load_pickled_predictor
import main.processing.pandas_utility as pd_util
from main.load_data import load_augmented_framed_dataset
from main.evaluation.default_processor_settings import DefaultProcessorSettings
import dice_ml

processor_settings = DefaultProcessorSettings()

sample_input = {'Material=Steel': -1.2089779626768866, 'Material=Aluminum': -0.46507861303022335,
             'Material=Titanium': 1.8379997074342262, 'SSB_Include': 1.0581845284004865,
             'CSB_Include': -0.9323228669601348, 'CS Length': -0.4947762070020683,
             'BB Drop': 0.19327064177679704, 'Stack': -0.036955840782382385,
             'SS E': -0.4348758585162575, 'ST Angle': 1.203226228166099, 'BB OD': -0.14197615979296274,
             'TT OD': -0.5711431568166616, 'HT OD': -0.879229453202825, 'DT OD': -0.8924125880651749,
             'CS OD': -0.6971543225296617, 'SS OD': -0.7226114906751929, 'ST OD': -0.8962254490159303,
             'CS F': 0.1664798679079193, 'HT LX': -0.5559202673887266, 'ST UX': -0.5875970924732736,
             'HT UX': -0.1666775498399638, 'HT Angle': 1.5120924379123033,
             'HT Length': 0.7032710935570091, 'ST Length': 0.980667290296069,
             'BB Length': -0.25473226064604454, 'Dropout Offset': -0.0325700226355687,
             'SSB OD': -2.1985552817712657, 'CSB OD': -0.279547847307574,
             'SSB Offset': -0.09050848378506038, 'CSB Offset': 0.5823537937924539,
             'SS Z': -0.06959536571235439, 'SS Thickness': 0.5180142556590571,
             'CS Thickness': 1.7994950500929077, 'TT Thickness': 0.2855204217004274,
             'BB Thickness': -0.11934492802927218, 'HT Thickness': -0.7465363724789722,
             'ST Thickness': -0.5700521782698762, 'DT Thickness': -1.0553146425778421,
             'DT Length': 0.10253602811555089}
predictor = load_pickled_predictor()
x, y, x_scaler, y_scaler = load_augmented_framed_dataset()
class ModelWrapper:
    def __init__(self):
        pass
    def predict(self, _x):
        return predictor.predict(_x).rename(
            columns=processor_settings.get_label_replacements()).drop(
            columns=y.columns.difference(["Model Mass Magnitude"])
        )


wrapper = ModelWrapper()
wrapper.predict(x)

dice_model = dice_ml.Model(model=ModelWrapper(), backend="sklearn", model_type=ModelTypes.Regressor)
data_for_dice = pd.concat([x, y["Model Mass Magnitude"]], axis=1)
print(data_for_dice.columns.values)
dice_data = dice_ml.Data(dataframe=data_for_dice, continuous_features=list(x.columns.values),
                         outcome_name="Model Mass Magnitude")
explainer = dice_ml.Dice(dice_data, dice_model, method="random")
e1 = explainer.generate_counterfactuals(x[0:1], total_CFs=5, desired_range=[0, 1])
e1.visualize_as_dataframe(show_only_changes=True)
e1.visualize_as_dataframe(show_only_changes=False)
