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
    Versão 2: Agenda com pontuação positiva
    - Genoma = Matriz (agenda) 5 dias x 4 horários
    - Fitness = Soma de pontuações positivas
    - Garantia de todas as disciplinas atendidas
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
        
        # Lista de todas as aulas necessárias
        self.aulas_obrigatorias = []
        
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
        """Cria lista de todas as aulas que devem ser alocadas"""
        self.aulas_obrigatorias = []
        
        for disc_codigo, disciplina in self.disciplinas.items():
            # Encontrar professor da disciplina
            professor = None
            for prof_codigo, prof in self.professores.items():
                if prof.disciplina == disc_codigo:
                    professor = prof_codigo
                    break
            
            # Criar aulas necessárias
            for _ in range(disciplina.carga_horaria):
                aula = Aula(
                    disciplina=disc_codigo,
                    professor=professor,
                    sala=list(self.salas.keys())[0]  # Por enquanto só temos uma sala
                )
                self.aulas_obrigatorias.append(aula)
        
        print(f"📚 Total de aulas obrigatórias: {len(self.aulas_obrigatorias)}")
    
    def criar_agenda_vazia(self) -> np.ndarray:
        """Cria uma agenda vazia (matriz 5x4)"""
        return np.full((self.num_dias, self.num_horarios), None, dtype=object)
    
    def criar_cromossomo(self) -> np.ndarray:
        """
        Cria um cromossomo (agenda completa) garantindo que todas as disciplinas sejam atendidas
        EXATAMENTE com a carga horária especificada
        """
        agenda = self.criar_agenda_vazia()
        aulas_para_alocar = copy.deepcopy(self.aulas_obrigatorias)
        
        # Embaralhar as aulas para aleatoriedade
        random.shuffle(aulas_para_alocar)
        
        # Criar lista de slots disponíveis
        slots_disponiveis = [(d, h) for d in range(self.num_dias) for h in range(self.num_horarios)]
        random.shuffle(slots_disponiveis)
        
        # Alocar APENAS as aulas necessárias (sem extras)
        for aula in aulas_para_alocar:
            if not slots_disponiveis:  # Se não há mais slots, parar
                break
                
            # Tentar encontrar um slot válido para a aula
            slot_encontrado = False
            for i, (dia, horario) in enumerate(slots_disponiveis):
                if agenda[dia, horario] is None:
                    # Verificar se o professor está disponível (se possível)
                    if self._professor_disponivel(aula.professor, dia, horario):
                        agenda[dia, horario] = aula
                        slots_disponiveis.pop(i)
                        slot_encontrado = True
                        break
            
            # Se não encontrou slot com disponibilidade, forçar alocação em qualquer slot livre
            if not slot_encontrado and slots_disponiveis:
                for i, (dia, horario) in enumerate(slots_disponiveis):
                    if agenda[dia, horario] is None:
                        agenda[dia, horario] = aula
                        slots_disponiveis.pop(i)
                        break
        
        return agenda
    
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
        
        # 3. Pontuação por distribuição equilibrada
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
        """Pontua distribuição equilibrada das aulas"""
        pontos = 0
        
        # Contar aulas por dia
        aulas_por_dia = []
        for dia in range(self.num_dias):
            count = sum(1 for h in range(self.num_horarios) if agenda[dia, h] is not None)
            aulas_por_dia.append(count)
        
        # Calcular variação
        if len(aulas_por_dia) > 0:
            media = np.mean(aulas_por_dia)
            variacao = np.std(aulas_por_dia)
            
            # Menos variação = mais pontos
            pontos += self.pesos['distribuicao_equilibrada'] * max(0, (2.0 - variacao))
        
        return pontos
    
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
        """Exibe estatísticas da agenda com verificação de carga horária"""
        print("📊 ESTATÍSTICAS DA AGENDA")
        print("-" * 50)
        
        # Aulas por dia
        print("Distribuição por dia:")
        total_aulas_agenda = 0
        for d, dia in enumerate(self.dias):
            aulas = sum(1 for h in range(self.num_horarios) if agenda[d, h] is not None)
            total_aulas_agenda += aulas
            print(f"  {dia}: {aulas} aulas")
        
        # Aulas por disciplina com verificação
        print("\nAulas por disciplina:")
        aulas_por_disc = {}
        for d in range(self.num_dias):
            for h in range(self.num_horarios):
                aula = agenda[d, h]
                if aula is not None:
                    disc = aula.disciplina
                    aulas_por_disc[disc] = aulas_por_disc.get(disc, 0) + 1
        
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
                
            print(f"  {status} {disciplina.nome[:30]}: {count}/{necessarias}h", end="")
            if count > necessarias:
                print(f" (⚠️ {count - necessarias} extra{'s' if count - necessarias > 1 else ''})")
            else:
                print()
        
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
        
        if disciplinas_corretas == total_disciplinas:
            print("  ✅ Todas as disciplinas têm carga horária correta!")
        else:
            print("  ⚠️ Algumas disciplinas têm carga horária incorreta!")

# Exemplo de uso
if __name__ == "__main__":
    # Criar e executar o algoritmo genético versão 2
    ga = ScheduleGA_V2()
    
    melhor_agenda, fitness, historico = ga.executar()
    
    # Exibir resultados
    ga.exibir_agenda(melhor_agenda)
    
    print(f"\n🏆 Fitness final: {fitness:.0f} pontos")
    print(f"📈 Melhoria: {historico[-1] - historico[0]:.0f} pontos")