*This project was developed as part of the 42 curriculum by Oscar Mischler.

#Libft

## Description



Libft represents the initial project at 42 that requires building a personalized C library from the ground up. The objective is to recreate a collection of standard C library functions, along with supplementary utility functions that prove valuable throughout the program. This project acts as a cornerstone for grasping low-level programming concepts, memory handling, and the underlying mechanics of standard library functions.



The library contains implementations of string handling functions, memory operations, character validations, linked list tools, and more. Through constructing these functions from scratch, students acquire an in-depth comprehension of C programming essentials and build a reusable library for subsequent projects.



## Instructions



### Compilation



The project provides a Makefile with the following commands:



```bash

make          # Compiles the library and generates libft.a

make clean    # Deletes object files

make fclean   # Deletes object files and the library

make re       # Recompiles everything from the beginning

```



To compile the library:



```bash

make

```

### Usage



To integrate the library into your project:



1. Include the header file in your source code:



```c

#include "libft.h"

```



2. Compile your project with the library:



```bash

gcc your_file.c -L. -lft -o your_program

```



## Library Functions



### Part 1 - Libc Functions



Reimplemented standard C library functions:



#### Character Checks



`ft_isalpha` - Verifies if character is alphabetic

`ft_isdigit` - Verifies if character is a digit

`ft_isalnum` - Verifies if character is alphanumeric

`ft_isascii` - Verifies if character is ASCII

`ft_isprint` - Verifies if character is printable

`ft_toupper` - Transforms character to uppercase

`ft_tolower` - Transforms character to lowercase



#### String Functions



`ft_strlen` - Computes string length

`ft_strlcpy` - Copies string with size limitation

`ft_strlcat` - Concatenates strings with size limitation

`ft_strchr` - Finds first occurrence of character

`ft_strrchr` - Finds last occurrence of character

`ft_strncmp` - Compares strings up to n characters

`ft_strnstr` - Finds substring in string

`ft_strdup` - Duplicates a string



#### Memory Functions



`ft_memset` - Fills memory with constant byte

`ft_bzero` - Sets memory to zero

`ft_memcpy` - Copies memory area

`ft_memmove` - Copies memory area (handles overlap)

`ft_memchr` - Scans memory for character

`ft_memcmp` - Compares memory areas



#### Conversion



`ft_atoi` - Transforms string to integer

`ft_calloc` - Allocates and zeros memory



### Part 2 - Additional Functions



Custom utility functions:



`ft_substr` - Extracts substring from string

`ft_strjoin` - Joins two strings (allocates new string)

`ft_strtrim` - Removes characters from start and end

`ft_split` - Divides string into array using delimiter

`ft_itoa` - Transforms integer to string

`ft_strmapi` - Applies function to each character with index

`ft_striteri` - Iterates through string applying function

`ft_putchar_fd` - Writes character to file descriptor

`ft_putstr_fd` - Writes string to file descriptor

`ft_putendl_fd` - Writes string with newline to file descriptor

`ft_putnbr_fd` - Writes integer to file descriptor



### Bonus Part - Linked List Functions



Functions for working with linked lists:



`ft_lstnew` - Creates new list node

`ft_lstadd_front` - Inserts node at beginning of list

`ft_lstsize` - Counts number of nodes in list

`ft_lstlast` - Returns last node of list

`ft_lstadd_back` - Inserts node at end of list

`ft_lstdelone` - Deletes single node

`ft_lstclear` - Deletes and frees list

`ft_lstiter` - Applies function to each node

`ft_lstmap` - Applies function to each node creating new list



## Resources



### Documentation



The C Programming Language (K&R) - Classic C programming reference

C Standard Library Reference - Comprehensive C library documentation at cppreference.com

GNU C Library Manual - Detailed explanations of libc functions

Linux Man Pages - Official documentation for system functions at man7.org



### Tutorials and Articles



Beej's Guide to C Programming - Beginner-friendly C programming guide

Understanding Makefiles - Complete Makefile tutorial at makefiletutorial.com

Memory Management in C - Guide to malloc, free, and memory



### AI Usage

AI tools were utilized exclusively for educational purposes during this project:

Concept explanation: AI was employed to understand and clarify programming concepts such as memory allocation, pointer manipulation, linked lists, and C library function behaviors

Documentation comprehension: AI helped explain man pages and technical documentation when certain aspects were unclear

Debugging assistance: AI was consulted to understand error messages and debugging techniques

All code implementation, algorithm design, function logic, memory management, testing, and problem-solving were completed independently without AI-generated code
