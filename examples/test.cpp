class Main {
protected:
    int a;

public:
    Main() : a(100) {
    }

    bool set(int a) {
        if (a > 0) {
            this->a = a;
            return true;
        } else {
            this->a = 0;
            return false;
        }
    }
};

int main() {
    Main h;
    int val = -10;
    bool res = h.set(val);

    return res ? 0 : 1;
}