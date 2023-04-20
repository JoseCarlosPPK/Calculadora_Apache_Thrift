class Matriz:
   def __init__(self, lista_numeros: list, dimension):
      """

      Args:
          lista_numeros (list): contenido de la matriz
          dimension (iterable): Dimensión de la matriz
      """
      self.__matriz = lista_numeros
      self.__dim = tuple(dimension)


   def crea_matriz(representacion):
      representacion = representacion.split(':')
      lista = list(map(float, representacion[0].replace('[', '').replace(']', '').split(',')))
      dimension = tuple(map(int, representacion[1].replace('[', '').replace(']', '').split(',')))

      return Matriz(lista, dimension)


   @property
   def matriz(self):
      return self.__matriz


   @property
   def dimension(self):
      return self.__dim
   

   def __repr__(self) -> str:
      dimension = str(self.__dim).replace('(', '[').replace(')', ']')
      return f"{self.__matriz}:{dimension}"
   

   def __str__(self) -> str:
      return self.__repr__()