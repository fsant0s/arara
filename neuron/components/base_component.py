from abc import ABC, abstractmethod
from typing import Any

class BaseComponent(ABC):
    """
    Base abstract class for components that define an execution process.
    Derived classes must implement the 'execute' method.
    """

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Abstract method that must be implemented by any subclass.
        Defines the execution process for the component.

        :param args: Positional arguments for the execution process.
        :param kwargs: Keyword arguments for the execution process.
        :return: Result of the execution process.
        """
        pass
