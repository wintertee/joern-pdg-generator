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


# def main():
#     h = Helper()
#     res = h.set(1)
#     print("Result:", res)


# if __name__ == "__main__":
#     main()
