# Sistema de Otimização de Horários Acadêmicos com Algoritmos Genéticos

## 📋 Descrição do Projeto

Este sistema resolve o problema de **alocação de horários acadêmicos** utilizando **Algoritmos Genéticos**. O objetivo é distribuir disciplinas, professores e salas em horários sem conflitos, respeitando restrições como carga horária, disponibilidade de professores e capacidade das salas.

### 🎯 Objetivos do Sistema

- **Minimizar conflitos** de horário (professor/sala em dois lugares ao mesmo tempo)
- **Respeitar disponibilidades** dos professores
- **Distribuir equilibradamente** as disciplinas ao longo da semana
- **Maximizar aproveitamento** dos recursos disponíveis

## 🏗️ Arquitetura da Solução

### Representação do Problema (Genoma)
```python
# Cada gene representa uma aula
gene = {
    'disciplina': '0223SI0006',    # Código da disciplina
    'professor': '20224',          # Código do professor
    'dia': 0,                      # 0=Segunda, 1=Terça, ..., 4=Sexta
    'horario': 1,                  # 0=18:50, 1=19:40, 2=20:30, 3=21:20
    'sala': '201'                  # Código da sala
}
```

### Função de Fitness
```python
def fitness(cromossomo):
    penalidades = 0
    
    # Penalidades graves (conflitos)
    penalidades += conflitos_professor(cromossomo) * 1000
    penalidades += conflitos_sala(cromossomo) * 1000
    penalidades += violacoes_disponibilidade(cromossomo) * 500
    
    # Penalidades moderadas (qualidade)
    penalidades += concentracao_disciplinas(cromossomo) * 100
    penalidades += janelas_horario(cromossomo) * 50
    
    # Bonificações
    bonus = distribuicao_equilibrada(cromossomo) * 10
    
    return 10000 - penalidades + bonus
```

### Operadores Genéticos

- **Seleção**: Torneio (tamanho 3-5)
- **Crossover**: Crossover de ordem adaptado (taxa 0.8)
- **Mutação**: Alteração aleatória de dia/horário (taxa 0.1)
- **Elitismo**: Mantém o melhor indivíduo

## 📁 Estrutura dos Arquivos

```
projeto/
├── dados/
│   ├── disciplinas.xlsx      # Disciplinas e cargas horárias
│   ├── professores.xlsx      # Professores e suas disciplinas
│   ├── salas.xlsx           # Salas e capacidades
│   ├── turmas.xlsx          # Turmas e informações
│   └── disponibilidade.xlsx # Disponibilidade dos professores
├── resultados/              # Pasta criada automaticamente
│   ├── horario_otimizado_*.xlsx
│   └── analises_parametros_*.xlsx
├── genetic_scheduler.py     # Algoritmo genético principal
├── visualization_script.py # Análises e visualizações
├── parameter_optimization.py # Otimização de parâmetros
└── README.md               # Este arquivo
```

## 🚀 Como Usar

### 1. Preparação dos Dados

Certifique-se de que os arquivos Excel estão no formato correto:

**disciplinas.xlsx**
```
CODDISC        | NOME                    | CARGAHORARIA | PERIODO | CODTURMA
0223SI0006     | CULTURA E SOCIEDADE     | 4            | 2       | SIN-2A-N
```

**professores.xlsx**
```
CODPROF | NOME     | CODDISC
20224   | ALTAMIR  | 0223SI0006
```

**salas.xlsx**
```
CODSALA | NOME     | CAPACIDADE
201     | SALA 201 | 60
```

**turmas.xlsx**
```
CODTURMA | SEMESTRE | CURSO                  | QUANTIDADE_ALUNOS | TURNO   | PERIODO
SIN-2A-N | 2/2025   | SISTEMAS DE INFORMAÇÃO | 53                | noturno | 2
```

**disponibilidade.xlsx**
```
CODPROF | TURNO   | DIADASEMANA | HORARIO
20224   | Noturno | Segunda     | 18:50
```

### 2. Execução Básica

```python
from genetic_scheduler import ScheduleGA

# Criar e executar o algoritmo
ga = ScheduleGA()
melhor_solucao, fitness, historico = ga.executar()

# Exibir o horário otimizado
ga.exibir_horario(melhor_solucao)
```

### 3. Análise Completa com Visualizações

```python
from visualization_script import executar_analise_completa

# Executa AG + análises + gráficos + relatório
solucao, fitness, historico, ga_instance, df_prof = executar_analise_completa()
```

### 4. Otimização de Parâmetros

```python
from parameter_optimization import executar_teste_rapido

# Encontra os melhores parâmetros
melhor_config = executar_teste_rapido()
```

## 📊 Saídas do Sistema

