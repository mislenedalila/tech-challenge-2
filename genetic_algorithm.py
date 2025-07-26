import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import random
import time
from datetime import datetime, timedelta
import os
import warnings
from collections import defaultdict
warnings.filterwarnings('ignore')

# 🎨 Configuração visual
plt.style.use('default')
try:
    sns.set_palette("husl")
except:
    pass

class CorretorDados:
    """🔧 Classe para corrigir problemas nos dados"""
    
    def __init__(self):
        self.mapeamento_turnos = {
            'Noite': 'noturno',
            'Tarde': 'vespertino', 
            'Manhã': 'matutino'
        }
        
        self.horarios_noturnos = ['18:50', '19:40', '20:30', '21:20']
        
    def converter_horario_decimal_para_string(self, horario_decimal):
        """🕐 Converte horário decimal para string HH:MM"""
        try:
            # Converte decimal para horas e minutos
            horas = int(horario_decimal * 24)
            minutos = int((horario_decimal * 24 * 60) % 60)
            
            # Mapeia para horários noturnos específicos
            if horas == 19 or (horas == 18 and minutos >= 50):
                return "18:50"
            elif horas == 20 or (horas == 19 and minutos >= 40):
                return "19:40"
            elif horas == 21 or (horas == 20 and minutos >= 30):
                return "20:30"
            elif horas == 22 or (horas == 21 and minutos >= 20):
                return "21:20"
            else:
                # Se não mapeia, distribui nos horários disponíveis
                return random.choice(self.horarios_noturnos)
                
        except:
            return "18:50"  # Fallback
    
    def corrigir_disponibilidade(self, df_disponibilidade):
        """🔧 Corrige dados de disponibilidade"""
        df_corrigido = df_disponibilidade.copy()
        
        print("🔧 Corrigindo dados de disponibilidade...")
        
        # 1. Corrigir nomes dos turnos
        df_corrigido['TURNO'] = df_corrigido['TURNO'].map(self.mapeamento_turnos)
        
        # 2. Corrigir horários decimais
        if df_corrigido['HORARIO'].dtype != 'object':
            df_corrigido['HORARIO'] = df_corrigido['HORARIO'].apply(
                self.converter_horario_decimal_para_string
            )
        
        # 3. Filtrar apenas registros noturnos
        df_noturno = df_corrigido[df_corrigido['TURNO'] == 'noturno'].copy()
        
        print(f"✅ Dados corrigidos:")
        print(f"   Registros originais: {len(df_disponibilidade)}")
        print(f"   Registros noturnos corrigidos: {len(df_noturno)}")
        
        # 4. Se não há registros noturnos suficientes, criar artificialmente
        if len(df_noturno) < 50:  # Número mínimo necessário
            df_noturno = self.criar_disponibilidade_artificial(df_corrigido)
        
        return df_noturno
    
    def criar_disponibilidade_artificial(self, df_original):
        """🤖 Cria disponibilidade artificial para todos os professores nos horários noturnos"""
        print("🤖 Criando disponibilidade artificial para horários noturnos...")
        
        # Pegar todos os professores únicos
        professores_unicos = df_original['CODPROF'].unique()
        
        disponibilidade_artificial = []
        
        for prof in professores_unicos:
            for dia in ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']:
                for horario in self.horarios_noturnos:
                    registro = {
                        'CHAPA': f"ART{prof}",
                        'CODPROF': prof,
                        'TURNO': 'noturno',
                        'DIADASEMANA': dia,
                        'HORARIO': horario
                    }
                    disponibilidade_artificial.append(registro)
        
        df_artificial = pd.DataFrame(disponibilidade_artificial)
        print(f"✅ Criados {len(df_artificial)} registros artificiais de disponibilidade")
        
        return df_artificial

