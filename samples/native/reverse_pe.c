__declspec(dllexport) int reverse_check(int value) {
    return (value ^ 0x1337) + 7;
}
int entry(void) {
    return reverse_check(0x1337) == 7 ? 0 : 1;
}
