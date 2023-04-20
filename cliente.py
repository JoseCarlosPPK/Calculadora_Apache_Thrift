from functools import reduce
import Calculadora
import numpy as np
from modo_calculadora import ModoCalculadora, MenuOperaciones
from matriz import Matriz
from ttypes import DivisionZero, MatrizNoTieneInversa, DimensionesMatricesError

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

SEPARADOR = 'x'
SALIR = 'º'


def menu_modo_calculadora() -> int:
   
   print("MODO CALCULADORA")
   print(f"{ModoCalculadora.MODO_CALCULO}) Modo cálculo")
   print(f"{ModoCalculadora.MODO_MATRIZ}) Modo matriz")
   print("*) Salir")

   try:
      modo = int(input().split()[0])
   except:
      modo = -1 # Salir

   return modo



def menu_modo_matrices() -> int:
   print("MATRICES")
   print(f"{MenuOperaciones.GUARDAR_VALORES}) Guardar matrices")
   print(f"{MenuOperaciones.VER_MATRICES}) Ver matrices")
   print(f"{MenuOperaciones.CALCULAR}) Calcular")

   try:
      modo = int(input().split()[0])
   except:
      modo = -1 # Salir

   return modo



def lee_dimension(txt, separador):
   try:
      dim = tuple(map(int, input(txt).lower().strip().split(separador)))
   except:
      dim = SALIR

   return dim


def lee_matriz(txt, num_elem):
   try:
      matriz = list(map(int, input(txt).split()))
      longitud = len(matriz)
      diff = num_elem - longitud
      
      if diff > 0: #Faltan elementos
         matriz.extend(lee_matriz(f"Faltan {diff} números: ", diff))

      elif diff < 0: #Sobran elementos
         print(f"Sobran {abs(diff)} elementos")
         matriz = matriz[:num_elem]
   except:
      matriz = SALIR

   return matriz








transport = TSocket.TSocket("localhost", 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)
client = Calculadora.Client(protocol)

transport.open()


matrices = {}


modo = menu_modo_calculadora()


while modo == ModoCalculadora.MODO_MATRIZ or modo == ModoCalculadora.MODO_CALCULO:

   if modo == ModoCalculadora.MODO_CALCULO:
      expresion = input(": ").strip()
      while expresion != SALIR:
         try:
            resultado = client.calcula_expresion_aritmetica(expresion)
            print("=", resultado)
         except DivisionZero as e:
            print(e.msg)

         expresion = input("\n: ")

   else: # Modo Matrices
      print()
      modo = menu_modo_matrices()

      while modo == MenuOperaciones.GUARDAR_VALORES or modo == MenuOperaciones.CALCULAR or modo == MenuOperaciones.VER_MATRICES:
         print()

         if modo == MenuOperaciones.GUARDAR_VALORES:
            key = input("Letra:").strip()[0]

            if key != SALIR:
               dimension = lee_dimension("Dimensión:", SEPARADOR)

               if dimension != SALIR:
                  lista = lee_matriz("Matriz:", reduce(lambda x,y: x*y, dimension))

                  if lista != SALIR:
                     if key in matrices:
                        respuesta = input(f"Se va a sobreescribir la matriz {key}. ¿Está seguro?[y/n]: ").lower()

                        if respuesta == 'y':
                           matriz = Matriz(lista, dimension)
                           matrices[key] = matriz
                     else:
                        matriz = Matriz(lista, dimension)
                        matrices[key] = matriz


         elif modo == MenuOperaciones.VER_MATRICES:
            print(matrices)
            print()

         elif modo == MenuOperaciones.CALCULAR:
            expresion = input(": ").strip()

            while expresion != SALIR:
               for letra in expresion:
                  if letra in matrices:
                     expresion = expresion.replace(letra, str(matrices[letra]))

               try:
                  resultado = client.calcula_expresion_matrices(expresion)
                  resultado = Matriz.crea_matriz(resultado)
                  resultado = np.array(resultado.matriz).reshape(resultado.dimension)
                  print("= ", resultado)
               
               except MatrizNoTieneInversa as e:
                  print(e.msg)
               except DimensionesMatricesError as e:
                  print(e.msg)

               expresion = input("\n: ")


         modo = menu_modo_matrices()


   modo = menu_modo_calculadora()


   

transport.close()
