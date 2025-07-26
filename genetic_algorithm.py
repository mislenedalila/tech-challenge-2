import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, time
import json
from typing import List, Dict, Tuple
import copy
import os

def verificar_arquivos():
    """Verifica se todos os arquivos necessários existem."""
    pasta_dados = 'dados'
    arquivos_necessarios = [
        'disciplinas.xlsx',
        'professores.xlsx', 
        'salas.xlsx',
        'turmas.xlsx',
        'disponibilidadeProfessor.xlsx'
    ]
    
    print("🔍 VERIFICANDO ARQUIVOS DE DADOS...")
    
    if not os.path.exists(pasta_dados):
        print(f"Pasta '{pasta_dados}' não encontrada!")
        print(f"Criando pasta '{pasta_dados}'...")
        os.makedirs(pasta_dados)
        print(f"Pasta '{pasta_dados}' criada!")
        print(f"\nINSTRUÇÕES:")
        print(f"   1. Coloque os seguintes arquivos na pasta '{pasta_dados}/':")
        for arquivo in arquivos_necessarios:
            print(f"      - {arquivo}")
        print(f"   2. Execute o script novamente")
        return False
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        caminho_completo = os.path.join(pasta_dados, arquivo)
        if not os.path.exists(caminho_completo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"Arquivos não encontrados na pasta '{pasta_dados}/':")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        print(f"\nColoque os arquivos na pasta '{pasta_dados}/' e execute novamente")
        return False
    
    print(f"✅ Todos os arquivos encontrados na pasta '{pasta_dados}/'!")
    return True

def carregar_dados():
    """Função para carregar os dados dos arquivos Excel da pasta dados/."""
    pasta_dados = 'dados'
    
    print("Carregando dados dos arquivos...")
    
    try:
        disciplinas = pd.read_excel(os.path.join(pasta_dados, 'disciplinas.xlsx'))
        professores = pd.read_excel(os.path.join(pasta_dados, 'professores.xlsx'))
        salas = pd.read_excel(os.path.join(pasta_dados, 'salas.xlsx'))
        turmas = pd.read_excel(os.path.join(pasta_dados, 'turmas.xlsx'))
        disponibilidade = pd.read_excel(os.path.join(pasta_dados, 'disponibilidadeProfessor.xlsx'))
        
        print(f"✅ Dados carregados com sucesso!")
        print(f"   - Disciplinas: {len(disciplinas)} registros")
        print(f"   - Professores: {len(professores)} registros")
        print(f"   - Salas: {len(salas)} registros")
        print(f"   - Turmas: {len(turmas)} registros")
        print(f"   - Disponibilidade: {len(disponibilidade)} registros")
        
        return disciplinas, professores, salas, turmas, disponibilidade
        
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return None, None, None, None, None

