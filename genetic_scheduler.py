import pandas as pd
import numpy as np
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import copy

@dataclass
class Disciplina:
    codigo: str
    nome: str
    carga_horaria: int
    periodo: int
    turma: str

@dataclass
class Professor:
    codigo: str
    nome: str
    disciplina: str

@dataclass
class Sala:
    codigo: str
    nome: str
    capacidade: int

@dataclass
class Turma:
    codigo: str
    semestre: str
    curso: str
    quantidade_alunos: int
    turno: str
    periodo: int

@dataclass
class Disponibilidade:
    professor: str
    turno: str
    dia: str
    horario: str

class ScheduleGA:
    def __init__(self):
        # Mapeamentos para facilitar o processamento
        self.dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        self.horarios = ['18:50', '19:40', '20:30', '21:20']
        self.disciplinas = {}
        self.professores = {}
        self.salas = {}
        self.turmas = {}
        self.disponibilidades = {}
        
        # Parâmetros do AG
        self.populacao_size = 50
        self.geracoes = 1000
        self.taxa_mutacao = 0.1
        self.taxa_crossover = 0.8
        self.tamanho_torneio = 3
        
    def carregar_dados(self):
        """Carrega os dados dos arquivos Excel"""
        
        # Definir caminho da pasta de dados
        pasta_dados = 'dados/'
        
        # Carregar disciplinas
        df_disc = pd.read_excel(pasta_dados + 'disciplinas.xlsx')
        for _, row in df_disc.iterrows():
            self.disciplinas[row['CODDISC']] = Disciplina(
                codigo=row['CODDISC'],
                nome=row['NOME'],
                carga_horaria=row['CARGAHORARIA'],
                periodo=row['PERIODO'],
                turma=row['CODTURMA']
            )
        
        # Carregar professores
        df_prof = pd.read_excel(pasta_dados + 'professores.xlsx')
        for _, row in df_prof.iterrows():
            self.professores[row['CODPROF']] = Professor(
                codigo=row['CODPROF'],
                nome=row['NOME'],
                disciplina=row['CODDISC']
            )
        
        # Carregar salas
        df_salas = pd.read_excel(pasta_dados + 'salas.xlsx')
        for _, row in df_salas.iterrows():
            self.salas[row['CODSALA']] = Sala(
                codigo=row['CODSALA'],
                nome=row['NOME'],
                capacidade=row['CAPACIDADE']
            )
        
        # Carregar turmas
        df_turmas = pd.read_excel(pasta_dados + 'turmas.xlsx')
        for _, row in df_turmas.iterrows():
            self.turmas[row['CODTURMA']] = Turma(
                codigo=row['CODTURMA'],
                semestre=row['SEMESTRE'],
                curso=row['CURSO'],
                quantidade_alunos=row['QUANTIDADE_ALUNOS'],
                turno=row['TURNO'],
                periodo=row['PERIODO']
            )
        
        # Carregar disponibilidades
        df_disp = pd.read_excel(pasta_dados + 'disponibilidade.xlsx')
        for _, row in df_disp.iterrows():
            prof = row['CODPROF']
            if prof not in self.disponibilidades:
                self.disponibilidades[prof] = []
            self.disponibilidades[prof].append(Disponibilidade(
                professor=prof,
                turno=row['TURNO'],
                dia=row['DIADASEMANA'],
                horario=row['HORARIO']
            ))
    
    def criar_gene(self, disciplina_codigo: str) -> Dict:
        """Cria um gene representando uma aula"""
        # Encontrar professor da disciplina
        professor = None
        for prof_codigo, prof in self.professores.items():
            if prof.disciplina == disciplina_codigo:
                professor = prof_codigo
                break
        
        return {
            'disciplina': disciplina_codigo,
            'professor': professor,
            'dia': random.choice(range(len(self.dias))),
            'horario': random.choice(range(len(self.horarios))),
            'sala': list(self.salas.keys())[0]  # Por enquanto só temos uma sala
        }
    
    def criar_cromossomo(self) -> List[Dict]:
        """Cria um cromossomo (solução completa)"""
        cromossomo = []
        
        # Para cada disciplina, criar o número de aulas necessário
        for disc_codigo, disciplina in self.disciplinas.items():
            for _ in range(disciplina.carga_horaria):
                gene = self.criar_gene(disc_codigo)
                cromossomo.append(gene)
        
        return cromossomo
    
    def inicializar_populacao(self) -> List[List[Dict]]:
        """Inicializa a população"""
        populacao = []
        for _ in range(self.populacao_size):
            cromossomo = self.criar_cromossomo()
            populacao.append(cromossomo)
        return populacao
    
    def avaliar_fitness(self, cromossomo: List[Dict]) -> float:
        """Avalia o fitness de um cromossomo"""
        penalidades = 0
        bonus = 0
        
        # Verificar conflitos de professor
        professor_horarios = {}
        for gene in cromossomo:
            key = (gene['professor'], gene['dia'], gene['horario'])
            if key in professor_horarios:
                penalidades += 1000  # Conflito grave
            else:
                professor_horarios[key] = True
        
        # Verificar conflitos de sala
        sala_horarios = {}
        for gene in cromossomo:
            key = (gene['sala'], gene['dia'], gene['horario'])
            if key in sala_horarios:
                penalidades += 1000  # Conflito grave
            else:
                sala_horarios[key] = True
        
        # Verificar disponibilidade dos professores
        for gene in cromossomo:
            professor = gene['professor']
            dia_nome = self.dias[gene['dia']]
            horario_nome = self.horarios[gene['horario']]
            
            disponivel = False
            if professor in self.disponibilidades:
                for disp in self.disponibilidades[professor]:
                    if disp.dia == dia_nome and disp.horario == horario_nome:
                        disponivel = True
                        break
            
            if not disponivel:
                penalidades += 500  # Violação de disponibilidade
        
        # Avaliar distribuição das disciplinas
        disciplina_dias = {}
        for gene in cromossomo:
            disc = gene['disciplina']
            if disc not in disciplina_dias:
                disciplina_dias[disc] = set()
            disciplina_dias[disc].add(gene['dia'])
        
        # Bonificar disciplinas bem distribuídas
        for disc, dias_utilizados in disciplina_dias.items():
            carga = self.disciplinas[disc].carga_horaria
            if len(dias_utilizados) == min(carga, 5):  # Ideal: um dia por aula
                bonus += 50
        
        # Penalizar concentração excessiva em um dia
        aulas_por_dia = [0] * 5
        for gene in cromossomo:
            aulas_por_dia[gene['dia']] += 1
        
        max_aulas_dia = max(aulas_por_dia)
        if max_aulas_dia > 4:  # Máximo recomendado por dia
            penalidades += (max_aulas_dia - 4) * 100
        
        return 10000 - penalidades + bonus
    
    def selecao_torneio(self, populacao: List[List[Dict]], fitness_scores: List[float]) -> List[Dict]:
        """Seleção por torneio"""
        indices = random.sample(range(len(populacao)), self.tamanho_torneio)
        melhor_indice = max(indices, key=lambda i: fitness_scores[i])
        return copy.deepcopy(populacao[melhor_indice])
    
    def crossover(self, pai1: List[Dict], pai2: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Crossover de ordem adaptado"""
        if random.random() > self.taxa_crossover:
            return copy.deepcopy(pai1), copy.deepcopy(pai2)
        
        tamanho = len(pai1)
        ponto1 = random.randint(0, tamanho // 2)
        ponto2 = random.randint(ponto1, tamanho)
        
        filho1 = copy.deepcopy(pai1)
        filho2 = copy.deepcopy(pai2)
        
        # Trocar segmento entre os pontos
        filho1[ponto1:ponto2] = pai2[ponto1:ponto2]
        filho2[ponto1:ponto2] = pai1[ponto1:ponto2]
        
        return filho1, filho2
    
    def mutacao(self, cromossomo: List[Dict]) -> List[Dict]:
        """Mutação do cromossomo"""
        cromossomo_mutado = copy.deepcopy(cromossomo)
        
        for i, gene in enumerate(cromossomo_mutado):
            if random.random() < self.taxa_mutacao:
                # Mutar dia ou horário aleatoriamente
                if random.choice([True, False]):
                    gene['dia'] = random.choice(range(len(self.dias)))
                else:
                    gene['horario'] = random.choice(range(len(self.horarios)))
        
        return cromossomo_mutado
    
    def executar(self) -> Tuple[List[Dict], float, List[float]]:
        """Executa o algoritmo genético"""
        print("Carregando dados...")
        self.carregar_dados()
        
        print("Inicializando população...")
        populacao = self.inicializar_populacao()
        
        historico_fitness = []
        melhor_global = None
        melhor_fitness_global = float('-inf')
        
        print("Iniciando evolução...")
        for geracao in range(self.geracoes):
            # Avaliar fitness
            fitness_scores = [self.avaliar_fitness(ind) for ind in populacao]
            
            # Encontrar melhor da geração
            melhor_fitness_geracao = max(fitness_scores)
            melhor_indice = fitness_scores.index(melhor_fitness_geracao)
            
            if melhor_fitness_geracao > melhor_fitness_global:
                melhor_fitness_global = melhor_fitness_geracao
                melhor_global = copy.deepcopy(populacao[melhor_indice])
            
            historico_fitness.append(melhor_fitness_geracao)
            
            # Log do progresso
            if geracao % 100 == 0:
                print(f"Geração {geracao}: Melhor fitness = {melhor_fitness_geracao:.2f}")
            
            # Verificar critério de parada
            if melhor_fitness_geracao >= 9500:  # Solução quase perfeita
                print(f"Solução ótima encontrada na geração {geracao}!")
                break
            
            # Criar nova população
            nova_populacao = []
            
            # Elitismo: manter o melhor
            nova_populacao.append(copy.deepcopy(populacao[melhor_indice]))
            
            # Gerar resto da população
            while len(nova_populacao) < self.populacao_size:
                pai1 = self.selecao_torneio(populacao, fitness_scores)
                pai2 = self.selecao_torneio(populacao, fitness_scores)
                
                filho1, filho2 = self.crossover(pai1, pai2)
                
                filho1 = self.mutacao(filho1)
                filho2 = self.mutacao(filho2)
                
                nova_populacao.extend([filho1, filho2])
            
            # Ajustar tamanho da população
            populacao = nova_populacao[:self.populacao_size]
        
        print(f"Evolução finalizada. Melhor fitness: {melhor_fitness_global:.2f}")
        return melhor_global, melhor_fitness_global, historico_fitness
    
    def exibir_horario(self, cromossomo: List[Dict]):
        """Exibe o horário de forma organizada"""
        print("\n" + "="*80)
        print("HORÁRIO GERADO")
        print("="*80)
        
        # Criar grade de horários
        grade = {}
        for dia_idx, dia in enumerate(self.dias):
            grade[dia] = {}
            for horario_idx, horario in enumerate(self.horarios):
                grade[dia][horario] = []
        
        # Preencher grade
        for gene in cromossomo:
            dia = self.dias[gene['dia']]
            horario = self.horarios[gene['horario']]
            disciplina = self.disciplinas[gene['disciplina']]
            professor = self.professores[gene['professor']]
            
            info = f"{disciplina.nome[:30]}\nProf: {professor.nome}\nSala: {gene['sala']}"
            grade[dia][horario].append(info)
        
        # Exibir grade
        print(f"{'HORÁRIO':<8}", end="")
        for dia in self.dias:
            print(f"{dia:<25}", end="")
        print()
        print("-" * 130)
        
        for horario in self.horarios:
            print(f"{horario:<8}", end="")
            for dia in self.dias:
                aulas = grade[dia][horario]
                if aulas:
                    print(f"{aulas[0][:23]:<25}", end="")
                else:
                    print(f"{'LIVRE':<25}", end="")
            print()
            print()

# Exemplo de uso
if __name__ == "__main__":
    # Criar e executar o algoritmo genético
    ga = ScheduleGA()
    
    melhor_solucao, fitness, historico = ga.executar()
    
    # Exibir resultados
    ga.exibir_horario(melhor_solucao)
    
    # Estatísticas
    print(f"\nFitness da melhor solução: {fitness:.2f}")
    print(f"Melhoria durante evolução: {historico[-1] - historico[0]:.2f}")