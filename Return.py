class Return(Exception):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value

    def __repr__(self):
        return 'Return({})'.format(self.value)
