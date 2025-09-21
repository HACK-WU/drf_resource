# -*- coding: utf-8 -*-
"""
DRF Resource 新自动注册机制演示

本文件展示了新的基于元类和装饰器的自动注册机制的使用方式。
新机制完全替代了旧的文件扫描注册机制，提供了更高的性能和更好的灵活性。
"""

from drf_resource import (
    Resource,
    register_resource,
    register_function,
    register_as,
    conditional_register,
    batch_register,
    resource_registry,
)


# ============================================================================
# 1. 元类自动注册（推荐方式）
# ============================================================================

class UserResource(Resource):
    """
    用户资源类 - 通过元类自动注册
    
    注册名称：user（自动推导：UserResource -> user）
    模块路径：examples.new_registration_demo（自动推导）
    """
    
    def perform_request(self, validated_request_data):
        user_id = validated_request_data.get('user_id')
        return {
            'user_id': user_id,
            'username': f'user_{user_id}',
            'email': f'user_{user_id}@example.com'
        }


class PaymentAPI(Resource):
    """
    支付API资源类 - 通过元类自动注册
    
    注册名称：payment_api（自动推导：PaymentAPI -> payment_api）
    模块路径：examples.new_registration_demo（自动推导）
    """
    
    def perform_request(self, validated_request_data):
        amount = validated_request_data.get('amount', 0)
        return {
            'payment_id': 'pay_123456',
            'amount': amount,
            'status': 'success'
        }


class OrderManagementResource(Resource):
    """
    订单管理资源 - 使用自定义注册名称
    
    注册名称：order_service（通过 register_name 自定义）
    模块路径：examples.new_registration_demo（自动推导）
    """
    register_name = 'order_service'
    
    def perform_request(self, validated_request_data):
        order_id = validated_request_data.get('order_id')
        return {
            'order_id': order_id,
            'status': 'processing',
            'items': ['item1', 'item2']
        }


class NoAutoRegisterResource(Resource):
    """
    禁用自动注册的资源类
    
    这个资源不会被自动注册，需要手动注册或使用装饰器
    """
    auto_register = False
    
    def perform_request(self, validated_request_data):
        return {'message': 'This resource is not auto-registered'}


# ============================================================================
# 2. 装饰器注册
# ============================================================================

@register_resource('product_service')
class ProductResource(Resource):
    """
    产品资源 - 使用装饰器注册
    
    注册名称：product_service（通过装饰器指定）
    模块路径：examples.new_registration_demo（自动推导）
    """
    auto_register = False  # 禁用元类自动注册，避免重复
    
    def perform_request(self, validated_request_data):
        product_id = validated_request_data.get('product_id')
        return {
            'product_id': product_id,
            'name': f'Product {product_id}',
            'price': 99.99
        }


@register_function('get_system_info')
def get_system_info():
    """
    系统信息函数 - 使用装饰器注册为资源
    
    注册名称：get_system_info（通过装饰器指定）
    模块路径：examples.new_registration_demo（自动推导）
    """
    return {
        'system': 'DRF Resource Demo',
        'version': '2.0.0',
        'status': 'running'
    }


@register_as('auth_service')
class AuthenticationResource(Resource):
    """
    认证资源 - 使用 register_as 装饰器
    
    注册名称：auth_service（通过 register_as 指定）
    模块路径：examples.new_registration_demo（自动推导）
    """
    auto_register = False
    
    def perform_request(self, validated_request_data):
        username = validated_request_data.get('username')
        password = validated_request_data.get('password')
        return {
            'token': 'jwt_token_123456',
            'user': username,
            'expires_in': 3600
        }


@register_as('calculate')
def calculate_total(items):
    """
    计算总价函数 - 使用 register_as 装饰器
    
    注册名称：calculate（通过 register_as 指定）
    模块路径：examples.new_registration_demo（自动推导）
    """
    return {
        'items': items,
        'total': sum(item.get('price', 0) for item in items),
        'count': len(items)
    }


# ============================================================================
# 3. 条件注册
# ============================================================================

import os

