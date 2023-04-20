exception DivisionZero {
   1: string msg
}


exception DimensionesMatricesError {
   1: string msg
}


exception MatrizNoTieneInversa {
   1: string msg
}

service Calculadora{
   string calcula_expresion_matrices(1:string expresion) throws (1:DimensionesMatricesError e, 2:MatrizNoTieneInversa m),
   double calcula_expresion_aritmetica(1:string expresion) throws (1: DivisionZero e)
}
