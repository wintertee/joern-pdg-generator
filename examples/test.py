class Helper:
    def fn0(a, b):
        x = 0
        if a > b:
            x = a
        else:
            x = b
        return x


def fn1(c, helper_obj):
    d = c + 1
    y = helper_obj.fn0(c, d)  # Call Helper's static method
    return y


helper_obj = Helper()
result = fn1(5, helper_obj)  # Example call to fn1
print(f"Result: {result}")
