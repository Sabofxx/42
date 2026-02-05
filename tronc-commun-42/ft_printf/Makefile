# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: omischle <omischle@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/01/30 15:06:14 by omischle          #+#    #+#              #
#    Updated: 2026/01/30 15:06:17 by omischle         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

HEADER 		= ft_printf.h
SRC 		= ft_printf.c printf_char.c printf_string.c printf_ptr.c \
				printf_nbr.c printf_hex.c printf_uint.c
OBJS 		= $(SRC:.c=.o)

NAME 		= libftprintf.a
CC 			= cc
CFLAGS 		= -Wall -Werror -Wextra
LIB_PATH 	= ./libft 
LIBFT 		= $(LIB_PATH)/libft.a

all: $(LIBFT) $(NAME)

$(NAME): $(OBJS)
	cp libft/libft.a $(NAME)
	ar -rcs $(NAME) $(OBJS)

$(LIBFT):
	make -C $(LIB_PATH) all 

%.o: %.c  $(HEADER)
	$(CC) -c $(CFLAGS) -I ./ $< -o $@  


fclean: clean
	make -C $(LIB_PATH) fclean
	rm -rf $(NAME)	

clean:
	rm -f $(OBJS)
	make -C $(LIB_PATH) clean

re: fclean all

.PHONY: all clean fclean re