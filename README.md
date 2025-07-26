# Sistema de Otimização de Horários Acadêmicos com Algoritmos Genéticos

## 📋 Descrição do Projeto - Tech Challenge Fase 2

Este sistema resolve o problema de **alocação de horários acadêmicos** utilizando **Algoritmos Genéticos** com duas abordagens distintas. O objetivo é distribuir disciplinas, professores e salas em horários sem conflitos, respeitando restrições como carga horária, disponibilidade de professores e capacidade das salas.

### 🎯 Objetivos do Sistema

- **Automatizar** o processo manual de criação de horários (redução de 90% do tempo)
- **Minimizar conflitos** de horário (professor/sala em dois lugares ao mesmo tempo)
- **Respeitar disponibilidades** dos professores
- **Distribuir equilibradamente** as disciplinas ao longo da semana
- **Maximizar aproveitamento** dos recursos disponíveis
- **Comparar abordagens** diferentes para o mesmo problema

## 🧬 Duas Abordagens Implementadas

### 🔸 **V1 - Penalização com Lista de Eventos**

```python
# Representação
cromossomo = [
    {'disciplina': 'MAT101', 'professor': 'Prof1', 'dia': 0, 'horario': 1, 'sala': '201'},
    {'disciplina': 'FIS102', 'professor': 'Prof2', 'dia': 1, 'horario': 0, 'sala': '201'},
    # ... mais eventos
]

# Fitness (Penalização)
fitness = 10000 - penalidades + bonificações
```

**💡 Conceito:**
- Modela o problema como uma **lista de eventos/aulas**
- Cada gene representa uma aula completa
- Cromossomo = lista de todos os genes necessários

**🎯 Função de Fitness:**
- Inicia com valor alto (10.000 pontos)
- **Subtrai penalidades** por violações:
  - Conflitos de professor: -1000 pontos
  - Conflitos de sala: -1000 pontos
  - Violações de disponibilidade: -500 pontos
  - Concentração excessiva: -100 pontos
- Adiciona bonificações por qualidades positivas

**✅ Vantagens:**
- Flexibilidade total na estrutura
- Fácil escalar para problemas maiores
- Crossover e mutação intuitivos
- Bom para problemas com restrições variáveis

**⚠️ Desvantagens:**
- Pode não garantir completude das disciplinas
- Fitness negativo confunde interpretação
- Necessita validação externa da solução

---

### 🔹 **V2 - Pontuação com Agenda (Matriz)**

```python
# Representação (matriz 5x4)
agenda[dia][horario] = Aula(disciplina='MAT101', professor='Prof1', sala='201')
agenda[dia][horario] = None  # slot vazio

# Fitness (Pontuação)
fitness = Σ(pontuações_positivas)
```

**📅 Conceito:**
- Modela como uma **agenda real**: matriz 5×4 (dias × horários)
- Cada célula contém uma aula ou está vazia
- Cromossomo = matriz completa da semana
- **Garantia** de que todas as disciplinas são atendidas

**🎯 Função de Fitness:**
- Inicia com zero e **acumula pontuações positivas**:
  - Disciplina completamente atendida: +1000 pontos
  - Disponibilidade respeitada: +500 pontos
  - Distribuição equilibrada: +200 pontos
  - Sem sobrecarga diária: +150 pontos
  - Sem janelas no horário: +100 pontos
  - Professor satisfeito: +80 pontos
  - Sala otimizada: +50 pontos

**✅ Vantagens:**
- **Garantia automática** de completude das disciplinas
- Fitness sempre **positivo e interpretável**
- Visualização natural como horário
- **Reparo automático** de soluções inválidas
- Foco em **maximizar qualidade**

**⚠️ Desvantagens:**
- Estrutura fixa (limitado a 5×4)
- Crossover mais complexo
- Pode desperdiçar slots vagos
- Menos flexível para variações do problema

## 🏗️ Arquitetura da Solução

### Operadores Genéticos

