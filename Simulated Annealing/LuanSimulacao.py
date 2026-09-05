import numpy as np
import random
import math

# 1. Coordenadas aproximadas (Latitude, Longitude) dos pontos em Goiânia
pontos_goiania = {
    'Campinas': (-16.6689, -49.2882),
    'Regiao 44': (-16.6644, -49.2598),
    'Setor Bueno': (-16.7025, -49.2662),
    'Flamboyant': (-16.7091, -49.2344),
    'Setor Sul': (-16.6892, -49.2592)
}

nomes_pontos = list(pontos_goiania.keys())
num_pontos = len(nomes_pontos)

# 2. Função para calcular a distância total de uma rota
def calcular_distancia_total(rota):
    distancia = 0
    for i in range(len(rota)):
        p1 = pontos_goiania[rota[i]]
        # Retorna ao início se for o último ponto
        p2 = pontos_goiania[rota[(i + 1) % len(rota)]] 
        distancia += math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
    return distancia

# 3. Parâmetros do Recozimento Simulado (Simulated Annealing)
temperatura_inicial = 100.0
temperatura_final = 0.01
taxa_resfriamento = 0.99
passos_por_temp = 50

# Estado inicial (Rota aleatória)
rota_atual = nomes_pontos.copy()
random.shuffle(rota_atual)
distancia_atual = calcular_distancia_total(rota_atual)

melhor_rota = rota_atual.copy()
melhor_distancia = distancia_atual

t = temperatura_inicial

# 4. Loop de Otimização
while t > temperatura_final:
    for _ in range(passos_por_temp):
        # Gera uma nova rota vizinha trocando dois pontos de lugar
        nova_rota = rota_atual.copy()
        idx1, idx2 = random.sample(range(num_pontos), 2)
        nova_rota[idx1], nova_rota[idx2] = nova_rota[idx2], nova_rota[idx1]
        
        nova_distancia = calcular_distancia_total(nova_rota)
        diff_energia = nova_distancia - distancia_atual
        
        # Critério de Aceitação de Metropolis
        if diff_energia < 0 or random.random() < math.exp(-diff_energia / t):
            rota_atual = nova_rota.copy()
            distancia_atual = nova_distancia
            
            # Atualiza o recorde global
            if distancia_atual < melhor_distancia:
                melhor_rota = rota_atual.copy()
                melhor_distancia = distancia_atual
                
    # Resfriamento do sistema
    t *= taxa_resfriamento

print(f"🚚 Rota Otimizada para Goiânia: {' -> '.join(melhor_rota)} -> {melhor_rota[0]}")