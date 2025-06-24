// Demonstrates using a reference as an in/out parameter in a function

void increment_by_ref(int &value)
{
    value = value + 1; // modifies the original variable
}

int increment_by_value(int value)
{
    return value + 1; // returns a new value, does not modify the original variable
}

int main()
{
    int x = 5;
    increment_by_ref(x); // x is passed by reference
    // x is now 6
    int y = increment_by_value(x); // x is passed by value, but the return value is assigned to y
    // x is still 6, y is 7
    return y;
}