### 1. Horário Otimizado
```
================================================================================
HORÁRIO GERADO
================================================================================
HORÁRIO  Segunda                  Terça                    Quarta
18:50    CULTURA E SOCIEDADE       ALGORITMOS II            SISTEMAS DE INFORMAÇÃO
         Prof: ALTAMIR             Prof: SANDRO             Prof: ALEXANDRE
         Sala: 201                 Sala: 201                Sala: 201

19:40    CULTURA E SOCIEDADE       ALGORITMOS II            ORGANIZAÇÃO E ARQUIT.
         Prof: ALTAMIR             Prof: SANDRO             Prof: LILIS
         Sala: 201                 Sala: 201                Sala: 201
```

### 2. Relatório de Análise
```
📊 MÉTRICAS GERAIS:
   • Fitness final: 9240.00
   • Melhoria total: 1850.00
   • Gerações executadas: 245
   • Total de aulas alocadas: 19

⚠️  ANÁLISE DE CONFLITOS:
   • Conflitos de professor: 0
   • Conflitos de sala: 0
   • Violações de disponibilidade: 2

📅 DISTRIBUIÇÃO POR DIA:
   • Segunda: 4 aulas
   • Terça: 4 aulas
   • Quarta: 4 aulas
   • Quinta: 4 aulas
   • Sexta: 3 aulas
```

### 3. Gráficos de Evolução

- **Evolução do fitness** ao longo das gerações
- **Distribuição de aulas** por dia e horário
- **Mapa de calor** da grade horária
- **Análise de carga** dos professores

## ⚙️ Configuração de Parâmetros

### Parâmetros Principais

```python
class ScheduleGA:
    def __init__(self):
        self.populacao_size = 50        # Tamanho da população
        self.geracoes = 1000           # Número máximo de gerações
        self.taxa_mutacao = 0.1        # Taxa de mutação (0.0-1.0)
        self.taxa_crossover = 0.8      # Taxa de crossover (0.0-1.0)
        self.tamanho_torneio = 3       # Tamanho do torneio
```

### Ajuste Fino

Para problemas menores (como o exemplo):
- **População**: 30-50 indivíduos
- **Mutação**: 0.1-0.15
- **Crossover**: 0.7-0.8

Para problemas maiores:
- **População**: 100-200 indivíduos
- **Mutação**: 0.05-0.1
- **Crossover**: 0.8-0.9

## 🔧 Personalização

### Adicionando Novas Restrições

```python
def fitness_personalizado(cromossomo):
    penalidades = 0
    
    # Suas restrições personalizadas aqui
    penalidades += minha_restricao_customizada(cromossomo) * peso
    
    return 10000 - penalidades
```

### Modificando Operadores

```python
def minha_mutacao_customizada(cromossomo):
    # Implementar sua estratégia de mutação
    return cromossomo_mutado
```

## 📈 Interpretação dos Resultados

### Valores de Fitness

- **9500+**: Excelente (poucos ou nenhum conflito)
- **8500-9499**: Bom (conflitos menores)
- **7000-8499**: Regular (alguns conflitos)
- **< 7000**: Ruim (muitos conflitos)

### Indicadores de Qualidade

- **Taxa de conflitos**: < 5% é excelente
- **Distribuição equilibrada**: Variação ≤ 1 aula entre dias
- **Aproveitamento de disponibilidade**: > 90%

## 🚨 Solução de Problemas

### Problema: Fitness muito baixo
**Soluções:**
- Verificar disponibilidades dos professores
- Aumentar tamanho da população
- Ajustar pesos das penalidades

### Problema: Não converge
**Soluções:**
- Aumentar número de gerações
- Ajustar taxa de mutação
- Implementar reinicialização

### Problema: Muitos conflitos
**Soluções:**
- Verificar consistência dos dados
- Aumentar penalidades de conflitos
- Melhorar inicialização

## 📚 Extensões Possíveis

### 1. Múltiplas Turmas
```python
# Modificar para lidar com várias turmas simultaneamente
def criar_cromossomo_multiturma(self):
    # Implementação para múltiplas turmas
    pass
```

### 2. Preferências de Professores
```python
# Adicionar sistema de preferências
def penalidade_preferencia(cromossomo):
    # Penalizar horários não preferidos
    pass
```

### 3. Otimização Multi-objetivo
```python
# Usar NSGA-II para múltiplos objetivos
from deap import creator, base, tools
```

### 4. Interface Gráfica
```python
# Criar interface com tkinter ou Streamlit
import streamlit as st
```

### Entregáveis

1. **Código no GitHub**: Repositório "Tech Challenge"
2. **Vídeo no YouTube**: Link na descrição com explicação
3. **Documento PDF**: Links do GitHub e YouTube
