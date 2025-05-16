class Test {
    protected int a;

    public Test() {
        this.a = 100;
    }

    public boolean set(int a) {
        if (a > 0) {
            this.a = a;
            return true;
        }
        else {
            this.a = 0;
            return false;
        }
    }

    public static void main(String[] args) {
    }
}