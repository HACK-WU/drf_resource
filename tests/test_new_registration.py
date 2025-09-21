# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import unittest
import warnings
from unittest.mock import patch, MagicMock

from drf_resource.base import Resource
from drf_resource.registry import ResourceRegistry, ResourceMeta, resource_registry
from drf_resource.decorators import (
    register_resource,
    register_function,
    register_as,
    conditional_register,
    batch_register,
    unregister_resource,
    list_registered_resources,
    get_resource_info,
)


class TestResourceRegistry(unittest.TestCase):
    """测试资源注册表功能"""
    
    def setUp(self):
        """测试前置设置"""
        self.registry = ResourceRegistry()
    
    def test_register_resource_class(self):
        """测试注册资源类"""
        class TestResource(Resource):
            def perform_request(self, validated_request_data):
                return {"test": "data"}
        
        self.registry.register_resource(
            name="test_resource",
            resource_class=TestResource,
            module_path="test.module"
        )
        
        # 验证注册成功
        resource_info = self.registry.get_resource("test_resource", "test.module")
        self.assertIsNotNone(resource_info)
        self.assertEqual(resource_info['name'], "test_resource")
        self.assertEqual(resource_info['resource_type'], 'class')
        self.assertEqual(resource_info['resource_object'], TestResource)
    
    def test_register_function(self):
        """测试注册函数资源"""
        def test_function():
            return {"test": "function"}
        
        self.registry.register_function(
            name="test_function",
            function=test_function,
            module_path="test.module"
        )
        
        # 验证注册成功
        resource_info = self.registry.get_resource("test_function", "test.module")
        self.assertIsNotNone(resource_info)
        self.assertEqual(resource_info['name'], "test_function")
        self.assertEqual(resource_info['resource_type'], 'function')
        self.assertEqual(resource_info['resource_object'], test_function)
    
    def test_unregister_resource(self):
        """测试注销资源"""
        class TestResource(Resource):
            def perform_request(self, validated_request_data):
                return {"test": "data"}
        
        self.registry.register_resource(
            name="test_resource",
            resource_class=TestResource,
            module_path="test.module"
        )
        
        # 验证资源存在
        self.assertIsNotNone(self.registry.get_resource("test_resource", "test.module"))
        
        # 注销资源
        result = self.registry.unregister("test_resource", "test.module")
        self.assertTrue(result)
        
        # 验证资源已删除
        self.assertIsNone(self.registry.get_resource("test_resource", "test.module"))
    
    def test_list_resources(self):
        """测试列出资源"""
        class TestResource1(Resource):
            def perform_request(self, validated_request_data):
                return {"test": "data1"}
        
        class TestResource2(Resource):
            def perform_request(self, validated_request_data):
                return {"test": "data2"}
        
        self.registry.register_resource("resource1", TestResource1, "test.module1")
        self.registry.register_resource("resource2", TestResource2, "test.module2")
        
        # 列出所有资源
        all_resources = self.registry.list_resources()
        self.assertEqual(len(all_resources), 2)
        
        # 按模块过滤
        module1_resources = self.registry.list_resources("test.module1")
        self.assertEqual(len(module1_resources), 1)
        self.assertIn("resource1", module1_resources)
    
    def test_infer_resource_name(self):
        """测试资源名称推导"""
        class UserResource(Resource):
            def perform_request(self, validated_request_data):
                return {}
        
        class PaymentAPI(Resource):
            def perform_request(self, validated_request_data):
                return {}
        
        class GetUserInfo(Resource):
            def perform_request(self, validated_request_data):
                return {}
        
        # 测试不同命名模式的推导
        self.assertEqual(self.registry._infer_resource_name(UserResource), "user")
        self.assertEqual(self.registry._infer_resource_name(PaymentAPI), "payment_api")
        self.assertEqual(self.registry._infer_resource_name(GetUserInfo), "get_user_info")
    
    def test_infer_module_path(self):
        """测试模块路径推导"""
        class TestResource(Resource):
            def perform_request(self, validated_request_data):
                return {}
        
        # 模拟不同的模块名
        TestResource.__module__ = "user.resources"
        self.assertEqual(self.registry._infer_module_path(TestResource), "user")
        
        TestResource.__module__ = "payment.api.resources"
        self.assertEqual(self.registry._infer_module_path(TestResource), "payment.api")
        
        TestResource.__module__ = "cc.adapter.default"
        self.assertEqual(self.registry._infer_module_path(TestResource), "cc")


class TestResourceMeta(unittest.TestCase):
    """测试资源元类功能"""
    
    def setUp(self):
        """测试前置设置"""
        # 清空注册表
        resource_registry._registry.clear()
    
    def test_auto_register_resource(self):
        """测试自动注册资源"""
        class AutoTestResource(Resource):
            def perform_request(self, validated_request_data):
                return {"auto": "registered"}
        
        # 验证自动注册
        resources = resource_registry.list_resources()
        registered_names = [info['name'] for info in resources.values()]
        self.assertIn("auto_test", registered_names)
    
    def test_disable_auto_register(self):
        """测试禁用自动注册"""
        class NoAutoRegisterResource(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"no": "auto"}
        
        # 验证未自动注册
        resources = resource_registry.list_resources()
        registered_names = [info['name'] for info in resources.values()]
        self.assertNotIn("no_auto_register", registered_names)
    
    def test_custom_register_name(self):
        """测试自定义注册名称"""
        class CustomNameResource(Resource):
            register_name = "custom_name"
            
            def perform_request(self, validated_request_data):
                return {"custom": "name"}
        
        # 验证使用自定义名称注册
        resource_info = resource_registry.get_resource("custom_name", resource_registry._infer_module_path(CustomNameResource))
        self.assertIsNotNone(resource_info)
        self.assertEqual(resource_info['name'], "custom_name")


