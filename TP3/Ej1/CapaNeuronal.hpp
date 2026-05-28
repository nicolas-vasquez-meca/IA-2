#ifndef _CAPANEURONAL_
#define _CAPANEURONAL_

#include <iostream>
#include <vector>
#include <cmath>
#include <random>

/*

Neurona:
y = sig( w_1.m * x_m.1 + b )

Capa:
y_n.1 = sig( W_nm * x_m.1 + b_n.1 )

Ejemplo caso 3 neuronas y 5 entradas:

y_n.1 = f(W_m.n * x_m.1 + b_n.1) 
                                  | 1.7 |
         (    | coefs N1 |        | 1.5 |   | 0.2 |    )
y = f_act(    | coefs N2 |     *  | 4.2 | + | 0.3 |    )
         (    | coefs N3 |        | 3.3 |   | 0.1 |    )
                                  | 8.9 |
*/

class CapaNeuronal {
    private:
        size_t num_entradas;
        size_t num_neuronas;
        std::string tipo_de_funcion;

        std::vector<double> W; 
        std::vector<double> B;

    public:
        CapaNeuronal(size_t entradas, size_t neuronas, const std::string f_activacion)
            : num_entradas(entradas),
            num_neuronas(neuronas),
            tipo_de_funcion(f_activacion),
            W(entradas * neuronas),
            B(neuronas)
        {
            std::mt19937 gen(123);
            std::uniform_real_distribution<double> dist(-0.2, 0.2);

            for (auto& peso : W) {
                peso = dist(gen);
            }
            for (auto& b : B) {
                b = dist(gen);
            }
        }

        size_t get_size_neuronas() const;
        size_t get_size_entradas() const;
        double f(double z) const;
        double df(double z) const;

        std::vector<double> forward(const std::vector<double>& x) const;

        // Retorna el vector de derivadas de cada neurona para esta capa
        std::vector<double> entrenar(const std::vector<double>& dL_da,
                                     const std::vector<double>& x,
                                     double lr);
};

#endif