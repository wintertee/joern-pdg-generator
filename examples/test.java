public class Test {

    public static void main(String[] args) {
        Helper HelperObj = new Helper();
        int result = fn1(5, HelperObj);  // Example call to fn1
        System.out.println("Result: " + result);
    }

    public static int fn1(int c, Helper HelperObj) {
        int d = c + 1;
        int y = HelperObj.fn0(c, d);  // Call Helper's static method
        return y;
    }
}

class Helper {
    public static int fn0(int a, int b) {
        int x = 0;
        if (a > b) {
            x = a;
        } else {
            x = b;
        }
        return x;
    }
}