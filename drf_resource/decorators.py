# -*- coding: utf-8 -*-
import inspect
import logging
from typing import Union, Type, Callable, Optional

from drf_resource.registry import resource_registry

logger = logging.getLogger(__name__)


def register_resource(name: str = None, module_path: str = None):
    """
    装饰器：注册资源类
    
    Args:
        name: 自定义注册名称，如果不提供则自动推导
        module_path: 自定义模块路径，如果不提供则自动推导
        
    Usage:
        @register_resource('custom_name')
        class MyResource(Resource):
            pass
            
        @register_resource(name='user_api', module_path='user.api')
        class UserAPIResource(Resource):
            pass
    """
    def decorator(cls: Type):
        if not inspect.isclass(cls):
            raise TypeError("register_resource can only be applied to classes")
        
        # 确定注册名称
        register_name = name
        if register_name is None:
            register_name = resource_registry._infer_resource_name(cls)
        
        # 确定模块路径
        register_module = module_path
        if register_module is None:
            register_module = resource_registry._infer_module_path(cls)
        
        # 注册资源
        resource_registry.register_resource(
            name=register_name,
            resource_class=cls,
            module_path=register_module,
            custom_name=name is not None
        )
        
        # 设置类属性用于标识
        cls.register_name = register_name
        cls.register_module = register_module
        cls.auto_register = False  # 防止元类重复注册
        
        return cls
    
    return decorator


def register_function(name: str = None, module_path: str = None):
    """
    装饰器：注册函数资源
    
    Args:
        name: 自定义注册名称，如果不提供则使用函数名
        module_path: 自定义模块路径，如果不提供则使用函数所在模块
        
    Usage:
        @register_function()
        def get_user_info(user_id):
            return {"id": user_id, "name": "test"}
            
        @register_function(name='custom_func', module_path='user.api')
        def my_function():
            pass
    """
    def decorator(func: Callable):
        if not inspect.isfunction(func):
            raise TypeError("register_function can only be applied to functions")
        
        # 确定注册名称
        register_name = name if name is not None else func.__name__
        
        # 确定模块路径
        register_module = module_path if module_path is not None else func.__module__
        
        # 注册函数
        resource_registry.register_function(
            name=register_name,
            function=func,
            module_path=register_module,
            custom_name=name is not None
        )
        
        # 添加标识属性
        func.register_name = register_name
        func.register_module = register_module
        
        return func
    
    return decorator


def register_as(name: str, module_path: str = None):
    """
    装饰器：指定注册名称注册类或函数
    
    Args:
        name: 注册名称
        module_path: 自定义模块路径，如果不提供则自动推导
        
    Usage:
        @register_as('user_service')
        class UserResource(Resource):
            pass
            
        @register_as('get_data', 'api.data')
        def fetch_data():
            pass
    """
    def decorator(obj: Union[Type, Callable]):
        if inspect.isclass(obj):
            return register_resource(name=name, module_path=module_path)(obj)
        elif inspect.isfunction(obj):
            return register_function(name=name, module_path=module_path)(obj)
        else:
            raise TypeError("register_as can only be applied to classes or functions")
    
    return decorator


def conditional_register(condition: Union[bool, Callable[[], bool]], 
                        name: str = None, module_path: str = None):
    """
    装饰器：条件注册资源
    
    Args:
        condition: 注册条件，可以是布尔值或返回布尔值的函数
        name: 自定义注册名称
        module_path: 自定义模块路径
        
    Usage:
        @conditional_register(settings.DEBUG)
        class DebugResource(Resource):
            pass
            
        @conditional_register(lambda: os.getenv('ENABLE_FEATURE') == 'true')
        class FeatureResource(Resource):
            pass
    """
    def decorator(obj: Union[Type, Callable]):
        # 评估条件
        should_register = condition() if callable(condition) else condition
        
        if should_register:
            if inspect.isclass(obj):
                return register_resource(name=name, module_path=module_path)(obj)
            elif inspect.isfunction(obj):
                return register_function(name=name, module_path=module_path)(obj)
        
        # 如果不需要注册，设置标识避免元类自动注册
        if inspect.isclass(obj):
            obj.auto_register = False
        
        return obj
    
    return decorator


def batch_register(*resources):
    """
    函数：批量注册资源
    
    Args:
        *resources: 资源类或函数的列表
        
    Usage:
        batch_register(UserResource, OrderResource, get_data_func)
    """
    for resource in resources:
        if inspect.isclass(resource):
            # 检查是否已经有注册信息
            if not hasattr(resource, 'register_name'):
                register_name = resource_registry._infer_resource_name(resource)
                register_module = resource_registry._infer_module_path(resource)
                
                resource_registry.register_resource(
                    name=register_name,
                    resource_class=resource,
                    module_path=register_module,
                    custom_name=False
                )
                
                resource.register_name = register_name
                resource.register_module = register_module
                resource.auto_register = False
                
        elif inspect.isfunction(resource):
            if not hasattr(resource, 'register_name'):
                register_name = resource.__name__
                register_module = resource.__module__
                
                resource_registry.register_function(
                    name=register_name,
                    function=resource,
                    module_path=register_module,
                    custom_name=False
                )
                
                resource.register_name = register_name
                resource.register_module = register_module


def unregister_resource(name: str, module_path: str):
    """
    函数：注销资源
    
    Args:
        name: 资源名称
        module_path: 模块路径
        
    Returns:
        bool: 是否成功注销
        
    Usage:
        unregister_resource('user_service', 'user.api')
    """
    return resource_registry.unregister(name, module_path)


def list_registered_resources(module_path: str = None):
    """
    函数：列出已注册的资源
    
    Args:
        module_path: 可选的模块路径过滤
        
    Returns:
        Dict: 资源信息字典
        
    Usage:
        all_resources = list_registered_resources()
        user_resources = list_registered_resources('user.api')
    """
    return resource_registry.list_resources(module_path)


def get_resource_info(name: str, module_path: str):
    """
    函数：获取资源信息
    
    Args:
        name: 资源名称
        module_path: 模块路径
        
    Returns:
        Optional[Dict]: 资源信息或 None
        
    Usage:
        info = get_resource_info('user_service', 'user.api')
    """
    return resource_registry.get_resource(name, module_path)


# 为了向后兼容，提供便捷的导入
__all__ = [
    'register_resource',
    'register_function', 
    'register_as',
    'conditional_register',
    'batch_register',
    'unregister_resource',
    'list_registered_resources',
    'get_resource_info'
]