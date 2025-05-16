class Helper {
    protected int a;

    public Helper() {
        this.a = 100;
    }

    public bool set(int a) {
        if (a > 0) {
            this.a = a;
            return true;
        }
        else {
            this.a = 0;
            return false;
        }
    }
}


public class Test {
    public static void main(String[] args) {
        Helper h = new Helper();
        res = h.set(1);
        System.out.println("Result: " + res);
    }
}