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
        Test h = new Test();
        int val = 10;
        boolean res = h.set(val);
        System.exit(res ? 0 : 1);
    }
}