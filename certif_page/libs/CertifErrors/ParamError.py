class ParamError(Exception):
    def __init__(self, ErrorInfo='参数错误'):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo