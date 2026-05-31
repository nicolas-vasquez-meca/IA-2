#include "RedNeuronal.hpp"
#include "CapaNeuronal.hpp"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono> 

void cargar_datos(std::vector<std::vector<double>>& X, std::vector<std::vector<double>>& Y) {
    std::ifstream archivo("data.txt");
    std::string linea;
    while (std::getline(archivo, linea)) {
        size_t inicio = linea.find('(');
        size_t coma = linea.find(',');
        size_t fin = linea.find(')');
        if (inicio != std::string::npos && coma != std::string::npos && fin != std::string::npos) {
            double x_val = std::stod(linea.substr(inicio + 1, coma - inicio - 1));
            double y_val = std::stod(linea.substr(coma + 1, fin - coma - 1));
            X.push_back({x_val});
            Y.push_back({y_val});
        }
    }
}

int main(int argc, char* argv[]){
    std::vector<std::vector<double>> X_train;
    std::vector<std::vector<double>> Y_train;
    cargar_datos(X_train, Y_train);

    if (X_train.empty()) {
        std::cerr << "Error: No se pudieron cargar los datos." << std::endl;
        return 1;
    }

    std::cout << "Datos cargados: " << X_train.size() << " muestras." << std::endl;

    // 1. Configurar Arquitectura
    CapaNeuronal capa_entrada(1, 20, "sigmoide"); 
    // CapaNeuronal capa_oculta1(20, 20, "sigmoide"); 
    // CapaNeuronal capa_oculta2(20, 20, "sigmoide"); 
    // CapaNeuronal capa_oculta3(20, 20, "sigmoide"); 
    // CapaNeuronal capa_oculta4(20, 20, "sigmoide"); 
    CapaNeuronal capa_salida(20, 1, "lineal");    
    
    RedNeuronal red(capa_entrada);
    // red.agregarCapa(capa_oculta1);
    // red.agregarCapa(capa_oculta2);
    // red.agregarCapa(capa_oculta3);
    // red.agregarCapa(capa_oculta4);
    red.agregarCapa(capa_salida);

    std::cout << "=== CONFIGURACION DEL MODELO ===" << std::endl;
    std::cout << "[-] Total de capas en la Red: 6" << std::endl;
    std::cout << "    -> Capa Entrada 1: 20 neuronas (Activacion: Sigmoide)" << std::endl;
    // std::cout << "    -> Capa Oculta 1 hasta 4: 20 neuronas (Activacion: Sigmoide)" << std::endl;
    std::cout << "    -> Capa de Salida: 1 neurona (Activacion: Lineal)" << std::endl;
    std::cout << "=================================" << std::endl;

    int epocas = 3000;
    double learning_rate = 0.001; 

    std::cout << "\nIniciando entrenamiento..." << std::endl;

    // ---> INICIO DEL CRONÓMETRO <---
    auto inicio_tiempo = std::chrono::high_resolution_clock::now();

    for(int epoca = 0; epoca < epocas; epoca++){
        double error_acumulado = 0.0;
        for(size_t i = 0; i < X_train.size(); i++){
            std::vector<double> x_instancia = X_train[i];
            std::vector<double> target_instancia = Y_train[i];

            std::vector<double> prediccion = red.forward(x_instancia);
            double error = prediccion[0] - target_instancia[0];
            error_acumulado += error * error;

            red.entrenar(x_instancia, target_instancia, learning_rate);
        }
        if(epoca % 500 == 0){
            std::cout << "Epoca " << epoca << " | Error Cuadratico Medio (MSE): " << error_acumulado / X_train.size() << std::endl;
        }
    }

    // ---> FIN DEL CRONÓMETRO <---
    auto fin_tiempo = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duracion = fin_tiempo - inicio_tiempo;

    std::cout << "Entrenamiento finalizado exitosamente." << std::endl;
    std::cout << "[-] Tiempo total de ejecucion: " << duracion.count() << " segundos." << std::endl;

    // 3. Exportar resultados de la regresion para graficar
    std::ofstream archivo_out("predicciones.txt");
    archivo_out << "x,y_real,y_prediccion\n";
    for(size_t i = 0; i < X_train.size(); i++) {
        std::vector<double> pred = red.forward(X_train[i]);
        archivo_out << X_train[i][0] << "," << Y_train[i][0] << "," << pred[0] << "\n";
    }
    archivo_out.close();
    std::cout << "\n[OK] Datos de tendencia guardados en 'predicciones.txt'." << std::endl;

    return 0;
}