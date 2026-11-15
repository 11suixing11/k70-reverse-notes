#include <stdio.h>

__attribute__((noinline)) int reverse_check(int value) {
    return (value ^ 0x1337) + 7;
}

int main(void) {
    int value = reverse_check(0x1337);
    printf("K70 native sample: %d\n", value);
    return value == 7 ? 0 : 1;
}
