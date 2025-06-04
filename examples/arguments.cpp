void fn(int a, int b) {
    int c = a + b;
}

void another_function() {
    fn(10, 20);
    int x = 5;
    fn(x, 30);
    fn(10, 20); // 重复调用
}

int main() {
    another_function();
    fn(100, 200);
    return 0;
}