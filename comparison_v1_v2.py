import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from genetic_scheduler import ScheduleGA  # V1 - Penalização + Lista
from genetic_scheduler_v2 import ScheduleGA_V2  # V2 - Pontuação + Agenda

def comparar_abordagens():
    """Compara as duas abordagens: V1 (Penalização) vs V2 (Pontuação)"""
    
    print("🔬 COMPARAÇÃO: PENALIZAÇÃO vs PONTUAÇÃO")
    print("="*60)
    
    resultados = {
        'abordagem': [],
        'tempo_execucao': [],
        'fitness_final': [],
        'fitness_normalizado': [],
        'convergencia_geracao': [],
        'disciplinas_completas': [],
        'disponibilidade_respeitada': []
    }
    
    # Testar V1 - Penalização com Lista
    print("\n🔸 Testando V1 - Penalização com Lista de Eventos")
    print("-" * 50)
    
    start_time = time.time()
    ga_v1 = ScheduleGA()
    ga_v1.populacao_size = 30
    ga_v1.geracoes = 200
    
    try:
        solucao_v1, fitness_v1, historico_v1 = ga_v1.executar()
        tempo_v1 = time.time() - start_time
        
        # Analisar resultados V1
        stats_v1 = analisar_solucao_v1(solucao_v1, ga_v1)
        
        resultados['abordagem'].append('V1 - Penalização')
        resultados['tempo_execucao'].append(tempo_v1)
        resultados['fitness_final'].append(fitness_v1)
        resultados['fitness_normalizado'].append(fitness_v1 / 10000)  # Normalizar para 0-1
        resultados['convergencia_geracao'].append(len(historico_v1))
        resultados['disciplinas_completas'].append(stats_v1['disciplinas_completas'])
        resultados['disponibilidade_respeitada'].append(stats_v1['disponibilidade_respeitada'])
        
        print(f"✅ V1 concluído - Fitness: {fitness_v1:.0f}, Tempo: {tempo_v1:.1f}s")
        
    except Exception as e:
        print(f"❌ Erro no V1: {e}")
        return None
    
    # Testar V2 - Pontuação com Agenda
    print("\n🔹 Testando V2 - Pontuação com Agenda (Matriz)")
    print("-" * 50)
    
    start_time = time.time()
    ga_v2 = ScheduleGA_V2()
    ga_v2.populacao_size = 30
    ga_v2.geracoes = 200
    
    try:
        agenda_v2, fitness_v2, historico_v2 = ga_v2.executar()
        tempo_v2 = time.time() - start_time
        
        # Analisar resultados V2
        stats_v2 = analisar_solucao_v2(agenda_v2, ga_v2)
        
        resultados['abordagem'].append('V2 - Pontuação')
        resultados['tempo_execucao'].append(tempo_v2)
        resultados['fitness_final'].append(fitness_v2)
        resultados['fitness_normalizado'].append(fitness_v2 / 15000)  # Normalizar considerando pontuação máxima estimada
        resultados['convergencia_geracao'].append(len(historico_v2))
        resultados['disciplinas_completas'].append(stats_v2['disciplinas_completas'])
        resultados['disponibilidade_respeitada'].append(stats_v2['disponibilidade_respeitada'])
        
        print(f"✅ V2 concluído - Fitness: {fitness_v2:.0f}, Tempo: {tempo_v2:.1f}s")
        
    except Exception as e:
        print(f"❌ Erro no V2: {e}")
        return None
    
    # Gerar relatório comparativo
    gerar_relatorio_comparativo(resultados, historico_v1, historico_v2)
    
    # Plotar comparações
    plotar_comparacao(resultados, historico_v1, historico_v2)
    
    return resultados, (solucao_v1, ga_v1), (agenda_v2, ga_v2)

def analisar_solucao_v1(cromossomo, ga):
    """Analisa estatísticas da solução V1"""
    stats = {}
    
    # Contar disciplinas completas
    disciplina_count = {}
    for gene in cromossomo:
        disc = gene['disciplina']
        disciplina_count[disc] = disciplina_count.get(disc, 0) + 1
    
    disciplinas_completas = 0
    for disc_codigo, disciplina in ga.disciplinas.items():
        if disciplina_count.get(disc_codigo, 0) >= disciplina.carga_horaria:
            disciplinas_completas += 1
    
    stats['disciplinas_completas'] = disciplinas_completas / len(ga.disciplinas)
    
    # Verificar disponibilidade
    aulas_com_disponibilidade = 0
    total_aulas = len(cromossomo)
    
    for gene in cromossomo:
        professor = gene['professor']
        dia_nome = ga.dias[gene['dia']]
        horario_nome = ga.horarios[gene['horario']]
        
        if professor in ga.disponibilidades:
            for disp in ga.disponibilidades[professor]:
                if disp.dia == dia_nome and disp.horario == horario_nome:
                    aulas_com_disponibilidade += 1
                    break
    
    stats['disponibilidade_respeitada'] = aulas_com_disponibilidade / max(total_aulas, 1)
    
    return stats

