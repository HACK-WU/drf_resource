class APIExplorerException(Exception):
    """API Explorer 基础异常类"""

    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundError(APIExplorerException):
    """指定的 API 资源不存在"""

    def __init__(self, message):
        super().__init__(message, code="404")


class InvocationError(APIExplorerException):
    """API 调用过程中发生错误"""

    def __init__(self, message):
        super().__init__(message, code="500")


class EnvironmentDeniedError(APIExplorerException):
    """非测试环境拒绝访问"""

    def __init__(self, message="API Explorer 仅在开发/测试环境可用"):
        super().__init__(message, code="403")
