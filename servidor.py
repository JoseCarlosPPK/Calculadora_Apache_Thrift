
import Calculadora
import numpy as np
from operadores import OperadorAritmetico, OperadorMatricial
from matriz import Matriz

from ttypes import DimensionesMatricesError, DivisionZero, MatrizNoTieneInversa
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import logging

logging.basicConfig(level=logging.DEBUG)


class CalculadoraHandler:
    
    __PRECEDENCIA_ARITMETICA = {
        '*':3,
        '/':3,
        '+':2,
        '-':2,
        '(':1
    }

    __PRECEDENCIA_MATRICES = {
        '*':3,
        '/':3,
        '+':2,
        '-':2,
        '(':1
    }

    def __init__(self):
        self.log = {}


    def __es_operador_aritmetico(caracter: str) -> bool:
        try:
            return OperadorAritmetico(caracter) in OperadorAritmetico
        except:
            return False
        

    def __es_simbolo_aritmetico(caracter: str) -> bool:
        return CalculadoraHandler.__es_operador_aritmetico(caracter) or caracter == '(' or caracter == ')'
        
    
    def __es_operador_matricial(caracter: str) -> bool:
        try:
            return OperadorMatricial(caracter) in OperadorMatricial
        except:
            return False


    def __es_simbolo_matricial(caracter: str) -> bool:
        return CalculadoraHandler.__es_operador_matricial(caracter) or caracter == '(' or caracter == ')'


    def __transformar_expresion_str_a_lista_matrices(expresion: str) -> list:
        expresion = expresion.strip() #quitamos espacios en blanco
        ind = 0
        tam = len(expresion)
        lista = []

        while ind < tam:
            if not CalculadoraHandler.__es_simbolo_matricial(expresion[ind]):
                j = ind
                while j < tam and not CalculadoraHandler.__es_simbolo_matricial(expresion[j]):
                    j += 1

                matriz = Matriz.crea_matriz(expresion[ind:j])
                elemento = np.array(matriz.matriz).reshape(matriz.dimension)

                ind = j
            
            else:
                elemento = expresion[ind]
                ind += 1


            lista.append(elemento)
            
        
        return lista


    def __transformar_expresion_str_a_lista_aritmetica(expresion: str) -> list:
        expresion = expresion.strip() #quitamos espacios en blanco
        ind = 0
        tam = len(expresion)
        lista = []

        while ind < tam:
            if not CalculadoraHandler.__es_simbolo_aritmetico(expresion[ind]):
                j = ind

                while j < tam and not CalculadoraHandler.__es_simbolo_aritmetico(expresion[j]):
                    j += 1

                elemento = float(expresion[ind:j]) # si hay un error de sintaxis se lanza una excepción ValueError

                ind = j
            
            else:
                elemento = expresion[ind]
                ind += 1


            lista.append(elemento)


        return lista


    def __expresion_infija_a_sufija_matrices(expresion: list) -> list:
        pila_operadores = []
        lista_sufija = []

        for elemento in expresion:
            if isinstance(elemento, np.ndarray):
                lista_sufija.append(elemento)
            elif elemento == '(':
                pila_operadores.append(elemento)
            elif elemento == ')':
                tope = pila_operadores.pop()

                while tope != '(':
                    lista_sufija.append(tope)
                    tope = pila_operadores.pop()
                
                
            else:
                while len(pila_operadores) > 0 and CalculadoraHandler.__PRECEDENCIA_MATRICES[pila_operadores[-1]] >= CalculadoraHandler.__PRECEDENCIA_MATRICES[elemento]:
                    lista_sufija.append(pila_operadores.pop())

                pila_operadores.append(elemento)

        # end for

        while len(pila_operadores) > 0:
            lista_sufija.append(pila_operadores.pop())


        return lista_sufija
    



    def __expresion_infija_a_sufija_aritmetica(expresion: list) -> list:
        pila_operadores = []
        lista_sufija = []

        for elemento in expresion:
            if isinstance(elemento, float):
                lista_sufija.append(elemento)
            elif elemento == '(':
                pila_operadores.append(elemento)
            elif elemento == ')':
                tope = pila_operadores.pop()

                while tope != '(':
                    lista_sufija.append(tope)
                    tope = pila_operadores.pop()

                
            else:
                while len(pila_operadores) > 0 and CalculadoraHandler.__PRECEDENCIA_ARITMETICA[pila_operadores[-1]] >= CalculadoraHandler.__PRECEDENCIA_ARITMETICA[elemento]:
                    lista_sufija.append(pila_operadores.pop())

                pila_operadores.append(elemento)

        # end for

        while len(pila_operadores) > 0:
            lista_sufija.append(pila_operadores.pop())


        return lista_sufija


    def __evalua_expresion_sujija_matrices(lista_sufija) -> np.ndarray:
        pila_matrices = []

        for elemento in lista_sufija:
            if isinstance(elemento, np.ndarray):
                pila_matrices.append(elemento)
            
            else: # es una operación
                m2 = pila_matrices.pop()
                m1 = pila_matrices.pop()

                resultado = CalculadoraHandler.__calculo_matricial(m1,m2, elemento)
                pila_matrices.append(resultado)

        return pila_matrices.pop()


    def __calculo_matricial(m1: np.ndarray, m2: np.ndarray, operacion: OperadorMatricial) -> np.ndarray:
        operacion = OperadorMatricial(operacion)

        try:
            if operacion == OperadorMatricial.SUMA:
                return m1+m2
            elif operacion == OperadorMatricial.RESTA:
                return m1-m2
            elif operacion == OperadorMatricial.MULTIPLICACION:
                return np.dot(m1,m2)
            elif operacion == OperadorMatricial.DIVISION:
                try:
                    inversa_m2 = np.linalg.inv(m2)
                    return np.dot(m1,inversa_m2)
                except np.linalg.LinAlgError:
                    raise MatrizNoTieneInversa(f"{m2} NO TIENE INVERSA")
        except ValueError:
            raise DimensionesMatricesError(f"La matriz m1 {m1.shape} y m2 {m2.shape} no son compatibles en esta operación")



    def __evalua_expresion_sujija_aritmetica(lista_sufija) -> float:
        pila_numeros = []

        for elemento in lista_sufija:
            if isinstance(elemento, float):
                pila_numeros.append(elemento)
            
            else: # es una operación
                num2 = pila_numeros.pop()
                num1 = pila_numeros.pop()

                resultado = CalculadoraHandler.__calculo_aritmetico(num1,num2, elemento)
                pila_numeros.append(resultado)

        return pila_numeros.pop()


    def __calculo_aritmetico(num1: float, num2: float, operacion: OperadorAritmetico):
        operacion = OperadorAritmetico(operacion)

        if operacion == OperadorAritmetico.SUMA:
            return num1+num2
        elif operacion == OperadorAritmetico.RESTA:
            return num1-num2
        elif operacion == OperadorAritmetico.MULTIPLICACION:
            return num1*num2
        elif operacion == OperadorAritmetico.DIVISION:
            try:
                return num1/num2
            except ZeroDivisionError:
                raise DivisionZero(f"{num1}/{num2}: División por cero no permitida")



    def calcula_expresion_matrices(self, expresion) -> str:
        expresion_lista = CalculadoraHandler.__transformar_expresion_str_a_lista_matrices(expresion)
        lista_sufija = CalculadoraHandler.__expresion_infija_a_sufija_matrices(expresion_lista)
        resultado = CalculadoraHandler.__evalua_expresion_sujija_matrices(lista_sufija)
        matriz_lista = resultado.flatten().tolist()
        dimension = resultado.shape

        return str(Matriz(matriz_lista, dimension))
    

    def calcula_expresion_aritmetica(self, expresion) -> float:
        expresion_lista = CalculadoraHandler.__transformar_expresion_str_a_lista_aritmetica(expresion)
        lista_sufija = CalculadoraHandler.__expresion_infija_a_sufija_aritmetica(expresion_lista)
        resultado = CalculadoraHandler.__evalua_expresion_sujija_aritmetica(lista_sufija)

        return resultado

    # def calculo(expresion):
    #     transformar datos a matrices
    #     pasar de notación infija a sufija
    #     evaluar notación infija






if __name__ == "__main__":
    handler = CalculadoraHandler()
    processor = Calculadora.Processor(handler)
    transport = TSocket.TServerSocket(host="127.0.0.1", port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print("iniciando servidor...")
    server.serve()
    print("fin")
