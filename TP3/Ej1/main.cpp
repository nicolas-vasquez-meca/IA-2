#include "RedNeuronal.hpp"
#include "CapaNeuronal.hpp"
#include <vector>

CapaNeuronal capa_entrada(1, 3, "sigmoide");
CapaNeuronal capa_salida(3, 1, "sigmoide");
RedNeuronal red(capa_entrada);

std::vector<double> x;
std::vector<double> y;

int main(int argc, char* argv[]){

    red.agregarCapa(capa_salida);


    size_t i=0;
    while(i<1000){

        red.entrenar(x, y, 0.2);
    }

    return 0;
}