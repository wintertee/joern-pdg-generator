#include <iostream>

class Point
{
public:
    int x, y;

    Point(int x, int y) : x(x), y(y) {}

    Point operator+(const Point &other) const
    {
        return Point(x + other.x, y + other.y);
    }
};

int main()
{
    Point p1(2, 3);
    Point p2(4, 5);
    Point sum = p1 + p2;
    return 0;
}