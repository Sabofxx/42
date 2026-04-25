NAME	= codexion
CC		= cc
CFLAGS	= -Wall -Wextra -Werror -pthread

SRCS	= srcs/main.c \
		  srcs/parse_args.c \
		  srcs/init_sim.c \
		  srcs/destroy_sim.c \
		  srcs/coder.c \
		  srcs/dongle.c \
		  srcs/dongle_acquire.c \
		  srcs/priority_queue.c \
		  srcs/pq_helpers.c \
		  srcs/monitor.c \
		  srcs/utils.c

OBJS	= $(SRCS:.c=.o)

all: $(NAME)

$(NAME): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(NAME)

%.o: %.c includes/codexion.h
	$(CC) $(CFLAGS) -I includes -c $< -o $@

clean:
	rm -f $(OBJS)

fclean: clean
	rm -f $(NAME)

re: fclean all

.PHONY: all clean fclean re
