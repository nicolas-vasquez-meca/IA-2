#include "CapaNeuronal.hpp"
#include "vector"


size_t CapaNeuronal::get_size_neuronas() const{
    return this->num_neuronas;
}

size_t CapaNeuronal::get_size_entradas() const{
    return this->num_entradas;
}

double CapaNeuronal::f(double z) const{
    if(this->tipo_de_funcion == "sigmoide"){
        return 1.0 / (1.0 + std::exp(-z));
    } else if (this->tipo_de_funcion == "lineal") {
        return z; // Activación lineal (identidad)
    }
    return 0.0;
}

double CapaNeuronal::df(double z) const{
    if(this->tipo_de_funcion == "sigmoide"){
        double salida = f(z);
        return salida * (1 - salida);
    } else if (this->tipo_de_funcion == "lineal") {
        return 1.0; // La derivada de z respecto a z es 1
    }
    return 0.0;
}

std::vector<double> CapaNeuronal::forward(const std::vector<double>& x) const {
    if (x.size() != num_entradas) {
        throw std::runtime_error("Entrada de tamaño incorrecto");
    }

    std::vector<double> y(num_neuronas);

    for (size_t i = 0; i < num_neuronas; i++) {
        double z = B[i];

        for (size_t j = 0; j < num_entradas; j++) {
            z += W[i * num_entradas + j] * x[j];
        }

        y[i] = f(z);
    }

    return y;
}


std::vector<double> CapaNeuronal::entrenar(
    const std::vector<double>& dL_da,
    const std::vector<double>& x,
    double lr
)
{
    std::vector<double> delta(num_neuronas, 0.0);
    std::vector<double> dL_dx(num_entradas, 0.0);

    // 1. Calcular delta de cada neurona
    for (size_t i = 0; i < this->num_neuronas; i++)
    {
        double z = this->B[i];

        for (size_t j = 0; j < this->num_entradas; j++)
        {
            z += W[i * num_entradas + j] * x[j];
        }

        delta[i] = dL_da[i] * df(z);
    }

    // 2. Calcular derivada para la capa anterior ANTES de actualizar W
    for (size_t j = 0; j < this->num_entradas; j++)
    {
        for (size_t i = 0; i < this->num_neuronas; i++)
        {
            dL_dx[j] += delta[i] * W[i * num_entradas + j];
        }
    }

    // 3. Actualizar pesos y bias
    for (size_t i = 0; i < this->num_neuronas; i++)
    {
        for (size_t j = 0; j < this->num_entradas; j++)
        {
            double dL_dW = delta[i] * x[j];
            W[i * num_entradas + j] -= lr * dL_dW;
        }

        B[i] -= lr * delta[i];
    }

    // 4. Devolver derivada heredada para la capa anterior
    return dL_dx;
}

///////////////////////////// Funciones ///////////////////////////////////