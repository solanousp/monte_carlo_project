# Simulação Monte Carlo – Cs-137 com TOPAS (Geant4)

Este projeto realiza a simulação da deposição de energia em um cristal cintilador (GAGG:Ce) utilizando o TOPAS (baseado em Geant4), com uma fonte gama de 662 keV (Cs-137).

O foco é obter e analisar a energia depositada no cristal a partir de dados por evento.

---

## 🎯 Objetivo

- Simular a interação de fótons gama no cristal
- Registrar a energia depositada por evento
- Gerar dados para construção de espectro

---

## ⚙️ Configuração

### Geometria

- Cristal GAGG:Ce (5 × 5 × 10 mm³)
- Gap (vácuo)
- SiPM (apenas geometria)
- Mundo preenchido com ar

### Fonte

- Tipo: pontual isotrópica
- Partícula: gama
- Energia: 662 keV
- Posição: 30 mm antes do cristal

### Física

- Lista eletromagnética padrão (`g4em-standard_opt3`)

---

## 📊 Saída da simulação

O projeto utiliza um scorer customizado:

- Energia depositada acumulada por evento
- Um valor por evento
- Arquivo de saída em formato ASCII/CSV

---

## 🧠 Análise

O script de análise:

- Lê os dados de energia por evento
- Calcula estatísticas básicas:
  - número de eventos
  - fração com interação
  - energia média
  - energia máxima

---

## 📁 Estrutura do projeto

Projeto/
├── Espectro_s_otica.txt
├── analise_event_edep_ascii.py
├── output/
└── output_event/

topas_extensions/
└── scoring/
├── EventEdepCrystal.cc
└── EventEdepCrystal.hh


## 🚀 Execução

### Rodar simulação

```bash
./run_topas.sh Projeto/Espectro_s_otica.txt

python Projeto/analise_event_edep_ascii.py