#ifndef _REDNEURONAL_
#define _REDANEURONAL_

#include <iostream>
#include <vector>
#include <cmath>
#include "CapaNeuronal.hpp"

class RedNeuronal {
    private:
        std::vector<CapaNeuronal> capas;

    public:
        RedNeuronal(CapaNeuronal& capa_inicial){
            this->capas.push_back(capa_inicial);
        }
        
        void agregarCapa( CapaNeuronal& capa);
        std::vector<double> forward(std::vector<double> x);
        void entrenar(std::vector<double> x, std::vector<double> yt, double lr);
};

#endif