class Helper {
public:
    int a;

    Helper() : a(100) {}

    bool set(int val) {
        if (val > 0) {
            this->a = val;
            return true;
        } else {
            this->a = 0;
            return false;
        }
    }
};

void main() {
}