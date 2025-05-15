class Helper {
    protected int a;

    public Helper() {
        this.a = 100;
    }

    public void set(int a) {
        this.a = a;
    }
}

class Helper2 extends Helper {
    // Inherits everything from Helper
}

public class Test {
    public static void main(String[] args) {
        Helper h = new Helper();
        h.set(1);

        Helper2 h2 = new Helper2();
        h2.set(1);
    }
}