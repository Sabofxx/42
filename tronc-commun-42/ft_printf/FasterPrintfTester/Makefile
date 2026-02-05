CFLAGS	= -Wall -Wextra -Werror

SRC		= main.c tests/print_tests.c tests/test_basic_extended.c tests/test_basic.c tests/test_minus.c tests/test_dot.c \
			tests/test_number.c print_header.c utils.c tests/test_zero.c tests/test_allbonus.c tests/test_everything.c
OBJS	= $(SRC:.c=.o)

all: compile
	./run_test

clean:
	$(RM) $(OBJS)

fclean: clean
	$(RM) output.txt run_test

re: fclean all

s short: compile
	./run_test s

b basic: compile
	./run_test b

m more: compile
	./run_test m

compile: copy_header $(OBJS) printf
	$(CC) $(CFLAGS) $(OBJS) -L.. -lftprintf -o run_test
	make clean

copy_header:
	find .. -type d -name "*test*" -prune -o -name "ft_printf.h" -exec cp {} . \;

$(OBJS): copy_header

printf:
	cd .. && $(MAKE) re

.PHONY: all clean fclean re copy_header