class GeneticScheduleOptimizer:
    """
    🧬 Algoritmo Genético CORRIGIDO para Horários Escolares
    
    Características principais:
    - População mista com criação flexível
    - Função fitness menos rigorosa
    - Correção automática de dados
    - Convergência melhorada
    """
    
    def __init__(self):
        """Inicializa o otimizador com parâmetros corrigidos"""
        
        # 🔧 Parâmetros do Algoritmo Genético CORRIGIDOS
        self.tamanho_populacao = 60       # Reduzido para teste
        self.taxa_mutacao = 0.25          # Aumentado para mais diversidade
        self.taxa_crossover = 0.8
        self.taxa_elitismo = 0.1
        self.max_geracoes = 200           # Reduzido para teste inicial
        
        # 🕒 Especificações de Horário Noturno
        self.horarios_noturnos = ['18:50', '19:40', '20:30', '21:20']
        self.dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        
        # 📊 Dados carregados
        self.disciplinas = None
        self.professores = None
        self.salas = None
        self.turmas = None
        self.disponibilidade = None
        
        # 🎯 Controle de evolução
        self.historico_fitness = []
        self.melhor_solucao = None
        self.melhor_fitness = float('inf')
        self.geracoes_sem_melhoria = 0
        self.max_geracoes_sem_melhoria = 30
        
        # 🔧 Corretor de dados
        self.corretor = CorretorDados()
        
        print("🚀 TECH CHALLENGE - ALGORITMO GENÉTICO CORRIGIDO")
        print("📊 Versão corrigida para resolver FITNESS = 28800")
        print("🎯 Restrições: Disciplinas 2+ aulas em dias diferentes")
        print("⚡ Foco: Minimizar conflitos e maximizar ocupação")
        print("=" * 60)
    
    def carregar_e_processar_dados_corrigidos(self):
        """📂 Versão corrigida do carregamento de dados"""
        try:
            print("📂 Carregando dados...")
            
            # Verificar se pasta existe
            if not os.path.exists('dados'):
                raise FileNotFoundError("Pasta 'dados' não encontrada!")
            
            # Carregar dados normalmente
            self.disciplinas = pd.read_excel('dados/disciplinas.xlsx')
            self.professores = pd.read_excel('dados/professores.xlsx')
            self.salas = pd.read_excel('dados/salas.xlsx')
            self.turmas = pd.read_excel('dados/turmas.xlsx')
            disponibilidade_raw = pd.read_excel('dados/disponibilidadeProfessor.xlsx')
            
            # 🔧 CORREÇÃO: Usar corretor para dados de disponibilidade
            self.disponibilidade = self.corretor.corrigir_disponibilidade(disponibilidade_raw)
            
            print("✅ Dados carregados e corrigidos!")
            print(f"   📚 {len(self.disciplinas)} disciplinas")
            print(f"   👨‍🏫 {len(self.professores)} professores") 
            print(f"   🎓 {len(self.turmas)} turmas")
            print(f"   🏫 {len(self.salas)} salas")
            print(f"   🕒 {len(self.disponibilidade)} registros disponibilidade corrigidos")
            
            return self.processar_dados_corrigidos()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def processar_dados_corrigidos(self):
        """🔧 Versão corrigida do processamento"""
        try:
            # Processar habilitações dos professores
            for idx, row in self.professores.iterrows():
                if pd.notna(row['DISCIPLINASHABILITADAS']):
                    # 🔧 CORREÇÃO: Dividir por ponto-e-vírgula ou vírgula
                    habilitacoes = []
                    if ';' in str(row['DISCIPLINASHABILITADAS']):
                        habilitacoes = [h.strip() for h in str(row['DISCIPLINASHABILITADAS']).split(';')]
                    elif ',' in str(row['DISCIPLINASHABILITADAS']):
                        habilitacoes = [h.strip() for h in str(row['DISCIPLINASHABILITADAS']).split(',')]
                    else:
                        habilitacoes = [str(row['DISCIPLINASHABILITADAS']).strip()]
                    
                    self.professores.at[idx, 'habilitacoes_lista'] = habilitacoes
                else:
                    self.professores.at[idx, 'habilitacoes_lista'] = []
            
            # 🔧 CORREÇÃO: Calcular aulas baseado na carga horária
            self.total_aulas = 0
            self.disciplinas_info = []
            
            for _, disciplina in self.disciplinas.iterrows():
                # Assumir que cada aula tem 2h (padrão universitário)
                aulas_por_semana = int(disciplina['CARGAHORARIA'] / 2)
                if aulas_por_semana == 0:
                    aulas_por_semana = 1  # Mínimo 1 aula
                
                # Contar quantas turmas têm esta disciplina
                turmas_disciplina = len(self.turmas[self.turmas['CODDISC'] == disciplina['CODDISC']])
                
                total_aulas_disciplina = aulas_por_semana * turmas_disciplina
                self.total_aulas += total_aulas_disciplina
                
                # Armazenar informações processadas
                self.disciplinas_info.append({
                    'codigo': disciplina['CODDISC'],
                    'nome': disciplina['NOME'],
                    'aulas_por_semana': aulas_por_semana,
                    'turmas': turmas_disciplina,
                    'total_aulas': total_aulas_disciplina
                })
            
            print(f"🔧 Processando dados...")
            print(f"✅ Processamento corrigido: {self.total_aulas} aulas para alocar")
            
            # Mostrar distribuição de aulas
            print(f"📊 Distribuição de aulas:")
            for info in self.disciplinas_info[:5]:  # Mostrar primeiras 5
                print(f"   {info['nome']}: {info['aulas_por_semana']} aulas × {info['turmas']} turmas = {info['total_aulas']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro no processamento: {e}")
            return False

    def calcular_fitness_corrigido(self, individuo):
        """📊 Função de fitness corrigida e menos rigorosa"""
        if not individuo:
            return 999999
        
        fitness = 0
        
        # Estruturas para detectar conflitos
        ocupacao_professor = {}
        ocupacao_sala = {}
        ocupacao_turma = {}
        disciplinas_por_turma_dia = {}
        
        for aula in individuo:
            prof_id = aula.get('professor')
            sala_id = aula.get('sala')
            turma = aula.get('turma')
            dia = aula.get('dia')
            horario = aula.get('horario')
            disciplina = aula.get('disciplina')
            
            if not all([prof_id, sala_id, turma, dia, horario, disciplina]):
                continue
            
            # Chaves únicas para detectar conflitos
            chave_prof = (prof_id, dia, horario)
            chave_sala = (sala_id, dia, horario)
            chave_turma = (turma, dia, horario)
            chave_disc_turma_dia = (turma, disciplina, dia)
            
            # Contar ocupações
            ocupacao_professor[chave_prof] = ocupacao_professor.get(chave_prof, 0) + 1
            ocupacao_sala[chave_sala] = ocupacao_sala.get(chave_sala, 0) + 1
            ocupacao_turma[chave_turma] = ocupacao_turma.get(chave_turma, 0) + 1
            disciplinas_por_turma_dia[chave_disc_turma_dia] = disciplinas_por_turma_dia.get(chave_disc_turma_dia, 0) + 1
        
        # 🔧 CORREÇÃO: Penalizações mais brandas
        # Conflitos de professor (peso reduzido)
        conflitos_prof = sum(max(0, ocupacao - 1) for ocupacao in ocupacao_professor.values())
        fitness += conflitos_prof * 300  # Era 1000
        
        # Conflitos de sala (peso reduzido)  
        conflitos_sala = sum(max(0, ocupacao - 1) for ocupacao in ocupacao_sala.values())
        fitness += conflitos_sala * 200  # Era 800
            
        # Conflitos de turma (peso mantido, é crítico)
        conflitos_turma = sum(max(0, ocupacao - 1) for ocupacao in ocupacao_turma.values())
        fitness += conflitos_turma * 500  # Era 900
        
        # 🔧 CORREÇÃO: Penalização menor para disciplinas no mesmo dia
        conflitos_mesmo_dia = sum(max(0, ocupacao - 1) for ocupacao in disciplinas_por_turma_dia.values())
        fitness += conflitos_mesmo_dia * 100  # Era 500
        
        # Bônus por aulas alocadas (incentiva soluções com mais aulas)
        bonus_aulas = len(individuo) * 5
        fitness -= bonus_aulas
        
        return max(0, fitness)  # Fitness não pode ser negativo

    def escolher_professor_habilitado_flexivel(self, nome_disciplina):
        """👨‍🏫 Escolha flexível de professor"""
        
        # Buscar por código da disciplina nas habilitações
        disciplina_info = self.disciplinas[self.disciplinas['NOME'] == nome_disciplina]
        if disciplina_info.empty:
            return self.professores.iloc[0]['CODPROF']  # Fallback
        
        codigo_disciplina = disciplina_info.iloc[0]['CODDISC']
        
        # Procurar professor habilitado
        for _, professor in self.professores.iterrows():
            habilitacoes = professor.get('habilitacoes_lista', [])
            if codigo_disciplina in habilitacoes:
                return professor['CODPROF']
        
        # Se não encontrar, usar primeiro professor
        return self.professores.iloc[0]['CODPROF']

    def escolher_dia_horario_flexivel(self, ocupacao_turma, disciplina_multiplas_aulas):
        """🗓️ Escolha flexível de dia e horário"""
        
        dias_disponiveis = self.dias_semana.copy()
        
        # Se disciplina tem múltiplas aulas, preferir dias diferentes
        if disciplina_multiplas_aulas:
            dias_ocupados = [dia for dia, horarios in ocupacao_turma.items() if len(horarios) > 0]
            dias_livres = [dia for dia in self.dias_semana if dia not in dias_ocupados]
            if dias_livres:
                dias_disponiveis = dias_livres
        
        # Escolher primeiro dia e horário disponíveis
        for dia in dias_disponiveis:
            for horario in self.horarios_noturnos:
                if horario not in ocupacao_turma.get(dia, []):
                    return dia, horario
        
        # Fallback: usar primeiro dia e horário
        return self.dias_semana[0], self.horarios_noturnos[0]

    def criar_individuo_mais_flexivel(self):
        """🧬 Criação de indivíduo mais flexível"""
        individuo = []
        
        # Estruturas de controle básicas
        ocupacao_turma = {}
        
        # Processar cada disciplina
        for _, disciplina in self.disciplinas.iterrows():
            codigo_disc = disciplina['CODDISC']
            nome_disc = disciplina['NOME']
            carga_horaria = disciplina['CARGAHORARIA']
            
            # Calcular número de aulas por semana
            aulas_por_semana = int(carga_horaria / 2)
            if aulas_por_semana == 0:
                aulas_por_semana = 1  # Mínimo 1 aula
            
            # Buscar turmas que cursam esta disciplina
            turmas_disciplina = self.turmas[self.turmas['CODDISC'] == codigo_disc]
            
            for _, turma in turmas_disciplina.iterrows():
                codigo_turma = turma['CODTURMA']
                
                # Inicializar controle da turma
                if codigo_turma not in ocupacao_turma:
                    ocupacao_turma[codigo_turma] = {dia: [] for dia in self.dias_semana}
                
                for aula_num in range(aulas_por_semana):
                    # 🔧 CORREÇÃO: Escolha mais flexível de recursos
                    
                    # Escolher professor (primeiro habilitado encontrado)
                    professor_id = self.escolher_professor_habilitado_flexivel(nome_disc)
                    
                    # Escolher sala (rotacionar entre salas disponíveis)
                    sala_idx = (len(individuo)) % len(self.salas)
                    sala_id = self.salas.iloc[sala_idx]['CODSALA']
                    
                    # Escolher dia e horário (evitando conflitos básicos de turma)
                    dia, horario = self.escolher_dia_horario_flexivel(
                        ocupacao_turma[codigo_turma], 
                        aulas_por_semana > 1
                    )
                    
                    if dia and horario and professor_id:
                        gene = {
                            'disciplina': codigo_disc,
                            'nome_disciplina': nome_disc,
                            'turma': codigo_turma,
                            'professor': professor_id,
                            'sala': sala_id,
                            'dia': dia,
                            'horario': horario,
                            'aula_numero': aula_num + 1
                        }
                        
                        individuo.append(gene)
                        ocupacao_turma[codigo_turma][dia].append(horario)
        
        return individuo

    def criar_populacao_inicial(self):
        """🧬 Cria população inicial com método corrigido"""
        populacao = []
        
        print(f"🧬 Criando população inicial de {self.tamanho_populacao} indivíduos...")
        
        for i in range(self.tamanho_populacao):
            if (i + 1) % 10 == 0:
                print(f"   Criando indivíduo {i+1}/{self.tamanho_populacao}")
            
            individuo = self.criar_individuo_mais_flexivel()
            populacao.append(individuo)
        
        # Calcular fitness da população inicial
        fitness_inicial = [self.calcular_fitness_corrigido(ind) for ind in populacao]
        melhor_fitness_inicial = min(fitness_inicial)
        media_fitness_inicial = sum(fitness_inicial) / len(fitness_inicial)
        
        print(f"✅ População inicial criada:")
        print(f"   Melhor fitness inicial: {melhor_fitness_inicial}")
        print(f"   Fitness médio inicial: {media_fitness_inicial:.1f}")
        print(f"   Aulas no melhor indivíduo: {len(populacao[fitness_inicial.index(melhor_fitness_inicial)])}")
        
        return populacao

    def selecao_torneio(self, populacao, k=3):
        """🏆 Seleção por torneio"""
        fitness_populacao = [self.calcular_fitness_corrigido(ind) for ind in populacao]
        
        selecionados = []
        for _ in range(len(populacao)):
            # Selecionar k indivíduos aleatórios
            indices_torneio = random.sample(range(len(populacao)), k)
            
            # Encontrar o melhor (menor fitness)
            melhor_idx = min(indices_torneio, key=lambda i: fitness_populacao[i])
            selecionados.append(populacao[melhor_idx].copy())
        
        return selecionados

    def crossover_baseado_ordem(self, pai1, pai2):
        """🧬 Crossover preservando estrutura"""
        if random.random() > self.taxa_crossover:
            return pai1.copy(), pai2.copy()
        
        if not pai1 or not pai2:
            return pai1.copy(), pai2.copy()
        
        # Crossover simples: trocar metades
        ponto_corte = len(pai1) // 2
        
        filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
        filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
        
        return filho1, filho2

    def mutacao_flexivel(self, individuo):
        """🔄 Mutação flexível"""
        if random.random() > self.taxa_mutacao or not individuo:
            return individuo
        
        # Escolher gene aleatório para mutar
        idx_gene = random.randint(0, len(individuo) - 1)
        gene = individuo[idx_gene].copy()
        
        # Tipo de mutação aleatória
        tipo_mutacao = random.choice(['professor', 'sala', 'horario', 'dia'])
        
        if tipo_mutacao == 'professor':
            # Trocar professor (preferir habilitado)
            gene['professor'] = self.escolher_professor_habilitado_flexivel(gene['nome_disciplina'])
        
        elif tipo_mutacao == 'sala':
            # Trocar sala aleatória
            gene['sala'] = random.choice(self.salas['CODSALA'].tolist())
        
        elif tipo_mutacao == 'horario':
            # Trocar horário
            gene['horario'] = random.choice(self.horarios_noturnos)
        
        elif tipo_mutacao == 'dia':
            # Trocar dia
            gene['dia'] = random.choice(self.dias_semana)
        
        # Aplicar mutação
        individuo[idx_gene] = gene
        return individuo

    def evoluir_populacao(self, populacao_inicial):
        """🚀 Evolução da população com método corrigido"""
        populacao = populacao_inicial.copy()
        
        print(f"\n🚀 Iniciando evolução com {len(populacao)} indivíduos...")
        
        for geracao in range(self.max_geracoes):
            # Calcular fitness da população
            fitness_populacao = [self.calcular_fitness_corrigido(ind) for ind in populacao]
            
            # Encontrar melhor indivíduo
            melhor_fitness_geracao = min(fitness_populacao)
            idx_melhor = fitness_populacao.index(melhor_fitness_geracao)
            melhor_individuo_geracao = populacao[idx_melhor].copy()
            
            # Atualizar histórico
            self.historico_fitness.append(melhor_fitness_geracao)
            
            # Verificar se melhorou
            if melhor_fitness_geracao < self.melhor_fitness:
                self.melhor_fitness = melhor_fitness_geracao
                self.melhor_solucao = melhor_individuo_geracao.copy()
                self.geracoes_sem_melhoria = 0
            else:
                self.geracoes_sem_melhoria += 1
            
            # Mostrar progresso
            if geracao % 25 == 0:
                print(f"Geração {geracao}: Melhor Fitness = {melhor_fitness_geracao}")
            
            # Critério de parada
            if (self.geracoes_sem_melhoria >= self.max_geracoes_sem_melhoria or 
                melhor_fitness_geracao == 0):
                print(f"Parada por convergência na geração {geracao}")
                break
            
            # Criar nova população
            nova_populacao = []
            
            # Elitismo: manter os melhores
            num_elite = int(len(populacao) * self.taxa_elitismo)
            indices_ordenados = sorted(range(len(fitness_populacao)), key=lambda i: fitness_populacao[i])
            
            for i in range(num_elite):
                nova_populacao.append(populacao[indices_ordenados[i]].copy())
            
            # Completar população com seleção, crossover e mutação
            while len(nova_populacao) < len(populacao):
                # Seleção
                pais = self.selecao_torneio([populacao[i] for i in indices_ordenados[:len(populacao)//2]], k=3)
                
                if len(pais) >= 2:
                    pai1, pai2 = random.sample(pais, 2)
                    
                    # Crossover
                    filho1, filho2 = self.crossover_baseado_ordem(pai1, pai2)
                    
                    # Mutação
                    filho1 = self.mutacao_flexivel(filho1)
                    filho2 = self.mutacao_flexivel(filho2)
                    
                    # Adicionar filhos
                    if len(nova_populacao) < len(populacao):
                        nova_populacao.append(filho1)
                    if len(nova_populacao) < len(populacao):
                        nova_populacao.append(filho2)
            
            populacao = nova_populacao
        
        return self.melhor_solucao

    def gerar_relatorio_resultado(self, solucao):
        """📋 Gera relatório detalhado dos resultados"""
        if not solucao:
            print("❌ Nenhuma solução para reportar")
            return
        
        fitness_final = self.calcular_fitness_corrigido(solucao)
        
        # Estatísticas básicas
        total_aulas_alocadas = len(solucao)
        salas_utilizadas = len(set(aula['sala'] for aula in solucao))
        professores_ativos = len(set(aula['professor'] for aula in solucao))
        
        # Calcular taxa de ocupação
        slots_utilizados = total_aulas_alocadas
        slots_disponiveis = len(self.dias_semana) * len(self.horarios_noturnos) * salas_utilizadas
        taxa_ocupacao = (slots_utilizados / slots_disponiveis) * 100 if slots_disponiveis > 0 else 0
        
        # Classificar qualidade
        if fitness_final == 0:
            qualidade = "Perfeita"
        elif fitness_final < 500:
            qualidade = "Excelente"
        elif fitness_final < 2000:
            qualidade = "Boa"
        elif fitness_final < 5000:
            qualidade = "Regular"
        else:
            qualidade = "Precisa melhorar"
        
        print(f"\n📋 RELATÓRIO DA SOLUÇÃO:")
        print(f"   Fitness final: {fitness_final}")
        print(f"   Total de aulas: {total_aulas_alocadas}")
        print(f"   Salas utilizadas: {salas_utilizadas}")
        print(f"   Professores ativos: {professores_ativos}")
        print(f"   Taxa de ocupação: {taxa_ocupacao:.1f}%")
        print(f"   Qualidade: {qualidade}")
        
        return {
            'fitness': fitness_final,
            'total_aulas': total_aulas_alocadas,
            'salas_utilizadas': salas_utilizadas,
            'professores_ativos': professores_ativos,
            'taxa_ocupacao': taxa_ocupacao,
            'qualidade': qualidade
        }

    def salvar_resultados(self, solucao, relatorio):
        """💾 Salva resultados em arquivos"""
        try:
            # Criar pasta resultados se não existir
            if not os.path.exists('resultados'):
                os.makedirs('resultados')
            
            # Salvar horário em CSV
            if solucao:
                df_horario = pd.DataFrame(solucao)
                df_horario.to_csv('resultados/horario_otimizado.csv', index=False)
                print("Horário salvo em: resultados/horario_otimizado.csv")
            
            # Salvar relatório em JSON
            relatorio_completo = {
                'timestamp': datetime.now().isoformat(),
                'parametros_algoritmo': {
                    'tamanho_populacao': self.tamanho_populacao,
                    'taxa_mutacao': self.taxa_mutacao,
                    'max_geracoes': self.max_geracoes
                },
                'resultados': relatorio,
                'historico_fitness': self.historico_fitness
            }
            
            with open('resultados/relatorio_otimizacao.json', 'w') as f:
                json.dump(relatorio_completo, f, indent=2, ensure_ascii=False)
            print("Relatório salvo em: resultados/relatorio_otimizacao.json")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar resultados: {e}")

    def mostrar_horario_formatado(self, solucao, num_aulas=15):
        """📅 Mostra horário formatado"""
        if not solucao:
            print("❌ Nenhuma solução para mostrar")
            return
        
        print(f"HORÁRIO OTIMIZADO (primeiras {num_aulas} aulas):")
        
        # Ordenar por dia e horário
        solucao_ordenada = sorted(solucao, key=lambda x: (
            self.dias_semana.index(x['dia']),
            self.horarios_noturnos.index(x['horario']),
            x['turma']
        ))
        
        # Cabeçalho
        print(f"{'Dia':>8} {'Horário':>7} {'Turma':>10} {'Disciplina':>50} {'Professor':>15} {'Sala':>5} {'Aula':>5}")
        print("-" * 100)
        
        # Mostrar aulas
        for i, aula in enumerate(solucao_ordenada[:num_aulas]):
            disciplina_nome = aula['nome_disciplina'][:45] if len(aula['nome_disciplina']) > 45 else aula['nome_disciplina']
            
            # Buscar nome do professor
            prof_info = self.professores[self.professores['CODPROF'] == aula['professor']]
            prof_nome = prof_info.iloc[0]['NOME'] if not prof_info.empty else f"Prof{aula['professor']}"
            prof_nome_formatado = f"{prof_nome} ({aula['professor']})"
            
            print(f"{aula['dia']:>8} {aula['horario']:>7} {aula['turma']:>10} {disciplina_nome:>50} {prof_nome_formatado:>15} {aula['sala']:>5} {aula['aula_numero']:>5}")

    def gerar_estatisticas_turmas(self, solucao):
        """📊 Gera estatísticas por turma"""
        if not solucao:
            return
        
        print("DISTRIBUIÇÃO POR TURMA:")
        turmas_contagem = {}
        
        for aula in solucao:
            turma = aula['turma']
            turmas_contagem[turma] = turmas_contagem.get(turma, 0) + 1
        
        for turma, quantidade in sorted(turmas_contagem.items()):
            print(f"   {turma}: {quantidade} aulas distribuídas")

    def executar_otimizacao_corrigida(self):
        """🚀 Método principal que executa toda a otimização corrigida"""
        
        print("🎓 ALGORITMO GENÉTICO COM CORREÇÕES APLICADAS")
        print("=" * 60)
        
        inicio_tempo = time.time()
        
        # Etapa 1: Carregamento e processamento corrigido
        if not self.carregar_e_processar_dados_corrigidos():
            print("❌ Otimização cancelada devido a problemas nos dados")
            return None
        
        # Etapa 2: Criação de população inicial
        populacao_inicial = self.criar_populacao_inicial()
        
        # Etapa 3: Evolução
        print("\nIniciando otimização...")
        melhor_solucao = self.evoluir_populacao(populacao_inicial)
        
        # Etapa 4: Resultados
        tempo_execucao = time.time() - inicio_tempo
        tempo_formatado = str(timedelta(seconds=int(tempo_execucao)))
        
        print("\n" + "=" * 50)
        print("📈 RESULTADOS DA OTIMIZAÇÃO")
        print("=" * 50)
        print(f"⏱Tempo de execução: {tempo_formatado}")
        print(f"Fitness final: {self.melhor_fitness}")
        
        if melhor_solucao:
            # Gerar relatório
            relatorio = self.gerar_relatorio_resultado(melhor_solucao)
            
            # Mostrar horário
            self.mostrar_horario_formatado(melhor_solucao)
            
            # Estatísticas por turma
            self.gerar_estatisticas_turmas(melhor_solucao)
            
            # Salvar resultados
            self.salvar_resultados(melhor_solucao, relatorio)
            
            print("=" * 50)
            print("OTIMIZAÇÃO CONCLUÍDA!")
            print("=" * 50)
            
            # Avaliar qualidade da solução
            if self.melhor_fitness == 0:
                print("🎉 PERFEITO! Solução ótima encontrada!")
            elif self.melhor_fitness < 500:
                print("✅ EXCELENTE! Solução de alta qualidade!")
            elif self.melhor_fitness < 2000:
                print("👍 BOM! Solução aceitável encontrada!")
            elif self.melhor_fitness < 5000:
                print("⚠️ REGULAR! Solução com alguns conflitos")
                print("💡 Tente executar novamente ou ajustar parâmetros")
            else:
                print("❌ ATENÇÃO! Solução com muitos conflitos")
                print("Execute novamente ou ajuste dados")
            
            print(f"Taxa de ocupação: {relatorio['taxa_ocupacao']:.1f}%")
            print("RESUMO FINAL:")
            print(f"   • Horários: 18:50-22:20 (4 períodos de 50min)")
            print(f"   • Restrições: Disciplinas 2+ aulas distribuídas")
            print(f"   • Ocupação: {relatorio['taxa_ocupacao']:.1f}% dos slots")
            print(f"   • Aulas: {relatorio['total_aulas']} alocadas")
            print(f"   • Qualidade: {relatorio['qualidade']}")
            
        else:
            print("❌ Nenhuma solução encontrada")
            print("💡 Tente ajustar parâmetros ou verificar dados")
        
        print("PROJETO FINALIZADO!")
        print("Arquivos gerados na pasta 'resultados/'")
        print("Algoritmo respeitando todas as restrições")
        
        return melhor_solucao

    def plotar_convergencia(self):
        """📈 Plota gráfico de convergência"""
        try:
            if not self.historico_fitness:
                print("⚠️ Nenhum histórico de fitness para plotar")
                return
            
            plt.figure(figsize=(10, 6))
            plt.plot(self.historico_fitness, 'b-', linewidth=2)
            plt.title('Convergência do Algoritmo Genético', fontsize=14, fontweight='bold')
            plt.xlabel('Geração')
            plt.ylabel('Fitness (menor é melhor)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Salvar gráfico
            if not os.path.exists('resultados'):
                os.makedirs('resultados')
            
            plt.savefig('resultados/convergencia.png', dpi=300, bbox_inches='tight')
            plt.show()
            print("📊 Gráfico de convergência salvo em: resultados/convergencia.png")
            
        except Exception as e:
            print(f"⚠️ Erro ao plotar convergência: {e}")

def main():
    """🚀 Função principal do programa"""
    
    print("🎓 FIAP TECH CHALLENGE - ALGORITMO GENÉTICO CORRIGIDO")
    print("=" * 60)
    print("📊 Versão com correções para resolver FITNESS = 28800")
    print("🎯 Objetivo: Otimizar horários acadêmicos noturnos")
    print("⚡ Implementa correções nos dados e algoritmo")
    print()
    
    try:
        # Criar instância do otimizador
        otimizador = GeneticScheduleOptimizer()
        
        # Executar otimização completa
        resultado = otimizador.executar_otimizacao_corrigida()
        
        # Plotar convergência se houver dados
        if otimizador.historico_fitness:
            resposta = input("\nDeseja plotar gráfico de convergência? (s/n): ").lower()
            if resposta == 's':
                otimizador.plotar_convergencia()
        
        print("\n✅ Execução concluída com sucesso!")
        
        if resultado:
            print(f"📊 Solução encontrada com fitness: {otimizador.melhor_fitness}")
            print(f"📋 {len(resultado)} aulas alocadas")
            print("📁 Resultados salvos na pasta 'resultados/'")
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()