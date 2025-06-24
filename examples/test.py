class Test:
    def __init__(self):
        self.a = 100

    def set(self, a):
        if a > 0:
            self.a = a
            return True
        else:
            self.a = 0
            return False


def main():
    h = Test()
    val = 10
    res = h.set(val)


main()
