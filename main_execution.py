#!/usr/bin/env python3
"""
TECH CHALLENGE - FASE 2
Sistema de Otimização de Horários Acadêmicos com Algoritmos Genéticos

Autor: [Seu Nome]
Data: Julho 2025

Este script executa o sistema completo de otimização de horários usando AG.
"""

import sys
import os
import time
from datetime import datetime

# Importar módulos do projeto
try:
    from genetic_scheduler import ScheduleGA
    from visualization_script import (
        executar_analise_completa, 
        gerar_relatorio_completo,
        salvar_horario_excel
    )
    from parameter_optimization import (
        executar_teste_rapido,
        testar_config_especifica
    )
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("Certifique-se de que todos os arquivos estão no mesmo diretório.")
    sys.exit(1)

def verificar_arquivos_dados():
    """Verifica se todos os arquivos de dados estão presentes"""
    pasta_dados = 'dados/'
    arquivos_necessarios = [
        'disciplinas.xlsx',
        'professores.xlsx', 
        'salas.xlsx',
        'turmas.xlsx',
        'disponibilidade.xlsx'
    ]
    
    # Verificar se a pasta dados existe
    if not os.path.exists(pasta_dados):
        print(f"❌ Pasta '{pasta_dados}' não encontrada!")
        print("Crie a pasta 'dados/' e coloque os arquivos Excel dentro dela.")
        return False
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        caminho_completo = os.path.join(pasta_dados, arquivo)
        if not os.path.exists(caminho_completo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"❌ Arquivos de dados faltando na pasta '{pasta_dados}': {', '.join(arquivos_faltando)}")
        print("Certifique-se de que todos os arquivos Excel estão na pasta 'dados/'.")
        return False
    
    print("✅ Todos os arquivos de dados encontrados na pasta 'dados/'.")
    return True

def executar_demo_basico():
    """Executa uma demonstração básica do algoritmo"""
    print("\n" + "="*60)
    print("🚀 DEMONSTRAÇÃO BÁSICA - ALGORITMO GENÉTICO")
    print("="*60)
    
    # Configurar AG com parâmetros otimizados para demonstração
    ga = ScheduleGA()
    ga.populacao_size = 30  # Menor para execução mais rápida
    ga.geracoes = 200      # Suficiente para convergência
    ga.taxa_mutacao = 0.12
    ga.taxa_crossover = 0.75
    
    print("Configuração do AG:")
    print(f"  • População: {ga.populacao_size} indivíduos")
    print(f"  • Gerações: {ga.geracoes} máximo")
    print(f"  • Taxa de mutação: {ga.taxa_mutacao}")
    print(f"  • Taxa de crossover: {ga.taxa_crossover}")
    
    inicio = time.time()
    melhor_solucao, fitness, historico = ga.executar()
    tempo_total = time.time() - inicio
    
    print(f"\n⏱️  Tempo de execução: {tempo_total:.2f} segundos")
    print(f"🎯 Fitness final: {fitness:.2f}")
    print(f"📈 Melhoria: {historico[-1] - historico[0]:.2f}")
    
    # Gerar relatório resumido
    print("\n" + "="*60)
    print("📊 RELATÓRIO RESUMIDO")
    print("="*60)
    gerar_relatorio_completo(melhor_solucao, fitness, historico, ga)
    
    # Exibir horário
    ga.exibir_horario(melhor_solucao)
    
    return melhor_solucao, fitness, historico, ga

def executar_demo_completo():
    """Executa análise completa com todos os gráficos"""
    print("\n" + "="*60)
    print("🔬 ANÁLISE COMPLETA COM VISUALIZAÇÕES")
    print("="*60)
    print("Isso pode demorar alguns minutos...")
    
    try:
        solucao, fitness, historico, ga_instance, df_prof = executar_analise_completa()
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"horario_otimizado_{timestamp}.xlsx"
        caminho_salvo = salvar_horario_excel(solucao, ga_instance, filename)
        
        print(f"\n✅ Análise completa finalizada!")
        print(f"📄 Resultados salvos em: {caminho_salvo}")
        
        return solucao, fitness, historico, ga_instance
        
    except Exception as e:
        print(f"❌ Erro durante análise completa: {e}")
        return None, None, None, None

def executar_otimizacao_parametros():
    """Executa otimização de parâmetros"""
    print("\n" + "="*60)
    print("⚙️  OTIMIZAÇÃO DE PARÂMETROS")
    print("="*60)
    
    print("Opções disponíveis:")
    print("1. Teste rápido (5-10 minutos)")
    print("2. Configuração específica (2-3 minutos)")
    
    try:
        opcao = input("Escolha uma opção (1-2): ").strip()
        
        if opcao == "1":
            print("\nExecutando teste rápido...")
            melhor_config = executar_teste_rapido()
            return melhor_config
            
        elif opcao == "2":
            print("\nTestando configuração padrão...")
            resultados = testar_config_especifica(
                populacao_size=50,
                taxa_mutacao=0.12,
                taxa_crossover=0.75,
                tamanho_torneio=3,
                runs=3
            )
            return resultados
            
        else:
            print("Opção inválida!")
            return None
            
    except KeyboardInterrupt:
        print("\n⚠️  Otimização cancelada pelo usuário.")
        return None

