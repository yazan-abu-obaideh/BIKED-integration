from abc import abstractmethod


class RecommendationSettings:

    @abstractmethod
    def max_n(self) -> int:
        pass