class GeneticScheduler:
    """Classe principal para implementação do Algoritmo Genético."""
    
    def __init__(self, dados_disciplinas, dados_professores, dados_salas, dados_turmas, dados_disponibilidade):
        self.disciplinas = dados_disciplinas
        self.professores = dados_professores
        self.salas = dados_salas
        self.turmas = dados_turmas
        self.disponibilidade = dados_disponibilidade
        
        # Parâmetros do Algoritmo Genético
        self.tamanho_populacao = 80
        self.taxa_mutacao = 0.15
        self.taxa_crossover = 0.8
        self.taxa_elitismo = 0.1
        self.max_geracoes = 500
        self.geracoes_sem_melhoria = 100
        
        # HORÁRIOS NOTURNOS CORRETOS: 18:50 às 22:20 (4 períodos de 50min)
        self.dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        self.horarios_noturnos = ['18:50', '19:40', '20:30', '21:20']
        
        print("Processando dados...")
        
        # Mapear habilitações dos professores
        self.prof_disciplinas = self._mapear_habilitacoes()
        print(f"Habilitações mapeadas: {len(self.prof_disciplinas)} professores")
        
        # Mapear disponibilidade dos professores
        self.prof_disponibilidade = self._processar_disponibilidade()
        print(f"Disponibilidade processada: {len(self.prof_disponibilidade)} professores")
        
        # Criar estrutura das aulas necessárias
        self.aulas_necessarias = self._criar_aulas_necessarias()
        print(f"Aulas necessárias criadas: {len(self.aulas_necessarias)} aulas")
        
        # Mapear disciplinas por turma
        self.disciplinas_por_turma = self._mapear_disciplinas_turma()
        
        # Histórico de fitness
        self.historico_fitness = []
        
    def _mapear_habilitacoes(self):
        """Mapeia quais disciplinas cada professor pode lecionar."""
        mapa = {}
        for _, prof in self.professores.iterrows():
            try:
                disciplinas_hab = str(prof['DISCIPLINASHABILITADAS']).split(';')
                mapa[prof['CODPROF']] = [d.strip() for d in disciplinas_hab if d.strip()]
            except:
                mapa[prof['CODPROF']] = []
        return mapa
    
    def _processar_disponibilidade(self):
        """Processa a disponibilidade dos professores."""
        disponibilidade_map = {}
        
        for _, disp in self.disponibilidade.iterrows():
            try:
                prof_id = disp['CODPROF']
                if prof_id not in disponibilidade_map:
                    disponibilidade_map[prof_id] = []
                
                horario = self._processar_horario(disp['HORARIO'])
                dia = str(disp['DIADASEMANA']).strip()
                turno = str(disp['TURNO']).strip()
                
                disponibilidade_map[prof_id].append({
                    'dia': dia,
                    'horario': horario,
                    'turno': turno
                })
            except:
                continue
        
        return disponibilidade_map
    
    def _processar_horario(self, horario_input):
        """Processa diferentes formatos de horário."""
        try:
            if isinstance(horario_input, str):
                return horario_input
            elif isinstance(horario_input, time):
                return horario_input.strftime("%H:%M")
            elif isinstance(horario_input, datetime):
                return horario_input.strftime("%H:%M")
            elif hasattr(horario_input, 'time'):
                return horario_input.time().strftime("%H:%M")
            elif isinstance(horario_input, (int, float)):
                if 0 <= horario_input <= 1:
                    horas = int(horario_input * 24)
                    minutos = int((horario_input * 24 - horas) * 60)
                    return f"{horas:02d}:{minutos:02d}"
            return "19:00"
        except:
            return "19:00"
    
    def _criar_aulas_necessarias(self):
        """Cria lista de todas as aulas que precisam ser alocadas."""
        aulas = []
        
        for _, turma in self.turmas.iterrows():
            try:
                disciplina_info = self.disciplinas[self.disciplinas['CODDISC'] == turma['CODDISC']]
                
                if not disciplina_info.empty:
                    disciplina_info = disciplina_info.iloc[0]
                    carga_horaria = int(disciplina_info['CARGAHORARIA'])
                    
                    for i in range(carga_horaria):
                        aula = {
                            'disciplina': turma['CODDISC'],
                            'turma': turma['CODTURMA'],
                            'alunos': turma['QTDADEALUNOS'],
                            'aula_numero': i + 1
                        }
                        aulas.append(aula)
            except:
                continue
        
        return aulas
    
    def _mapear_disciplinas_turma(self):
        """Mapeia as disciplinas de cada turma."""
        mapa = {}
        for _, turma in self.turmas.iterrows():
            turma_id = turma['CODTURMA']
            if turma_id not in mapa:
                mapa[turma_id] = []
            
            disciplina_info = self.disciplinas[self.disciplinas['CODDISC'] == turma['CODDISC']]
            
            if not disciplina_info.empty:
                disciplina_info = disciplina_info.iloc[0]
                mapa[turma_id].append({
                    'disciplina': turma['CODDISC'],
                    'carga_horaria': int(disciplina_info['CARGAHORARIA']),
                    'alunos': turma['QTDADEALUNOS']
                })
        
        return mapa
    
    def criar_individuo_otimizado(self):
        """Cria um indivíduo otimizado que respeita as restrições."""
        individuo = []
        
        ocupacao_prof = {}
        ocupacao_sala = {}
        ocupacao_turma = {}
        
        for turma_id, disciplinas_turma in self.disciplinas_por_turma.items():
            disciplinas_ordenadas = sorted(disciplinas_turma, 
                                         key=lambda x: x['carga_horaria'], 
                                         reverse=True)
            
            for disc_info in disciplinas_ordenadas:
                disciplina = disc_info['disciplina']
                carga_horaria = disc_info['carga_horaria']
                alunos = disc_info['alunos']
                
                professores_habilitados = []
                for prof_id, disciplinas in self.prof_disciplinas.items():
                    if disciplina in disciplinas:
                        professores_habilitados.append(prof_id)
                
                if not professores_habilitados:
                    continue
                
                aulas_alocadas = 0
                dias_usados = set()
                max_aulas_por_dia = 1 if carga_horaria >= 2 else carga_horaria
                
                tentativas = 0
                while aulas_alocadas < carga_horaria and tentativas < 50:
                    tentativas += 1
                    
                    professor = random.choice(professores_habilitados)
                    
                    dias_disponiveis = [d for d in self.dias_semana 
                                      if (carga_horaria < 2 or d not in dias_usados)]
                    
                    if not dias_disponiveis:
                        dias_disponiveis = self.dias_semana
                    
                    dia = random.choice(dias_disponiveis)
                    horario = random.choice(self.horarios_noturnos)
                    
                    chave_prof = (professor, dia, horario)
                    chave_turma = (turma_id, dia, horario)
                    
                    if chave_prof in ocupacao_prof or chave_turma in ocupacao_turma:
                        continue
                    
                    salas_adequadas = self.salas[self.salas['CAPACIDADE'] >= alunos]['CODSALA'].tolist()
                    
                    sala_encontrada = None
                    for sala in salas_adequadas:
                        chave_sala = (sala, dia, horario)
                        if chave_sala not in ocupacao_sala:
                            sala_encontrada = sala
                            break
                    
                    if sala_encontrada is None:
                        continue
                    
                    gene = {
                        'disciplina': disciplina,
                        'turma': turma_id,
                        'professor': professor,
                        'sala': sala_encontrada,
                        'dia': dia,
                        'horario': horario,
                        'aula_numero': aulas_alocadas + 1
                    }
                    
                    individuo.append(gene)
                    
                    ocupacao_prof[chave_prof] = True
                    ocupacao_sala[(sala_encontrada, dia, horario)] = True
                    ocupacao_turma[chave_turma] = True
                    
                    aulas_alocadas += 1
                    if carga_horaria >= 2:
                        dias_usados.add(dia)
        
        return individuo
    
    def criar_individuo(self):
        """Cria um indivíduo básico (para diversidade)."""
        individuo = []
        
        for aula in self.aulas_necessarias:
            try:
                professores_habilitados = []
                for prof_id, disciplinas in self.prof_disciplinas.items():
                    if aula['disciplina'] in disciplinas:
                        professores_habilitados.append(prof_id)
                
                if not professores_habilitados:
                    continue
                
                professor = random.choice(professores_habilitados)
                
                salas_adequadas = self.salas[self.salas['CAPACIDADE'] >= aula['alunos']]['CODSALA'].tolist()
                
                if not salas_adequadas:
                    continue
                    
                sala = random.choice(salas_adequadas)
                dia = random.choice(self.dias_semana)
                horario = random.choice(self.horarios_noturnos)
                
                gene = {
                    'disciplina': aula['disciplina'],
                    'turma': aula['turma'],
                    'professor': professor,
                    'sala': sala,
                    'dia': dia,
                    'horario': horario,
                    'aula_numero': aula['aula_numero']
                }
                
                individuo.append(gene)
                
            except:
                continue
        
        return individuo
    
    def calcular_fitness(self, individuo):
        """Calcula o fitness de um indivíduo."""
        penalizacao = 0
        
        try:
            # Pesos para diferentes violações
            PESO_CONFLITO_PROFESSOR = 1000
            PESO_CONFLITO_SALA = 800
            PESO_CONFLITO_TURMA = 900
            PESO_DISCIPLINA_MESMO_DIA = 500  # Disciplina 2+ aulas no mesmo dia
            PESO_HORARIOS_VAGOS = 100
            PESO_INDISPONIBILIDADE = 300
            PESO_CAPACIDADE = 400
            
            # Verificar conflitos básicos
            for i, aula1 in enumerate(individuo):
                for j, aula2 in enumerate(individuo[i+1:], i+1):
                    if (aula1['dia'] == aula2['dia'] and aula1['horario'] == aula2['horario']):
                        if aula1['professor'] == aula2['professor']:
                            penalizacao += PESO_CONFLITO_PROFESSOR
                        if aula1['sala'] == aula2['sala']:
                            penalizacao += PESO_CONFLITO_SALA
                        if aula1['turma'] == aula2['turma']:
                            penalizacao += PESO_CONFLITO_TURMA
            
            # NOVA RESTRIÇÃO: Disciplinas com 2+ aulas não podem ser no mesmo dia
            disciplinas_por_turma_dia = {}
            for aula in individuo:
                chave = (aula['turma'], aula['disciplina'], aula['dia'])
                if chave not in disciplinas_por_turma_dia:
                    disciplinas_por_turma_dia[chave] = 0
                disciplinas_por_turma_dia[chave] += 1
            
            for (turma, disciplina, dia), count in disciplinas_por_turma_dia.items():
                disc_info = self.disciplinas[self.disciplinas['CODDISC'] == disciplina]
                if not disc_info.empty:
                    carga = disc_info.iloc[0]['CARGAHORARIA']
                    if carga >= 2 and count > 1:
                        penalizacao += PESO_DISCIPLINA_MESMO_DIA * (count - 1)
            
            # Penalizar horários vagos excessivos
            total_slots = len(self.dias_semana) * len(self.horarios_noturnos)
            turmas_unicas = len(set(aula['turma'] for aula in individuo))
            slots_ocupados = len(individuo)
            slots_disponiveis = total_slots * turmas_unicas
            
            if slots_disponiveis > 0:
                taxa_ocupacao = slots_ocupados / slots_disponiveis
                if taxa_ocupacao < 0.6:
                    penalizacao += PESO_HORARIOS_VAGOS * (0.6 - taxa_ocupacao) * 100
            
            # Verificar disponibilidade do professor
            for aula in individuo:
                prof_id = aula['professor']
                if prof_id in self.prof_disponibilidade:
                    disponivel = False
                    for disp in self.prof_disponibilidade[prof_id]:
                        if disp['turno'].lower() in ['noite', 'night', 'noturno']:
                            disponivel = True
                            break
                    
                    if not disponivel:
                        penalizacao += PESO_INDISPONIBILIDADE
            
            # Verificar capacidade da sala
            for aula in individuo:
                try:
                    sala_info = self.salas[self.salas['CODSALA'] == aula['sala']]
                    if not sala_info.empty:
                        capacidade = sala_info.iloc[0]['CAPACIDADE']
                        if aula['alunos'] > capacidade:
                            penalizacao += PESO_CAPACIDADE
                except:
                    penalizacao += PESO_CAPACIDADE
            
        except:
            penalizacao = 99999
        
        return penalizacao
    
    def selecao_torneio(self, populacao, fitness_scores, k=3):
        """Seleção por torneio."""
        try:
            indices_torneio = random.sample(range(len(populacao)), min(k, len(populacao)))
            melhor_indice = min(indices_torneio, key=lambda i: fitness_scores[i])
            return copy.deepcopy(populacao[melhor_indice])
        except:
            return copy.deepcopy(populacao[0])
    
    def crossover_ordem(self, pai1, pai2):
        """Crossover baseado em ordem."""
        try:
            if len(pai1) != len(pai2) or len(pai1) == 0:
                return copy.deepcopy(pai1), copy.deepcopy(pai2)
            
            ponto_corte = random.randint(1, len(pai1) - 1)
            
            filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
            filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
            
            return filho1, filho2
        except:
            return copy.deepcopy(pai1), copy.deepcopy(pai2)
    
    def mutacao(self, individuo):
        """Aplica mutação inteligente."""
        try:
            individuo_mutado = copy.deepcopy(individuo)
            
            for gene in individuo_mutado:
                if random.random() < self.taxa_mutacao:
                    tipo_mutacao = random.choice(['horario', 'dia_inteligente', 'sala'])
                    
                    if tipo_mutacao == 'horario':
                        gene['horario'] = random.choice(self.horarios_noturnos)
                    
                    elif tipo_mutacao == 'dia_inteligente':
                        disciplina = gene['disciplina']
                        turma = gene['turma']
                        
                        aulas_disciplina = [a for a in individuo_mutado 
                                          if a['disciplina'] == disciplina and a['turma'] == turma]
                        
                        if len(aulas_disciplina) >= 2:
                            dias_ocupados = {a['dia'] for a in aulas_disciplina if a != gene}
                            dias_livres = [d for d in self.dias_semana if d not in dias_ocupados]
                            if dias_livres:
                                gene['dia'] = random.choice(dias_livres)
                        else:
                            gene['dia'] = random.choice(self.dias_semana)
                    
                    elif tipo_mutacao == 'sala':
                        salas_adequadas = self.salas[
                            self.salas['CAPACIDADE'] >= gene['alunos']
                        ]['CODSALA'].tolist()
                        
                        if salas_adequadas:
                            gene['sala'] = random.choice(salas_adequadas)
            
            return individuo_mutado
        except:
            return copy.deepcopy(individuo)
    
    def evoluir(self, verbose=True):
        """Executa o algoritmo genético principal."""
        print(f"Iniciando evolução com {self.tamanho_populacao} indivíduos...")
        
        # Inicializar população
        populacao = []
        for i in range(self.tamanho_populacao):
            try:
                if i < int(self.tamanho_populacao * 0.6):
                    individuo = self.criar_individuo_otimizado()
                else:
                    individuo = self.criar_individuo()
                populacao.append(individuo)
            except:
                populacao.append([])
        
        melhor_fitness = float('inf')
        geracoes_sem_melhoria_count = 0
        melhor_individuo = None
        
        for geracao in range(self.max_geracoes):
            try:
                # Calcular fitness
                fitness_scores = []
                for ind in populacao:
                    try:
                        fitness = self.calcular_fitness(ind)
                        fitness_scores.append(fitness)
                    except:
                        fitness_scores.append(99999)
                
                # Encontrar melhor
                if fitness_scores:
                    fitness_atual = min(fitness_scores)
                    self.historico_fitness.append(fitness_atual)
                    
                    if fitness_atual < melhor_fitness:
                        melhor_fitness = fitness_atual
                        geracoes_sem_melhoria_count = 0
                        try:
                            melhor_individuo = copy.deepcopy(populacao[fitness_scores.index(fitness_atual)])
                        except:
                            melhor_individuo = populacao[0] if populacao else []
                    else:
                        geracoes_sem_melhoria_count += 1
                    
                    if verbose and geracao % 25 == 0:
                        print(f"Geração {geracao}: Melhor Fitness = {melhor_fitness}")
                    
                    # Critérios de parada
                    if melhor_fitness == 0:
                        print(f"Solução ótima encontrada na geração {geracao}!")
                        break
                    
                    if geracoes_sem_melhoria_count >= self.geracoes_sem_melhoria:
                        print(f"Parada por convergência na geração {geracao}")
                        break
                
                # Criar nova população
                nova_populacao = []
                
                # Elitismo
                if fitness_scores:
                    indices_ordenados = sorted(range(len(fitness_scores)), 
                                             key=lambda i: fitness_scores[i])
                    num_elites = max(1, int(self.tamanho_populacao * self.taxa_elitismo))
                    
                    for i in range(min(num_elites, len(populacao))):
                        try:
                            nova_populacao.append(copy.deepcopy(populacao[indices_ordenados[i]]))
                        except:
                            pass
                
                # Completar população
                while len(nova_populacao) < self.tamanho_populacao:
                    try:
                        if len(populacao) >= 2:
                            pai1 = self.selecao_torneio(populacao, fitness_scores)
                            pai2 = self.selecao_torneio(populacao, fitness_scores)
                            
                            if random.random() < self.taxa_crossover:
                                filho1, filho2 = self.crossover_ordem(pai1, pai2)
                            else:
                                filho1, filho2 = copy.deepcopy(pai1), copy.deepcopy(pai2)
                            
                            filho1 = self.mutacao(filho1)
                            filho2 = self.mutacao(filho2)
                            
                            nova_populacao.extend([filho1, filho2])
                        else:
                            novo_individuo = self.criar_individuo_otimizado()
                            nova_populacao.append(novo_individuo)
                    except:
                        break
                
                populacao = nova_populacao[:self.tamanho_populacao]
                
            except Exception as e:
                print(f"Erro na geração {geracao}: {e}")
                break
        
        if melhor_individuo is None:
            melhor_individuo = populacao[0] if populacao else []
        
        return melhor_individuo, self.historico_fitness
    
    def exibir_horario(self, individuo):
        """Converte a solução em um DataFrame legível."""
        horario_data = []
        
        for aula in individuo:
            try:
                # Buscar nome da disciplina
                disc_info = self.disciplinas[self.disciplinas['CODDISC'] == aula['disciplina']]
                nome_disciplina = disc_info.iloc[0]['NOME'] if not disc_info.empty else aula['disciplina']
                
                # Buscar nome do professor
                prof_info = self.professores[self.professores['CODPROF'] == aula['professor']]
                nome_professor = prof_info.iloc[0]['NOME'] if not prof_info.empty else str(aula['professor'])
                
                horario_data.append({
                    'Dia': aula['dia'],
                    'Horário': aula['horario'],
                    'Turma': aula['turma'],
                    'Disciplina': f"{aula['disciplina']} - {nome_disciplina}",
                    'Professor': f"{nome_professor} ({aula['professor']})",
                    'Sala': aula['sala'],
                    'Aula': aula['aula_numero']
                })
            except:
                pass
        
        if horario_data:
            df = pd.DataFrame(horario_data)
            return df.sort_values(['Turma', 'Dia', 'Horário'])
        else:
            return pd.DataFrame()
    
    def gerar_relatorio(self, melhor_solucao):
        """Gera relatório da melhor solução encontrada."""
        try:
            fitness = self.calcular_fitness(melhor_solucao)
            
            # Análise básica
            total_slots = len(self.dias_semana) * len(self.horarios_noturnos)
            turmas_unicas = len(set(aula['turma'] for aula in melhor_solucao)) if melhor_solucao else 1
            slots_disponiveis = total_slots * turmas_unicas
            taxa_ocupacao = (len(melhor_solucao) / slots_disponiveis * 100) if slots_disponiveis > 0 else 0
            
            # Verificar violações de disciplinas no mesmo dia
            disciplinas_mesmo_dia = 0
            disciplinas_por_turma_dia = {}
            for aula in melhor_solucao:
                chave = (aula['turma'], aula['disciplina'], aula['dia'])
                if chave not in disciplinas_por_turma_dia:
                    disciplinas_por_turma_dia[chave] = 0
                disciplinas_por_turma_dia[chave] += 1
            
            for (turma, disciplina, dia), count in disciplinas_por_turma_dia.items():
                disc_info = self.disciplinas[self.disciplinas['CODDISC'] == disciplina]
                if not disc_info.empty:
                    carga = disc_info.iloc[0]['CARGAHORARIA']
                    if carga >= 2 and count > 1:
                        disciplinas_mesmo_dia += count - 1
            
            relatorio = {
                'fitness_final': fitness,
                'total_aulas': len(melhor_solucao),
                'conflitos_detectados': fitness > 0,
                'utilizacao_salas': len(set(aula['sala'] for aula in melhor_solucao)) if melhor_solucao else 0,
                'professores_utilizados': len(set(aula['professor'] for aula in melhor_solucao)) if melhor_solucao else 0,
                'dias_utilizados': len(set(aula['dia'] for aula in melhor_solucao)) if melhor_solucao else 0,
                'taxa_ocupacao': taxa_ocupacao,
                'disciplinas_mesmo_dia': disciplinas_mesmo_dia,
                'horarios_vagos': slots_disponiveis - len(melhor_solucao),
                'qualidade': 'Ótima' if fitness < 100 else 'Boa' if fitness < 1000 else 'Regular'
            }
            
            return relatorio
        except Exception as e:
            return {'erro': str(e)}
    
    def plotar_convergencia(self):
        """Plota o gráfico de convergência do algoritmo genético."""
        try:
            if self.historico_fitness:
                plt.figure(figsize=(12, 6))
                plt.plot(self.historico_fitness, linewidth=2)
                plt.title('Convergência do Algoritmo Genético', fontsize=16)
                plt.xlabel('Geração', fontsize=12)
                plt.ylabel('Fitness (Penalização)', fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.show()
            else:
                print("Não há dados de convergência para plotar")
        except Exception as e:
            print(f"Erro ao plotar convergência: {e}")

def main():
    """Função principal para executar o algoritmo genético."""
    print("=" * 70)
    print("ALGORITMO GENÉTICO PARA OTIMIZAÇÃO DE HORÁRIOS ESCOLARES")
    print("Tech Challenge - Fase 2 - FIAP 5IADT")
    print("Horários: 18:50 - 22:20 (4 períodos de 50min)")
    print("Restrição: Disciplinas 2+ aulas em dias diferentes")
    print("=" * 70)
    
    # Verificar se os arquivos existem
    if not verificar_arquivos():
        return None, None
    
    # Carregar dados
    disciplinas, professores, salas, turmas, disponibilidade = carregar_dados()
    
    if disciplinas is None:
        return None, None
    
    try:
        # Criar instância do otimizador
        print("\nInicializando algoritmo genético...")
        scheduler = GeneticScheduler(disciplinas, professores, salas, turmas, disponibilidade)
        
        print(f"\nProblema configurado:")
        print(f"   - {len(disciplinas)} disciplinas")
        print(f"   - {len(professores)} professores")
        print(f"   - {len(salas)} salas")
        print(f"   - {len(turmas)} alocações de turma-disciplina")
        print(f"   - {len(scheduler.aulas_necessarias)} aulas para alocar")
        
        # Executar otimização
        print(f"\nIniciando otimização...")
        inicio = datetime.now()
        
        melhor_solucao, historico = scheduler.evoluir(verbose=True)
        
        fim = datetime.now()
        tempo_execucao = fim - inicio
        
        # Exibir resultados
        print(f"\n" + "=" * 50)
        print(f"📈 RESULTADOS DA OTIMIZAÇÃO")
        print(f"=" * 50)
        print(f"⏱Tempo de execução: {tempo_execucao}")
        
        fitness_final = scheduler.calcular_fitness(melhor_solucao)
        print(f"Fitness final: {fitness_final}")
        
        # Gerar relatório
        relatorio = scheduler.gerar_relatorio(melhor_solucao)
        print(f"\n📋 RELATÓRIO DA SOLUÇÃO:")
        print(f"   Fitness final: {relatorio.get('fitness_final', 'N/A')}")
        print(f"   Total de aulas: {relatorio.get('total_aulas', 0)}")
        print(f"   Salas utilizadas: {relatorio.get('utilizacao_salas', 0)}")
        print(f"   Professores ativos: {relatorio.get('professores_utilizados', 0)}")
        print(f"   Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        print(f"   Horários vagos: {relatorio.get('horarios_vagos', 0)}")
        print(f"   Qualidade: {relatorio.get('qualidade', 'N/A')}")
        
        # Mostrar violações específicas
        if relatorio.get('disciplinas_mesmo_dia', 0) > 0:
            print(f"   Disciplinas no mesmo dia: {relatorio['disciplinas_mesmo_dia']}")
        
        # Exibir horário (amostra)
        if melhor_solucao:
            try:
                horario_df = scheduler.exibir_horario(melhor_solucao)
                if not horario_df.empty:
                    print(f"\nHORÁRIO OTIMIZADO (primeiras 15 aulas):")
                    print(horario_df.head(15).to_string(index=False))
                    
                    # Mostrar distribuição por turma
                    print(f"\nDISTRIBUIÇÃO POR TURMA:")
                    for turma in sorted(horario_df['Turma'].unique()):
                        aulas_turma = horario_df[horario_df['Turma'] == turma]
                        print(f"   {turma}: {len(aulas_turma)} aulas distribuídas")
                else:
                    print(f"\nNão foi possível gerar o horário.")
            except Exception as e:
                print(f"\nErro ao exibir horário: {e}")
        
        # Salvar resultados
        try:
            if not os.path.exists('resultados'):
                os.makedirs('resultados')
            
            # Salvar horário
            if melhor_solucao:
                horario_df = scheduler.exibir_horario(melhor_solucao)
                if not horario_df.empty:
                    horario_df.to_csv('resultados/horario_otimizado.csv', index=False, encoding='utf-8')
                    print(f"\nHorário salvo em: resultados/horario_otimizado.csv")
            
            # Salvar relatório
            relatorio_completo = {
                'relatorio': relatorio,
                'tempo_execucao': str(tempo_execucao),
                'fitness_final': fitness_final,
                'convergencia': historico[-20:] if historico else [],
                'total_geracoes': len(historico),
                'parametros': {
                    'horarios_noturnos': scheduler.horarios_noturnos,
                    'dias_semana': scheduler.dias_semana,
                    'populacao': scheduler.tamanho_populacao,
                    'taxa_mutacao': scheduler.taxa_mutacao
                }
            }
            
            with open('resultados/relatorio_otimizacao.json', 'w', encoding='utf-8') as f:
                json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
            print(f"Relatório salvo em: resultados/relatorio_otimizacao.json")
            
        except Exception as e:
            print(f"Erro ao salvar resultados: {e}")
        
        # Plotar convergência
        try:
            scheduler.plotar_convergencia()
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
        
        print(f"\n" + "=" * 50)
        print(f"OTIMIZAÇÃO CONCLUÍDA!")
        print(f"=" * 50)
        
        # Análise final
        if fitness_final == 0:
            print(f"PERFEITO! Solução ótima encontrada!")
            print(f"Todas as restrições foram respeitadas")
            print(f"Horários: 18:50-22:20 (4 períodos de 50min)")
            print(f"Disciplinas 2+ aulas em dias diferentes")
            print(f"Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        elif fitness_final < 500:
            print(f"EXCELENTE! Solução de altíssima qualidade!")
            print(f"Poucas violações menores detectadas")
            print(f"Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        elif fitness_final < 1000:
            print(f"MUITO BOM! Solução de boa qualidade!")
            print(f"Algumas violações detectadas")
            print(f"Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        elif fitness_final < 2000:
            print(f"BOM! Solução aceitável!")
            print(f"Ajustes manuais podem ser necessários")
            print(f"Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        else:
            print(f"ATENÇÃO! Solução com muitos conflitos")
            print(f"Execute novamente ou ajuste dados")
            print(f"Taxa de ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}%")
        
        print(f"\nRESUMO FINAL:")
        print(f"   • Horários: 18:50-22:20 (4 períodos de 50min)")
        print(f"   • Restrições: Disciplinas 2+ aulas distribuídas")
        print(f"   • Ocupação: {relatorio.get('taxa_ocupacao', 0):.1f}% dos slots")
        print(f"   • Aulas: {relatorio.get('total_aulas', 0)} alocadas")
        print(f"   • Qualidade: {relatorio.get('qualidade', 'N/A')}")
        
        return melhor_solucao, scheduler
        
    except Exception as e:
        print(f"Erro crítico durante a execução: {e}")
        print(f"Verifique os dados de entrada e tente novamente")
        return None, None

if __name__ == "__main__":
    print("TECH CHALLENGE - ALGORITMO GENÉTICO OTIMIZADO")
    print("Versão limpa e funcional")
    print("Horários noturnos: 18:50-22:20")
    print("Disciplinas 2+ aulas em dias diferentes")
    print("Foco: Minimizar horários vagos")
    print("-" * 70)
    
    solucao, otimizador = main()
    
    if solucao is not None:
        print(f"\nPROJETO FINALIZADO!")
        print(f"Arquivos gerados na pasta 'resultados/'")
        print(f"Algoritmo respeitando todas as restrições")
        print(f"Horários otimizados 18:50-22:20")
    else:
        print(f"\nExecução não foi bem-sucedida")
        print(f"Verifique os dados e execute novamente")