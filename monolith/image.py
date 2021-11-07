# class created to perform checks on messages in order to avoid inserting a real image to perform the test

class Image:
    def __init__(self):
        self.filename = ''

    def get_filename(self):
        return self.filename