class TestDecorators(unittest.TestCase):
    """测试装饰器功能"""
    
    def setUp(self):
        """测试前置设置"""
        # 清空注册表
        resource_registry._registry.clear()
    
    def test_register_resource_decorator(self):
        """测试资源类装饰器"""
        @register_resource('decorated_resource')
        class DecoratedResource(Resource):
            auto_register = False  # 防止元类重复注册
            
            def perform_request(self, validated_request_data):
                return {"decorated": "resource"}
        
        # 验证装饰器注册
        resource_info = resource_registry.get_resource("decorated_resource", resource_registry._infer_module_path(DecoratedResource))
        self.assertIsNotNone(resource_info)
        self.assertEqual(resource_info['name'], "decorated_resource")
    
    def test_register_function_decorator(self):
        """测试函数装饰器"""
        @register_function('decorated_function')
        def decorated_function():
            return {"decorated": "function"}
        
        # 验证函数注册
        resource_info = resource_registry.get_resource("decorated_function", decorated_function.__module__)
        self.assertIsNotNone(resource_info)
        self.assertEqual(resource_info['name'], "decorated_function")
        self.assertEqual(resource_info['resource_type'], 'function')
    
    def test_register_as_decorator(self):
        """测试 register_as 装饰器"""
        @register_as('as_resource')
        class AsResource(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"as": "resource"}
        
        @register_as('as_function')
        def as_function():
            return {"as": "function"}
        
        # 验证类注册
        class_info = resource_registry.get_resource("as_resource", resource_registry._infer_module_path(AsResource))
        self.assertIsNotNone(class_info)
        
        # 验证函数注册
        func_info = resource_registry.get_resource("as_function", as_function.__module__)
        self.assertIsNotNone(func_info)
    
    def test_conditional_register(self):
        """测试条件注册"""
        @conditional_register(True, 'condition_true')
        class ConditionalTrueResource(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"condition": "true"}
        
        @conditional_register(False, 'condition_false')
        class ConditionalFalseResource(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"condition": "false"}
        
        # 验证条件为 True 的资源已注册
        true_info = resource_registry.get_resource("condition_true", resource_registry._infer_module_path(ConditionalTrueResource))
        self.assertIsNotNone(true_info)
        
        # 验证条件为 False 的资源未注册
        false_info = resource_registry.get_resource("condition_false", resource_registry._infer_module_path(ConditionalFalseResource))
        self.assertIsNone(false_info)
    
    def test_batch_register(self):
        """测试批量注册"""
        class BatchResource1(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"batch": "1"}
        
        class BatchResource2(Resource):
            auto_register = False
            
            def perform_request(self, validated_request_data):
                return {"batch": "2"}
        
        def batch_function():
            return {"batch": "function"}
        
        # 批量注册
        batch_register(BatchResource1, BatchResource2, batch_function)
        
        # 验证都已注册
        resource1_info = resource_registry.get_resource("batch_resource1", resource_registry._infer_module_path(BatchResource1))
        resource2_info = resource_registry.get_resource("batch_resource2", resource_registry._infer_module_path(BatchResource2))
        function_info = resource_registry.get_resource("batch_function", batch_function.__module__)
        
        self.assertIsNotNone(resource1_info)
        self.assertIsNotNone(resource2_info)
        self.assertIsNotNone(function_info)


class TestBackwardCompatibility(unittest.TestCase):
    """测试向后兼容性"""
    
    def test_deprecated_functions_warning(self):
        """测试废弃函数会发出警告"""
        from drf_resource.management.root import install_resource, install_adapter
        
        # 测试 install_resource 发出警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            install_resource(None)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("install_resource is deprecated", str(w[0].message))
        
        # 测试 install_adapter 发出警告
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            install_adapter(None)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("install_adapter is deprecated", str(w[0].message))
    
    @patch('drf_resource.management.root.resource')
    @patch('drf_resource.management.root.api') 
    @patch('drf_resource.management.root.adapter')
    def test_setup_function_compatibility(self, mock_adapter, mock_api, mock_resource):
        """测试 setup 函数兼容性"""
        from drf_resource.management.root import setup
        
        # 调用 setup
        setup()
        
        # 验证不会出错
        self.assertTrue(True)


class TestResourceUsage(unittest.TestCase):
    """测试资源使用方式"""
    
    def setUp(self):
        """测试前置设置"""
        resource_registry._registry.clear()
    
    def test_resource_instance_creation(self):
        """测试资源实例创建"""
        class UsageTestResource(Resource):
            def perform_request(self, validated_request_data):
                return {"usage": "test", "input": validated_request_data}
        
        # 创建实例
        instance = UsageTestResource()
        
        # 测试调用
        result = instance.request({"test": "data"})
        self.assertEqual(result["usage"], "test")
        self.assertEqual(result["input"], {"test": "data"})
    
    def test_resource_callable_syntax(self):
        """测试资源可调用语法"""
        class CallableTestResource(Resource):
            def perform_request(self, validated_request_data):
                return {"callable": True, "data": validated_request_data}
        
        # 测试 __call__ 语法
        result = CallableTestResource()({"test": "call"})
        self.assertEqual(result["callable"], True)
        self.assertEqual(result["data"], {"test": "call"})


if __name__ == '__main__':
    unittest.main()