#include "RedNeuronal.hpp"
#include "CapaNeuronal.hpp"

void RedNeuronal::agregarCapa( CapaNeuronal& capa) {

    if (capas.back().get_size_neuronas() != capa.get_size_entradas())
    {
        throw std::runtime_error(
            "La cantidad de neuronas de la ultima capa es distinta" 
            "de la cantidad de entradas de la capa a agregar");

    }else{
        
        capas.push_back(capa);
    }
}

std::vector<double> RedNeuronal::forward(std::vector<double> x) {

    for (const auto& capa : capas)
    {
        x = capa.forward(x);
    }

    return x;
}

void RedNeuronal::entrenar(std::vector<double> x, std::vector<double> yt, double lr){

    if (!capas.empty()) throw std::runtime_error("faltan agragar capas");

    // Guardamos todas las activaciones (salidas), empezando desde las entrada inicial
    // como si fuera la salida de una capa neuronal 0
    std::vector<std::vector<double>> activaciones;
    activaciones.push_back(x);

    std::vector<double> a = x;

    for (const auto& capa : capas) {
        a = capa.forward(a);
        activaciones.push_back(a);
    }

    // Validamos tamaño del target
    if (activaciones.back().size() != yt.size()) {
        throw std::runtime_error("El target no coincide con la salida de la red");
    }

    // Calculamos la derivada del error 
    std::vector<double> dL_dy(yt.size(), 0.0);
    
    for (size_t i=0; i<yt.size() ; i++){
        dL_dy[i] = activaciones.back()[i] - yt[i];
    }

    // Entrenamiento
    std::vector<double> dL_da = dL_dy;
    size_t sz = static_cast<size_t>(this->capas.size());

  
    for (long int j = sz-1 ; j>=0 ;j--) {
        dL_da = capas[j].entrenar(dL_da, activaciones[j], lr);
    }
}