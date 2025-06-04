int main(){
    int x = 5;
    switch (x) {
        case 1:
            x += 1;
        case 2:
            x += 2;
            break;
        default:
            x += 3;
            break;
    }
    return x;
}