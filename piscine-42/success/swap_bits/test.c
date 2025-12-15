#include <unistd.h>

unsigned char	swap_bits(unsigned char octet)
{
	return (octet >> 4 | octet << 4);
}

int main()
{
	char c = '&';
	write(1, &c, 1);
	c = swap_bits(c);
	write(1, &c, 1);
}
