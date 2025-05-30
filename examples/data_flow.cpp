#include <stdio.h>
#include <random>

int y1(int a, int b);
int y2(int a, int b);

int main()
{
    int c = 5;
    int a = 1;
    int b = 2;
    b = b + 3;
    int r = std::rand() % 2;
    if (r == 0)
        c = y1(a, b);
    else
        c = y2(a, b);
    return c;
}