def analisar_solucao_v2(agenda, ga):
    """Analisa estatísticas da solução V2"""
    stats = {}
    
    # Contar disciplinas completas
    disciplina_count = {}
    total_aulas = 0
    
    for dia in range(ga.num_dias):
        for horario in range(ga.num_horarios):
            aula = agenda[dia, horario]
            if aula is not None:
                disc = aula.disciplina
                disciplina_count[disc] = disciplina_count.get(disc, 0) + 1
                total_aulas += 1
    
    disciplinas_completas = 0
    for disc_codigo, disciplina in ga.disciplinas.items():
        if disciplina_count.get(disc_codigo, 0) >= disciplina.carga_horaria:
            disciplinas_completas += 1
    
    stats['disciplinas_completas'] = disciplinas_completas / len(ga.disciplinas)
    
    # Verificar disponibilidade
    aulas_com_disponibilidade = 0
    
    for dia in range(ga.num_dias):
        for horario in range(ga.num_horarios):
            aula = agenda[dia, horario]
            if aula is not None:
                if ga._professor_disponivel(aula.professor, dia, horario):
                    aulas_com_disponibilidade += 1
    
    stats['disponibilidade_respeitada'] = aulas_com_disponibilidade / max(total_aulas, 1)
    
    return stats

def gerar_relatorio_comparativo(resultados, historico_v1, historico_v2):
    """Gera relatório detalhado da comparação"""
    print("\n" + "="*80)
    print("📊 RELATÓRIO COMPARATIVO DETALHADO")
    print("="*80)
    
    df = pd.DataFrame(resultados)
    
    print("\n🏆 MÉTRICAS PRINCIPAIS:")
    print("-" * 60)
    for i, row in df.iterrows():
        print(f"\n{row['abordagem']}:")
        print(f"  ⏱️  Tempo de execução: {row['tempo_execucao']:.2f} segundos")
        print(f"  🎯 Fitness final: {row['fitness_final']:.0f}")
        print(f"  📊 Fitness normalizado: {row['fitness_normalizado']:.2%}")
        print(f"  🔄 Gerações executadas: {row['convergencia_geracao']}")
        print(f"  ✅ Disciplinas completas: {row['disciplinas_completas']:.1%}")
        print(f"  📅 Disponibilidade respeitada: {row['disponibilidade_respeitada']:.1%}")
    
    print("\n" + "="*80)
    print("🔍 ANÁLISE COMPARATIVA")
    print("="*80)
    
    # Comparar métricas
    v1_idx, v2_idx = 0, 1
    
    print(f"\n⚡ VELOCIDADE:")
    if df.iloc[v1_idx]['tempo_execucao'] < df.iloc[v2_idx]['tempo_execucao']:
        diferenca = df.iloc[v2_idx]['tempo_execucao'] - df.iloc[v1_idx]['tempo_execucao']
        print(f"  🏃 V1 foi {diferenca:.1f}s mais rápido")
    else:
        diferenca = df.iloc[v1_idx]['tempo_execucao'] - df.iloc[v2_idx]['tempo_execucao']
        print(f"  🏃 V2 foi {diferenca:.1f}s mais rápido")
    
    print(f"\n🎯 QUALIDADE DA SOLUÇÃO:")
    if df.iloc[v1_idx]['fitness_normalizado'] > df.iloc[v2_idx]['fitness_normalizado']:
        print(f"  🏆 V1 obteve melhor fitness normalizado")
    elif df.iloc[v2_idx]['fitness_normalizado'] > df.iloc[v1_idx]['fitness_normalizado']:
        print(f"  🏆 V2 obteve melhor fitness normalizado")
    else:
        print(f"  🤝 Empate no fitness normalizado")
    
    print(f"\n📚 COMPLETUDE DAS DISCIPLINAS:")
    if df.iloc[v1_idx]['disciplinas_completas'] > df.iloc[v2_idx]['disciplinas_completas']:
        print(f"  ✅ V1 completou mais disciplinas")
    elif df.iloc[v2_idx]['disciplinas_completas'] > df.iloc[v1_idx]['disciplinas_completas']:
        print(f"  ✅ V2 completou mais disciplinas")
    else:
        print(f"  🤝 Ambos completaram o mesmo número de disciplinas")
    
    print(f"\n📅 RESPEITO À DISPONIBILIDADE:")
    if df.iloc[v1_idx]['disponibilidade_respeitada'] > df.iloc[v2_idx]['disponibilidade_respeitada']:
        print(f"  👨‍🏫 V1 respeitou melhor a disponibilidade dos professores")
    elif df.iloc[v2_idx]['disponibilidade_respeitada'] > df.iloc[v1_idx]['disponibilidade_respeitada']:
        print(f"  👨‍🏫 V2 respeitou melhor a disponibilidade dos professores")
    else:
        print(f"  🤝 Ambos respeitaram igualmente a disponibilidade")

