#include <iostream>

class Helper {
public:
    int a;

    Helper() : a(100) {}

    bool set(int val) {
        if (val > 0) {
            a = val;
            return true;
        } else {
            a = 0;
            return false;
        }
    }
};

int main() {
    Helper h;
    bool res = h.set(1);
    std::cout << "Result: " << std::boolalpha << res << std::endl;
    return 0;
}