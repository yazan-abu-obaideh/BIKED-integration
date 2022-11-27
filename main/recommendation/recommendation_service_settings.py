from abc import abstractmethod

from typing import List


class RecommendationSettings:

    @abstractmethod
    def max_n(self) -> int:
        pass

    @abstractmethod
    def weights(self) -> List[float]:
        pass
