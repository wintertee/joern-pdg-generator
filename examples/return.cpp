// Demonstrates using a reference as an in/out parameter in a function

int increment_by_value(int value)
{
    return value + 1; // returns a new value, does not modify the original variable
}

int main()
{
    int x = 5;
    int y = increment_by_value(x);
    return 0;
}
