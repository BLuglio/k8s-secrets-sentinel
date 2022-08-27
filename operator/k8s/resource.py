from abc import ABC, abstractmethod

class ResourceHandler(ABC):
    @abstractmethod
    def create(self, name, data={}, namespace='default'):
        pass

    @abstractmethod
    def update(self, name, data={}, namespace='default'):
        pass

    @abstractmethod
    def delete(self, name, namespace='default'):
        pass

    @abstractmethod
    def get(self, name, namespace='default'):
        pass

    @abstractmethod
    def get_all(self, namespace=None):
        pass

    @abstractmethod
    def exists(self, name) -> bool:
        pass