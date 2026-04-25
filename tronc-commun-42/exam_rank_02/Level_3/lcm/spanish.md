## Subject

```c
Nombre de la tarea: lcm
Archivos esperados: lcm.c
Funciones permitidas: Ninguna
--------------------------------------------------------------------------------

Escribe una función que tome dos enteros sin signo como parámetros y devuelva
el mínimo común múltiplo (LCM) calculado de esos parámetros.

El LCM (Mínimo Común Múltiplo) de dos enteros no nulos es el menor entero positivo
divisible por ambos enteros.

Un LCM se puede calcular de dos maneras:

- Puedes calcular todos los múltiplos de cada entero hasta que tengas un múltiplo común
diferente de 0.

- Puedes usar el HCF (Mayor Común Factor) de estos dos enteros y
calcular de la siguiente manera:

	LCM(x, y) = | x * y | / HCF(x, y)

  | x * y | significa "Valor absoluto del producto de x por y".

Si al menos uno de los enteros es nulo, el LCM es igual a 0.

Tu función debe tener el siguiente prototipo:

  unsigned int    lcm(unsigned int a, unsigned int b);

```
