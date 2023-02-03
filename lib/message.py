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