@conditional_register(
    condition=os.getenv('ENABLE_DEBUG_FEATURES', 'false').lower() == 'true',
    name='debug_service'
)
class DebugResource(Resource):
    """
    调试资源 - 条件注册
    
    只有在环境变量 ENABLE_DEBUG_FEATURES=true 时才会注册
    """
    auto_register = False
    
    def perform_request(self, validated_request_data):
        return {
            'debug': True,
            'request_data': validated_request_data,
            'env': dict(os.environ)
        }


@conditional_register(
    condition=lambda: hasattr(os, 'uname'),  # Unix-like 系统
    name='system_uname'
)
def get_uname():
    """
    系统信息函数 - 动态条件注册
    
    只有在 Unix-like 系统上才会注册
    """
    if hasattr(os, 'uname'):
        uname = os.uname()
        return {
            'system': uname.sysname,
            'node': uname.nodename,
            'release': uname.release,
            'version': uname.version,
            'machine': uname.machine
        }
    return {'error': 'uname not available'}


# ============================================================================
# 4. 批量注册（适用于需要禁用自动注册的场景）
# ============================================================================

class BatchResource1(Resource):
    auto_register = False
    
    def perform_request(self, validated_request_data):
        return {'batch': 'resource1', 'data': validated_request_data}


class BatchResource2(Resource):
    auto_register = False
    
    def perform_request(self, validated_request_data):
        return {'batch': 'resource2', 'data': validated_request_data}


def batch_function1():
    return {'batch': 'function1'}


def batch_function2():
    return {'batch': 'function2'}


# 批量注册多个资源
batch_register(
    BatchResource1,
    BatchResource2,
    batch_function1,
    batch_function2
)


# ============================================================================
# 5. 演示使用方式
# ============================================================================

def demo_new_registration_system():
    """
    演示新注册系统的使用方式
    """
    print("=== DRF Resource 新自动注册机制演示 ===\n")
    
    # 1. 列出所有已注册的资源
    print("1. 已注册的资源列表：")
    all_resources = resource_registry.list_resources()
    for resource_key, info in all_resources.items():
        print(f"   - {resource_key}: {info['resource_type']} ({info['resource_object']})")
    print()
    
    # 2. 演示元类自动注册的资源使用
    print("2. 使用元类自动注册的资源：")
    user_resource = UserResource()
    result = user_resource.request({'user_id': 123})
    print(f"   UserResource 调用结果: {result}")
    
    payment_resource = PaymentAPI()
    result = payment_resource.request({'amount': 100.50})
    print(f"   PaymentAPI 调用结果: {result}")
    print()
    
    # 3. 演示装饰器注册的资源使用
    print("3. 使用装饰器注册的资源：")
    product_resource = ProductResource()
    result = product_resource.request({'product_id': 'PROD001'})
    print(f"   ProductResource 调用结果: {result}")
    
    # 直接调用注册的函数
    result = get_system_info()
    print(f"   get_system_info 函数调用结果: {result}")
    print()
    
    # 4. 演示资源信息查询
    print("4. 资源信息查询：")
    user_info = resource_registry.get_resource('user', 'examples.new_registration_demo')
    if user_info:
        print(f"   用户资源信息: {user_info['name']}, 类型: {user_info['resource_type']}")
    
    auth_info = resource_registry.get_resource('auth_service', 'examples.new_registration_demo')
    if auth_info:
        print(f"   认证资源信息: {auth_info['name']}, 类型: {auth_info['resource_type']}")
    print()
    
    # 5. 演示新老机制对比
    print("5. 新老机制对比：")
    print("   ✅ 新机制: 基于元类和装饰器的自动注册")
    print("   ✅ 性能提升: 消除启动时的文件扫描开销")
    print("   ✅ 更灵活: 支持自定义名称、条件注册、批量注册")
    print("   ✅ 向后兼容: 现有调用方式完全不变")
    print("   ❌ 旧机制: 基于文件扫描的注册（已废弃）")
    print()
    
    print("=== 演示完成 ===")


if __name__ == '__main__':
    demo_new_registration_system()