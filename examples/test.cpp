class Test
{
public:
    int a;

    Test() : a(100) {}

    bool set(int val)
    {
        if (val > 0)
        {
            a = val;
            return true;
        }
        else
        {
            a = 0;
            return false;
        }
    }
};

int main(void)
{
    Test h;
    int val = 10;
    bool res = h.set(val);
    return res ? 0 : 1;
}