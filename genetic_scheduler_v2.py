import pandas as pd
import numpy as np
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
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

@dataclass
class Aula:
    disciplina: str
    professor: str
    sala: str
    
    def __str__(self):
        return f"{self.disciplina}|{self.professor}|{self.sala}"

class ScheduleGA_V2:
    """
    Versão 2: Agenda com pontuação positiva e distribuição inteligente
    - Genoma = Matriz (agenda) 5 dias x 4 horários
    - Fitness = Soma de pontuações positivas
    - Garantia de todas as disciplinas atendidas
    - Distribuição inteligente das disciplinas
    """
    
    def __init__(self):
        # Dimensões da agenda (5 dias x 4 horários)
        self.num_dias = 5
        self.num_horarios = 4
        
        # Mapeamentos
        self.dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        self.horarios = ['18:50', '19:40', '20:30', '21:20']
        
        # Dados do problema
        self.disciplinas = {}
        self.professores = {}
        self.salas = {}
        self.turmas = {}
        self.disponibilidades = {}
        
        # Lista de todas as aulas necessárias e distribuição planejada
        self.aulas_obrigatorias = []
        self.distribuicao_disciplinas = {}
        
        # Parâmetros do AG
        self.populacao_size = 50
        self.geracoes = 1000
        self.taxa_mutacao = 0.15
        self.taxa_crossover = 0.8
        self.tamanho_torneio = 3
        
        # Pesos para pontuação
        self.pesos = {
            'disciplina_atendida': 1000,          # Todas as aulas de uma disciplina alocadas
            'disponibilidade_respeitada': 500,    # Professor disponível no horário
            'distribuicao_equilibrada': 200,      # Aulas bem distribuídas na semana
            'distribuicao_inteligente': 300,      # Distribuição planejada respeitada
            'sem_sobrecarga_dia': 150,           # Não mais que 4 aulas por dia
            'sem_janelas': 100,                  # Aulas consecutivas por dia
            'professor_satisfeito': 80,          # Professor com horário concentrado
            'sala_otimizada': 50                 # Uso eficiente da sala
        }
    
    def carregar_dados(self):
        """Carrega os dados dos arquivos Excel"""
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
        
        # Criar lista de aulas obrigatórias
        self._criar_aulas_obrigatorias()
    
    def _criar_aulas_obrigatorias(self):
        """Cria lista de todas as aulas que devem ser alocadas com distribuição inteligente"""
        self.aulas_obrigatorias = []
        self.distribuicao_disciplinas = {}  # Para controlar distribuição por dia
        
        for disc_codigo, disciplina in self.disciplinas.items():
            # Encontrar professor da disciplina
            professor = None
            for prof_codigo, prof in self.professores.items():
                if prof.disciplina == disc_codigo:
                    professor = prof_codigo
                    break
            
            # Definir distribuição inteligente baseada na carga horária
            carga = disciplina.carga_horaria
            if carga == 4:
                # 4 aulas: 2 aulas por dia em 2 dias diferentes
                distribuicao = [2, 2]
            elif carga == 3:
                # 3 aulas: 2 aulas em um dia, 1 aula em outro dia
                distribuicao = [2, 1]
            elif carga == 2:
                # 2 aulas: 1 aula por dia em 2 dias diferentes
                distribuicao = [1, 1]
            elif carga == 1:
                # 1 aula: apenas 1 dia
                distribuicao = [1]
            else:
                # Para cargas maiores: distribuir o mais equilibrado possível
                # Ex: 5 aulas = [3, 2], 6 aulas = [2, 2, 2]
                distribuicao = self._calcular_distribuicao_equilibrada(carga)
            
            # Armazenar distribuição para esta disciplina
            self.distribuicao_disciplinas[disc_codigo] = {
                'distribuicao': distribuicao,
                'professor': professor,
                'aulas_criadas': 0
            }
            
            # Criar aulas com identificação de grupo
            for grupo_idx, aulas_no_grupo in enumerate(distribuicao):
                for aula_no_grupo in range(aulas_no_grupo):
                    aula = Aula(
                        disciplina=disc_codigo,
                        professor=professor,
                        sala=list(self.salas.keys())[0]  # Por enquanto só temos uma sala
                    )
                    # Adicionar metadata para controle de distribuição
                    aula.grupo_dia = grupo_idx
                    aula.posicao_no_grupo = aula_no_grupo
                    self.aulas_obrigatorias.append(aula)
        
        print(f"📚 Total de aulas obrigatórias: {len(self.aulas_obrigatorias)}")
        print("📋 Distribuição planejada por disciplina:")
        for disc_codigo, info in self.distribuicao_disciplinas.items():
            disciplina = self.disciplinas[disc_codigo]
            print(f"   • {disciplina.nome[:30]}: {info['distribuicao']} aulas por dia")
    
    def _calcular_distribuicao_equilibrada(self, carga_total):
        """Calcula distribuição equilibrada para cargas horárias maiores"""
        if carga_total <= 5:
            # Para 5 aulas: [3, 2] ou [2, 3]
            maior = (carga_total + 1) // 2
            menor = carga_total - maior
            return [maior, menor] if maior != menor else [maior, menor]
        else:
            # Para cargas muito grandes, dividir em grupos de no máximo 3
            grupos = []
            restante = carga_total
            while restante > 0:
                if restante >= 3:
                    grupos.append(3)
                    restante -= 3
                else:
                    grupos.append(restante)
                    restante = 0
            return grupos
    
    def criar_agenda_vazia(self) -> np.ndarray:
        """Cria uma agenda vazia (matriz 5x4)"""
        return np.full((self.num_dias, self.num_horarios), None, dtype=object)
    
    def criar_cromossomo(self) -> np.ndarray:
        """
        Cria um cromossomo (agenda completa) respeitando a distribuição inteligente das disciplinas
        """
        agenda = self.criar_agenda_vazia()
        
        # Organizar aulas por disciplina e grupo
        aulas_por_disciplina = {}
        for aula in self.aulas_obrigatorias:
            disc = aula.disciplina
            if disc not in aulas_por_disciplina:
                aulas_por_disciplina[disc] = {}
            
            grupo = aula.grupo_dia
            if grupo not in aulas_por_disciplina[disc]:
                aulas_por_disciplina[disc][grupo] = []
            
            aulas_por_disciplina[disc][grupo].append(aula)
        
        # Lista de dias disponíveis para cada disciplina
        dias_disponiveis = list(range(self.num_dias))
        
        # Alocar cada disciplina respeitando a distribuição
        for disc_codigo, grupos in aulas_por_disciplina.items():
            disciplina = self.disciplinas[disc_codigo]
            dias_escolhidos = []
            
            # Escolher dias diferentes para cada grupo da disciplina
            dias_para_esta_disciplina = random.sample(dias_disponiveis, 
                                                     min(len(grupos), len(dias_disponiveis)))
            
            for grupo_idx, (grupo, aulas_do_grupo) in enumerate(grupos.items()):
                if grupo_idx < len(dias_para_esta_disciplina):
                    dia_escolhido = dias_para_esta_disciplina[grupo_idx]
                    dias_escolhidos.append(dia_escolhido)
                    
                    # Encontrar horários consecutivos disponíveis neste dia
                    horarios_consecutivos = self._encontrar_horarios_consecutivos(
                        agenda, dia_escolhido, len(aulas_do_grupo)
                    )
                    
                    if horarios_consecutivos:
                        # Alocar aulas em horários consecutivos
                        for i, aula in enumerate(aulas_do_grupo):
                            if i < len(horarios_consecutivos):
                                horario = horarios_consecutivos[i]
                                agenda[dia_escolhido, horario] = aula
                    else:
                        # Se não conseguir consecutivos, alocar em qualquer horário disponível
                        self._alocar_aulas_disponiveis(agenda, dia_escolhido, aulas_do_grupo)
        
        # Verificar se sobrou alguma aula não alocada e alocar em slots livres
        self._alocar_aulas_restantes(agenda, aulas_por_disciplina)
        
        return agenda
    
    def _encontrar_horarios_consecutivos(self, agenda: np.ndarray, dia: int, num_aulas: int) -> list:
        """Encontra horários consecutivos livres em um dia específico"""
        horarios_livres = []
        for h in range(self.num_horarios):
            if agenda[dia, h] is None:
                horarios_livres.append(h)
        
        # Tentar encontrar sequência consecutiva
        for start in range(len(horarios_livres) - num_aulas + 1):
            sequencia = horarios_livres[start:start + num_aulas]
            # Verificar se é realmente consecutiva
            if all(sequencia[i] == sequencia[0] + i for i in range(len(sequencia))):
                return sequencia
        
        # Se não encontrar consecutivos, retornar os primeiros disponíveis
        return horarios_livres[:num_aulas] if len(horarios_livres) >= num_aulas else horarios_livres
    
    def _alocar_aulas_disponiveis(self, agenda: np.ndarray, dia: int, aulas: list):
        """Aloca aulas em horários disponíveis de um dia específico"""
        horarios_livres = [h for h in range(self.num_horarios) if agenda[dia, h] is None]
        
        for i, aula in enumerate(aulas):
            if i < len(horarios_livres):
                horario = horarios_livres[i]
                agenda[dia, horario] = aula
    
    def _alocar_aulas_restantes(self, agenda: np.ndarray, aulas_por_disciplina: dict):
        """Aloca qualquer aula que não foi alocada ainda"""
        # Verificar quais aulas ainda não foram alocadas
        aulas_na_agenda = set()
        for d in range(self.num_dias):
            for h in range(self.num_horarios):
                if agenda[d, h] is not None:
                    # Criar identificador único para a aula
                    aula = agenda[d, h]
                    aulas_na_agenda.add((aula.disciplina, aula.grupo_dia, aula.posicao_no_grupo))
        
        # Encontrar aulas não alocadas
        aulas_nao_alocadas = []
        for aula in self.aulas_obrigatorias:
            id_aula = (aula.disciplina, aula.grupo_dia, aula.posicao_no_grupo)
            if id_aula not in aulas_na_agenda:
                aulas_nao_alocadas.append(aula)
        
        # Alocar em qualquer slot livre
        slots_livres = [(d, h) for d in range(self.num_dias) for h in range(self.num_horarios) 
                       if agenda[d, h] is None]
        
        for i, aula in enumerate(aulas_nao_alocadas):
            if i < len(slots_livres):
                d, h = slots_livres[i]
                agenda[d, h] = aula
    
    def _professor_disponivel(self, professor_codigo: str, dia: int, horario: int) -> bool:
        """Verifica se professor está disponível no dia/horário"""
        if professor_codigo not in self.disponibilidades:
            return False
        
        dia_nome = self.dias[dia]
        horario_nome = self.horarios[horario]
        
        for disp in self.disponibilidades[professor_codigo]:
            if disp.dia == dia_nome and disp.horario == horario_nome:
                return True
        
        return False
    
    def inicializar_populacao(self) -> List[np.ndarray]:
        """Inicializa a população garantindo viabilidade"""
        populacao = []
        
        print("🧬 Inicializando população...")
        for i in range(self.populacao_size):
            cromossomo = self.criar_cromossomo()
            populacao.append(cromossomo)
            
            if (i + 1) % 10 == 0:
                print(f"   Criados {i + 1}/{self.populacao_size} cromossomos")
        
        return populacao
    
    def calcular_fitness(self, agenda: np.ndarray) -> float:
        """
        Calcula fitness usando pontuação positiva
        Quanto maior, melhor a solução
        """
        pontuacao_total = 0
        
        # 1. Pontuação por disciplinas completamente atendidas
        pontuacao_total += self._pontuar_disciplinas_atendidas(agenda)
        
        # 2. Pontuação por disponibilidade respeitada
        pontuacao_total += self._pontuar_disponibilidade(agenda)
        
        # 3. Pontuação por distribuição equilibrada e inteligente
        pontuacao_total += self._pontuar_distribuicao(agenda)
        
        # 4. Pontuação por não sobrecarga de dias
        pontuacao_total += self._pontuar_carga_diaria(agenda)
        
        # 5. Pontuação por ausência de janelas
        pontuacao_total += self._pontuar_continuidade(agenda)
        
        # 6. Pontuação por satisfação do professor
        pontuacao_total += self._pontuar_professor(agenda)
        
        # 7. Pontuação por uso da sala
        pontuacao_total += self._pontuar_sala(agenda)
        
        return pontuacao_total
    
    def _pontuar_disciplinas_atendidas(self, agenda: np.ndarray) -> float:
        """Pontua disciplinas que tiveram EXATAMENTE a carga horária alocada"""
        pontos = 0
        
        # Contar aulas por disciplina na agenda
        aulas_por_disciplina = {}
        for dia in range(self.num_dias):
            for horario in range(self.num_horarios):
                aula = agenda[dia, horario]
                if aula is not None:
                    disc = aula.disciplina
                    aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
        
        # Verificar se cada disciplina foi atendida EXATAMENTE
        for disc_codigo, disciplina in self.disciplinas.items():
            aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
            aulas_necessarias = disciplina.carga_horaria
            
            if aulas_alocadas == aulas_necessarias:
                # Disciplina atendida EXATAMENTE - pontuação máxima
                pontos += self.pesos['disciplina_atendida']
            elif aulas_alocadas < aulas_necessarias:
                # Disciplina incompleta - pontuação proporcional
                proporcao = aulas_alocadas / aulas_necessarias
                pontos += self.pesos['disciplina_atendida'] * proporcao * 0.7
            else:
                # Disciplina com AULAS EXTRAS - penalizar
                aulas_extras = aulas_alocadas - aulas_necessarias
                penalidade = min(aulas_extras * 200, self.pesos['disciplina_atendida'] * 0.5)
                pontos += self.pesos['disciplina_atendida'] * 0.8 - penalidade
        
        return max(0, pontos)  # Garantir que não seja negativo
    
    def _pontuar_disponibilidade(self, agenda: np.ndarray) -> float:
        """Pontua aulas em horários onde o professor está disponível"""
        pontos = 0
        
        for dia in range(self.num_dias):
            for horario in range(self.num_horarios):
                aula = agenda[dia, horario]
                if aula is not None and self._professor_disponivel(aula.professor, dia, horario):
                    pontos += self.pesos['disponibilidade_respeitada']
        
        return pontos
    
    def _pontuar_distribuicao(self, agenda: np.ndarray) -> float:
        """Pontua distribuição equilibrada das aulas e respeito à distribuição planejada"""
        pontos = 0
        
        # 1. Pontuar distribuição geral equilibrada entre dias
        aulas_por_dia = []
        for dia in range(self.num_dias):
            count = sum(1 for h in range(self.num_horarios) if agenda[dia, h] is not None)
            aulas_por_dia.append(count)
        
        if len(aulas_por_dia) > 0:
            media = np.mean(aulas_por_dia)
            variacao = np.std(aulas_por_dia)
            # Menos variação = mais pontos
            pontos += self.pesos['distribuicao_equilibrada'] * max(0, (2.0 - variacao)) * 0.5
        
        # 2. Pontuar respeito à distribuição planejada por disciplina
        for disc_codigo, info_dist in self.distribuicao_disciplinas.items():
            distribuicao_planejada = info_dist['distribuicao']
            
            # Contar como as aulas desta disciplina estão distribuídas na agenda
            distribuicao_real = [0] * self.num_dias
            for dia in range(self.num_dias):
                for horario in range(self.num_horarios):
                    aula = agenda[dia, horario]
                    if aula is not None and aula.disciplina == disc_codigo:
                        distribuicao_real[dia] += 1
            
            # Filtrar apenas dias com aulas desta disciplina
            dias_com_aulas = [count for count in distribuicao_real if count > 0]
            dias_com_aulas.sort(reverse=True)  # Ordenar do maior para o menor
            
            # Verificar se a distribuição real corresponde à planejada
            if len(dias_com_aulas) == len(distribuicao_planejada):
                # Comparar distribuições ordenadas
                distribuicao_planejada_ordenada = sorted(distribuicao_planejada, reverse=True)
                
                if dias_com_aulas == distribuicao_planejada_ordenada:
                    # Distribuição perfeita!
                    pontos += self.pesos['distribuicao_inteligente']
                else:
                    # Distribuição parcial - pontuar proporcionalmente
                    diferenca = sum(abs(real - planejado) 
                                  for real, planejado in zip(dias_com_aulas, distribuicao_planejada_ordenada))
                    total_aulas = sum(distribuicao_planejada)
                    if total_aulas > 0:
                        similarity = max(0, 1 - (diferenca / total_aulas))
                        pontos += self.pesos['distribuicao_inteligente'] * similarity
            
            # 3. Bonificar aulas consecutivas no mesmo dia para a mesma disciplina
            for dia in range(self.num_dias):
                aulas_consecutivas = self._contar_aulas_consecutivas_disciplina(agenda, dia, disc_codigo)
                if aulas_consecutivas >= 2:
                    # Bonificar por ter aulas consecutivas (melhor para o aluno)
                    pontos += 50 * (aulas_consecutivas - 1)
        
        return pontos
    
    def _contar_aulas_consecutivas_disciplina(self, agenda: np.ndarray, dia: int, disciplina: str) -> int:
        """Conta o maior número de aulas consecutivas de uma disciplina em um dia"""
        max_consecutivas = 0
        consecutivas_atual = 0
        
        for horario in range(self.num_horarios):
            aula = agenda[dia, horario]
            if aula is not None and aula.disciplina == disciplina:
                consecutivas_atual += 1
                max_consecutivas = max(max_consecutivas, consecutivas_atual)
            else:
                consecutivas_atual = 0
        
        return max_consecutivas
    
    def _pontuar_carga_diaria(self, agenda: np.ndarray) -> float:
        """Pontua dias sem sobrecarga (máximo 4 aulas)"""
        pontos = 0
        
        for dia in range(self.num_dias):
            aulas_no_dia = sum(1 for h in range(self.num_horarios) if agenda[dia, h] is not None)
            if aulas_no_dia <= 4:  # Máximo recomendado
                pontos += self.pesos['sem_sobrecarga_dia']
        
        return pontos
    
    def _pontuar_continuidade(self, agenda: np.ndarray) -> float:
        """Pontua aulas consecutivas (sem janelas)"""
        pontos = 0
        
        for dia in range(self.num_dias):
            # Verificar continuidade no dia
            aulas_dia = [agenda[dia, h] is not None for h in range(self.num_horarios)]
            
            if any(aulas_dia):
                # Encontrar primeiro e último slot ocupado
                primeiro_slot = next(i for i, ocupado in enumerate(aulas_dia) if ocupado)
                ultimo_slot = next(i for i in reversed(range(len(aulas_dia))) if aulas_dia[i])
                
                # Contar janelas (slots vazios entre primeiro e último)
                janelas = sum(1 for i in range(primeiro_slot, ultimo_slot + 1) if not aulas_dia[i])
                
                # Menos janelas = mais pontos
                pontos += self.pesos['sem_janelas'] * max(0, (4 - janelas))
        
        return pontos
    
    def _pontuar_professor(self, agenda: np.ndarray) -> float:
        """Pontua concentração de horários por professor"""
        pontos = 0
        
        # Contar dias trabalhados por professor
        professor_dias = {}
        for dia in range(self.num_dias):
            for horario in range(self.num_horarios):
                aula = agenda[dia, horario]
                if aula is not None:
                    prof = aula.professor
                    if prof not in professor_dias:
                        professor_dias[prof] = set()
                    professor_dias[prof].add(dia)
        
        # Menos dias trabalhados = mais concentrado = mais pontos
        for prof, dias_trabalhados in professor_dias.items():
            concentracao = max(0, (6 - len(dias_trabalhados)))  # Máximo 5 dias
            pontos += self.pesos['professor_satisfeito'] * concentracao
        
        return pontos
    
    def _pontuar_sala(self, agenda: np.ndarray) -> float:
        """Pontua uso eficiente da sala"""
        pontos = 0
        
        # Contar utilização total da sala
        slots_utilizados = sum(1 for d in range(self.num_dias) 
                             for h in range(self.num_horarios) 
                             if agenda[d, h] is not None)
        
        total_slots = self.num_dias * self.num_horarios
        utilizacao = slots_utilizados / total_slots
        
        pontos += self.pesos['sala_otimizada'] * utilizacao
        
        return pontos
    
    def selecao_torneio(self, populacao: List[np.ndarray], fitness_scores: List[float]) -> np.ndarray:
        """Seleção por torneio"""
        indices = random.sample(range(len(populacao)), self.tamanho_torneio)
        melhor_indice = max(indices, key=lambda i: fitness_scores[i])
        return copy.deepcopy(populacao[melhor_indice])
    
    def crossover_agenda(self, pai1: np.ndarray, pai2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Crossover específico para agenda
        Troca blocos de dias entre os pais
        """
        if random.random() > self.taxa_crossover:
            return copy.deepcopy(pai1), copy.deepcopy(pai2)
        
        filho1 = copy.deepcopy(pai1)
        filho2 = copy.deepcopy(pai2)
        
        # Escolher dias para trocar
        dias_trocar = random.sample(range(self.num_dias), random.randint(1, 3))
        
        for dia in dias_trocar:
            # Trocar dia completo
            temp = filho1[dia, :].copy()
            filho1[dia, :] = filho2[dia, :]
            filho2[dia, :] = temp
        
        # Garantir que todas as disciplinas ainda estejam atendidas
        filho1 = self._reparar_cromossomo(filho1)
        filho2 = self._reparar_cromossomo(filho2)
        
        return filho1, filho2
    
    def mutacao_agenda(self, agenda: np.ndarray) -> np.ndarray:
        """
        Mutação específica para agenda
        Move aulas para outros slots
        """
        agenda_mutada = copy.deepcopy(agenda)
        
        # Número de mutações baseado no tamanho da agenda
        num_mutacoes = max(1, int(self.taxa_mutacao * self.num_dias * self.num_horarios))
        
        for _ in range(num_mutacoes):
            if random.random() < self.taxa_mutacao:
                # Escolher dois slots aleatórios e trocar
                dia1, hora1 = random.randint(0, self.num_dias-1), random.randint(0, self.num_horarios-1)
                dia2, hora2 = random.randint(0, self.num_dias-1), random.randint(0, self.num_horarios-1)
                
                # Trocar conteúdo dos slots
                temp = agenda_mutada[dia1, hora1]
                agenda_mutada[dia1, hora1] = agenda_mutada[dia2, hora2]
                agenda_mutada[dia2, hora2] = temp
        
        return agenda_mutada
    
    def _reparar_cromossomo(self, agenda: np.ndarray) -> np.ndarray:
        """
        Repara cromossomo para garantir que todas as disciplinas sejam atendidas
        EXATAMENTE com a carga horária especificada (sem aulas extras)
        """
        # Contar aulas atuais por disciplina
        aulas_atuais = {}
        for dia in range(self.num_dias):
            for horario in range(self.num_horarios):
                aula = agenda[dia, horario]
                if aula is not None:
                    disc = aula.disciplina
                    aulas_atuais[disc] = aulas_atuais.get(disc, 0) + 1
        
        # Primeiro: remover aulas extras
        for disc_codigo, disciplina in self.disciplinas.items():
            aulas_presentes = aulas_atuais.get(disc_codigo, 0)
            aulas_necessarias = disciplina.carga_horaria
            
            if aulas_presentes > aulas_necessarias:
                # Remover aulas extras
                aulas_extras = aulas_presentes - aulas_necessarias
                aulas_removidas = 0
                
                for dia in range(self.num_dias):
                    for horario in range(self.num_horarios):
                        if aulas_removidas >= aulas_extras:
                            break
                        aula = agenda[dia, horario]
                        if aula is not None and aula.disciplina == disc_codigo:
                            agenda[dia, horario] = None
                            aulas_removidas += 1
                    if aulas_removidas >= aulas_extras:
                        break
        
        # Segundo: adicionar aulas faltantes (se necessário)
        for disc_codigo, disciplina in self.disciplinas.items():
            # Recontar após remoção
            aulas_presentes = sum(1 for dia in range(self.num_dias) 
                                for horario in range(self.num_horarios)
                                if agenda[dia, horario] is not None and 
                                agenda[dia, horario].disciplina == disc_codigo)
            aulas_necessarias = disciplina.carga_horaria
            
            if aulas_presentes < aulas_necessarias:
                # Adicionar aulas faltantes
                aulas_faltando = aulas_necessarias - aulas_presentes
                
                # Encontrar professor da disciplina
                professor = None
                for prof_codigo, prof in self.professores.items():
                    if prof.disciplina == disc_codigo:
                        professor = prof_codigo
                        break
                
                # Procurar slots vazios e adicionar aulas
                slots_vazios = [(d, h) for d in range(self.num_dias) 
                               for h in range(self.num_horarios) 
                               if agenda[d, h] is None]
                
                aulas_adicionadas = 0
                for dia, horario in slots_vazios:
                    if aulas_adicionadas >= aulas_faltando:
                        break
                    nova_aula = Aula(
                        disciplina=disc_codigo,
                        professor=professor,
                        sala=list(self.salas.keys())[0]
                    )
                    nova_aula.grupo_dia = 0  # Grupo padrão para aulas de reparo
                    nova_aula.posicao_no_grupo = aulas_adicionadas
                    agenda[dia, horario] = nova_aula
                    aulas_adicionadas += 1
        
        return agenda
    
    def executar(self) -> Tuple[np.ndarray, float, List[float]]:
        """Executa o algoritmo genético"""
        print("📚 Carregando dados...")
        self.carregar_dados()
        
        print("🧬 Inicializando população...")
        populacao = self.inicializar_populacao()
        
        historico_fitness = []
        melhor_global = None
        melhor_fitness_global = 0
        
        print("🚀 Iniciando evolução...")
        for geracao in range(self.geracoes):
            # Avaliar fitness
            fitness_scores = [self.calcular_fitness(ind) for ind in populacao]
            
            # Encontrar melhor da geração
            melhor_fitness_geracao = max(fitness_scores)
            melhor_indice = fitness_scores.index(melhor_fitness_geracao)
            
            if melhor_fitness_geracao > melhor_fitness_global:
                melhor_fitness_global = melhor_fitness_geracao
                melhor_global = copy.deepcopy(populacao[melhor_indice])
            
            historico_fitness.append(melhor_fitness_geracao)
            
            # Log do progresso
            if geracao % 50 == 0:
                print(f"Geração {geracao}: Melhor fitness = {melhor_fitness_geracao:.0f}")
            
            # Verificar critério de parada
            if geracao > 100 and len(set(historico_fitness[-50:])) == 1:
                print(f"Convergência detectada na geração {geracao}!")
                break
            
            # Criar nova população
            nova_populacao = []
            
            # Elitismo: manter os melhores
            elite_size = max(1, self.populacao_size // 10)
            indices_elite = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i], reverse=True)[:elite_size]
            
            for i in indices_elite:
                nova_populacao.append(copy.deepcopy(populacao[i]))
            
            # Gerar resto da população
            while len(nova_populacao) < self.populacao_size:
                pai1 = self.selecao_torneio(populacao, fitness_scores)
                pai2 = self.selecao_torneio(populacao, fitness_scores)
                
                filho1, filho2 = self.crossover_agenda(pai1, pai2)
                
                filho1 = self.mutacao_agenda(filho1)
                filho2 = self.mutacao_agenda(filho2)
                
                nova_populacao.extend([filho1, filho2])
            
            # Ajustar tamanho da população
            populacao = nova_populacao[:self.populacao_size]
        
        print(f"✅ Evolução finalizada. Melhor fitness: {melhor_fitness_global:.0f}")
        return melhor_global, melhor_fitness_global, historico_fitness
    
    def exibir_agenda(self, agenda: np.ndarray):
        """Exibe a agenda de forma organizada"""
        print("\n" + "="*100)
        print("📅 AGENDA OTIMIZADA")
        print("="*100)
        
        # Cabeçalho
        print(f"{'HORÁRIO':<10}", end="")
        for dia in self.dias:
            print(f"{dia:<18}", end="")
        print()
        print("-" * 100)
        
        # Linhas da agenda
        for h, horario in enumerate(self.horarios):
            print(f"{horario:<10}", end="")
            for d in range(self.num_dias):
                aula = agenda[d, h]
                if aula is not None:
                    disciplina = self.disciplinas[aula.disciplina]
                    professor = self.professores[aula.professor]
                    texto = f"{disciplina.nome[:12]}({professor.nome[:4]})"
                    print(f"{texto:<18}", end="")
                else:
                    print(f"{'LIVRE':<18}", end="")
            print()
        
        # Estatísticas
        print("\n" + "="*100)
        self._exibir_estatisticas(agenda)
    
    def _exibir_estatisticas(self, agenda: np.ndarray):
        """Exibe estatísticas da agenda com verificação de carga horária e distribuição"""
        print("📊 ESTATÍSTICAS DA AGENDA")
        print("-" * 50)
        
        # Aulas por dia
        print("Distribuição por dia:")
        total_aulas_agenda = 0
        for d, dia in enumerate(self.dias):
            aulas = sum(1 for h in range(self.num_horarios) if agenda[d, h] is not None)
            total_aulas_agenda += aulas
            print(f"  {dia}: {aulas} aulas")
        
        # Aulas por disciplina com verificação de distribuição
        print("\nAulas por disciplina:")
        aulas_por_disc = {}
        distribuicao_por_disc = {}
        
        for d in range(self.num_dias):
            for h in range(self.num_horarios):
                aula = agenda[d, h]
                if aula is not None:
                    disc = aula.disciplina
                    aulas_por_disc[disc] = aulas_por_disc.get(disc, 0) + 1
                    
                    if disc not in distribuicao_por_disc:
                        distribuicao_por_disc[disc] = [0] * self.num_dias
                    distribuicao_por_disc[disc][d] += 1
        
        total_aulas_necessarias = sum(disc.carga_horaria for disc in self.disciplinas.values())
        
        for disc_codigo, count in aulas_por_disc.items():
            disciplina = self.disciplinas[disc_codigo]
            necessarias = disciplina.carga_horaria
            
            if count == necessarias:
                status = "✅"
            elif count < necessarias:
                status = "❌"
            else:
                status = "⚠️"  # Aulas extras
            
            # Mostrar distribuição real vs planejada
            dist_real = [x for x in distribuicao_por_disc[disc_codigo] if x > 0]
            dist_real.sort(reverse=True)
            dist_planejada = sorted(self.distribuicao_disciplinas[disc_codigo]['distribuicao'], reverse=True)
            
            print(f"  {status} {disciplina.nome[:30]}: {count}/{necessarias}h")
            
            # Mostrar distribuição
            dist_status = "✅" if dist_real == dist_planejada else "⚠️"
            print(f"      {dist_status} Distribuição: {dist_real} (planejado: {dist_planejada})")
        
        # Verificar aulas consecutivas por disciplina
        print("\nAulas consecutivas por disciplina:")
        for disc_codigo, disciplina in self.disciplinas.items():
            max_consecutivas = 0
            dias_com_consecutivas = []
            
            for d in range(self.num_dias):
                consecutivas = self._contar_aulas_consecutivas_disciplina_stats(agenda, disc_codigo, d)
                if consecutivas >= 2:
                    max_consecutivas = max(max_consecutivas, consecutivas)
                    dias_com_consecutivas.append(f"{self.dias[d]}({consecutivas})")
            
            if dias_com_consecutivas:
                print(f"  📚 {disciplina.nome[:30]}: {', '.join(dias_com_consecutivas)}")
            else:
                print(f"  ⚠️ {disciplina.nome[:30]}: Sem aulas consecutivas")
        
        # Resumo de slots
        slots_ocupados = total_aulas_agenda
        slots_totais = self.num_dias * self.num_horarios
        slots_necessarios = total_aulas_necessarias
        
        print(f"\nResumo de slots:")
        print(f"  • Slots necessários: {slots_necessarios}")
        print(f"  • Slots ocupados: {slots_ocupados}")
        print(f"  • Slots disponíveis: {slots_totais}")
        print(f"  • Slots livres: {slots_totais - slots_ocupados}")
        
        if slots_ocupados > slots_necessarios:
            print(f"  ⚠️ Aulas extras detectadas: {slots_ocupados - slots_necessarios}")
        
        # Disponibilidade
        aulas_disponiveis = sum(1 for d in range(self.num_dias) for h in range(self.num_horarios) 
                               if agenda[d, h] is not None and 
                               self._professor_disponivel(agenda[d, h].professor, d, h))
        
        if total_aulas_agenda > 0:
            perc_disponibilidade = (aulas_disponiveis / total_aulas_agenda) * 100
            print(f"\nDisponibilidade respeitada: {perc_disponibilidade:.1f}%")
            
        # Verificação de integridade
        print(f"\n🔍 Verificação de integridade:")
        disciplinas_corretas = sum(1 for disc_codigo, disciplina in self.disciplinas.items()
                                 if aulas_por_disc.get(disc_codigo, 0) == disciplina.carga_horaria)
        total_disciplinas = len(self.disciplinas)
        print(f"  • Disciplinas com carga correta: {disciplinas_corretas}/{total_disciplinas}")
        
        # Verificação de distribuição
        disciplinas_bem_distribuidas = 0
        for disc_codigo in self.disciplinas.keys():
            if disc_codigo in distribuicao_por_disc:
                dist_real = [x for x in distribuicao_por_disc[disc_codigo] if x > 0]
                dist_real.sort(reverse=True)
                dist_planejada = sorted(self.distribuicao_disciplinas[disc_codigo]['distribuicao'], reverse=True)
                if dist_real == dist_planejada:
                    disciplinas_bem_distribuidas += 1
        
        print(f"  • Disciplinas com distribuição correta: {disciplinas_bem_distribuidas}/{total_disciplinas}")
        
        if disciplinas_corretas == total_disciplinas and disciplinas_bem_distribuidas == total_disciplinas:
            print("  ✅ Todas as disciplinas têm carga e distribuição corretas!")
        elif disciplinas_corretas == total_disciplinas:
            print("  ✅ Carga horária correta, ⚠️ algumas distribuições podem ser melhoradas!")
        else:
            print("  ⚠️ Algumas disciplinas têm problemas de carga ou distribuição!")
    
    def _contar_aulas_consecutivas_disciplina_stats(self, agenda: np.ndarray, disciplina: str, dia: int) -> int:
        """Conta aulas consecutivas de uma disciplina em um dia específico para estatísticas"""
        max_consecutivas = 0
        consecutivas_atual = 0
        
        for horario in range(self.num_horarios):
            aula = agenda[dia, horario]
            if aula is not None and aula.disciplina == disciplina:
                consecutivas_atual += 1
                max_consecutivas = max(max_consecutivas, consecutivas_atual)
            else:
                consecutivas_atual = 0
        
        return max_consecutivas

# Exemplo de uso
if __name__ == "__main__":
    # Criar e executar o algoritmo genético versão 2
    ga = ScheduleGA_V2()
    
    melhor_agenda, fitness, historico = ga.executar()
    
    # Exibir resultados
    ga.exibir_agenda(melhor_agenda)
    
    # Estatísticas
    print(f"\nFitness da melhor solução: {fitness:.0f}")
    print(f"Melhoria durante evolução: {historico[-1] - historico[0]:.0f}")