#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎓 FIAP Tech Challenge - Algoritmo Genético para Otimização de Horários
📊 Versão FINAL OTIMIZADA para cenário específico
🎯 Regras implementadas:
   - Aulas começam SEMPRE às 18:50
   - 2 aulas: seguidas no mesmo dia
   - 3 aulas: dividir em 2 dias (2+1)
   - 4 aulas: dividir em 2 dias (2+2)
   - Evitar janelas de horário
   - Sexta-feira mais leve

Desenvolvido para: Tech Challenge FIAP - Fase 2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import random
import time
from datetime import datetime
import os
import warnings
from collections import defaultdict
warnings.filterwarnings('ignore')

# Configuração visual
plt.style.use('default')
try:
    import platform
    system = platform.system().lower()
    if system == 'windows':
        plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans', 'sans-serif']
    elif system == 'darwin':
        plt.rcParams['font.family'] = ['Helvetica', 'Arial', 'DejaVu Sans', 'sans-serif']
    else:
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
except:
    plt.rcParams['font.family'] = 'sans-serif'

class AlgoritmoGeneticoHorarios:
    """🧬 Algoritmo Genético para Horários Acadêmicos"""
    
    def __init__(self):
        # Parâmetros
        self.tamanho_populacao = 40
        self.taxa_mutacao = 0.2
        self.taxa_crossover = 0.8
        self.taxa_elitismo = 0.15
        self.max_geracoes = 150
        
        # Horários e dias
        self.horarios = ['18:50', '19:40', '20:30', '21:20']
        self.dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        
        # Dados
        self.disciplinas = None
        self.professores = None
        self.salas = None
        self.turmas = None
        self.disponibilidade = None
        
        # Controle
        self.historico_fitness = []
        self.melhor_solucao = None
        self.melhor_fitness = float('inf')
        
        print("🎓 ALGORITMO GENÉTICO OTIMIZADO - TECH CHALLENGE FIAP")
        print("=" * 60)
    
    def converter_horario_decimal(self, horario_decimal):
        """🕐 Converte horário decimal para string"""
        try:
            if isinstance(horario_decimal, str):
                return horario_decimal
            
            horas = int(horario_decimal * 24)
            minutos = int((horario_decimal * 24 * 60) % 60)
            
            if horas >= 21:
                return "21:20"
            elif horas >= 20:
                return "20:30"
            elif horas >= 19:
                return "19:40"
            else:
                return "18:50"
        except:
            return "18:50"
    
    def carregar_dados(self):
        """📂 Carrega dados"""
        try:
            print("📂 Carregando dados...")
            
            if not os.path.exists('dados'):
                raise FileNotFoundError("Pasta 'dados' não encontrada!")
            
            self.disciplinas = pd.read_excel('dados/disciplinas.xlsx')
            self.professores = pd.read_excel('dados/professores.xlsx')
            self.salas = pd.read_excel('dados/salas.xlsx')
            self.turmas = pd.read_excel('dados/turmas.xlsx')
            
            # Carregar e processar disponibilidade
            disp_raw = pd.read_excel('dados/disponibilidadeProfessor.xlsx')
            disp_raw['HORARIO'] = disp_raw['HORARIO'].apply(self.converter_horario_decimal)
            self.disponibilidade = disp_raw[disp_raw['TURNO'].str.lower().str.contains('notur', na=False)]
            
            print("✅ Dados carregados!")
            print(f"   📚 {len(self.disciplinas)} disciplinas")
            print(f"   👨‍🏫 {len(self.professores)} professores")
            print(f"   🎓 {len(self.turmas)} turmas")
            print(f"   🏫 {len(self.salas)} salas")
            
            return self.processar_dados()
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def processar_dados(self):
        """🔧 Processa dados CORRIGIDO"""
        try:
            self.total_aulas = 0
            
            # CORREÇÃO: Cada disciplina é cursada por apenas 1 turma (SIN-2A-N)
            print(f"🔧 Processando dados para turma única...")
            
            turmas_unicas = self.turmas['CODTURMA'].unique()
            print(f"   Turma encontrada: {turmas_unicas[0]}")
            
            for _, disciplina in self.disciplinas.iterrows():
                num_aulas = disciplina['CARGAHORARIA']
                # CORREÇÃO: Cada disciplina tem apenas 1 turma cursando
                self.total_aulas += num_aulas
                
                regra = self.determinar_regra(num_aulas)
                print(f"   {disciplina['NOME']}: {num_aulas} aulas - {regra}")
            
            print(f"📊 Total aulas para a turma: {self.total_aulas}")
            
            # Verificar se cabe perfeitamente
            slots_total = len(self.dias) * len(self.horarios)  # 5 dias × 4 horários = 20 slots
            print(f"📊 Slots disponíveis: {slots_total}")
            
            if self.total_aulas <= slots_total:
                print(f"✅ Perfeito! {self.total_aulas} aulas cabem em {slots_total} slots")
            else:
                print(f"⚠️ Problema: {self.total_aulas} aulas para {slots_total} slots")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro processamento: {e}")
            return False
    
    def determinar_regra(self, num_aulas):
        """📋 Determina regra"""
        if num_aulas == 2:
            return "2 seguidas mesmo dia"
        elif num_aulas == 3:
            return "DIVIDIR 2+1"
        elif num_aulas == 4:
            return "DIVIDIR 2+2"
        else:
            return f"{num_aulas} aulas"
    
    def professor_esta_disponivel(self, codprof, dia, horario):
        """
        Verifica se o professor está disponível no dia e horário especificados.
        """
        if self.disponibilidade is None:
            return True  # Assume disponível caso não tenha dados

        try:
            disponiveis = self.disponibilidade[
                (self.disponibilidade["CODPROF"] == codprof) &
                (self.disponibilidade["DIADASEMANA"].str.lower() == dia.lower()) &
                (self.disponibilidade["HORARIO"].astype(str).str.startswith(horario))
            ]
            return not disponiveis.empty
        except Exception as e:
            print(f"[Erro na verificação de disponibilidade] {e}")
            return False
    
    def criar_gene(self, codigo_disc, nome_disc, codigo_turma, professor_id, sala_id, dia, horario, aula_num):
        """🧬 Cria gene"""
        return {
            'disciplina': codigo_disc,
            'nome_disciplina': nome_disc,
            'turma': codigo_turma,
            'professor': professor_id,
            'sala': sala_id,
            'dia': dia,
            'horario': horario,
            'aula_numero': aula_num
        }
    
    def encontrar_slot_seguido(self, ocupacao, quantidade):
        """🕒 Encontra slot seguido"""
        dias_priorizados = ['Segunda', 'Terça', 'Quarta', 'Quinta']
        if quantidade == 1:
            dias_priorizados.append('Sexta')
        
        for dia in dias_priorizados:
            horarios_ocupados = ocupacao.get(dia, [])
            horarios_necessarios = []
            
            for i in range(quantidade):
                if i < len(self.horarios):
                    horario = self.horarios[i]
                    if horario not in horarios_ocupados:
                        horarios_necessarios.append(horario)
                    else:
                        break
            
            if len(horarios_necessarios) == quantidade:
                return dia, horarios_necessarios
        
        return None, None
    
    def alocar_dividido(self, codigo_disc, nome_disc, codigo_turma, professor_id, sala_id, divisoes, ocupacao):
        """📅 Aloca dividido"""
        aulas = []
        aula_num = 1
        
        for quantidade in divisoes:
            dia, horarios = self.encontrar_slot_seguido(ocupacao, quantidade)
            if dia and horarios:
                for horario in horarios:
                    aulas.append(self.criar_gene(codigo_disc, nome_disc, codigo_turma,
                                               professor_id, sala_id, dia, horario, aula_num))
                    if dia not in ocupacao:
                        ocupacao[dia] = []
                    ocupacao[dia].append(horario)
                    aula_num += 1
        
        return aulas
    
    def alocar_aulas_por_regra(self, codigo_disc, nome_disc, num_aulas, codigo_turma, ocupacao):
        """🎯 Aloca por regra"""
        aulas = []
        
        # Professor
        professor_info = self.professores[self.professores['CODDISC'] == codigo_disc]
        if professor_info.empty:
            professor_id = self.professores.iloc[0]['CODPROF']
        else:
            professor_id = professor_info.iloc[0]['CODPROF']
        
        # Sala
        sala_id = self.salas.iloc[0]['CODSALA']
        
        if num_aulas == 2:
            # 2 seguidas
            dia, horarios = self.encontrar_slot_seguido(ocupacao, 2)
            if dia and horarios:
                for i, horario in enumerate(horarios):
                    aulas.append(self.criar_gene(codigo_disc, nome_disc, codigo_turma, 
                                               professor_id, sala_id, dia, horario, i+1))
                    if dia not in ocupacao:
                        ocupacao[dia] = []
                    ocupacao[dia].append(horario)
        
        elif num_aulas == 3:
            # 3 = 2+1
            aulas.extend(self.alocar_dividido(codigo_disc, nome_disc, codigo_turma,
                                            professor_id, sala_id, [2, 1], ocupacao))
        
        elif num_aulas == 4:
            # 4 = 2+2
            aulas.extend(self.alocar_dividido(codigo_disc, nome_disc, codigo_turma,
                                            professor_id, sala_id, [2, 2], ocupacao))
        else:
            # 1 aula
            dia, horarios = self.encontrar_slot_seguido(ocupacao, 1)
            if dia and horarios:
                aulas.append(self.criar_gene(codigo_disc, nome_disc, codigo_turma,
                                           professor_id, sala_id, dia, horarios[0], 1))
                if dia not in ocupacao:
                    ocupacao[dia] = []
                ocupacao[dia].append(horarios[0])
        
        return aulas
    
    def gerar_populacao_inicial(self):
        """
        Gera a população inicial respeitando carga horária por disciplina,
        criando alocações distribuídas e completas.
        """
        populacao = []

        for _ in range(self.tamanho_populacao):
            individuo = []

            for _, row in self.disciplinas.iterrows():
                cod_disciplina = row["CODDISC"]
                nome_disciplina = row["NOME"]
                cod_turma = row["CODTURMA"]
                carga = row["CARGAHORARIA"]

                # Encontrar professor da disciplina
                prof_row = self.professores[self.professores["CODDISC"] == cod_disciplina]
                if prof_row.empty:
                    continue
                professor = prof_row.iloc[0]["CODPROF"]

                # Definir padrão de distribuição da carga horária
                if carga == 2:
                    dias_para_usar = random.sample(self.dias, 1)
                    horarios_para_usar = self.horarios[:2]
                    distribuicao = [(dias_para_usar[0], h) for h in horarios_para_usar]
                elif carga == 3:
                    dias_para_usar = random.sample(self.dias, 2)
                    distribuicao = [(dias_para_usar[0], self.horarios[0]), 
                                    (dias_para_usar[0], self.horarios[1]),
                                    (dias_para_usar[1], self.horarios[0])]
                elif carga == 4:
                    dias_para_usar = random.sample(self.dias, 2)
                    distribuicao = [(dias_para_usar[0], self.horarios[0]),
                                    (dias_para_usar[0], self.horarios[1]),
                                    (dias_para_usar[1], self.horarios[0]),
                                    (dias_para_usar[1], self.horarios[1])]
                else:
                    dias_para_usar = random.sample(self.dias, carga)
                    distribuicao = [(dias_para_usar[i], self.horarios[i % len(self.horarios)]) for i in range(carga)]

                # Criar as aulas
                for dia, horario in distribuicao:
                    sala = self.salas.sample(1).iloc[0]["CODSALA"]

                    aula = {
                        "disciplina": cod_disciplina,
                        "turma": cod_turma,
                        "professor": professor,
                        "dia": dia,
                        "horario": horario,
                        "sala": sala
                    }
                    individuo.append(aula)

            populacao.append(individuo)

        return populacao
    
    def criar_individuo_otimizado(self):
        """🧬 Cria indivíduo CORRIGIDO com debug completo"""
        individuo = []
        ocupacao = {}
        
        # CORREÇÃO: Processar apenas a turma SIN-2A-N
        codigo_turma = 'SIN-2A-N'  # Turma única
        
        print(f"\n🧬 CRIANDO HORÁRIO PARA TURMA: {codigo_turma}")
        print("=" * 50)
        
        total_aulas_esperadas = sum(disc['CARGAHORARIA'] for _, disc in self.disciplinas.iterrows())
        print(f"📊 Total de aulas esperadas: {total_aulas_esperadas}")
        
        for _, disciplina in self.disciplinas.iterrows():
            codigo_disc = disciplina['CODDISC']
            nome_disc = disciplina['NOME']
            num_aulas = disciplina['CARGAHORARIA']
            
            print(f"\n📚 PROCESSANDO: {nome_disc}")
            print(f"   Aulas necessárias: {num_aulas}")
            
            aulas_antes = len(individuo)
            
            aulas_criadas = self.alocar_aulas_por_regra(
                codigo_disc, nome_disc, num_aulas, codigo_turma, ocupacao
            )
            
            individuo.extend(aulas_criadas)
            aulas_depois = len(individuo)
            aulas_adicionadas = aulas_depois - aulas_antes
            
            print(f"   ✅ Resultado: {aulas_adicionadas} aulas alocadas")
            if aulas_adicionadas != num_aulas:
                print(f"   ⚠️ PROBLEMA: Esperado {num_aulas}, obtido {aulas_adicionadas}")
        
        print(f"\n📊 RESUMO FINAL:")
        print(f"   Total esperado: {total_aulas_esperadas}")
        print(f"   Total obtido: {len(individuo)}")
        print(f"   Diferença: {total_aulas_esperadas - len(individuo)}")
        
        if len(individuo) == total_aulas_esperadas:
            print(f"   🎉 PERFEITO! Todas as aulas foram alocadas!")
        else:
            print(f"   ❌ PROBLEMA! {total_aulas_esperadas - len(individuo)} aulas perdidas")
        
        # Mostrar ocupação final
        print(f"\n📅 OCUPAÇÃO FINAL:")
        for dia in self.dias:
            aulas_dia = ocupacao.get(dia, [])
            print(f"   {dia}: {len(aulas_dia)} aulas - {sorted(aulas_dia)}")
        
        return individuo
    
    def fitness(self, individuo):
        """
        Avalia a qualidade de um indivíduo priorizando:
        1. Cobertura total das aulas por disciplina-turma
        2. Depois, conflitos (sala, professor, turma)
        """
        penalidade = 0
        horarios_ocupados = {}
        professor_ocupado = {}
        turma_ocupada = {}
        aulas_alocadas = {}

        for aula in individuo:
            turma = aula["turma"]
            professor = aula["professor"]
            dia = aula["dia"]
            horario = aula["horario"]
            sala = aula["sala"]
            disciplina = aula["disciplina"]

            chave_horario = (dia, horario, sala)
            chave_prof = (dia, horario, professor)
            chave_turma = (dia, horario, turma)
            chave_disc_turma = (disciplina, turma)

            aulas_alocadas[chave_disc_turma] = aulas_alocadas.get(chave_disc_turma, 0) + 1

            # Penalidade leve por conflitos (antes era 10)
            if chave_horario in horarios_ocupados:
                penalidade += 2
            else:
                horarios_ocupados[chave_horario] = True

            if chave_prof in professor_ocupado:
                penalidade += 2
            else:
                professor_ocupado[chave_prof] = True

            if chave_turma in turma_ocupada:
                penalidade += 2
            else:
                turma_ocupada[chave_turma] = True

            # Penalizar indisponibilidade
            if not self.professor_esta_disponivel(professor, dia, horario):
                penalidade += 5

            # Penalizar levemente sexta
            if dia == "Sexta":
                penalidade += 1

        # Penalidade forte por aulas faltantes
        for _, row in self.disciplinas.iterrows():
            chave = (row["CODDISC"], row["CODTURMA"])
            carga = row["CARGAHORARIA"]
            alocadas = aulas_alocadas.get(chave, 0)
            if alocadas < carga:
                faltam = carga - alocadas
                penalidade += faltam * 50  # MUITO mais pesado

        return penalidade
    
    def calcular_fitness(self, individuo):
        """📊 Calcula fitness CORRIGIDO para distribuição perfeita"""
        if not individuo:
            return 10000
        
        fitness = 0
        
        # Estruturas para análise
        ocupacao_slots = defaultdict(list)
        distribuicao_semanal = defaultdict(int)
        aulas_por_disciplina_dia = defaultdict(lambda: defaultdict(int))
        
        for aula in individuo:
            slot = (aula['dia'], aula['horario'])
            ocupacao_slots[slot].append(aula)
            distribuicao_semanal[aula['dia']] += 1
            aulas_por_disciplina_dia[aula['disciplina']][aula['dia']] += 1
        
        # 1. PENALIZAÇÃO CRÍTICA: Conflitos de horário
        for conflitos in ocupacao_slots.values():
            if len(conflitos) > 1:
                fitness += (len(conflitos) - 1) * 2000  # Peso altíssimo
        
        # 2. OBJETIVO PRINCIPAL: Distribuição perfeita
        # Segunda-Quinta: 4 aulas cada (18:50-21:20)
        for dia in ['Segunda', 'Terça', 'Quarta', 'Quinta']:
            aulas_dia = distribuicao_semanal[dia]
            if aulas_dia == 4:
                fitness -= 200  # BÔNUS GRANDE por dia completo
            else:
                fitness += abs(4 - aulas_dia) * 100  # Penalização por não ter 4
        
        # Sexta: Ideal 3 aulas (18:50-20:30)
        aulas_sexta = distribuicao_semanal['Sexta']
        if aulas_sexta == 3:
            fitness -= 150  # BÔNUS por sexta ideal
        elif aulas_sexta < 3:
            fitness += (3 - aulas_sexta) * 50  # Penalização leve por menos
        else:
            fitness += (aulas_sexta - 3) * 200  # Penalização pesada por mais
        
        # 3. BÔNUS: Aulas começando às 18:50 (máxima prioridade)
        for dia in self.dias:
            aulas_dia = [a for a in individuo if a['dia'] == dia]
            if aulas_dia:
                # Verificar se primeira aula é às 18:50
                primeira_aula = min(aulas_dia, key=lambda x: self.horarios.index(x['horario']))
                if primeira_aula['horario'] == '18:50':
                    fitness -= 100  # BÔNUS por começar cedo
                else:
                    fitness += 150  # PENALIZAÇÃO por não começar às 18:50
        
        # 4. PENALIZAÇÃO: Janelas de horário
        for dia in self.dias:
            aulas_dia = sorted([a for a in individuo if a['dia'] == dia], 
                             key=lambda x: self.horarios.index(x['horario']))
            
            if len(aulas_dia) > 1:
                horarios_indices = [self.horarios.index(a['horario']) for a in aulas_dia]
                for i in range(len(horarios_indices) - 1):
                    if horarios_indices[i+1] - horarios_indices[i] > 1:
                        fitness += 300  # PENALIZAÇÃO PESADA por janela
        
        # 5. VERIFICAÇÃO: Regras específicas das disciplinas
        for _, disciplina in self.disciplinas.iterrows():
            codigo = disciplina['CODDISC']
            num_aulas = disciplina['CARGAHORARIA']
            dias_disciplina = aulas_por_disciplina_dia[codigo]
            
            if num_aulas == 2:
                # Deve estar em 1 dia com 2 aulas seguidas
                if len(dias_disciplina) == 1 and list(dias_disciplina.values())[0] == 2:
                    fitness -= 50  # BÔNUS por regra correta
                else:
                    fitness += 400  # PENALIZAÇÃO por regra incorreta
            
            elif num_aulas == 3:
                # Deve estar em 2 dias (2+1)
                if len(dias_disciplina) == 2 and sorted(dias_disciplina.values()) == [1, 2]:
                    fitness -= 50  # BÔNUS por regra correta
                else:
                    fitness += 400  # PENALIZAÇÃO por regra incorreta
            
            elif num_aulas == 4:
                # Deve estar em 2 dias (2+2)
                if len(dias_disciplina) == 2 and sorted(dias_disciplina.values()) == [2, 2]:
                    fitness -= 50  # BÔNUS por regra correta
                else:
                    fitness += 400  # PENALIZAÇÃO por regra incorreta
        
        # 6. BÔNUS: Total de aulas alocadas
        fitness -= len(individuo) * 5
        
        return max(0, fitness)
    
    def relatorio_aulas_faltantes(self, individuo):
        """📋 Relatório de aulas faltantes"""
        aulas_alocadas = {}

        for aula in individuo:
            chave = (aula["disciplina"], aula["turma"])
            aulas_alocadas[chave] = aulas_alocadas.get(chave, 0) + 1

        print("\n🔍 RELATÓRIO DE AULAS FALTANTES:")
        for _, row in self.disciplinas.iterrows():
            chave = (row["CODDISC"], 'SIN-2A-N')  # CORREÇÃO: usar turma única
            carga = row["CARGAHORARIA"]
            alocadas = aulas_alocadas.get(chave, 0)
            if alocadas < carga:
                print(f"- {row['NOME']} (Turma SIN-2A-N): {alocadas}/{carga} aulas alocadas")
    
    def criar_populacao_inicial(self):
        """🧬 Cria população"""
        populacao = []
        
        print(f"🧬 Criando população de {self.tamanho_populacao} indivíduos...")
        
        for i in range(self.tamanho_populacao):
            individuo = self.criar_individuo_otimizado()
            populacao.append(individuo)
        
        return populacao
    
    def selecao_torneio(self, populacao, k=3):
        """🏆 Seleção"""
        fitness_populacao = [self.calcular_fitness(ind) for ind in populacao]
        
        selecionados = []
        for _ in range(len(populacao)):
            indices_torneio = random.sample(range(len(populacao)), min(k, len(populacao)))
            melhor_idx = min(indices_torneio, key=lambda i: fitness_populacao[i])
            selecionados.append(populacao[melhor_idx].copy())
        
        return selecionados
    
    def crossover(self, pai1, pai2):
        """🧬 Crossover"""
        if random.random() > self.taxa_crossover or not pai1 or not pai2:
            return pai1.copy(), pai2.copy()
        
        ponto_corte = len(pai1) // 2
        
        filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
        filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
        
        return filho1, filho2
    
    def mutacao(self, individuo):
        """🔄 Mutação"""
        if random.random() > self.taxa_mutacao or not individuo:
            return individuo
        
        # Mutação simples: trocar dia de uma aula
        if len(individuo) > 0:
            idx = random.randint(0, len(individuo) - 1)
            individuo[idx]['dia'] = random.choice(self.dias)
        
        return individuo
    
    def evoluir(self):
        """🚀 Evolução"""
        populacao = self.criar_populacao_inicial()
        
        print(f"🚀 Iniciando evolução...")
        
        for geracao in range(self.max_geracoes):
            fitness_populacao = [self.calcular_fitness(ind) for ind in populacao]
            
            melhor_fitness_geracao = min(fitness_populacao)
            idx_melhor = fitness_populacao.index(melhor_fitness_geracao)
            melhor_individuo = populacao[idx_melhor].copy()
            
            self.historico_fitness.append(melhor_fitness_geracao)
            
            if melhor_fitness_geracao < self.melhor_fitness:
                self.melhor_fitness = melhor_fitness_geracao
                self.melhor_solucao = melhor_individuo.copy()
            
            if geracao % 25 == 0:
                print(f"Geração {geracao}: Fitness = {melhor_fitness_geracao}")
            
            if melhor_fitness_geracao == 0:
                print(f"🎯 Solução perfeita na geração {geracao}!")
                break
            
            # Nova população
            nova_populacao = []
            
            # Elitismo
            num_elite = int(len(populacao) * self.taxa_elitismo)
            indices_ordenados = sorted(range(len(populacao)), key=lambda i: fitness_populacao[i])
            
            for i in range(num_elite):
                nova_populacao.append(populacao[indices_ordenados[i]].copy())
            
            # Completar população
            while len(nova_populacao) < len(populacao):
                pais = self.selecao_torneio(populacao)
                pai1, pai2 = random.sample(pais, 2)
                
                filho1, filho2 = self.crossover(pai1, pai2)
                filho1 = self.mutacao(filho1)
                filho2 = self.mutacao(filho2)
                
                if len(nova_populacao) < len(populacao):
                    nova_populacao.append(filho1)
                if len(nova_populacao) < len(populacao):
                    nova_populacao.append(filho2)
            
            populacao = nova_populacao
        
        return self.melhor_solucao
    
    def analisar_solucao(self, solucao):
        """📊 Analisa solução"""
        print(f"\n📊 ANÁLISE DA SOLUÇÃO:")
        
        distribuicao = defaultdict(int)
        for aula in solucao:
            distribuicao[aula['dia']] += 1
        
        print(f"📅 Distribuição semanal:")
        for dia in self.dias:
            aulas = distribuicao[dia]
            print(f"   {dia}: {aulas} aulas")
    
    def salvar_resultados(self, solucao):
        """💾 Salva resultados"""
        try:
            if not os.path.exists('resultados'):
                os.makedirs('resultados')
            
            df_solucao = pd.DataFrame(solucao)
            df_solucao.to_csv('resultados/horario_otimizado.csv', index=False)
            
            relatorio = {
                'timestamp': datetime.now().isoformat(),
                'fitness_final': self.melhor_fitness,
                'total_aulas': len(solucao),
                'historico_fitness': self.historico_fitness
            }
            
            with open('resultados/relatorio_otimizacao.json', 'w') as f:
                json.dump(relatorio, f, indent=2)
            
            print(f"💾 Resultados salvos!")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar: {e}")
    
    def plotar_evolucao(self):
        """📈 Plota gráfico da evolução"""
        if not self.historico_fitness:
            print("❌ Nenhum histórico para plotar")
            return
        
        plt.figure(figsize=(12, 6))
        
        # Gráfico da evolução do fitness
        plt.subplot(1, 2, 1)
        plt.plot(self.historico_fitness, 'b-', linewidth=2, label='Melhor Fitness')
        plt.xlabel('Geração')
        plt.ylabel('Fitness')
        plt.title('Evolução do Fitness ao Longo das Gerações')
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        # Gráfico da melhoria por geração
        plt.subplot(1, 2, 2)
        melhorias = []
        for i in range(1, len(self.historico_fitness)):
            if self.historico_fitness[i] < self.historico_fitness[i-1]:
                melhorias.append(1)
            else:
                melhorias.append(0)
        
        if melhorias:
            plt.bar(range(1, len(melhorias)+1), melhorias, alpha=0.7, color='green')
        plt.xlabel('Geração')
        plt.ylabel('Houve Melhoria (1=Sim, 0=Não)')
        plt.title('Melhorias por Geração')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Salvar gráfico
        try:
            plt.savefig('resultados/evolucao_fitness.png', dpi=300, bbox_inches='tight')
            print("📈 Gráfico salvo em 'resultados/evolucao_fitness.png'")
        except Exception as e:
            print(f"⚠️ Erro ao salvar gráfico: {e}")
        
        plt.show()
    
    def gerar_grade_visual(self, solucao):
        """📅 Gera visualização da grade de horários"""
        if not solucao:
            print("❌ Nenhuma solução para visualizar")
            return
        
        print(f"\n📅 GRADE DE HORÁRIOS - TURMA SIN-2A-N:")
        print("=" * 80)
        
        # Cabeçalho
        header = f"{'Horário':<8}"
        for dia in self.dias:
            header += f" | {dia:<12}"
        print(header)
        print("-" * 80)
        
        # Organizar aulas por slot
        grade = {}
        for aula in solucao:
            slot = (aula['dia'], aula['horario'])
            if slot not in grade:
                grade[slot] = []
            grade[slot].append(aula)
        
        # Imprimir grade
        for horario in self.horarios:
            linha = f"{horario:<8}"
            
            for dia in self.dias:
                slot = (dia, horario)
                if slot in grade:
                    # Pegar primeira aula do slot (em caso de conflito)
                    aula = grade[slot][0]
                    disciplina_nome = aula['nome_disciplina'][:10]  # Truncar nome
                    conteudo = f"{disciplina_nome}"
                    
                    # Indicar conflito se houver
                    if len(grade[slot]) > 1:
                        conteudo += "*"
                    
                    linha += f" | {conteudo:<12}"
                else:
                    linha += f" | {'':<12}"
            
            print(linha)
        
        print("-" * 80)
        print("* = Conflito de horário")
        
        # Salvar grade em arquivo texto
        try:
            with open('resultados/grade_visual.txt', 'w', encoding='utf-8') as f:
                f.write("GRADE DE HORÁRIOS - TURMA SIN-2A-N\n")
                f.write("=" * 80 + "\n")
                f.write(f"Gerada em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
                f.write(f"Fitness: {self.melhor_fitness}\n\n")
                
                f.write(header + "\n")
                f.write("-" * 80 + "\n")
                
                for horario in self.horarios:
                    linha = f"{horario:<8}"
                    for dia in self.dias:
                        slot = (dia, horario)
                        if slot in grade:
                            aula = grade[slot][0]
                            disciplina_nome = aula['nome_disciplina'][:10]
                            conteudo = f"{disciplina_nome}"
                            if len(grade[slot]) > 1:
                                conteudo += "*"
                            linha += f" | {conteudo:<12}"
                        else:
                            linha += f" | {'':<12}"
                    f.write(linha + "\n")
                
                f.write("-" * 80 + "\n")
                f.write("* = Conflito de horário\n")
            
            print("📄 Grade visual salva em 'resultados/grade_visual.txt'")
            
        except Exception as e:
            print(f"⚠️ Erro ao salvar grade visual: {e}")
    
    def executar(self):
        """🚀 Execução principal"""
        print("🎓 EXECUTANDO ALGORITMO GENÉTICO")
        print("=" * 50)
        
        inicio = time.time()
        
        if not self.carregar_dados():
            return None
        
        solucao = self.evoluir()
        
        tempo_execucao = time.time() - inicio
        
        print(f"\n🏆 RESULTADOS:")
        print(f"⏱️ Tempo: {tempo_execucao:.2f}s")
        print(f"🎯 Fitness: {self.melhor_fitness}")
        print(f"🧬 Gerações: {len(self.historico_fitness)}")
        
        if solucao:
            self.analisar_solucao(solucao)
            self.gerar_grade_visual(solucao)
            self.relatorio_aulas_faltantes(solucao)
            self.salvar_resultados(solucao)
            
            # Tentar plotar evolução
            try:
                self.plotar_evolucao()
            except Exception as e:
                print(f"⚠️ Erro ao plotar: {e}")
            
            print(f"\n🎉 EXECUÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"📁 Verifique a pasta 'resultados/' para todos os arquivos")
        
        return solucao

def main():
    """🚀 Função principal"""
    print("🎓 TECH CHALLENGE FIAP - ALGORITMO GENÉTICO")
    print("📊 Otimização de Grade de Horários Acadêmicos")
    print("=" * 60)
    
    algoritmo = AlgoritmoGeneticoHorarios()
    solucao = algoritmo.executar()
    
    if solucao:
        print(f"\n✅ SUCESSO!")
        print(f"📈 Grade de horários otimizada gerada com {len(solucao)} aulas")
        print(f"🎯 Fitness final: {algoritmo.melhor_fitness}")
        print(f"📁 Resultados salvos em 'resultados/'")
        return solucao
    else:
        print(f"\n❌ FALHA na execução")
        print(f"💡 Verifique:")
        print(f"   - Se todos os arquivos estão na pasta 'dados/'")
        print(f"   - Se os dados estão no formato correto")
        print(f"   - Se há disponibilidade suficiente dos professores")
        return None

if __name__ == "__main__":
    # Executar programa principal
    solucao_final = main()
    
    if solucao_final:
        print(f"\n🔍 ANÁLISE FINAL:")
        print(f"   Total de aulas alocadas: {len(solucao_final)}")
        
        # Mostrar estatísticas básicas
        disciplinas_count = {}
        for aula in solucao_final:
            disc = aula['nome_disciplina']
            disciplinas_count[disc] = disciplinas_count.get(disc, 0) + 1
        
        print(f"   Disciplinas processadas:")
        for disc, count in disciplinas_count.items():
            print(f"     - {disc}: {count} aulas")
        
        print(f"\n🎓 Algoritmo Genético executado com sucesso!")
        print(f"📚 Para mais detalhes, consulte os arquivos na pasta 'resultados/'")
    else:
        print(f"\n🔧 Para resolver problemas:")
        print(f"   1. Verifique se a pasta 'dados/' existe")
        print(f"   2. Confirme que todos os 5 arquivos .xlsx estão presentes")
        print(f"   3. Valide se os dados seguem o formato esperado")
        print(f"   4. Execute novamente o programa")