from abc import ABC, abstractmethod

class AccommodationCostProvider(ABC):

    @abstractmethod
    def get_cost_profile(
        self,
        city: str,
        country: str,         
    ) -> dict:
        pass




# print(get_cost_profile("Paris", "France"))