from abc import ABC, ABCMeta, abstractmethod


class BaseEventPluginResource(metaclass=ABCMeta):
    @abstractmethod
    def perform_request(self):
        pass  # 抽象方法，没有具体实现


# ✅ 正确做法：子类实现抽象方法
class MyEventPluginResource(BaseEventPluginResource):
    pass


# 现在可以实例化了！
obj = MyEventPluginResource()  # ✔️ 不再报错
obj.perform_request()  # 输出: 具体执行请求的逻辑
