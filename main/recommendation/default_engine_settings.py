from main.recommendation.similarity_engine_settings import EngineSettings


class DefaultBikeSettings(EngineSettings):
    light = ["Head tube upper extension2", "Seat tube extension2", "Head tube lower extension2",
             "Wheel width rear", "Wheel width front", "Head tube type", "BB length", "Head tube diameter",
             "Wheel cut", "BB diameter", "Seat tube diameter", "Top tube type", "CHAINSTAYbrdgdia1",
             "CHAINSTAYbrdgshift", "SEATSTAYbrdgdia1", "SEATSTAYbrdgshift", "bottle SEATTUBE0 show",
             "bottle DOWNTUBE0 show", "Front Fender include", "Rear Fender include", "Display RACK"]
    heavy = ["BB textfield", "Seat tube length", "Stack", "Seat angle", "CS textfield", "FCD textfield",
           "Head angle", "Saddle height", "Head tube length textfield", "ERD rear", "Dropout spacing style",
           "BSD front", "ERD front", "BSD rear", "Fork type", "Stem kind", "Display AEROBARS",
           "Handlebar style", "CHAINSTAYbrdgCheck", "SEATSTAYbrdgCheck", "Display WATERBOTTLES", "BELTorCHAIN",
           "Number of cogs", "Number of chainrings"]

    def max_n(self) -> int:
        return 10

    def include(self) -> list:
        return self.light + self.heavy

    def weights(self) -> dict:
        light_ = {key: 1 for key in self.light}
        heavy_ = {key: 3 for key in self.heavy}
        weights = light_
        weights.update(heavy_)
        return weights
