from pyteal.ast import *

dos = Int(2)
uno = Int(1)
tres = dos + uno
cuatro = uno + uno + uno + uno
siete = tres + cuatro
cinco = Int(5)
dos = siete - cinco
catorce = siete * dos
quince = catorce + uno
tres = Int(3)
cinco = quince / tres
diez = cinco + cinco
cien = diez * diez
mil = cien * diez
doscientos = cien + cien
cuatrocientos = doscientos + doscientos
trescientos = cuatrocientos - cien
mil_trescientos = mil + trescientos
setenta = diez * siete
treinta_y_cinco = setenta >> uno
cinco = Int(5)
treinta = treinta_y_cinco - cinco
mil_trescientos_treinta = mil_trescientos + treinta
mil_trescientos_treinta_y_siete = mil_trescientos_treinta + siete

program = mil_trescientos_treinta_y_siete
