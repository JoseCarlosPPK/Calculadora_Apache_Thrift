from enum import Enum,unique

@unique
class OperadorAritmetico(Enum):
   SUMA = '+'
   RESTA = '-'
   MULTIPLICACION = '*'
   DIVISION = '/'



@unique
class OperadorMatricial(Enum):
   SUMA = '+'
   RESTA = '-'
   MULTIPLICACION = '*'
   DIVISION = '/'