class Helper:
    def __init__(self):
        self.a = 100

    def set(self, a):
        self.a = a


class Helper2(Helper):
    pass


def main():
    
    h = Helper()
    h.set(1)

    h2 = Helper2()
    h2.set(1)

main()