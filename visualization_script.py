import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os
from genetic_scheduler import ScheduleGA

def plotar_evolucao_fitness(historico_fitness):
    """Plota a evolução do fitness ao longo das gerações"""
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(historico_fitness, linewidth=2, color='blue')
    plt.title('Evolução do Fitness', fontsize=14, fontweight='bold')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.grid(True, alpha=0.3)
    
    # Plotar últimas 100 gerações para ver convergência
    plt.subplot(1, 2, 2)
    if len(historico_fitness) > 100:
        plt.plot(historico_fitness[-100:], linewidth=2, color='red')
        plt.title('Últimas 100 Gerações', fontsize=14, fontweight='bold')
    else:
        plt.plot(historico_fitness, linewidth=2, color='red')
        plt.title('Todas as Gerações', fontsize=14, fontweight='bold')
    plt.xlabel('Geração')
    plt.ylabel('Fitness')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def analisar_distribuicao_horarios(cromossomo, ga):
    """Analisa a distribuição das aulas por dia e horário"""
    # Contar aulas por dia
    aulas_por_dia = [0] * 5
    aulas_por_horario = [0] * 4
    
    for gene in cromossomo:
        aulas_por_dia[gene['dia']] += 1
        aulas_por_horario[gene['horario']] += 1
    
    plt.figure(figsize=(15, 5))
    
    # Distribuição por dia
    plt.subplot(1, 3, 1)
    bars1 = plt.bar(ga.dias, aulas_por_dia, color='skyblue', edgecolor='navy')
    plt.title('Distribuição por Dia da Semana', fontweight='bold')
    plt.ylabel('Número de Aulas')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # Distribuição por horário
    plt.subplot(1, 3, 2)
    bars2 = plt.bar(ga.horarios, aulas_por_horario, color='lightgreen', edgecolor='darkgreen')
    plt.title('Distribuição por Horário', fontweight='bold')
    plt.ylabel('Número de Aulas')
    plt.xticks(rotation=45)
    
    # Adicionar valores nas barras
    for bar in bars2:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom')
    
    # Mapa de calor da grade horária
    plt.subplot(1, 3, 3)
    grade_matriz = np.zeros((4, 5))  # 4 horários x 5 dias
    
    for gene in cromossomo:
        grade_matriz[gene['horario'], gene['dia']] += 1
    
    sns.heatmap(grade_matriz, 
                xticklabels=ga.dias, 
                yticklabels=ga.horarios,
                annot=True, 
                fmt='g',
                cmap='YlOrRd',
                cbar_kws={'label': 'Número de Aulas'})
    plt.title('Mapa de Calor - Grade Horária', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def analisar_carga_professores(cromossomo, ga):
    """Analisa a distribuição de carga horária entre professores"""
    carga_professores = {}
    
    for gene in cromossomo:
        prof = gene['professor']
        if prof not in carga_professores:
            carga_professores[prof] = 0
        carga_professores[prof] += 1
    
    # Criar DataFrame para visualização
    dados_prof = []
    for prof_codigo, carga in carga_professores.items():
        professor = ga.professores[prof_codigo]
        disciplina = ga.disciplinas[professor.disciplina]
        dados_prof.append({
            'Professor': professor.nome,
            'Disciplina': disciplina.nome[:20] + '...' if len(disciplina.nome) > 20 else disciplina.nome,
            'Carga_Alocada': carga,
            'Carga_Prevista': disciplina.carga_horaria
        })
    
    df_prof = pd.DataFrame(dados_prof)
    
    plt.figure(figsize=(12, 6))
    
    x = range(len(df_prof))
    width = 0.35
    
    plt.bar([i - width/2 for i in x], df_prof['Carga_Prevista'], 
            width, label='Carga Prevista', color='lightcoral', alpha=0.8)
    plt.bar([i + width/2 for i in x], df_prof['Carga_Alocada'], 
            width, label='Carga Alocada', color='lightblue', alpha=0.8)
    
    plt.xlabel('Professores')
    plt.ylabel('Horas Semanais')
    plt.title('Comparação: Carga Prevista vs Alocada', fontweight='bold')
    plt.xticks(x, df_prof['Professor'], rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adicionar informações das disciplinas
    for i, (prof, disc) in enumerate(zip(df_prof['Professor'], df_prof['Disciplina'])):
        plt.text(i, max(df_prof.loc[i, 'Carga_Prevista'], df_prof.loc[i, 'Carga_Alocada']) + 0.1,
                disc, rotation=90, ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.show()
    
    return df_prof

def verificar_conflitos(cromossomo, ga):
    """Verifica e reporta conflitos detalhados"""
    conflitos = {
        'professor': [],
        'sala': [],
        'disponibilidade': []
    }
    
    # Verificar conflitos de professor
    professor_horarios = {}
    for i, gene in enumerate(cromossomo):
        key = (gene['professor'], gene['dia'], gene['horario'])
        if key in professor_horarios:
            conflitos['professor'].append({
                'professor': ga.professores[gene['professor']].nome,
                'dia': ga.dias[gene['dia']],
                'horario': ga.horarios[gene['horario']],
                'aula1': professor_horarios[key],
                'aula2': i
            })
        else:
            professor_horarios[key] = i
    
    # Verificar conflitos de sala
    sala_horarios = {}
    for i, gene in enumerate(cromossomo):
        key = (gene['sala'], gene['dia'], gene['horario'])
        if key in sala_horarios:
            conflitos['sala'].append({
                'sala': gene['sala'],
                'dia': ga.dias[gene['dia']],
                'horario': ga.horarios[gene['horario']],
                'aula1': sala_horarios[key],
                'aula2': i
            })
        else:
            sala_horarios[key] = i
    
    # Verificar disponibilidade
    for i, gene in enumerate(cromossomo):
        professor = gene['professor']
        dia_nome = ga.dias[gene['dia']]
        horario_nome = ga.horarios[gene['horario']]
        
        disponivel = False
        if professor in ga.disponibilidades:
            for disp in ga.disponibilidades[professor]:
                if disp.dia == dia_nome and disp.horario == horario_nome:
                    disponivel = True
                    break
        
        if not disponivel:
            conflitos['disponibilidade'].append({
                'professor': ga.professores[professor].nome,
                'dia': dia_nome,
                'horario': horario_nome,
                'disciplina': ga.disciplinas[gene['disciplina']].nome,
                'aula': i
            })
    
    return conflitos

def gerar_relatorio_completo(cromossomo, fitness, historico, ga):
    """Gera um relatório completo da solução"""
    print("\n" + "="*100)
    print("RELATÓRIO COMPLETO DA SOLUÇÃO")
    print("="*100)
    
    # Métricas gerais
    print(f"\n📊 MÉTRICAS GERAIS:")
    print(f"   • Fitness final: {fitness:.2f}")
    print(f"   • Melhoria total: {historico[-1] - historico[0]:.2f}")
    print(f"   • Gerações executadas: {len(historico)}")
    print(f"   • Total de aulas alocadas: {len(cromossomo)}")
    
    # Verificar conflitos
    conflitos = verificar_conflitos(cromossomo, ga)
    
    print(f"\n⚠️  ANÁLISE DE CONFLITOS:")
    print(f"   • Conflitos de professor: {len(conflitos['professor'])}")
    print(f"   • Conflitos de sala: {len(conflitos['sala'])}")
    print(f"   • Violações de disponibilidade: {len(conflitos['disponibilidade'])}")
    
    # Detalhar conflitos se existirem
    if conflitos['professor']:
        print(f"\n   🔴 CONFLITOS DE PROFESSOR:")
        for conf in conflitos['professor']:
            print(f"      - {conf['professor']} tem duas aulas em {conf['dia']} às {conf['horario']}")
    
    if conflitos['disponibilidade']:
        print(f"\n   🔴 VIOLAÇÕES DE DISPONIBILIDADE:")
        for conf in conflitos['disponibilidade'][:5]:  # Mostrar apenas as primeiras 5
            print(f"      - {conf['professor']} não está disponível {conf['dia']} às {conf['horario']}")
        if len(conflitos['disponibilidade']) > 5:
            print(f"      ... e mais {len(conflitos['disponibilidade']) - 5} violações")
    
    # Análise de distribuição
    aulas_por_dia = [0] * 5
    for gene in cromossomo:
        aulas_por_dia[gene['dia']] += 1
    
    print(f"\n📅 DISTRIBUIÇÃO POR DIA:")
    for i, dia in enumerate(ga.dias):
        print(f"   • {dia}: {aulas_por_dia[i]} aulas")
    
    # Análise por disciplina
    print(f"\n📚 DISTRIBUIÇÃO POR DISCIPLINA:")
    disciplina_count = {}
    for gene in cromossomo:
        disc = gene['disciplina']
        if disc not in disciplina_count:
            disciplina_count[disc] = 0
        disciplina_count[disc] += 1
    
    for disc_codigo, count in disciplina_count.items():
        disciplina = ga.disciplinas[disc_codigo]
        professor = None
        for prof in ga.professores.values():
            if prof.disciplina == disc_codigo:
                professor = prof.nome
                break
        
        status = "✅" if count == disciplina.carga_horaria else "❌"
        print(f"   {status} {disciplina.nome[:40]:40} | {count}/{disciplina.carga_horaria}h | Prof: {professor}")
    
    print("\n" + "="*100)

def executar_analise_completa():
    """Executa o algoritmo genético e faz análise completa"""
    print("🚀 Iniciando Algoritmo Genético para Horários Acadêmicos")
    print("="*60)
    
    # Executar algoritmo genético
    ga = ScheduleGA()
    melhor_solucao, fitness, historico = ga.executar()
    
    # Gerar relatório
    gerar_relatorio_completo(melhor_solucao, fitness, historico, ga)
    
    # Plotar evolução
    print("\n📈 Gerando gráficos de análise...")
    plotar_evolucao_fitness(historico)
    
    # Analisar distribuição
    analisar_distribuicao_horarios(melhor_solucao, ga)
    
    # Analisar carga dos professores
    df_professores = analisar_carga_professores(melhor_solucao, ga)
    
    # Exibir horário final
    ga.exibir_horario(melhor_solucao)
    
    return melhor_solucao, fitness, historico, ga, df_professores

def salvar_horario_excel(cromossomo, ga, filename="horario_otimizado.xlsx"):
    """Salva o horário otimizado em Excel"""
    
    # Criar pasta resultados se não existir
    pasta_resultados = 'resultados/'
    if not os.path.exists(pasta_resultados):
        os.makedirs(pasta_resultados)
        print(f"📁 Pasta '{pasta_resultados}' criada.")
    
    # Caminho completo do arquivo
    caminho_arquivo = os.path.join(pasta_resultados, filename)
    
    dados_horario = []
    
    for gene in cromossomo:
        disciplina = ga.disciplinas[gene['disciplina']]
        professor = ga.professores[gene['professor']]
        
        dados_horario.append({
            'Dia': ga.dias[gene['dia']],
            'Horario': ga.horarios[gene['horario']],
            'Disciplina': disciplina.nome,
            'Professor': professor.nome,
            'Sala': gene['sala'],
            'Carga_Horaria': disciplina.carga_horaria,
            'Turma': disciplina.turma
        })
    
    df = pd.DataFrame(dados_horario)
    df_sorted = df.sort_values(['Dia', 'Horario'])
    
    with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
        df_sorted.to_excel(writer, sheet_name='Horario_Completo', index=False)
        
        # Criar planilha resumo por dia
        for dia in ga.dias:
            df_dia = df_sorted[df_sorted['Dia'] == dia]
            df_dia.to_excel(writer, sheet_name=f'Horario_{dia}', index=False)
    
    print(f"💾 Horário salvo em: {caminho_arquivo}")
    return caminho_arquivo

# Função principal para execução
if __name__ == "__main__":
    # Executar análise completa
    solucao, fitness, historico, ga_instance, df_prof = executar_analise_completa()
    
    # Salvar resultado em Excel
    salvar_horario_excel(solucao, ga_instance)
    
    # Opções adicionais
    print("\n🔧 OPÇÕES ADICIONAIS:")
    print("1. Para ajustar parâmetros do AG, modifique a classe ScheduleGA")
    print("2. Para executar novamente: executar_analise_completa()")
    print("3. Para salvar em Excel: salvar_horario_excel(solucao, ga_instance)")