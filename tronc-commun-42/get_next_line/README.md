*This project has been created as part of the 42 curriculum by Mischler Oscar.*

# Get Next Line

## Description

Get Next Line is a project from 42 that implements a function to read a file descriptor line by line. Each call returns the next line, including the newline character if present, without reading the entire file at once. This project teaches file descriptors, static variables, buffered reading, and memory management in C.

## Instructions

### Compilation
```bash
gcc -Wall -Wextra -Werror get_next_line.c get_next_line_utils.c -D BUFFER_SIZE=42
```

You can change BUFFER_SIZE to test different behaviors.

### Usage
```c
#include "get_next_line.h"

int fd = open("file.txt", O_RDONLY);
char *line;

while ((line = get_next_line(fd)) != NULL)
{
    printf("%s", line);
    free(line);
}
close(fd);
```

## Function

**get_next_line(int fd)** – returns the next line from the file descriptor, or NULL at EOF or error.

## Algorithm

- Read from the file descriptor in chunks of BUFFER_SIZE.
- Store leftover data in a static buffer.
- Extract the next line including \n.
- Return the line and keep the remainder for the next call.
- Works with any line length and file descriptor.

## Files

- **get_next_line.c** – main logic
- **get_next_line_utils.c** – helper functions
- **get_next_line.h** – prototypes and includes

## Resources

- Linux Man Pages (read, malloc, free)
- The C Programming Language (K&R)
- cppreference.com

## AI Usage

AI was used only for understanding concepts, documentation, and debugging. All code and logic were implemented independently.