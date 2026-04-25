# ft_printf

*This project has been created as part of the 42 curriculum by omischle.* 

## Description

ft_printf is a project at 42 that consists of recreating a simplified version of the standard C printf function.
The objective is to understand how formatted output works internally and to learn how to manage a variable number of arguments using variadic functions.

The goal is to implement a function called ft_printf that behaves like the original printf for a defined set of format specifiers. This project strengthens knowledge of:

variadic functions (stdarg.h)

low-level output using write

number conversions

memory handling

modular and extensible code design

The result is a static library containing a custom implementation of printf that can be reused in future 42 projects.

## Instructions

### Compilation

The project provides a Makefile with the following commands:

```bash

make          # Compiles the library and generates libftprintf.a

make clean    # Deletes object files

make fclean   # Deletes object files and the library

make re       # Recompiles everything from the beginning

```

To compile the library:

```bash 

make

```

## Usage

To use ft_printf in your project:

Include the header file in your source code:

#include "ft_printf.h"


Compile your project with the library:

gcc your_file.c -L. -lftprintf -o your_program

Supported Conversions

The function supports the following format specifiers:

Specifier	Description

````

%c	Prints a single character
%s	Prints a string
%p	Prints a pointer address in hexadecimal
%d	Prints a decimal integer
%i	Prints an integer in base 10
%u	Prints an unsigned decimal integer
%x	Prints a hexadecimal number (lowercase)
%X	Prints a hexadecimal number (uppercase)
%%	Prints a percent sign

````
````
Project Structure
ft_printf/
│
├── Makefile
├── ft_printf.h
├── ft_printf.c
├── ft_handle.c
│
├── ft_print_char.c
├── ft_print_str.c
├── ft_print_percent.c
├── ft_print_nbr.c
├── ft_print_unsigned.c
├── ft_print_hex.c
├── ft_print_ptr.c

````

## Implementation Overview

The ft_printf function parses the format string character by character.

### General algorithm

Read each character of the format string.

If the character is not %, print it directly.

If % is found:

Read the next character.

Determine the conversion type.

Extract the corresponding argument using va_arg.

Call the appropriate printing function.

Count and return the total number of printed characters.

This modular design makes the code easy to extend for future features such as flags and width handling.

## Resources
Documentation

The C Programming Language (K&R) – Classic C programming reference
C Standard Library Reference – cppreference.com
GNU C Library Manual
Linux Man Pages – man7.org

Tutorials and Articles

Beej’s Guide to C Programming
Understanding Variadic Functions in C
Understanding Makefiles – makefiletutorial.com

### AI Usage

AI tools were used strictly as a learning aid during this project:

Concept explanations: understanding variadic functions, format parsing, and number conversions

Debugging assistance: interpreting error messages and fixing logic issues

Code structure advice: guidance on modular design and project organization

All implementation, algorithms, logic, memory handling, and testing were written and understood independently without copying AI-generated solutions.
