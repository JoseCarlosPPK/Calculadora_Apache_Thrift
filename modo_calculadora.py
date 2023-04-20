from enum import IntEnum, unique

@unique
class ModoCalculadora(IntEnum):
   MODO_CALCULO = 1,
   MODO_MATRIZ = 2



@unique
class MenuOperaciones(IntEnum):
   GUARDAR_VALORES = 1,
   VER_MATRICES = 2,
   CALCULAR = 3
