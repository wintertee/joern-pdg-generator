class Helper:
    def __init__(self):
        self.a = 100

    def set(self, a):
        if a > 0:
            self.a = a
            return True
        else:
            self.a = 0
            return False


class Helper2(Helper):
    pass


print(Helper2().set(-1))
