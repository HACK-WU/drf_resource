
import abc

from core.statistics.metric import Metric


class Storage(metaclass=abc.ABCMeta):
    """
    指标存储
    """

    def get(self, metric_names: list[str]) -> list[Metric]:
        raise NotImplementedError

    def put(self, metrics: list[Metric]):
        raise NotImplementedError
