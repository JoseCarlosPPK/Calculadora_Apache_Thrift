import glob
import sys

import Calculadora

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import logging

logging.basicConfig(level=logging.DEBUG)


class CalculadoraHandler:
    def __init__(self):
        self.log = {}


    def suma_matrices(self, m1, m2):
        dimension_m1 = (len(m1), len(m1[0]))
        dimension_m2 = (len(m2), len(m2[0]))

        if dimension_m1 != dimension_m2:
            return None
        
        matriz_suma = []

        for fila_m1, fila_m2 in zip(m1,m2):
            fila_suma = []
            for col_m1, col_m2 in zip(fila_m1, fila_m2):
                fila_suma.append(col_m1+col_m2)

        return matriz_suma




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
