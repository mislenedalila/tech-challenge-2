import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from datetime import datetime
from genetic_scheduler_v2 import ScheduleGA_V2
from utils_v2 import salvar_agenda_excel, analisar_qualidade_agenda, gerar_relatorio_agenda_v2

def plotar_evolucao_fitness_v2(historico_fitness):
    """Plota a evolução do fitness V2 ao longo das gerações"""
    plt.figure(figsize=(15, 8))
    
    # Subplot 1: Evolução completa
    plt.subplot(2, 2, 1)
    plt.plot(historico_fitness, linewidth=2, color='darkgreen', alpha=0.8)
    plt.title('Evolução do Fitness V2 (Pontuação)', fontsize=14, fontweight='bold')
    plt.xlabel('Geração')
    plt.ylabel('Fitness (Pontos)')
    plt.grid(True, alpha=0.3)
    
    # Subplot 2: Últimas gerações para convergência
    plt.subplot(2, 2, 2)
    if len(historico_fitness) > 50:
        plt.plot(range(len(historico_fitness)-50, len(historico_fitness)), 
                historico_fitness[-50:], linewidth=2, color='red', alpha=0.8)
        plt.title('Últimas 50 Gerações (Convergência)', fontsize=14, fontweight='bold')
    else:
        plt.plot(historico_fitness, linewidth=2, color='red', alpha=0.8)
        plt.title('Todas as Gerações', fontsize=14, fontweight='bold')
    plt.xlabel('Geração')
    plt.ylabel('Fitness (Pontos)')
    plt.grid(True, alpha=0.3)
    
    # Subplot 3: Estatísticas do fitness
    plt.subplot(2, 2, 3)
    melhoria_total = historico_fitness[-1] - historico_fitness[0]
    plt.bar(['Inicial', 'Final', 'Melhoria'], 
           [historico_fitness[0], historico_fitness[-1], melhoria_total],
           color=['lightcoral', 'lightgreen', 'gold'], alpha=0.8)
    plt.title('Estatísticas do Fitness', fontsize=14, fontweight='bold')
    plt.ylabel('Pontos')
    
    # Adicionar valores nas barras
    for i, v in enumerate([historico_fitness[0], historico_fitness[-1], melhoria_total]):
        plt.text(i, v + max(historico_fitness) * 0.01, f'{v:.0f}', 
                ha='center', va='bottom', fontweight='bold')
    
    # Subplot 4: Distribuição de valores
    plt.subplot(2, 2, 4)
    plt.hist(historico_fitness, bins=20, alpha=0.7, color='skyblue', edgecolor='navy')
    plt.axvline(np.mean(historico_fitness), color='red', linestyle='--', 
               label=f'Média: {np.mean(historico_fitness):.0f}')
    plt.title('Distribuição dos Valores de Fitness', fontsize=14, fontweight='bold')
    plt.xlabel('Fitness')
    plt.ylabel('Frequência')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def plotar_distribuicao_agenda_v2(agenda, ga_v2):
    """Plota análises da distribuição da agenda V2"""
    plt.figure(figsize=(18, 12))
    
    # 1. Distribuição por dia
    plt.subplot(2, 3, 1)
    aulas_por_dia = []
    for d in range(ga_v2.num_dias):
        aulas = sum(1 for h in range(ga_v2.num_horarios) if agenda[d, h] is not None)
        aulas_por_dia.append(aulas)
    
    bars1 = plt.bar(ga_v2.dias, aulas_por_dia, color='lightblue', edgecolor='navy', alpha=0.8)
    plt.title('Distribuição por Dia da Semana', fontweight='bold', fontsize=12)
    plt.ylabel('Número de Aulas')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars1, aulas_por_dia):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.1,
                f'{valor}', ha='center', va='bottom', fontweight='bold')
    
    # 2. Distribuição por horário
    plt.subplot(2, 3, 2)
    aulas_por_horario = []
    for h in range(ga_v2.num_horarios):
        aulas = sum(1 for d in range(ga_v2.num_dias) if agenda[d, h] is not None)
        aulas_por_horario.append(aulas)
    
    bars2 = plt.bar(ga_v2.horarios, aulas_por_horario, color='lightgreen', edgecolor='darkgreen', alpha=0.8)
    plt.title('Distribuição por Horário', fontweight='bold', fontsize=12)
    plt.ylabel('Número de Aulas')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars2, aulas_por_horario):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.1,
                f'{valor}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Mapa de calor da agenda
    plt.subplot(2, 3, 3)
    grade_matriz = np.zeros((ga_v2.num_horarios, ga_v2.num_dias))
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            if agenda[d, h] is not None:
                grade_matriz[h, d] = 1
    
    sns.heatmap(grade_matriz, 
                xticklabels=ga_v2.dias, 
                yticklabels=ga_v2.horarios,
                annot=True, 
                fmt='g',
                cmap='RdYlGn',
                cbar_kws={'label': 'Ocupação (0=Livre, 1=Ocupado)'})
    plt.title('Mapa de Calor - Grade Horária', fontweight='bold', fontsize=12)
    
    # 4. Utilização de slots
    plt.subplot(2, 3, 4)
    slots_ocupados = sum(1 for d in range(ga_v2.num_dias) for h in range(ga_v2.num_horarios) 
                        if agenda[d, h] is not None)
    slots_totais = ga_v2.num_dias * ga_v2.num_horarios
    slots_livres = slots_totais - slots_ocupados
    
    plt.pie([slots_ocupados, slots_livres], 
           labels=['Ocupados', 'Livres'], 
           colors=['lightcoral', 'lightgray'],
           autopct='%1.1f%%', 
           startangle=90)
    plt.title(f'Utilização de Slots\n({slots_ocupados}/{slots_totais})', fontweight='bold', fontsize=12)
    
    # 5. Aulas por disciplina
    plt.subplot(2, 3, 5)
    aulas_por_disciplina = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
    
    disciplinas_nomes = []
    aulas_counts = []
    cargas_esperadas = []
    
    for disc_codigo in aulas_por_disciplina.keys():
        disciplina = ga_v2.disciplinas[disc_codigo]
        disciplinas_nomes.append(disciplina.nome[:15] + '...' if len(disciplina.nome) > 15 else disciplina.nome)
        aulas_counts.append(aulas_por_disciplina[disc_codigo])
        cargas_esperadas.append(disciplina.carga_horaria)
    
    x = np.arange(len(disciplinas_nomes))
    width = 0.35
    
    plt.bar(x - width/2, cargas_esperadas, width, label='Carga Esperada', 
           color='lightsteelblue', alpha=0.8)
    plt.bar(x + width/2, aulas_counts, width, label='Aulas Alocadas', 
           color='orange', alpha=0.8)
    
    plt.title('Carga Esperada vs Alocada', fontweight='bold', fontsize=12)
    plt.xlabel('Disciplinas')
    plt.ylabel('Horas')
    plt.xticks(x, disciplinas_nomes, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 6. Concentração de professores
    plt.subplot(2, 3, 6)
    dias_por_professor = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                prof = aula.professor
                if prof not in dias_por_professor:
                    dias_por_professor[prof] = set()
                dias_por_professor[prof].add(d)
    
    professores_nomes = []
    dias_trabalhados = []
    
    for prof_codigo, dias_set in dias_por_professor.items():
        professor = ga_v2.professores[prof_codigo]
        professores_nomes.append(professor.nome)
        dias_trabalhados.append(len(dias_set))
    
    colors = ['green' if d <= 3 else 'orange' if d <= 4 else 'red' for d in dias_trabalhados]
    bars = plt.bar(professores_nomes, dias_trabalhados, color=colors, alpha=0.8)
    
    plt.title('Concentração dos Professores\n(Dias Trabalhados)', fontweight='bold', fontsize=12)
    plt.ylabel('Número de Dias')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, dias_trabalhados):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.05,
                f'{valor}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def plotar_metricas_qualidade_v2(metricas):
    """Plota métricas de qualidade da agenda V2"""
    plt.figure(figsize=(15, 10))
    
    # 1. Radar chart das métricas principais
    plt.subplot(2, 2, 1)
    
    categorias = ['Completude\nDisciplinas', 'Respeito\nDisponibilidade', 
                 'Equilíbrio\nDistribuição', 'Utilização\nSlots', 'Concentração\nProfessores']
    valores = [metricas['completude_disciplinas'], metricas['respeito_disponibilidade'],
              metricas['equilibrio_distribuicao'], metricas['utilizacao_slots'], 
              metricas['concentracao_professores']]
    
    # Fechar o polígono
    valores += valores[:1]
    categorias += categorias[:1]
    
    angles = np.linspace(0, 2 * np.pi, len(categorias), endpoint=True)
    
    ax = plt.subplot(2, 2, 1, projection='polar')
    ax.plot(angles, valores, 'o-', linewidth=2, color='blue', alpha=0.8)
    ax.fill(angles, valores, alpha=0.25, color='blue')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias[:-1])
    ax.set_ylim(0, 1)
    ax.set_title('Métricas de Qualidade\n(Radar Chart)', fontweight='bold', pad=20)
    
    # Adicionar grid customizado
    ax.grid(True)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
    
    # 2. Barras das métricas
    plt.subplot(2, 2, 2)
    metricas_nomes = ['Completude\nDisciplinas', 'Respeito\nDisponibilidade', 
                     'Equilíbrio\nDistribuição', 'Utilização\nSlots', 'Concentração\nProfessores']
    metricas_valores = [metricas['completude_disciplinas'], metricas['respeito_disponibilidade'],
                       metricas['equilibrio_distribuicao'], metricas['utilizacao_slots'], 
                       metricas['concentracao_professores']]
    
    colors = ['red' if v < 0.5 else 'orange' if v < 0.8 else 'green' for v in metricas_valores]
    bars = plt.bar(range(len(metricas_nomes)), metricas_valores, color=colors, alpha=0.8)
    
    plt.title('Métricas de Qualidade (Barras)', fontweight='bold', fontsize=12)
    plt.ylabel('Score (0-1)')
    plt.xticks(range(len(metricas_nomes)), metricas_nomes, rotation=45, ha='right')
    plt.ylim(0, 1.1)
    plt.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, metricas_valores):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.02,
                f'{valor:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Score geral
    plt.subplot(2, 2, 3)
    score_geral = metricas['score_geral']
    
    # Criar gauge chart
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta)
    
    # Fundo do gauge
    plt.polar(theta, r, color='lightgray', linewidth=20, alpha=0.3)
    
    # Score atual
    score_theta = np.linspace(0, score_geral * np.pi, int(score_geral * 100))
    score_r = np.ones_like(score_theta)
    
    if score_geral < 0.5:
        color = 'red'
    elif score_geral < 0.8:
        color = 'orange'
    else:
        color = 'green'
    
    plt.polar(score_theta, score_r, color=color, linewidth=20, alpha=0.8)
    
    plt.ylim(0, 1)
    plt.title(f'Score Geral de Qualidade\n{score_geral:.1%}', fontweight='bold', fontsize=14)
    plt.xticks([])
    plt.yticks([])
    
    # 4. Comparação com benchmarks
    plt.subplot(2, 2, 4)
    benchmarks = {
        'Solução Manual': 0.6,
        'Algoritmo Simples': 0.7,
        'AG V2 (Nossa Solução)': score_geral,
        'Solução Ideal': 1.0
    }
    
    nomes = list(benchmarks.keys())
    valores_bench = list(benchmarks.values())
    colors_bench = ['lightcoral', 'orange', 'green', 'gold']
    
    bars = plt.bar(nomes, valores_bench, color=colors_bench, alpha=0.8)
    plt.title('Comparação com Benchmarks', fontweight='bold', fontsize=12)
    plt.ylabel('Score de Qualidade')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1.1)
    plt.grid(True, alpha=0.3)
    
    # Destacar nossa solução
    bars[2].set_edgecolor('black')
    bars[2].set_linewidth(3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, valores_bench):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.02,
                f'{valor:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def plotar_analise_disciplinas_v2(agenda, ga_v2):
    """Plota análise detalhada das disciplinas"""
    plt.figure(figsize=(16, 10))
    
    # Coletar dados das disciplinas
    aulas_por_disciplina = {}
    distribuicao_dias_disciplina = {}
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
                
                if disc not in distribuicao_dias_disciplina:
                    distribuicao_dias_disciplina[disc] = set()
                distribuicao_dias_disciplina[disc].add(d)
    
    # 1. Status de completude das disciplinas
    plt.subplot(2, 3, 1)
    disciplinas_nomes = []
    status_completude = []
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        nome_curto = disciplina.nome[:20] + '...' if len(disciplina.nome) > 20 else disciplina.nome
        disciplinas_nomes.append(nome_curto)
        
        if aulas_alocadas >= disciplina.carga_horaria:
            status_completude.append(1)  # Completa
        else:
            status_completude.append(aulas_alocadas / disciplina.carga_horaria)  # Parcial
    
    colors = ['green' if s == 1 else 'orange' if s >= 0.8 else 'red' for s in status_completude]
    bars = plt.barh(disciplinas_nomes, status_completude, color=colors, alpha=0.8)
    
    plt.title('Status de Completude das Disciplinas', fontweight='bold')
    plt.xlabel('Completude (0=Incompleta, 1=Completa)')
    plt.xlim(0, 1.1)
    plt.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, status_completude):
        plt.text(valor + 0.02, bar.get_y() + bar.get_height()/2.,
                f'{valor:.2f}', ha='left', va='center', fontweight='bold')
    
    # 2. Distribuição temporal das disciplinas
    plt.subplot(2, 3, 2)
    dias_utilizados_por_disc = []
    for disc_codigo in ga_v2.disciplinas.keys():
        dias_set = distribuicao_dias_disciplina.get(disc_codigo, set())
        dias_utilizados_por_disc.append(len(dias_set))
    
    plt.hist(dias_utilizados_por_disc, bins=range(0, 7), alpha=0.7, color='skyblue', edgecolor='navy')
    plt.title('Distribuição: Dias por Disciplina', fontweight='bold')
    plt.xlabel('Número de Dias Utilizados')
    plt.ylabel('Número de Disciplinas')
    plt.xticks(range(0, 6))
    plt.grid(True, alpha=0.3)
    
    # 3. Eficiência da alocação
    plt.subplot(2, 3, 3)
    eficiencia_disciplinas = []
    nomes_disc_efic = []
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        eficiencia = min(aulas_alocadas / disciplina.carga_horaria, 1.0)
        eficiencia_disciplinas.append(eficiencia)
        nomes_disc_efic.append(disciplina.nome[:15])
    
    plt.scatter(range(len(eficiencia_disciplinas)), eficiencia_disciplinas, 
               s=100, alpha=0.7, c=eficiencia_disciplinas, cmap='RdYlGn')
    plt.title('Eficiência da Alocação por Disciplina', fontweight='bold')
    plt.xlabel('Disciplina (Índice)')
    plt.ylabel('Eficiência (0-1)')
    plt.xticks(range(len(nomes_disc_efic)), nomes_disc_efic, rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.colorbar(label='Eficiência')
    
    # 4. Matriz disciplina x dia
    plt.subplot(2, 3, 4)
    matriz_disc_dia = np.zeros((len(ga_v2.disciplinas), ga_v2.num_dias))
    
    disc_indices = {disc: i for i, disc in enumerate(ga_v2.disciplinas.keys())}
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc_idx = disc_indices[aula.disciplina]
                matriz_disc_dia[disc_idx, d] += 1
    
    sns.heatmap(matriz_disc_dia, 
                xticklabels=ga_v2.dias,
                yticklabels=[ga_v2.disciplinas[disc].nome[:15] for disc in ga_v2.disciplinas.keys()],
                annot=True, 
                fmt='g',
                cmap='Blues',
                cbar_kws={'label': 'Aulas por Dia'})
    plt.title('Distribuição: Disciplinas x Dias', fontweight='bold')
    
    # 5. Análise de carga horária
    plt.subplot(2, 3, 5)
    cargas_esperadas = []
    cargas_alocadas = []
    nomes_disciplinas = []
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        cargas_esperadas.append(disciplina.carga_horaria)
        cargas_alocadas.append(aulas_por_disciplina.get(disc_codigo, 0))
        nomes_disciplinas.append(disciplina.nome[:12])
    
    x = np.arange(len(nomes_disciplinas))
    width = 0.35
    
    plt.bar(x - width/2, cargas_esperadas, width, label='Esperada', 
           color='lightcoral', alpha=0.8)
    plt.bar(x + width/2, cargas_alocadas, width, label='Alocada', 
           color='lightgreen', alpha=0.8)
    
    plt.title('Carga Horária: Esperada vs Alocada', fontweight='bold')
    plt.xlabel('Disciplinas')
    plt.ylabel('Horas')
    plt.xticks(x, nomes_disciplinas, rotation=45, ha='right')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 6. Score de qualidade por disciplina
    plt.subplot(2, 3, 6)
    scores_disciplinas = []
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        dias_utilizados = len(distribuicao_dias_disciplina.get(disc_codigo, set()))
        
        # Score baseado em completude e distribuição
        completude = min(aulas_alocadas / disciplina.carga_horaria, 1.0)
        distribuicao_ideal = min(dias_utilizados / disciplina.carga_horaria, 1.0)
        score = (completude * 0.7 + distribuicao_ideal * 0.3)
        scores_disciplinas.append(score)
    
    colors_score = ['red' if s < 0.6 else 'orange' if s < 0.8 else 'green' for s in scores_disciplinas]
    bars = plt.bar(range(len(scores_disciplinas)), scores_disciplinas, 
                  color=colors_score, alpha=0.8)
    
    plt.title('Score de Qualidade por Disciplina', fontweight='bold')
    plt.xlabel('Disciplinas')
    plt.ylabel('Score (0-1)')
    plt.xticks(range(len(nomes_disciplinas)), nomes_disciplinas, rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    
    # Adicionar valores nas barras
    for bar, valor in zip(bars, scores_disciplinas):
        plt.text(bar.get_x() + bar.get_width()/2., valor + 0.02,
                f'{valor:.2f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
    
    plt.tight_layout()
    plt.show()

def executar_analise_completa_v2():
    """Executa análise completa V2 com todas as visualizações"""
    print("\n" + "="*80)
    print("🔬 ANÁLISE COMPLETA V2 - PONTUAÇÃO COM AGENDA")
    print("="*80)
    print("Esta análise pode demorar alguns minutos...")
    
    try:
        # Executar algoritmo genético V2
        print("\n🧬 Executando Algoritmo Genético V2...")
        ga_v2 = ScheduleGA_V2()
        
        # Configurar parâmetros otimizados
        ga_v2.populacao_size = 50
        ga_v2.geracoes = 200
        ga_v2.taxa_mutacao = 0.15
        ga_v2.taxa_crossover = 0.8
        
        agenda, fitness, historico = ga_v2.executar()
        
        # Análise de qualidade
        print("\n📊 Analisando qualidade da solução...")
        metricas = analisar_qualidade_agenda(agenda, ga_v2)
        
        # Gerar relatório textual
        print("\n📋 Gerando relatório detalhado...")
        gerar_relatorio_agenda_v2(agenda, fitness, historico, ga_v2)
        
        # Visualizações
        print("\n📈 Gerando visualizações...")
        
        print("   📊 1/4 - Evolução do Fitness...")
        plotar_evolucao_fitness_v2(historico)
        
        print("   📅 2/4 - Distribuição da Agenda...")
        plotar_distribuicao_agenda_v2(agenda, ga_v2)
        
        print("   🎯 3/4 - Métricas de Qualidade...")
        plotar_metricas_qualidade_v2(metricas)
        
        print("   📚 4/4 - Análise das Disciplinas...")
        plotar_analise_disciplinas_v2(agenda, ga_v2)
        
        # Salvar resultados
        print("\n💾 Salvando resultados...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analise_completa_v2_{timestamp}.xlsx"
        caminho_salvo = salvar_agenda_excel(agenda, ga_v2, filename)
        
        print(f"\n✅ Análise completa V2 finalizada!")
        print(f"📄 Resultados salvos em: {caminho_salvo}")
        print(f"🎯 Fitness final: {fitness:.0f} pontos")
        print(f"📊 Score de qualidade: {metricas['score_geral']:.1%}")
        print(f"⏱️  Gerações executadas: {len(historico)}")
        
        # Exibir agenda final
        print("\n📅 AGENDA FINAL:")
        ga_v2.exibir_agenda(agenda)
        
        return agenda, fitness, historico, ga_v2, metricas
        
    except Exception as e:
        print(f"❌ Erro durante análise V2: {e}")
        return None

def comparar_evolucao_v1_v2():
    """Compara a evolução do fitness entre V1 e V2"""
    print("🔬 COMPARANDO EVOLUÇÃO V1 vs V2")
    print("="*50)
    
    try:
        # Executar V1
        print("Executando V1...")
        from genetic_scheduler import ScheduleGA
        ga_v1 = ScheduleGA()
        ga_v1.populacao_size = 30
        ga_v1.geracoes = 100
        _, fitness_v1, historico_v1 = ga_v1.executar()
        
        # Executar V2
        print("Executando V2...")
        ga_v2 = ScheduleGA_V2()
        ga_v2.populacao_size = 30
        ga_v2.geracoes = 100
        _, fitness_v2, historico_v2 = ga_v2.executar()
        
        # Plotar comparação
        plt.figure(figsize=(15, 10))
        
        # 1. Evolução lado a lado
        plt.subplot(2, 2, 1)
        plt.plot(historico_v1, label='V1 - Penalização', linewidth=2, alpha=0.8, color='blue')
        # Normalizar V2 para comparação visual
        historico_v2_norm = np.array(historico_v2) / max(historico_v2) * max(historico_v1)
        plt.plot(historico_v2_norm, label='V2 - Pontuação (normalizado)', linewidth=2, alpha=0.8, color='red')
        plt.title('Comparação da Evolução do Fitness', fontweight='bold')
        plt.xlabel('Geração')
        plt.ylabel('Fitness')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 2. Convergência
        plt.subplot(2, 2, 2)
        melhoria_v1 = historico_v1[-1] - historico_v1[0]
        melhoria_v2 = historico_v2[-1] - historico_v2[0]
        
        plt.bar(['V1 - Penalização', 'V2 - Pontuação'], 
               [melhoria_v1, melhoria_v2],
               color=['blue', 'red'], alpha=0.7)
        plt.title('Melhoria Total do Fitness', fontweight='bold')
        plt.ylabel('Melhoria')
        
        # 3. Estabilidade (últimas 20 gerações)
        plt.subplot(2, 2, 3)
        estabilidade_v1 = np.std(historico_v1[-20:]) if len(historico_v1) >= 20 else np.std(historico_v1)
        estabilidade_v2 = np.std(historico_v2[-20:]) if len(historico_v2) >= 20 else np.std(historico_v2)
        
        plt.bar(['V1 - Penalização', 'V2 - Pontuação'], 
               [estabilidade_v1, estabilidade_v2],
               color=['blue', 'red'], alpha=0.7)
        plt.title('Estabilidade (Últimas Gerações)', fontweight='bold')
        plt.ylabel('Desvio Padrão')
        
        # 4. Eficiência temporal
        plt.subplot(2, 2, 4)
        eficiencia_v1 = melhoria_v1 / len(historico_v1)
        eficiencia_v2 = melhoria_v2 / len(historico_v2)
        
        plt.bar(['V1 - Penalização', 'V2 - Pontuação'], 
               [eficiencia_v1, eficiencia_v2],
               color=['blue', 'red'], alpha=0.7)
        plt.title('Eficiência de Convergência', fontweight='bold')
        plt.ylabel('Melhoria por Geração')
        
        plt.tight_layout()
        plt.show()
        
        print(f"\n📊 RESULTADOS DA COMPARAÇÃO:")
        print(f"V1 - Fitness final: {fitness_v1:.2f}")
        print(f"V2 - Fitness final: {fitness_v2:.0f}")
        print(f"V1 - Melhoria: {melhoria_v1:.2f}")
        print(f"V2 - Melhoria: {melhoria_v2:.0f}")
        print(f"V1 - Gerações: {len(historico_v1)}")
        print(f"V2 - Gerações: {len(historico_v2)}")
        
        return (historico_v1, fitness_v1), (historico_v2, fitness_v2)
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")
        return None

def criar_dashboard_v2(agenda, fitness, historico, ga_v2, metricas):
    """Cria um dashboard resumido da análise V2"""
    fig, axes = plt.subplots(3, 3, figsize=(20, 15))
    fig.suptitle('DASHBOARD V2 - ALGORITMO GENÉTICO COM PONTUAÇÃO', fontsize=20, fontweight='bold')
    
    # 1. Fitness ao longo do tempo
    axes[0,0].plot(historico, linewidth=2, color='darkgreen')
    axes[0,0].set_title('Evolução do Fitness')
    axes[0,0].set_xlabel('Geração')
    axes[0,0].set_ylabel('Pontos')
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Score geral (gauge)
    score = metricas['score_geral']
    theta = np.linspace(0, np.pi, 100)
    r = np.ones_like(theta)
    
    axes[0,1] = plt.subplot(3, 3, 2, projection='polar')
    axes[0,1].plot(theta, r, color='lightgray', linewidth=10, alpha=0.3)
    
    score_theta = np.linspace(0, score * np.pi, int(score * 100))
    score_r = np.ones_like(score_theta)
    color = 'green' if score > 0.8 else 'orange' if score > 0.6 else 'red'
    axes[0,1].plot(score_theta, score_r, color=color, linewidth=10)
    axes[0,1].set_ylim(0, 1)
    axes[0,1].set_title(f'Score Geral\n{score:.1%}', fontweight='bold')
    axes[0,1].set_xticks([])
    axes[0,1].set_yticks([])
    
    # 3. Distribuição por dia
    aulas_por_dia = [sum(1 for h in range(ga_v2.num_horarios) if agenda[d, h] is not None) 
                     for d in range(ga_v2.num_dias)]
    axes[0,2].bar(ga_v2.dias, aulas_por_dia, color='skyblue', alpha=0.8)
    axes[0,2].set_title('Aulas por Dia')
    axes[0,2].set_ylabel('Número de Aulas')
    axes[0,2].tick_params(axis='x', rotation=45)
    
    # 4. Mapa de calor da agenda
    grade_matriz = np.zeros((ga_v2.num_horarios, ga_v2.num_dias))
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            if agenda[d, h] is not None:
                grade_matriz[h, d] = 1
    
    im = axes[1,0].imshow(grade_matriz, cmap='RdYlGn', aspect='auto')
    axes[1,0].set_title('Grade Horária')
    axes[1,0].set_xticks(range(ga_v2.num_dias))
    axes[1,0].set_xticklabels(ga_v2.dias)
    axes[1,0].set_yticks(range(ga_v2.num_horarios))
    axes[1,0].set_yticklabels(ga_v2.horarios)
    
    # 5. Métricas de qualidade
    metricas_nomes = ['Completude', 'Disponibilidade', 'Equilíbrio', 'Utilização', 'Concentração']
    metricas_valores = [metricas['completude_disciplinas'], metricas['respeito_disponibilidade'],
                       metricas['equilibrio_distribuicao'], metricas['utilizacao_slots'], 
                       metricas['concentracao_professores']]
    
    colors = ['red' if v < 0.6 else 'orange' if v < 0.8 else 'green' for v in metricas_valores]
    axes[1,1].bar(range(len(metricas_nomes)), metricas_valores, color=colors, alpha=0.8)
    axes[1,1].set_title('Métricas de Qualidade')
    axes[1,1].set_xticks(range(len(metricas_nomes)))
    axes[1,1].set_xticklabels(metricas_nomes, rotation=45, ha='right')
    axes[1,1].set_ylabel('Score (0-1)')
    axes[1,1].set_ylim(0, 1)
    
    # 6. Status das disciplinas
    aulas_por_disciplina = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
    
    completas = sum(1 for disc_codigo, disciplina in ga_v2.disciplinas.items() 
                   if aulas_por_disciplina.get(disc_codigo, 0) >= disciplina.carga_horaria)
    incompletas = len(ga_v2.disciplinas) - completas
    
    axes[1,2].pie([completas, incompletas], labels=['Completas', 'Incompletas'], 
                 colors=['lightgreen', 'lightcoral'], autopct='%1.0f')
    axes[1,2].set_title('Status das Disciplinas')
    
    # 7. Utilização de slots
    slots_ocupados = sum(1 for d in range(ga_v2.num_dias) for h in range(ga_v2.num_horarios) 
                        if agenda[d, h] is not None)
    slots_totais = ga_v2.num_dias * ga_v2.num_horarios
    utilizacao_pct = (slots_ocupados / slots_totais) * 100
    
    axes[2,0].bar(['Ocupados', 'Livres'], [slots_ocupados, slots_totais - slots_ocupados],
                 color=['lightblue', 'lightgray'], alpha=0.8)
    axes[2,0].set_title(f'Utilização de Slots\n{utilizacao_pct:.1f}%')
    axes[2,0].set_ylabel('Número de Slots')
    
    # 8. Concentração dos professores
    dias_por_professor = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                prof = aula.professor
                if prof not in dias_por_professor:
                    dias_por_professor[prof] = set()
                dias_por_professor[prof].add(d)
    
    concentracao_counts = [0, 0, 0]  # Alta (1-2 dias), Média (3-4 dias), Baixa (5+ dias)
    for dias_set in dias_por_professor.values():
        dias_count = len(dias_set)
        if dias_count <= 2:
            concentracao_counts[0] += 1
        elif dias_count <= 4:
            concentracao_counts[1] += 1
        else:
            concentracao_counts[2] += 1
    
    axes[2,1].bar(['Alta\n(1-2 dias)', 'Média\n(3-4 dias)', 'Baixa\n(5+ dias)'], 
                 concentracao_counts, color=['green', 'orange', 'red'], alpha=0.8)
    axes[2,1].set_title('Concentração dos Professores')
    axes[2,1].set_ylabel('Número de Professores')
    
    # 9. Resumo estatístico
    axes[2,2].axis('off')
    stats_text = f"""
RESUMO ESTATÍSTICO

🎯 Fitness Final: {fitness:.0f} pontos
📊 Score Geral: {metricas['score_geral']:.1%}
🔄 Gerações: {len(historico)}
📈 Melhoria: {historico[-1] - historico[0]:.0f}

📚 Disciplinas:
   • Total: {len(ga_v2.disciplinas)}
   • Completas: {completas}
   • Taxa: {(completas/len(ga_v2.disciplinas)):.1%}

👨‍🏫 Professores: {len(ga_v2.professores)}
🏫 Salas: {len(ga_v2.salas)}
📅 Slots Utilizados: {slots_ocupados}/{slots_totais}

✅ Status: {'EXCELENTE' if metricas['score_geral'] > 0.8 else 'BOM' if metricas['score_geral'] > 0.6 else 'REGULAR'}
"""
    
    axes[2,2].text(0.1, 0.9, stats_text, transform=axes[2,2].transAxes, fontsize=11,
                   verticalalignment='top', fontfamily='monospace',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
    
    plt.tight_layout()
    plt.show()

# Função principal para execução
if __name__ == "__main__":
    print("🔬 SISTEMA DE ANÁLISE COMPLETA V2")
    print("="*50)
    print("Opções disponíveis:")
    print("1. Análise completa V2")
    print("2. Comparar evolução V1 vs V2")
    print("3. Apenas visualizações (com dados pré-carregados)")
    
    opcao = input("\nEscolha uma opção (1-3): ")
    
    if opcao == "1":
        resultado = executar_analise_completa_v2()
        if resultado:
            agenda, fitness, historico, ga_v2, metricas = resultado
            print("\n🎯 Gerando dashboard resumido...")
            criar_dashboard_v2(agenda, fitness, historico, ga_v2, metricas)
    elif opcao == "2":
        comparar_evolucao_v1_v2()
    elif opcao == "3":
        print("⚠️  Opção 3 requer dados pré-carregados (não implementada)")
    else:
        print("❌ Opção inválida!")