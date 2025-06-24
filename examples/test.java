class Main {
    protected int a;

    public Main() {
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
        Main h = new Main();
        int val = -10;
        boolean res = h.set(val);
        System.exit(res==true ? 0 : 1);
    }
}