| Operador | V1 (Penalização) | V2 (Pontuação) |
|----------|------------------|----------------|
| **Seleção** | Torneio (tamanho 3-5) | Torneio (tamanho 3-5) |
| **Crossover** | Crossover de ordem (taxa 0.8) | Crossover de blocos (taxa 0.8) |
| **Mutação** | Alteração dia/horário (taxa 0.1) | Troca de slots (taxa 0.15) |
| **Elitismo** | Mantém melhor indivíduo | Mantém 10% melhores |
| **Reparo** | Não implementado | Automático para completude |

### Critérios de Parada

- **Número máximo de gerações**: 1000
- **Estagnação**: 100 gerações sem melhoria (V1) / 50 gerações (V2)
- **Fitness alvo**: > 9500 (V1) / > 12000 (V2)
- **Tempo limite**: 5 minutos por execução

## 📁 Estrutura do Projeto

```
projeto/
├── dados/                           # Dados de entrada
│   ├── disciplinas.xlsx            # Disciplinas e cargas horárias
│   ├── professores.xlsx            # Professores e suas disciplinas
│   ├── salas.xlsx                  # Salas e capacidades
│   ├── turmas.xlsx                 # Turmas e informações
│   └── disponibilidade.xlsx       # Disponibilidade dos professores
├── resultados/                      # Resultados (criada automaticamente)
│   ├── v1_penalizacao_*.xlsx
│   ├── v2_pontuacao_*.xlsx
│   ├── comparacao_v1_v2.xlsx
│   └── analises_parametros_*.xlsx
├── genetic_scheduler.py             # V1 - Penalização com Lista
├── genetic_scheduler_v2.py          # V2 - Pontuação com Agenda
├── visualization_script.py         # Análises e visualizações V1
├── visualization_v2.py             # Análises e visualizações V2
├── utils_v2.py                     # Utilitários específicos V2
├── parameter_optimization.py       # Otimização de parâmetros (V1+V2)
├── comparison_v1_v2.py             # Comparação entre abordagens
├── main_integrated.py              # Sistema integrado principal
└── README.md                       # Esta documentação
```

## 🚀 Como Usar

### 1. Preparação dos Dados

Certifique-se de que os arquivos Excel estão na pasta `dados/` com o formato correto:

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

### 2. Execução do Sistema

#### **Opção 1: Sistema Integrado (Recomendado)**

```bash
python main_integrated.py
```

**Menu disponível:**
```
📋 EXECUÇÃO DAS ABORDAGENS:
1. V1 - Penalização com Lista de Eventos
2. V2 - Pontuação com Agenda (Matriz)
3. Comparação entre V1 e V2

⚙️ FERRAMENTAS AVANÇADAS:
4. Otimização de parâmetros (V1, V2 ou Comparação)
5. Análise completa com visualizações (V1)
6. Análise completa com visualizações (V2)
7. Análise detalhada de agenda (V2)

0. Sair
```

#### **Opção 2: Execução Direta**

```bash
# V1 - Penalização
python genetic_scheduler.py

# V2 - Pontuação
python genetic_scheduler_v2.py

# Comparação
python comparison_v1_v2.py

# Visualizações V1
python visualization_script.py

# Visualizações V2
python visualization_v2.py

# Otimização de parâmetros
python parameter_optimization.py
```

### 3. Configuração de Parâmetros

#### **Parâmetros Recomendados V1:**
```python
ga = ScheduleGA()
ga.populacao_size = 50
ga.geracoes = 300
ga.taxa_mutacao = 0.12
ga.taxa_crossover = 0.8
ga.tamanho_torneio = 3
```

#### **Parâmetros Recomendados V2:**
```python
ga = ScheduleGA_V2()
ga.populacao_size = 50
ga.geracoes = 300
ga.taxa_mutacao = 0.15
ga.taxa_crossover = 0.8
ga.tamanho_torneio = 3
```

## 📊 Saídas do Sistema

### 1. Horário Otimizado (V1)
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

### 2. Agenda Otimizada (V2)
```
================================================================================
📅 AGENDA OTIMIZADA
================================================================================
HORÁRIO    Segunda            Terça              Quarta             Quinta
18:50      CULTURA E SOC.     ALGORITMOS II      SISTEMAS INFO      CÁLCULO
           (ALTAMIR)          (SANDRO)           (ALEXANDRE)        (GERALDO)

19:40      CULTURA E SOC.     ALGORITMOS II      ORGANIZAÇÃO        PROJETO INT.
           (ALTAMIR)          (SANDRO)           (LILIS)            (DIANE)
```

