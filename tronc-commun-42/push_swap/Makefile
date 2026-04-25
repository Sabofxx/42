NAME	=	push_swap
CC		=	cc
CFLAGS	=	-Wall -Wextra -Werror

SRC		=	main.c \
			parse.c \
			parse_collect.c \
			parse_utils.c \
			split.c \
			stack.c \
			stack_utils.c \
			utils.c \
			io_utils.c \
			error.c \
			ops_log.c \
			ops_swap.c \
			ops_push.c \
			ops_rotate.c \
			ops_reverse_rotate.c \
			sort_small.c \
			sort_simple.c \
			sort_medium.c \
			sort_complex.c \
			strategy.c \
			disorder.c \
			bench.c

OBJ		=	$(SRC:.c=.o)

all: $(NAME)

$(NAME): $(OBJ)
	$(CC) $(CFLAGS) $(OBJ) -o $(NAME)

%.o: %.c
	$(CC) $(CFLAGS) -I. -c $< -o $@

clean:
	rm -f $(OBJ)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
