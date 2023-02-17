class ResponseMessage:
    def __init__(self, response=None):
        self.response = response
        if response:
            self.code = response['code']
            self.reason = response['reason']
            self.objects = response['objects']
        else:
            self.code = None
            self.reason = None
            self.objects = None

    def is_positive(self):
        return True if self.code == 'ok' else False

    def __str__(self):
        return str(self.response)


class LogMessage:
    '''
    log message generator
    '''
    def __init__(self, method: str, args: dict) -> None:
        self.method = method
        self.args = args
    
    def __str__(self) -> str:
        return f"LogMessage({self.method}, {self.args})"
    
    
    @classmethod
    def trace(cls, **kwargs):
        return cls("log", kwargs).__dict__

    def output(cls, **kwargs):
        return cls("terminal", kwargs).__dict__


if __name__ == '__main__':
    print(LogMessage.trace(name="maple"))
    