### 3. Relatórios Detalhados

**V1 - Relatório de Conflitos:**
```
📊 MÉTRICAS GERAIS:
   • Fitness final: 9240.00
   • Melhoria total: 1850.00
   • Gerações executadas: 245
   • Total de aulas alocadas: 19

⚠️ ANÁLISE DE CONFLITOS:
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

**V2 - Relatório de Qualidade:**
```
📊 MÉTRICAS GERAIS:
   • Fitness final: 12450 pontos
   • Score geral de qualidade: 87.2%
   • Gerações executadas: 180
   • Melhoria total: 8200 pontos

📚 ANÁLISE ACADÊMICA:
   • Completude das disciplinas: 100.0%
   • Disponibilidade respeitada: 94.7%
   • Equilíbrio na distribuição: 82.5%
   • Utilização de slots: 95.0%
   • Concentração dos professores: 78.3%
```

### 4. Visualizações Disponíveis

#### **V1 - Análises com Penalização:**
- Evolução do fitness (com penalidades)
- Distribuição de aulas por dia/horário
- Análise de conflitos detalhada
- Comparação carga esperada vs alocada
- Mapa de calor da grade horária

#### **V2 - Análises com Pontuação:**
- Evolução do fitness (com pontuações)
- Métricas de qualidade (radar chart)
- Score geral (gauge chart)
- Análise de completude das disciplinas
- Dashboard executivo completo
- Comparação com benchmarks

### 5. Arquivos Salvos Automaticamente

- `v1_penalizacao_YYYYMMDD_HHMMSS.xlsx` - Resultado V1
- `v2_pontuacao_YYYYMMDD_HHMMSS.xlsx` - Resultado V2
- `comparacao_v1_v2.xlsx` - Comparação entre abordagens
- `teste_rapido_parametros_V1.xlsx` - Otimização V1
- `teste_rapido_parametros_V2.xlsx` - Otimização V2

## ⚙️ Otimização de Parâmetros

### Funcionalidades Disponíveis

1. **Otimização V1** - Foca em minimizar penalidades
2. **Otimização V2** - Foca em maximizar pontuações
3. **Comparação V1 vs V2** - Teste simultâneo das abordagens

### Parâmetros Testados

- **Tamanho da população**: 30, 50, 100
- **Taxa de mutação**: 0.05, 0.1, 0.15, 0.2
- **Taxa de crossover**: 0.6, 0.7, 0.8, 0.9
- **Tamanho do torneio**: 3, 5, 7

### Métricas de Avaliação

| Métrica | V1 (Penalização) | V2 (Pontuação) |
|---------|------------------|----------------|
| **Fitness normalizado** | fitness/10000 | fitness/15000 |
| **Tempo de execução** | Segundos | Segundos |
| **Disciplinas completas** | % atendidas | % atendidas |
| **Disponibilidade respeitada** | % respeitada | % respeitada |
| **Convergência** | Gerações até estabilizar | Gerações até estabilizar |

## 🔧 Personalização e Extensões

### Adicionando Novas Restrições

**V1 - Sistema de Penalização:**
```python
def fitness_personalizado(cromossomo):
    penalidades = 0
    
    # Suas restrições personalizadas aqui
    penalidades += minha_restricao_customizada(cromossomo) * peso
    
    return 10000 - penalidades
```

**V2 - Sistema de Pontuação:**
```python
def fitness_personalizado_v2(agenda):
    pontuacao = 0
    
    # Suas métricas de qualidade aqui
    pontuacao += minha_metrica_qualidade(agenda) * peso
    
    return pontuacao
```

### Modificando Operadores

```python
def minha_mutacao_customizada(cromossomo):
    # V1: Implementar sua estratégia de mutação para lista
    return cromossomo_mutado

def minha_mutacao_agenda(agenda):
    # V2: Implementar sua estratégia de mutação para matriz
    return agenda_mutada