def plotar_comparacao(resultados, historico_v1, historico_v2):
    """Plota gráficos comparativos"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Comparação: Penalização vs Pontuação', fontsize=16, fontweight='bold')
    
    df = pd.DataFrame(resultados)
    
    # 1. Evolução do Fitness
    axes[0,0].plot(historico_v1, label='V1 - Penalização', linewidth=2, alpha=0.8)
    # Normalizar V2 para comparação visual
    historico_v2_norm = np.array(historico_v2) / max(historico_v2) * max(historico_v1)
    axes[0,0].plot(historico_v2_norm, label='V2 - Pontuação (norm)', linewidth=2, alpha=0.8)
    axes[0,0].set_title('Evolução do Fitness')
    axes[0,0].set_xlabel('Geração')
    axes[0,0].set_ylabel('Fitness')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # 2. Tempo de Execução
    axes[0,1].bar(df['abordagem'], df['tempo_execucao'], 
                  color=['skyblue', 'lightcoral'], alpha=0.8)
    axes[0,1].set_title('Tempo de Execução')
    axes[0,1].set_ylabel('Segundos')
    for i, v in enumerate(df['tempo_execucao']):
        axes[0,1].text(i, v + 0.1, f'{v:.1f}s', ha='center', fontweight='bold')
    
    # 3. Qualidade das Soluções
    metricas = ['fitness_normalizado', 'disciplinas_completas', 'disponibilidade_respeitada']
    x = np.arange(len(metricas))
    width = 0.35
    
    v1_values = [df.iloc[0][m] for m in metricas]
    v2_values = [df.iloc[1][m] for m in metricas]
    
    axes[1,0].bar(x - width/2, v1_values, width, label='V1 - Penalização', 
                  color='skyblue', alpha=0.8)
    axes[1,0].bar(x + width/2, v2_values, width, label='V2 - Pontuação', 
                  color='lightcoral', alpha=0.8)
    
    axes[1,0].set_title('Comparação de Qualidade')
    axes[1,0].set_ylabel('Score (0-1)')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(['Fitness\nNormalizado', 'Disciplinas\nCompletas', 'Disponibilidade\nRespeitada'])
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # 4. Convergência
    axes[1,1].plot(range(len(historico_v1)), historico_v1, 'b-', alpha=0.6, label='V1 - Penalização')
    axes[1,1].plot(range(len(historico_v2)), historico_v2_norm, 'r-', alpha=0.6, label='V2 - Pontuação')
    
    # Destacar últimas 50 gerações
    if len(historico_v1) > 50:
        axes[1,1].plot(range(len(historico_v1)-50, len(historico_v1)), 
                      historico_v1[-50:], 'b-', linewidth=3, label='V1 - Últimas 50')
    if len(historico_v2) > 50:
        axes[1,1].plot(range(len(historico_v2)-50, len(historico_v2)), 
                      historico_v2_norm[-50:], 'r-', linewidth=3, label='V2 - Últimas 50')
    
    axes[1,1].set_title('Análise de Convergência')
    axes[1,1].set_xlabel('Geração')
    axes[1,1].set_ylabel('Fitness')
    axes[1,1].legend()
    axes[1,1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def demonstrar_diferencas_modelagem():
    """Demonstra as diferenças conceituais entre as abordagens"""
    print("\n" + "="*80)
    print("🧠 DIFERENÇAS CONCEITUAIS ENTRE AS ABORDAGENS")
    print("="*80)
    
    print("\n📋 V1 - PENALIZAÇÃO COM LISTA DE EVENTOS:")
    print("-" * 50)
    print("✅ Representação:")
    print("   • Cromossomo = Lista de genes")
    print("   • Gene = [disciplina, professor, dia, horário, sala]")
    print("   • Exemplo: [(MAT101, Prof1, 0, 1, S201), (FIS202, Prof2, 1, 0, S201)]")
    print()
    print("✅ Função de Fitness:")
    print("   • Inicia com valor alto (10.000)")
    print("   • Subtrai penalidades por violações")
    print("   • Fitness = 10.000 - penalidades + bonificações")
    print("   • Foco: Evitar problemas")
    print()
    print("✅ Vantagens:")
    print("   • Flexível para diferentes tamanhos de problema")
    print("   • Fácil adicionar/remover aulas")
    print("   • Crossover e mutação mais diretos")
    print()
    print("✅ Desvantagens:")
    print("   • Pode não garantir todas as disciplinas")
    print("   • Fitness negativo confunde interpretação")
    print("   • Harder to ensure constraint satisfaction")
    
    print("\n📅 V2 - PONTUAÇÃO COM AGENDA (MATRIZ):")
    print("-" * 50)
    print("✅ Representação:")
    print("   • Cromossomo = Matriz 5x4 (dias x horários)")
    print("   • Célula = Aula(disciplina, professor, sala) ou None")
    print("   • Visualização direta como agenda")
    print()
    print("✅ Função de Fitness:")
    print("   • Inicia com zero")
    print("   • Soma pontuações por qualidades")
    print("   • Fitness = Σ(pontuações positivas)")
    print("   • Foco: Maximizar benefícios")
    print()
    print("✅ Vantagens:")
    print("   • Garantia de atendimento das disciplinas")
    print("   • Interpretação intuitiva do fitness")
    print("   • Visualização natural como horário")
    print("   • Reparo automático de soluções")
    print()
    print("✅ Desvantagens:")
    print("   • Estrutura fixa (5x4)")
    print("   • Crossover mais complexo")
    print("   • Pode ter desperdício de slots")
    
    print("\n🎯 RECOMENDAÇÕES DE USO:")
    print("-" * 50)
    print("🔸 Use V1 (Penalização) quando:")
    print("   • Flexibilidade na estrutura é importante")
    print("   • Número de aulas varia muito")
    print("   • Foco em evitar violações específicas")
    print("   • Problema tem muitas restrições hard")
    print()
    print("🔹 Use V2 (Pontuação) quando:")
    print("   • Estrutura de horário é fixa")
    print("   • Todas as disciplinas devem ser atendidas")
    print("   • Foco em otimização de qualidade")
    print("   • Interpretação intuitiva é importante")

def executar_comparacao_completa():
    """Executa comparação completa entre as abordagens"""
    print("🔬 COMPARAÇÃO COMPLETA: V1 vs V2")
    print("="*60)
    
    # Demonstrar diferenças conceituais
    demonstrar_diferencas_modelagem()
    
    # Executar comparação prática
    print("\n🚀 Iniciando testes práticos...")
    try:
        resultados, (sol_v1, ga_v1), (agenda_v2, ga_v2) = comparar_abordagens()
        
        if resultados:
            print("\n✅ Comparação concluída com sucesso!")
            
            # Salvar resultados
            df_resultados = pd.DataFrame(resultados)
            
            # Criar pasta resultados se não existir
            import os
            pasta_resultados = 'resultados'
            if not os.path.exists(pasta_resultados):
                os.makedirs(pasta_resultados)
            
            # Salvar comparação
            filename = os.path.join(pasta_resultados, 'comparacao_v1_v2.xlsx')
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df_resultados.to_excel(writer, sheet_name='Resultados_Comparacao', index=False)
            
            print(f"📄 Resultados salvos em: {filename}")
            
            # Perguntar se quer ver as soluções
            print("\n🔍 Quer visualizar as soluções encontradas?")
            opcao = input("Digite 's' para sim: ").strip().lower()
            
            if opcao == 's':
                print("\n" + "="*60)
                print("V1 - SOLUÇÃO COM PENALIZAÇÃO")
                print("="*60)
                ga_v1.exibir_horario(sol_v1)
                
                print("\n" + "="*60)
                print("V2 - SOLUÇÃO COM PONTUAÇÃO")
                print("="*60)
                ga_v2.exibir_agenda(agenda_v2)
        
        return resultados
        
    except Exception as e:
        print(f"❌ Erro durante comparação: {e}")
        return None

# Execução principal
if __name__ == "__main__":
    executar_comparacao_completa()