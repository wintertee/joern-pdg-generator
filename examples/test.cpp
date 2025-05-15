class Helper {
public:
    int a;

    Helper() : a(100) {}

    void set(int a) {
        this->a = a;
    }
};

class Helper2 : public Helper {
    // Inherits everything from Helper
};

int main() {
    Helper h;
    h.set(1);

    Helper2 h2;
    h2.set(1);

    return 0;
}