```

### Expandindo para Múltiplas Turmas

```python
# Modificar para lidar com várias turmas simultaneamente
def criar_cromossomo_multiturma(self):
    # Implementação para múltiplas turmas
    pass
```

## 📈 Interpretação dos Resultados

### Valores de Fitness

#### **V1 (Penalização):**
- **9500+**: Excelente (poucos ou nenhum conflito)
- **8500-9499**: Bom (conflitos menores)
- **7000-8499**: Regular (alguns conflitos)
- **< 7000**: Ruim (muitos conflitos)

#### **V2 (Pontuação):**
- **12000+**: Excelente (alta qualidade)
- **10000-11999**: Bom (qualidade satisfatória)
- **8000-9999**: Regular (qualidade básica)
- **< 8000**: Ruim (baixa qualidade)

### Indicadores de Qualidade

#### **Ambas as Versões:**
- **Taxa de conflitos**: < 5% é excelente
- **Distribuição equilibrada**: Variação ≤ 1 aula entre dias
- **Aproveitamento de disponibilidade**: > 90%

#### **Específicos V2:**
- **Completude de disciplinas**: Deve ser 100%
- **Score geral de qualidade**: > 80% é excelente
- **Utilização de slots**: > 85% é boa

## 🎯 Qual Abordagem Escolher?

### 🔸 **Escolha V1 (Penalização) quando:**
- Número de aulas varia muito
- Flexibilidade é mais importante que garantias
- Quer focar em **evitar violações específicas**
- Problema tem muitas restrições hard
- Precisa escalar para problemas muito grandes
- **Interpretação tradicional** de otimização

### 🔹 **Escolha V2 (Pontuação) quando:**
- Todas as disciplinas **DEVEM ser atendidas**
- Quer **interpretação intuitiva** do fitness
- Visualização como agenda é importante
- Foco é **maximizar qualidade** da solução
- Estrutura de horário é relativamente fixa
- Prefere **abordagem construtiva**

## 🚨 Solução de Problemas

### Problema: Fitness muito baixo (V1)
**Soluções:**
- Verificar disponibilidades dos professores
- Aumentar tamanho da população
- Ajustar pesos das penalidades
- Verificar consistência dos dados

### Problema: Score baixo (V2)
**Soluções:**
- Verificar se todas as disciplinas estão sendo alocadas
- Ajustar pesos de pontuação
- Aumentar taxa de mutação
- Verificar função de reparo

### Problema: Não converge
**Soluções:**
- Aumentar número de gerações
- Ajustar taxa de mutação
- Implementar reinicialização
- Verificar operadores genéticos

### Problema: Muitos conflitos
**Soluções:**
- Verificar dados de disponibilidade
- Aumentar penalidades de conflitos (V1)
- Melhorar inicialização
- Ajustar operadores de crossover

## 📋 Dependências

```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

### Versões Testadas
- Python 3.8+
- pandas 1.3+
- numpy 1.20+
- matplotlib 3.3+
- seaborn 0.11+
- openpyxl 3.0+


### Entregáveis

1. **Código no GitHub**: Repositório "Tech Challenge"
2. **Vídeo no YouTube**: Demonstração das duas abordagens
3. **Documento PDF**: Links do GitHub e YouTube

## 🏆 Resultados Esperados

- **Redução de 90%** no tempo de elaboração de horários
- **Eliminação de conflitos** de professor/sala
- **Otimização automática** de múltiplos critérios
- **Comparação científica** entre abordagens distintas
- **Sistema escalável** e reutilizável
- **Visualizações avançadas** para análise

## 💡 Inovações Implementadas

1. **Duas modelagens** do mesmo problema de otimização
2. **Sistema de pontuação positiva** vs penalização tradicional
3. **Garantia automática** de completude das disciplinas (V2)
4. **Comparação sistemática** entre abordagens
5. **Otimização automática** de parâmetros para ambas versões
6. **Visualizações específicas** para cada abordagem
7. **Sistema integrado** com menu unificado

---

**Desenvolvido para o Tech Challenge - Fase 2**  
**Algoritmos Genéticos aplicados à Otimização de Horários Acadêmicos**  
**Duas Abordagens: Penalização vs Pontuação**