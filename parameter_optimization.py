import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from genetic_scheduler import ScheduleGA  # V1
from genetic_scheduler_v2 import ScheduleGA_V2  # V2
import time

class ParameterOptimizer:
    """Classe para otimizar parâmetros dos algoritmos genéticos V1 e V2"""
    
    def __init__(self, versao="V1"):
        self.versao = versao
        self.resultados = []
        
        print(f"🔧 Inicializando otimizador para {versao}")
        
        if versao == "V1":
            self.classe_ag = ScheduleGA
            self.fitness_max_esperado = 10000
        elif versao == "V2":
            self.classe_ag = ScheduleGA_V2
            self.fitness_max_esperado = 15000  # Pontuação máxima estimada
        else:
            raise ValueError("Versão deve ser 'V1' ou 'V2'")
    
    def testar_parametros(self, 
                         populacao_sizes=[30, 50, 100],
                         taxas_mutacao=[0.05, 0.1, 0.2],
                         taxas_crossover=[0.6, 0.8, 0.9],
                         tamanhos_torneio=[3, 5, 7],
                         max_geracoes=200,
                         execucoes_por_config=3):
        """
        Testa diferentes combinações de parâmetros para a versão especificada
        """
        
        combinacoes = list(itertools.product(
            populacao_sizes, taxas_mutacao, taxas_crossover, tamanhos_torneio
        ))
        
        print(f"🔬 Testando {len(combinacoes)} combinações para {self.versao}")
        print(f"📊 {execucoes_por_config} execuções por combinação")
        print(f"⏱️  Estimativa: ~{len(combinacoes) * execucoes_por_config * 0.5:.1f} minutos")
        print("="*60)
        
        for i, (pop_size, mut_rate, cross_rate, tournament_size) in enumerate(combinacoes):
            print(f"\n[{i+1}/{len(combinacoes)}] Testando {self.versao}: Pop={pop_size}, Mut={mut_rate}, Cross={cross_rate}, Tournament={tournament_size}")
            
            fitness_runs = []
            tempos_runs = []
            
            for run in range(execucoes_por_config):
                start_time = time.time()
                
                try:
                    # Configurar AG com parâmetros específicos
                    ga = self.classe_ag()
                    ga.populacao_size = pop_size
                    ga.taxa_mutacao = mut_rate
                    ga.taxa_crossover = cross_rate
                    ga.tamanho_torneio = tournament_size
                    ga.geracoes = max_geracoes
                    
                    # Executar algoritmo
                    if self.versao == "V1":
                        _, fitness, historico = ga.executar()
                    else:  # V2
                        _, fitness, historico = ga.executar()
                    
                    tempo_execucao = time.time() - start_time
                    
                    fitness_runs.append(fitness)
                    tempos_runs.append(tempo_execucao)
                    
                    print(f"    Run {run+1}: Fitness={fitness:.2f}, Tempo={tempo_execucao:.1f}s")
                    
                except Exception as e:
                    print(f"    Run {run+1}: ERRO - {str(e)}")
                    fitness_runs.append(0)
                    tempos_runs.append(999)
            
            # Salvar resultados
            resultado = {
                'versao': self.versao,
                'populacao_size': pop_size,
                'taxa_mutacao': mut_rate,
                'taxa_crossover': cross_rate,
                'tamanho_torneio': tournament_size,
                'fitness_medio': np.mean(fitness_runs),
                'fitness_std': np.std(fitness_runs),
                'fitness_max': np.max(fitness_runs),
                'fitness_normalizado': np.mean(fitness_runs) / self.fitness_max_esperado,
                'tempo_medio': np.mean(tempos_runs),
                'tempo_std': np.std(tempos_runs)
            }
            
            self.resultados.append(resultado)
            
        return self.analisar_resultados()
    
    def analisar_resultados(self):
        """Analisa os resultados dos testes"""
        
        df = pd.DataFrame(self.resultados)
        
        print("\n" + "="*80)
        print(f"📊 ANÁLISE DOS RESULTADOS - {self.versao}")
        print("="*80)
        
        # Top 5 configurações
        df_sorted = df.sort_values('fitness_medio', ascending=False)
        
        print(f"\n🏆 TOP 5 CONFIGURAÇÕES PARA {self.versao}:")
        print("-" * 100)
        print(f"{'Rank':<4} {'Pop':<5} {'Mut':<6} {'Cross':<7} {'Tourn':<6} {'Fitness':<10} {'±Std':<8} {'Norm':<8} {'Tempo(s)':<10}")
        print("-" * 100)
        
        for i, (idx, row) in enumerate(df_sorted.head().iterrows()):
            print(f"{i+1:<4} "
                  f"{int(row['populacao_size']):<5} "
                  f"{row['taxa_mutacao']:<6.2f} "
                  f"{row['taxa_crossover']:<7.2f} "
                  f"{int(row['tamanho_torneio']):<6} "
                  f"{row['fitness_medio']:<10.2f} "
                  f"±{row['fitness_std']:<7.2f} "
                  f"{row['fitness_normalizado']:<8.3f} "
                  f"{row['tempo_medio']:<10.1f}")
        
        # Análise por parâmetro
        self._analisar_por_parametro(df)
        
        # Plotar resultados
        self._plotar_analise(df)
        
        return df_sorted.iloc[0].to_dict()
    
    def _analisar_por_parametro(self, df):
        """Analisa o impacto individual de cada parâmetro"""
        
        print(f"\n📈 IMPACTO DOS PARÂMETROS NO {self.versao}:")
        print("-" * 50)
        
        # Tamanho da população
        pop_impact = df.groupby('populacao_size')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTamanho da População:")
        for pop_size, stats in pop_impact.iterrows():
            print(f"  {pop_size:3d}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Taxa de mutação
        mut_impact = df.groupby('taxa_mutacao')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTaxa de Mutação:")
        for mut_rate, stats in mut_impact.iterrows():
            print(f"  {mut_rate:.2f}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Taxa de crossover
        cross_impact = df.groupby('taxa_crossover')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTaxa de Crossover:")
        for cross_rate, stats in cross_impact.iterrows():
            print(f"  {cross_rate:.2f}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Tamanho do torneio
        tourn_impact = df.groupby('tamanho_torneio')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTamanho do Torneio:")
        for tourn_size, stats in tourn_impact.iterrows():
            print(f"  {tourn_size:3d}: {stats['mean']:.2f} (±{stats['std']:.2f})")
    
    def _plotar_analise(self, df):
        """Plota análises visuais dos resultados"""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f'Análise de Parâmetros - {self.versao}', fontsize=16, fontweight='bold')
        
        # 1. Fitness vs Tamanho da População
        pop_stats = df.groupby('populacao_size')['fitness_medio'].agg(['mean', 'std'])
        axes[0,0].errorbar(pop_stats.index, pop_stats['mean'], yerr=pop_stats['std'], 
                          marker='o', capsize=5, capthick=2)
        axes[0,0].set_title('Fitness vs Tamanho da População')
        axes[0,0].set_xlabel('Tamanho da População')
        axes[0,0].set_ylabel('Fitness Médio')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Fitness vs Taxa de Mutação
        mut_stats = df.groupby('taxa_mutacao')['fitness_medio'].agg(['mean', 'std'])
        axes[0,1].errorbar(mut_stats.index, mut_stats['mean'], yerr=mut_stats['std'], 
                          marker='s', capsize=5, capthick=2, color='orange')
        axes[0,1].set_title('Fitness vs Taxa de Mutação')
        axes[0,1].set_xlabel('Taxa de Mutação')
        axes[0,1].set_ylabel('Fitness Médio')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Fitness vs Taxa de Crossover
        cross_stats = df.groupby('taxa_crossover')['fitness_medio'].agg(['mean', 'std'])
        axes[0,2].errorbar(cross_stats.index, cross_stats['mean'], yerr=cross_stats['std'], 
                          marker='^', capsize=5, capthick=2, color='green')
        axes[0,2].set_title('Fitness vs Taxa de Crossover')
        axes[0,2].set_xlabel('Taxa de Crossover')
        axes[0,2].set_ylabel('Fitness Médio')
        axes[0,2].grid(True, alpha=0.3)
        
        # 4. Fitness vs Tamanho do Torneio
        tourn_stats = df.groupby('tamanho_torneio')['fitness_medio'].agg(['mean', 'std'])
        axes[1,0].errorbar(tourn_stats.index, tourn_stats['mean'], yerr=tourn_stats['std'], 
                          marker='d', capsize=5, capthick=2, color='red')
        axes[1,0].set_title('Fitness vs Tamanho do Torneio')
        axes[1,0].set_xlabel('Tamanho do Torneio')
        axes[1,0].set_ylabel('Fitness Médio')
        axes[1,0].grid(True, alpha=0.3)
        
        # 5. Tempo vs Fitness
        axes[1,1].scatter(df['tempo_medio'], df['fitness_medio'], alpha=0.6, s=60)
        axes[1,1].set_title('Trade-off: Tempo vs Fitness')
        axes[1,1].set_xlabel('Tempo Médio (s)')
        axes[1,1].set_ylabel('Fitness Médio')
        axes[1,1].grid(True, alpha=0.3)
        
        # 6. Distribuição do Fitness Normalizado
        axes[1,2].hist(df['fitness_normalizado'], bins=15, alpha=0.7, edgecolor='black')
        axes[1,2].axvline(df['fitness_normalizado'].mean(), color='red', linestyle='--', 
                         label=f'Média: {df["fitness_normalizado"].mean():.3f}')
        axes[1,2].set_title('Distribuição do Fitness Normalizado')
        axes[1,2].set_xlabel('Fitness Normalizado')
        axes[1,2].set_ylabel('Frequência')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def salvar_resultados(self, filename="resultados_otimizacao.xlsx"):
        """Salva os resultados em Excel"""
        
        # Criar pasta resultados se não existir
        pasta_resultados = 'resultados'
        if not os.path.exists(pasta_resultados):
            os.makedirs(pasta_resultados)
            print(f"📁 Pasta '{pasta_resultados}/' criada.")
        
        # Adicionar versão ao nome do arquivo
        base_name = filename.replace('.xlsx', '')
        filename_versioned = f"{base_name}_{self.versao}.xlsx"
        
        # Caminho completo do arquivo - verificar se já tem o caminho completo
        if filename_versioned.startswith('resultados/') or filename_versioned.startswith('resultados\\'):
            caminho_arquivo = filename_versioned
        else:
            caminho_arquivo = os.path.join(pasta_resultados, filename_versioned)
        
        df = pd.DataFrame(self.resultados)
        df_sorted = df.sort_values('fitness_medio', ascending=False)
        
        try:
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name='Todos_Resultados', index=False)
                
                # Top 10
                df_sorted.head(10).to_excel(writer, sheet_name='Top_10', index=False)
                
                # Análise por parâmetro
                for param in ['populacao_size', 'taxa_mutacao', 'taxa_crossover', 'tamanho_torneio']:
                    param_analysis = df.groupby(param)['fitness_medio'].agg(['mean', 'std', 'min', 'max'])
                    param_analysis.to_excel(writer, sheet_name=f'Analise_{param}')
                
                # Resumo estatístico
                resumo = {
                    'Versao': [self.versao],
                    'Total_Testes': [len(df)],
                    'Melhor_Fitness': [df['fitness_medio'].max()],
                    'Fitness_Medio': [df['fitness_medio'].mean()],
                    'Tempo_Medio': [df['tempo_medio'].mean()],
                    'Melhor_Config_Pop': [df_sorted.iloc[0]['populacao_size']],
                    'Melhor_Config_Mut': [df_sorted.iloc[0]['taxa_mutacao']],
                    'Melhor_Config_Cross': [df_sorted.iloc[0]['taxa_crossover']],
                    'Melhor_Config_Tourn': [df_sorted.iloc[0]['tamanho_torneio']]
                }
                pd.DataFrame(resumo).to_excel(writer, sheet_name='Resumo_Geral', index=False)
            
            print(f"💾 Resultados salvos em: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            print(f"Tentando salvar em: {caminho_arquivo}")
            # Tentar salvar no diretório atual como fallback
            fallback_filename = os.path.basename(filename_versioned)
            print(f"Salvando como fallback em: {fallback_filename}")
            
            with pd.ExcelWriter(fallback_filename, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name='Todos_Resultados', index=False)
                df_sorted.head(10).to_excel(writer, sheet_name='Top_10', index=False)
                for param in ['populacao_size', 'taxa_mutacao', 'taxa_crossover', 'tamanho_torneio']:
                    param_analysis = df.groupby(param)['fitness_medio'].agg(['mean', 'std', 'min', 'max'])
                    param_analysis.to_excel(writer, sheet_name=f'Analise_{param}')
            
            print(f"💾 Arquivo salvo em: {fallback_filename}")
            return fallback_filename

def executar_teste_rapido_v1():
    """Executa um teste rápido com poucos parâmetros para V1"""
    print("🚀 Executando Teste Rápido de Parâmetros - V1 (Penalização)")
    
    optimizer = ParameterOptimizer(versao="V1")
    
    melhor_config = optimizer.testar_parametros(
        populacao_sizes=[30, 50],
        taxas_mutacao=[0.1, 0.15],
        taxas_crossover=[0.7, 0.8],
        tamanhos_torneio=[3, 5],
        max_geracoes=100,
        execucoes_por_config=2
    )
    
    print(f"\n🏆 MELHOR CONFIGURAÇÃO V1:")
    print(f"   • Tamanho da População: {int(melhor_config['populacao_size'])}")
    print(f"   • Taxa de Mutação: {melhor_config['taxa_mutacao']:.3f}")
    print(f"   • Taxa de Crossover: {melhor_config['taxa_crossover']:.3f}")
    print(f"   • Tamanho do Torneio: {int(melhor_config['tamanho_torneio'])}")
    print(f"   • Fitness Médio: {melhor_config['fitness_medio']:.2f}")
    
    try:
        caminho_salvo = optimizer.salvar_resultados("teste_rapido_parametros.xlsx")
        print(f"✅ Arquivo salvo com sucesso em: {caminho_salvo}")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
    return melhor_config

def executar_teste_rapido_v2():
    """Executa um teste rápido com poucos parâmetros para V2"""
    print("🚀 Executando Teste Rápido de Parâmetros - V2 (Pontuação)")
    
    optimizer = ParameterOptimizer(versao="V2")
    
    # Parâmetros ajustados para V2 (pontuação com agenda)
    melhor_config = optimizer.testar_parametros(
        populacao_sizes=[30, 50],
        taxas_mutacao=[0.12, 0.18],  # Um pouco mais alta para V2
        taxas_crossover=[0.7, 0.8],
        tamanhos_torneio=[3, 5],
        max_geracoes=100,
        execucoes_por_config=2
    )
    
    print(f"\n🏆 MELHOR CONFIGURAÇÃO V2:")
    print(f"   • Tamanho da População: {int(melhor_config['populacao_size'])}")
    print(f"   • Taxa de Mutação: {melhor_config['taxa_mutacao']:.3f}")
    print(f"   • Taxa de Crossover: {melhor_config['taxa_crossover']:.3f}")
    print(f"   • Tamanho do Torneio: {int(melhor_config['tamanho_torneio'])}")
    print(f"   • Fitness Médio: {melhor_config['fitness_medio']:.2f}")
    print(f"   • Fitness Normalizado: {melhor_config['fitness_normalizado']:.3f}")
    
    try:
        caminho_salvo = optimizer.salvar_resultados("teste_rapido_parametros.xlsx")
        print(f"✅ Arquivo salvo com sucesso em: {caminho_salvo}")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
    return melhor_config

def comparar_parametros_v1_v2():
    """Compara parâmetros ótimos entre V1 e V2"""
    print("🔬 COMPARAÇÃO DE PARÂMETROS ÓTIMOS: V1 vs V2")
    print("="*60)
    
    print("Executando testes para ambas as versões...")
    
    # Testar V1
    print("\n🔸 Testando V1...")
    config_v1 = executar_teste_rapido_v1()
    
    # Testar V2
    print("\n🔹 Testando V2...")
    config_v2 = executar_teste_rapido_v2()
    
    # Comparar resultados
    print("\n" + "="*80)
    print("📊 COMPARAÇÃO DE CONFIGURAÇÕES ÓTIMAS")
    print("="*80)
    
    parametros = ['populacao_size', 'taxa_mutacao', 'taxa_crossover', 'tamanho_torneio']
    
    print(f"{'Parâmetro':<20} {'V1 (Penalização)':<20} {'V2 (Pontuação)':<20} {'Diferença':<15}")
    print("-" * 75)
    
    for param in parametros:
        v1_val = config_v1[param]
        v2_val = config_v2[param]
        
        if isinstance(v1_val, float):
            diff = f"{v2_val - v1_val:+.3f}"
            v1_str = f"{v1_val:.3f}"
            v2_str = f"{v2_val:.3f}"
        else:
            diff = f"{v2_val - v1_val:+d}"
            v1_str = f"{v1_val}"
            v2_str = f"{v2_val}"
        
        print(f"{param:<20} {v1_str:<20} {v2_str:<20} {diff:<15}")
    
    print(f"\n{'Fitness Médio':<20} {config_v1['fitness_medio']:<20.2f} {config_v2['fitness_medio']:<20.2f}")
    print(f"{'Fitness Normalizado':<20} {config_v1.get('fitness_normalizado', 'N/A'):<20} {config_v2.get('fitness_normalizado', 'N/A'):<20}")
    
    # Insights
    print("\n💡 INSIGHTS:")
    if config_v2['taxa_mutacao'] > config_v1['taxa_mutacao']:
        print("   • V2 (Agenda) prefere taxa de mutação mais alta")
    if config_v2['populacao_size'] != config_v1['populacao_size']:
        print(f"   • Tamanhos de população diferentes: V1={config_v1['populacao_size']}, V2={config_v2['populacao_size']}")
    
    return config_v1, config_v2

def executar_teste_rapido():
    """Mantém compatibilidade com código existente - pergunta qual versão"""
    print("🔧 OTIMIZAÇÃO DE PARÂMETROS")
    print("="*40)
    print("Escolha a versão para otimizar:")
    print("1. V1 - Penalização com Lista")
    print("2. V2 - Pontuação com Agenda")
    print("3. Comparar ambas as versões")
    
    try:
        opcao = input("Opção (1-3): ").strip()
        
        if opcao == "1":
            return executar_teste_rapido_v1()
        elif opcao == "2":
            return executar_teste_rapido_v2()
        elif opcao == "3":
            return comparar_parametros_v1_v2()
        else:
            print("❌ Opção inválida!")
            return None
            
    except Exception as e:
        print(f"❌ Erro durante otimização: {e}")
        return None

def testar_config_especifica_v2(populacao_size=50, taxa_mutacao=0.15, 
                               taxa_crossover=0.8, tamanho_torneio=3, runs=5):
    """Testa uma configuração específica múltiplas vezes para V2"""
    
    print(f"🎯 Testando configuração específica V2:")
    print(f"   Pop: {populacao_size}, Mut: {taxa_mutacao}, Cross: {taxa_crossover}, Tournament: {tamanho_torneio}")
    
    resultados = []
    
    for run in range(runs):
        print(f"   Execução {run+1}/{runs}...")
        
        ga = ScheduleGA_V2()
        ga.populacao_size = populacao_size
        ga.taxa_mutacao = taxa_mutacao
        ga.taxa_crossover = taxa_crossover
        ga.tamanho_torneio = tamanho_torneio
        
        _, fitness, historico = ga.executar()
        resultados.append(fitness)
    
    print(f"\n📊 Resultados V2:")
    print(f"   • Fitness médio: {np.mean(resultados):.2f}")
    print(f"   • Desvio padrão: {np.std(resultados):.2f}")
    print(f"   • Melhor: {np.max(resultados):.2f}")
    print(f"   • Pior: {np.min(resultados):.2f}")
    print(f"   • Fitness normalizado: {np.mean(resultados)/15000:.3f}")
    
    return resultados

# Execução principal
if __name__ == "__main__":
    print("🔧 OTIMIZADOR DE PARÂMETROS - V1 e V2")
    print("="*60)
    print("Opções disponíveis:")
    print("1. Teste rápido V1 (5-10 minutos)")
    print("2. Teste rápido V2 (5-10 minutos)")
    print("3. Comparar V1 vs V2 (10-15 minutos)")
    print("4. Testar configuração específica V1")
    print("5. Testar configuração específica V2")
    
    opcao = input("\nEscolha uma opção (1-5): ")
    
    if opcao == "1":
        melhor = executar_teste_rapido_v1()
    elif opcao == "2":
        melhor = executar_teste_rapido_v2()
    elif opcao == "3":
        v1_config, v2_config = comparar_parametros_v1_v2()
    elif opcao == "4":
        resultados = testar_config_especifica()
    elif opcao == "5":
        resultados = testar_config_especifica_v2()
    else:
        print("Opção inválida!")
        
    def testar_parametros(self, 
                         populacao_sizes=[30, 50, 100],
                         taxas_mutacao=[0.05, 0.1, 0.2],
                         taxas_crossover=[0.6, 0.8, 0.9],
                         tamanhos_torneio=[3, 5, 7],
                         max_geracoes=200,
                         execucoes_por_config=3):
        """
        Testa diferentes combinações de parâmetros
        """
        
        combinacoes = list(itertools.product(
            populacao_sizes, taxas_mutacao, taxas_crossover, tamanhos_torneio
        ))
        
        print(f"🔬 Testando {len(combinacoes)} combinações de parâmetros")
        print(f"📊 {execucoes_por_config} execuções por combinação")
        print(f"⏱️  Estimativa: ~{len(combinacoes) * execucoes_por_config * 0.5:.1f} minutos")
        print("="*60)
        
        for i, (pop_size, mut_rate, cross_rate, tournament_size) in enumerate(combinacoes):
            print(f"\n[{i+1}/{len(combinacoes)}] Testando: Pop={pop_size}, Mut={mut_rate}, Cross={cross_rate}, Tournament={tournament_size}")
            
            fitness_runs = []
            tempos_runs = []
            
            for run in range(execucoes_por_config):
                start_time = time.time()
                
                # Configurar AG com parâmetros específicos
                ga = ScheduleGA()
                ga.populacao_size = pop_size
                ga.taxa_mutacao = mut_rate
                ga.taxa_crossover = cross_rate
                ga.tamanho_torneio = tournament_size
                ga.geracoes = max_geracoes
                
                try:
                    _, fitness, historico = ga.executar()
                    tempo_execucao = time.time() - start_time
                    
                    fitness_runs.append(fitness)
                    tempos_runs.append(tempo_execucao)
                    
                    print(f"    Run {run+1}: Fitness={fitness:.2f}, Tempo={tempo_execucao:.1f}s")
                    
                except Exception as e:
                    print(f"    Run {run+1}: ERRO - {str(e)}")
                    fitness_runs.append(0)
                    tempos_runs.append(999)
            
            # Salvar resultados
            resultado = {
                'populacao_size': pop_size,
                'taxa_mutacao': mut_rate,
                'taxa_crossover': cross_rate,
                'tamanho_torneio': tournament_size,
                'fitness_medio': np.mean(fitness_runs),
                'fitness_std': np.std(fitness_runs),
                'fitness_max': np.max(fitness_runs),
                'tempo_medio': np.mean(tempos_runs),
                'tempo_std': np.std(tempos_runs)
            }
            
            self.resultados.append(resultado)
            
        return self.analisar_resultados()
    
    def analisar_resultados(self):
        """Analisa os resultados dos testes"""
        
        df = pd.DataFrame(self.resultados)
        
        print("\n" + "="*80)
        print("📊 ANÁLISE DOS RESULTADOS")
        print("="*80)
        
        # Top 5 configurações
        df_sorted = df.sort_values('fitness_medio', ascending=False)
        
        print("\n🏆 TOP 5 CONFIGURAÇÕES:")
        print("-" * 100)
        print(f"{'Rank':<4} {'Pop':<5} {'Mut':<6} {'Cross':<7} {'Tourn':<6} {'Fitness':<10} {'±Std':<8} {'Tempo(s)':<10}")
        print("-" * 100)
        
        for i, row in df_sorted.head().iterrows():
            print(f"{df_sorted.index.get_loc(i)+1:<4} "
                  f"{int(row['populacao_size']):<5} "
                  f"{row['taxa_mutacao']:<6.2f} "
                  f"{row['taxa_crossover']:<7.2f} "
                  f"{int(row['tamanho_torneio']):<6} "
                  f"{row['fitness_medio']:<10.2f} "
                  f"±{row['fitness_std']:<7.2f} "
                  f"{row['tempo_medio']:<10.1f}")
        
        # Análise por parâmetro
        self._analisar_por_parametro(df)
        
        # Plotar resultados
        self._plotar_analise(df)
        
        return df_sorted.iloc[0].to_dict()
    
    def _analisar_por_parametro(self, df):
        """Analisa o impacto individual de cada parâmetro"""
        
        print("\n📈 IMPACTO DOS PARÂMETROS:")
        print("-" * 50)
        
        # Tamanho da população
        pop_impact = df.groupby('populacao_size')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTamanho da População:")
        for pop_size, stats in pop_impact.iterrows():
            print(f"  {pop_size:3d}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Taxa de mutação
        mut_impact = df.groupby('taxa_mutacao')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTaxa de Mutação:")
        for mut_rate, stats in mut_impact.iterrows():
            print(f"  {mut_rate:.2f}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Taxa de crossover
        cross_impact = df.groupby('taxa_crossover')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTaxa de Crossover:")
        for cross_rate, stats in cross_impact.iterrows():
            print(f"  {cross_rate:.2f}: {stats['mean']:.2f} (±{stats['std']:.2f})")
        
        # Tamanho do torneio
        tourn_impact = df.groupby('tamanho_torneio')['fitness_medio'].agg(['mean', 'std'])
        print(f"\nTamanho do Torneio:")
        for tourn_size, stats in tourn_impact.iterrows():
            print(f"  {tourn_size:3d}: {stats['mean']:.2f} (±{stats['std']:.2f})")
    
    def _plotar_analise(self, df):
        """Plota análises visuais dos resultados"""
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Análise de Parâmetros do Algoritmo Genético', fontsize=16, fontweight='bold')
        
        # 1. Fitness vs Tamanho da População
        pop_stats = df.groupby('populacao_size')['fitness_medio'].agg(['mean', 'std'])
        axes[0,0].errorbar(pop_stats.index, pop_stats['mean'], yerr=pop_stats['std'], 
                          marker='o', capsize=5, capthick=2)
        axes[0,0].set_title('Fitness vs Tamanho da População')
        axes[0,0].set_xlabel('Tamanho da População')
        axes[0,0].set_ylabel('Fitness Médio')
        axes[0,0].grid(True, alpha=0.3)
        
        # 2. Fitness vs Taxa de Mutação
        mut_stats = df.groupby('taxa_mutacao')['fitness_medio'].agg(['mean', 'std'])
        axes[0,1].errorbar(mut_stats.index, mut_stats['mean'], yerr=mut_stats['std'], 
                          marker='s', capsize=5, capthick=2, color='orange')
        axes[0,1].set_title('Fitness vs Taxa de Mutação')
        axes[0,1].set_xlabel('Taxa de Mutação')
        axes[0,1].set_ylabel('Fitness Médio')
        axes[0,1].grid(True, alpha=0.3)
        
        # 3. Fitness vs Taxa de Crossover
        cross_stats = df.groupby('taxa_crossover')['fitness_medio'].agg(['mean', 'std'])
        axes[0,2].errorbar(cross_stats.index, cross_stats['mean'], yerr=cross_stats['std'], 
                          marker='^', capsize=5, capthick=2, color='green')
        axes[0,2].set_title('Fitness vs Taxa de Crossover')
        axes[0,2].set_xlabel('Taxa de Crossover')
        axes[0,2].set_ylabel('Fitness Médio')
        axes[0,2].grid(True, alpha=0.3)
        
        # 4. Fitness vs Tamanho do Torneio
        tourn_stats = df.groupby('tamanho_torneio')['fitness_medio'].agg(['mean', 'std'])
        axes[1,0].errorbar(tourn_stats.index, tourn_stats['mean'], yerr=tourn_stats['std'], 
                          marker='d', capsize=5, capthick=2, color='red')
        axes[1,0].set_title('Fitness vs Tamanho do Torneio')
        axes[1,0].set_xlabel('Tamanho do Torneio')
        axes[1,0].set_ylabel('Fitness Médio')
        axes[1,0].grid(True, alpha=0.3)
        
        # 5. Tempo vs Fitness
        axes[1,1].scatter(df['tempo_medio'], df['fitness_medio'], alpha=0.6, s=60)
        axes[1,1].set_title('Trade-off: Tempo vs Fitness')
        axes[1,1].set_xlabel('Tempo Médio (s)')
        axes[1,1].set_ylabel('Fitness Médio')
        axes[1,1].grid(True, alpha=0.3)
        
        # 6. Distribuição do Fitness
        axes[1,2].hist(df['fitness_medio'], bins=15, alpha=0.7, edgecolor='black')
        axes[1,2].axvline(df['fitness_medio'].mean(), color='red', linestyle='--', 
                         label=f'Média: {df["fitness_medio"].mean():.2f}')
        axes[1,2].set_title('Distribuição do Fitness')
        axes[1,2].set_xlabel('Fitness')
        axes[1,2].set_ylabel('Frequência')
        axes[1,2].legend()
        axes[1,2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def salvar_resultados(self, filename="resultados_otimizacao.xlsx"):
        """Salva os resultados em Excel"""
        
        # Criar pasta resultados se não existir
        pasta_resultados = 'resultados'
        if not os.path.exists(pasta_resultados):
            os.makedirs(pasta_resultados)
            print(f"📁 Pasta '{pasta_resultados}/' criada.")
        
        # Caminho completo do arquivo - verificar se já tem o caminho completo
        if filename.startswith('resultados/') or filename.startswith('resultados\\'):
            caminho_arquivo = filename
        else:
            caminho_arquivo = os.path.join(pasta_resultados, filename)
        
        df = pd.DataFrame(self.resultados)
        df_sorted = df.sort_values('fitness_medio', ascending=False)
        
        try:
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name='Todos_Resultados', index=False)
                
                # Top 10
                df_sorted.head(10).to_excel(writer, sheet_name='Top_10', index=False)
                
                # Análise por parâmetro
                for param in ['populacao_size', 'taxa_mutacao', 'taxa_crossover', 'tamanho_torneio']:
                    param_analysis = df.groupby(param)['fitness_medio'].agg(['mean', 'std', 'min', 'max'])
                    param_analysis.to_excel(writer, sheet_name=f'Analise_{param}')
            
            print(f"💾 Resultados salvos em: {caminho_arquivo}")
            return caminho_arquivo
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")
            print(f"Tentando salvar em: {caminho_arquivo}")
            # Tentar salvar no diretório atual como fallback
            fallback_filename = os.path.basename(filename)
            print(f"Salvando como fallback em: {fallback_filename}")
            
            with pd.ExcelWriter(fallback_filename, engine='openpyxl') as writer:
                df_sorted.to_excel(writer, sheet_name='Todos_Resultados', index=False)
                df_sorted.head(10).to_excel(writer, sheet_name='Top_10', index=False)
                for param in ['populacao_size', 'taxa_mutacao', 'taxa_crossover', 'tamanho_torneio']:
                    param_analysis = df.groupby(param)['fitness_medio'].agg(['mean', 'std', 'min', 'max'])
                    param_analysis.to_excel(writer, sheet_name=f'Analise_{param}')
            
            print(f"💾 Arquivo salvo em: {fallback_filename}")
            return fallback_filename

def executar_teste_rapido():
    """Executa um teste rápido com poucos parâmetros"""
    print("🚀 Executando Teste Rápido de Parâmetros")
    
    optimizer = ParameterOptimizer()
    
    melhor_config = optimizer.testar_parametros(
        populacao_sizes=[30, 50],
        taxas_mutacao=[0.1, 0.15],
        taxas_crossover=[0.7, 0.8],
        tamanhos_torneio=[3, 5],
        max_geracoes=100,
        execucoes_por_config=2
    )
    
    print(f"\n🏆 MELHOR CONFIGURAÇÃO ENCONTRADA:")
    print(f"   • Tamanho da População: {int(melhor_config['populacao_size'])}")
    print(f"   • Taxa de Mutação: {melhor_config['taxa_mutacao']:.3f}")
    print(f"   • Taxa de Crossover: {melhor_config['taxa_crossover']:.3f}")
    print(f"   • Tamanho do Torneio: {int(melhor_config['tamanho_torneio'])}")
    print(f"   • Fitness Médio: {melhor_config['fitness_medio']:.2f}")
    
    # Debug do caminho
    print(f"\n🔧 DEBUG: Diretório atual: {os.getcwd()}")
    print(f"🔧 DEBUG: Tentando salvar arquivo...")
    
    try:
        caminho_salvo = optimizer.salvar_resultados("teste_rapido_parametros.xlsx")
        print(f"✅ Arquivo salvo com sucesso em: {caminho_salvo}")
    except Exception as e:
        print(f"❌ Erro ao salvar: {e}")
    
    return melhor_config

def executar_teste_completo():
    """Executa um teste completo e detalhado"""
    print("🔬 Executando Teste Completo de Parâmetros")
    print("⚠️  Este teste pode demorar 30-60 minutos!")
    
    confirmar = input("Deseja continuar? (s/n): ")
    if confirmar.lower() != 's':
        print("Teste cancelado.")
        return None
    
    optimizer = ParameterOptimizer()
    
    melhor_config = optimizer.testar_parametros(
        populacao_sizes=[20, 30, 50, 100],
        taxas_mutacao=[0.05, 0.1, 0.15, 0.2],
        taxas_crossover=[0.6, 0.7, 0.8, 0.9],
        tamanhos_torneio=[3, 5, 7],
        max_geracoes=300,
        execucoes_por_config=5
    )
    
    optimizer.salvar_resultados("teste_completo_parametros.xlsx")
    
    return melhor_config

def testar_config_especifica(populacao_size=50, taxa_mutacao=0.1, 
                           taxa_crossover=0.8, tamanho_torneio=3, runs=5):
    """Testa uma configuração específica múltiplas vezes"""
    
    print(f"🎯 Testando configuração específica:")
    print(f"   Pop: {populacao_size}, Mut: {taxa_mutacao}, Cross: {taxa_crossover}, Tournament: {tamanho_torneio}")
    
    resultados = []
    
    for run in range(runs):
        print(f"   Execução {run+1}/{runs}...")
        
        ga = ScheduleGA()
        ga.populacao_size = populacao_size
        ga.taxa_mutacao = taxa_mutacao
        ga.taxa_crossover = taxa_crossover
        ga.tamanho_torneio = tamanho_torneio
        
        _, fitness, historico = ga.executar()
        resultados.append(fitness)
    
    print(f"\n📊 Resultados:")
    print(f"   • Fitness médio: {np.mean(resultados):.2f}")
    print(f"   • Desvio padrão: {np.std(resultados):.2f}")
    print(f"   • Melhor: {np.max(resultados):.2f}")
    print(f"   • Pior: {np.min(resultados):.2f}")
    
    return resultados

# Execução principal
if __name__ == "__main__":
    print("🔧 OTIMIZADOR DE PARÂMETROS DO ALGORITMO GENÉTICO")
    print("="*60)
    print("Opções disponíveis:")
    print("1. Teste rápido (5-10 minutos)")
    print("2. Teste completo (30-60 minutos)")
    print("3. Testar configuração específica")
    
    opcao = input("\nEscolha uma opção (1-3): ")
    
    if opcao == "1":
        melhor = executar_teste_rapido()
    elif opcao == "2":
        melhor = executar_teste_completo()
    elif opcao == "3":
        resultados = testar_config_especifica()
    else:
        print("Opção inválida!")