#!/bin/bash
rm -r "FasterPrintfTester/"
rm -r "ft_printf_test/"
rm -r "printfTester/"
make fclean >/dev/null 2>&1 || true
rm -r "$0"
