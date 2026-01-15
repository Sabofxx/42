# Libft

*This project has been created as part of the 42 curriculum by Mischler Oscar.

## Description

Libft is the first project at 42 that involves creating a custom C library from scratch. The goal is to recode a set of standard C library functions, as well as additional utility functions that will be useful throughout the curriculum. This project serves as a foundation for understanding low-level programming, memory management, and the inner workings of standard library functions.

The library includes implementations of string manipulation functions, memory operations, character checks, linked list utilities, and more. By building these functions from the ground up, students develop a deep understanding of C programming fundamentals and create a reusable library for future projects.

## Instructions

### Compilation

The project includes a Makefile with the following rules:

```bash
make          # Compiles the library and creates libft.a
make bonus    # Compiles the library including bonus functions
make clean    # Removes object files
make fclean   # Removes object files and the library
make re       # Recompiles everything from scratch
```

To compile the library:

```bash
make
```

To compile with bonus functions:

```bash
make bonus
```

### Usage

To use the library in your project:

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

Standard C library functions reimplemented:

#### Character Checks

`ft_isalpha` - Checks if character is alphabetic
`ft_isdigit` - Checks if character is a digit
`ft_isalnum` - Checks if character is alphanumeric
`ft_isascii` - Checks if character is ASCII
`ft_isprint` - Checks if character is printable
`ft_toupper` - Converts character to uppercase
`ft_tolower` - Converts character to lowercase

#### String Functions

`ft_strlen` - Calculates string length
`ft_strlcpy` - Copies string with size limit
`ft_strlcat` - Concatenates strings with size limit
`ft_strchr` - Locates first occurrence of character
`ft_strrchr` - Locates last occurrence of character
`ft_strncmp` - Compares strings up to n characters
`ft_strnstr` - Locates substring in string
`ft_strdup` - Duplicates a string

#### Memory Functions

`ft_memset` - Fills memory with constant byte
`ft_bzero` - Sets memory to zero
`ft_memcpy` - Copies memory area
`ft_memmove` - Copies memory area (handles overlap)
`ft_memchr` - Scans memory for character
`ft_memcmp` - Compares memory areas

#### Conversion

`ft_atoi` - Converts string to integer
`ft_calloc` - Allocates and zeros memory

### Part 2 - Additional Functions

Custom utility functions:

`ft_substr` - Extracts substring from string
`ft_strjoin` - Concatenates two strings (allocates new string)
`ft_strtrim` - Trims characters from beginning and end
`ft_split` - Splits string into array using delimiter
`ft_itoa` - Converts integer to string
`ft_strmapi` - Applies function to each character with index
`ft_striteri` - Iterates through string applying function
`ft_putchar_fd` - Outputs character to file descriptor
`ft_putstr_fd` - Outputs string to file descriptor
`ft_putendl_fd` - Outputs string with newline to file descriptor
`ft_putnbr_fd` - Outputs integer to file descriptor

### Bonus Part - Linked List Functions

Functions for manipulating linked lists:

`ft_lstnew` - Creates new list node
`ft_lstadd_front` - Adds node at beginning of list
`ft_lstsize` - Counts number of nodes in list
`ft_lstlast` - Returns last node of list
`ft_lstadd_back` - Adds node at end of list
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

AI tools were used exclusively for educational purposes during this project:

Concept explanation: AI was used to understand and clarify programming concepts such as memory allocation, pointer manipulation, linked lists, and C library function behaviors

Documentation comprehension: AI helped explain man pages and technical documentation when certain aspects were unclear

Debugging assistance: AI was consulted to understand error messages and debugging techniques

All code implementation, algorithm design, function logic, memory management, testing, and problem-solving were completed independently without AI-generated code