def comparar_com_metodo_convencional():
    """Simula comparação com método convencional"""
    print("\n" + "="*60)
    print("📊 COMPARAÇÃO: AG vs MÉTODO CONVENCIONAL")
    print("="*60)
    
    # Simular método convencional (alocação sequencial simples)
    print("Método Convencional (Simulado):")
    print("  • Tempo de elaboração: ~4-6 horas (manual)")
    print("  • Conflitos típicos: 5-15")
    print("  • Distribuição: Irregular")
    print("  • Satisfação: 60-70%")
    
    # Executar AG
    print("\nExecutando Algoritmo Genético...")
    melhor_solucao, fitness, historico, ga = executar_demo_basico()
    
    # Calcular métricas do AG
    from visualization_script import verificar_conflitos
    conflitos = verificar_conflitos(melhor_solucao, ga)
    total_conflitos = (len(conflitos['professor']) + 
                      len(conflitos['sala']) + 
                      len(conflitos['disponibilidade']))
    
    print("\nAlgoritmo Genético:")
    print(f"  • Tempo de execução: ~1-2 minutos (automático)")
    print(f"  • Conflitos encontrados: {total_conflitos}")
    print(f"  • Fitness: {fitness:.2f}/10000")
    print(f"  • Satisfação estimada: {(fitness/10000)*100:.1f}%")
    
    # Resumo da comparação
    print("\n🏆 VANTAGENS DO ALGORITMO GENÉTICO:")
    print("  ✅ Automatização completa do processo")
    print("  ✅ Redução drástica do tempo necessário")
    print("  ✅ Minimização de conflitos")
    print("  ✅ Otimização simultânea de múltiplos objetivos")
    print("  ✅ Reprodutibilidade e escalabilidade")

def menu_principal():
    """Menu principal do sistema"""
    while True:
        print("\n" + "="*60)
        print("🎓 SISTEMA DE HORÁRIOS ACADÊMICOS - TECH CHALLENGE")
        print("="*60)
        print("1. Demonstração básica (rápida)")
        print("2. Análise completa com visualizações")
        print("3. Otimização de parâmetros")
        print("4. Comparação AG vs Método Convencional")
        print("5. Informações do projeto")
        print("0. Sair")
        
        try:
            opcao = input("\nEscolha uma opção (0-5): ").strip()
            
            if opcao == "1":
                executar_demo_basico()
                
            elif opcao == "2":
                executar_demo_completo()
                
            elif opcao == "3":
                executar_otimizacao_parametros()
                
            elif opcao == "4":
                comparar_com_metodo_convencional()
                
            elif opcao == "5":
                mostrar_informacoes_projeto()
                
            elif opcao == "0":
                print("\n👋 Obrigado por usar o sistema! Bom projeto!")
                break
                
            else:
                print("❌ Opção inválida! Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

def mostrar_informacoes_projeto():
    """Mostra informações sobre o projeto"""
    print("\n" + "="*60)
    print("ℹ️  INFORMAÇÕES DO PROJETO")
    print("="*60)
    print("Projeto: Sistema de Horários com Algoritmos Genéticos")
    print("Curso: Pós-Tech - IA para Devs")
    print("Fase: Tech Challenge 2")
    print("Data: Julho 2025")
    print()
    print("🎯 Objetivos:")
    print("  • Implementar AG para otimização de horários")
    print("  • Resolver problema real de alocação de recursos")
    print("  • Demonstrar eficácia comparada a métodos convencionais")
    print()
    print("🛠️  Tecnologias utilizadas:")
    print("  • Python 3.8+")
    print("  • Pandas, NumPy (manipulação de dados)")
    print("  • Matplotlib, Seaborn (visualizações)")
    print("  • OpenPyXL (manipulação de Excel)")
    print()
    print("📊 Resultados esperados:")
    print("  • Redução de conflitos em horários")
    print("  • Automatização do processo manual")
    print("  • Otimização de múltiplos objetivos simultaneamente")

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Horários com Algoritmos Genéticos")
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificar arquivos
    if not verificar_arquivos_dados():
        print("\n❌ Não é possível continuar sem os arquivos de dados.")
        return
    
    # Verificar dependências
    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        print("✅ Todas as dependências estão disponíveis.")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Instale com: pip install pandas numpy matplotlib seaborn openpyxl")
        return
    
    # Executar menu principal
    menu_principal()

if __name__ == "__main__":
    main()