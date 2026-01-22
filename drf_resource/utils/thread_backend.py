"""
线程后端工具模块

提供支持线程局部变量继承的线程池和线程类，用于多线程环境中
安全地传递用户信息、时区、语言等上下文信息。
"""

import logging
from contextlib import contextmanager
from functools import partial
from multiprocessing.pool import ThreadPool as _ThreadPool
from threading import Thread

from django import db
from django.utils import timezone, translation
from drf_resource.utils.local import local

logger = logging.getLogger(__name__)

# 尝试导入 OpenTelemetry，如果不可用则使用空实现
try:
    from opentelemetry.context import attach, get_current
except ImportError:

    def get_current():
        return None

    def attach(context):
        pass


@contextmanager
def ignored(*exceptions, log_exception=True):
    """
    忽略指定异常的上下文管理器

    :param exceptions: 要忽略的异常类型
    :param log_exception: 是否记录异常日志
    """
    try:
        yield
    except exceptions:
        if log_exception:
            import traceback

            logger.warning(traceback.format_exc())


class InheritParentThread(Thread):
    """
    支持继承父线程局部变量的线程类

    在线程启动时自动同步父线程的：
    - 线程局部变量（local 对象中的所有属性）
    - 时区设置
    - 语言设置
    - OpenTelemetry 追踪上下文
    """

    def __init__(self, *args, **kwargs):
        self.register()
        super().__init__(*args, **kwargs)

    def register(self):
        """注册需要继承的父线程数据"""
        # 同步 local 对象中的所有数据
        self.inherit_data = []
        for item in local:
            self.inherit_data.append(item)

        # 同步时区/语言
        self.timezone = timezone.get_current_timezone().zone
        self.language = translation.get_language()
        self.trace_context = get_current()

    def sync(self):
        """将父线程数据同步到当前线程"""
        for sync_item in self.inherit_data:
            setattr(local, sync_item[0], sync_item[1])
        timezone.activate(self.timezone)
        translation.activate(self.language)
        with ignored(Exception):
            attach(self.trace_context)

    def unsync(self):
        """
        清理当前线程的局部变量

        线程结束时需要清理所有线程相关变量，
        同时关闭数据库连接以防止连接泄露。
        """
        # 新的线程会往 local 再写一些数据
        # 线程结束的时候，需要把所有线程相关的变量都清空
        for item in local:
            delattr(local, item[0])

        # db._connections 也是线程变量，所以在线程结束的时候需要主动释放
        db.connections.close_all()

    def run(self):
        self.sync()
        try:
            super().run()
        except Exception as e:
            logger.exception(e)

        self.unsync()


def run_threads(th_list: list[InheritParentThread]):
    """
    批量运行线程并等待完成

    :param th_list: InheritParentThread 实例列表
    """
    [th.start() for th in th_list]
    [th.join() for th in th_list]


def run_func_with_local(items, tz, lang, func, trace_context, *args, **kwargs):
    """
    在继承父线程上下文的环境中执行函数

    :param items: 线程局部变量列表 [(key, value), ...]
    :param tz: 时区
    :param lang: 语言
    :param func: 待执行函数
    :param trace_context: OpenTelemetry 追踪上下文
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return: 函数返回值
    """
    # 同步 local 数据
    for item in items:
        setattr(local, item[0], item[1])

    # 设置时区及语言
    timezone.activate(tz)
    translation.activate(lang)
    with ignored(Exception):
        attach(trace_context)
    try:
        data = func(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        # 关闭 db 连接
        db.connections.close_all()

        # 清理 local 数据
        for item in local:
            delattr(local, item[0])

    return data


class ThreadPool(_ThreadPool):
    """
    支持线程局部变量继承的线程池

    对标准库的 ThreadPool 进行包装，使得在子线程中执行的任务
    能够自动继承父线程的上下文信息（用户名、时区、语言、追踪上下文等）。
    """

    @staticmethod
    def get_func_with_local(func):
        """
        包装函数以支持线程局部变量继承

        :param func: 原始函数
        :return: 包装后的函数
        """
        tz = timezone.get_current_timezone().zone
        lang = translation.get_language()
        trace_context = get_current()
        items = [item for item in local]
        return partial(run_func_with_local, items, tz, lang, func, trace_context)

    def map_ignore_exception(self, func, iterable, return_exception=False):
        """
        忽略错误版的 map

        执行过程中如果某个任务发生异常，不会中断其他任务的执行，
        而是记录异常日志后继续处理。

        :param func: 要执行的函数
        :param iterable: 参数可迭代对象
        :param return_exception: 是否将异常作为结果返回
        :return: 结果列表
        """
        futures = []
        for params in iterable:
            if not isinstance(params, tuple | list):
                params = (params,)
            futures.append(self.apply_async(func, args=params))

        results = []
        for future in futures:
            try:
                results.append(future.get())
            except Exception as e:
                if return_exception:
                    results.append(e)
                logger.exception(e)

        return results

    def map_async(self, func, iterable, chunksize=None, callback=None):
        return super().map_async(
            self.get_func_with_local(func),
            iterable,
            chunksize=chunksize,
            callback=callback,
        )

    def apply_async(self, func, args=(), kwds=None, callback=None):
        kwds = kwds or {}
        return super().apply_async(
            self.get_func_with_local(func), args=args, kwds=kwds, callback=callback
        )

    def imap(self, func, iterable, chunksize=1):
        return super().imap(self.get_func_with_local(func), iterable, chunksize)

    def imap_unordered(self, func, iterable, chunksize=1):
        return super().imap_unordered(
            self.get_func_with_local(func), iterable, chunksize=chunksize
        )


if __name__ == "__main__":
    InheritParentThread().start()
