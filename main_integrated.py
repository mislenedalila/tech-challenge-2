import sys
import os
import time
from datetime import datetime

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = {
        'pandas': 'pd',
        'numpy': 'np', 
        'matplotlib.pyplot': 'plt',
        'seaborn': 'sns'
    }
    
    faltando = []
    for dep, alias in dependencias.items():
        try:
            __import__(dep.split('.')[0])
        except ImportError:
            faltando.append(dep.split('.')[0])
    
    if faltando:
        print(f"❌ Dependências faltando: {', '.join(faltando)}")
        print("Instale com: pip install pandas numpy matplotlib seaborn openpyxl")
        return False
    
    print("✅ Todas as dependências estão disponíveis.")
    return True

def verificar_arquivos_dados():
    """Verifica se todos os arquivos de dados estão presentes"""
    pasta_dados = 'dados'
    arquivos_necessarios = [
        'disciplinas.xlsx',
        'professores.xlsx', 
        'salas.xlsx',
        'turmas.xlsx',
        'disponibilidade.xlsx'
    ]
    
    if not os.path.exists(pasta_dados):
        print(f"❌ Pasta '{pasta_dados}/' não encontrada!")
        print("Crie a pasta 'dados/' e coloque os arquivos Excel dentro dela.")
        return False
    
    arquivos_faltando = []
    for arquivo in arquivos_necessarios:
        caminho_completo = os.path.join(pasta_dados, arquivo)
        if not os.path.exists(caminho_completo):
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"❌ Arquivos faltando na pasta '{pasta_dados}/': {', '.join(arquivos_faltando)}")
        return False
    
    print("✅ Todos os arquivos de dados encontrados.")
    return True

def executar_v1_penalizacao():
    """Executa versão V1 - Penalização com Lista"""
    print("\n" + "="*60)
    print("🔸 EXECUTANDO V1 - PENALIZAÇÃO COM LISTA DE EVENTOS")
    print("="*60)
    
    try:
        from genetic_scheduler import ScheduleGA
        
        print("Configurando algoritmo...")
        ga = ScheduleGA()
        ga.populacao_size = 50
        ga.geracoes = 300
        ga.taxa_mutacao = 0.12
        ga.taxa_crossover = 0.8
        
        print("Parâmetros:")
        print(f"  • População: {ga.populacao_size}")
        print(f"  • Gerações: {ga.geracoes}")
        print(f"  • Mutação: {ga.taxa_mutacao}")
        print(f"  • Crossover: {ga.taxa_crossover}")
        
        inicio = time.time()
        melhor_solucao, fitness, historico = ga.executar()
        tempo_total = time.time() - inicio
        
        print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
        print(f"🎯 Fitness final: {fitness:.2f}")
        
        # Exibir solução
        ga.exibir_horario(melhor_solucao)
        
        # Salvar resultado
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar pasta resultados se não existir
        if not os.path.exists('resultados'):
            os.makedirs('resultados')
        
        # Importar função de salvamento
        from visualization_script import salvar_horario_excel
        filename = f"v1_penalizacao_{timestamp}.xlsx"
        caminho_salvo = salvar_horario_excel(melhor_solucao, ga, filename)
        
        print(f"💾 Resultado V1 salvo em: {caminho_salvo}")
        
        return melhor_solucao, fitness, historico, ga
        
    except ImportError as e:
        print(f"❌ Erro ao importar V1: {e}")
        print("Certifique-se de que o arquivo 'genetic_scheduler.py' está presente.")
        return None
    except Exception as e:
        print(f"❌ Erro durante execução V1: {e}")
        return None

def executar_v2_pontuacao():
    """Executa versão V2 - Pontuação com Agenda"""
    print("\n" + "="*60)
    print("🔹 EXECUTANDO V2 - PONTUAÇÃO COM AGENDA (MATRIZ)")
    print("="*60)
    
    try:
        from genetic_scheduler_v2 import ScheduleGA_V2
        
        print("Configurando algoritmo...")
        ga = ScheduleGA_V2()
        ga.populacao_size = 50
        ga.geracoes = 300
        ga.taxa_mutacao = 0.15
        ga.taxa_crossover = 0.8
        
        print("Parâmetros:")
        print(f"  • População: {ga.populacao_size}")
        print(f"  • Gerações: {ga.geracoes}")
        print(f"  • Mutação: {ga.taxa_mutacao}")
        print(f"  • Crossover: {ga.taxa_crossover}")
        
        print("\nPesos de pontuação:")
        for criterio, peso in ga.pesos.items():
            print(f"  • {criterio}: {peso}")
        
        inicio = time.time()
        melhor_agenda, fitness, historico = ga.executar()
        tempo_total = time.time() - inicio
        
        print(f"\n⏱️  Tempo total: {tempo_total:.2f} segundos")
        print(f"🎯 Fitness final: {fitness:.0f} pontos")
        
        # Exibir solução
        ga.exibir_agenda(melhor_agenda)
        
        # Salvar resultado usando utilitários V2
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar pasta resultados se não existir
        if not os.path.exists('resultados'):
            os.makedirs('resultados')
        
        # Salvar usando função específica para V2
        try:
            from utils_v2 import salvar_agenda_excel, gerar_relatorio_agenda_v2
            filename = f"v2_pontuacao_{timestamp}.xlsx"
            caminho_salvo = salvar_agenda_excel(melhor_agenda, ga, filename)
            
            # Gerar relatório detalhado
            print("\n📊 Gerando relatório detalhado...")
            metricas = gerar_relatorio_agenda_v2(melhor_agenda, fitness, historico, ga)
            
            print(f"💾 Resultado V2 salvo em: {caminho_salvo}")
            print(f"📈 Score de qualidade: {metricas['score_geral']:.1%}")
            
        except ImportError:
            print("⚠️  Utilitários V2 não encontrados. Resultado não foi salvo em Excel.")
            print("💾 Resultado V2 exibido apenas na tela.")
        
        return melhor_agenda, fitness, historico, ga
        
    except ImportError as e:
        print(f"❌ Erro ao importar V2: {e}")
        print("Certifique-se de que o arquivo 'genetic_scheduler_v2.py' está presente.")
        return None
    except Exception as e:
        print(f"❌ Erro durante execução V2: {e}")
        return None

def executar_comparacao():
    """Executa comparação entre V1 e V2"""
    print("\n" + "="*60)
    print("🔬 EXECUTANDO COMPARAÇÃO ENTRE ABORDAGENS")
    print("="*60)
    
    try:
        from comparison_v1_v2 import executar_comparacao_completa
        return executar_comparacao_completa()
    except ImportError as e:
        print(f"❌ Erro ao importar comparação: {e}")
        print("Certifique-se de que o arquivo 'comparison_v1_v2.py' está presente.")
        return None
    except Exception as e:
        print(f"❌ Erro durante comparação: {e}")
        return None

def executar_otimizacao_parametros():
    """Executa otimização de parâmetros"""
    print("\n" + "="*60)
    print("⚙️  EXECUTANDO OTIMIZAÇÃO DE PARÂMETROS")
    print("="*60)
    
    print("Escolha a versão para otimizar:")
    print("1. V1 - Penalização com Lista")
    print("2. V2 - Pontuação com Agenda")
    print("3. Comparar parâmetros de ambas")
    
    try:
        opcao = input("Opção (1-3): ").strip()
        
        if opcao == "1":
            print("Otimizando parâmetros para V1 - Penalização...")
            from parameter_optimization import executar_teste_rapido_v1
            return executar_teste_rapido_v1()
            
        elif opcao == "2":
            print("Otimizando parâmetros para V2 - Pontuação...")
            from parameter_optimization import executar_teste_rapido_v2
            return executar_teste_rapido_v2()
            
        elif opcao == "3":
            print("Comparando parâmetros entre V1 e V2...")
            from parameter_optimization import comparar_parametros_v1_v2
            return comparar_parametros_v1_v2()
            
        else:
            print("❌ Opção inválida!")
            return None
            
    except ImportError as e:
        print(f"❌ Erro ao importar otimização: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro durante otimização: {e}")
        return None

def menu_principal():
    """Menu principal do sistema integrado"""
    while True:
        print("\n" + "="*80)
        print("🎓 SISTEMA INTEGRADO - HORÁRIOS ACADÊMICOS COM AG")
        print("="*80)
        print("Escolha a abordagem ou função desejada:")
        print()
        print("📋 EXECUÇÃO DAS ABORDAGENS:")
        print("1. V1 - Penalização com Lista de Eventos")
        print("2. V2 - Pontuação com Agenda (Matriz)")
        print("3. Comparação entre V1 e V2")
        print()
        print("⚙️  FERRAMENTAS AVANÇADAS:")
        print("4. Otimização de parâmetros (V1, V2 ou Comparação)")
        print("5. Análise completa com visualizações (V1)")
        print("6. Análise completa com visualizações (V2)")
        print("7. Análise detalhada de agenda (V2)")
        print()
        print("0. Sair")
        
        try:
            opcao = input("\nEscolha uma opção (0-7): ").strip()
            
            if opcao == "1":
                resultado = executar_v1_penalizacao()
                if resultado:
                    print("\n✅ V1 executado com sucesso!")
                    
            elif opcao == "2":
                resultado = executar_v2_pontuacao()
                if resultado:
                    print("\n✅ V2 executado com sucesso!")
                    
            elif opcao == "3":
                resultado = executar_comparacao()
                if resultado:
                    print("\n✅ Comparação executada com sucesso!")
                    
            elif opcao == "4":
                resultado = executar_otimizacao_parametros()
                if resultado:
                    print("\n✅ Otimização executada com sucesso!")
                    
            elif opcao == "5":
                try:
                    from visualization_script import executar_analise_completa
                    print("\n🔬 Executando análise completa V1...")
                    resultado = executar_analise_completa()
                    if resultado:
                        print("\n✅ Análise completa V1 executada com sucesso!")
                except ImportError:
                    print("❌ Arquivo 'visualization_script.py' não encontrado.")
                except Exception as e:
                    print(f"❌ Erro durante análise V1: {e}")
                    
            elif opcao == "6":
                try:
                    from visualization_v2 import executar_analise_completa_v2
                    print("\n🔬 Executando análise completa V2...")
                    resultado = executar_analise_completa_v2()
                    if resultado:
                        print("\n✅ Análise completa V2 executada com sucesso!")
                except ImportError:
                    print("❌ Arquivo 'visualization_v2.py' não encontrado.")
                except Exception as e:
                    print(f"❌ Erro durante análise V2: {e}")
                    
            elif opcao == "7":
                try:
                    print("\n🔬 Executando análise detalhada V2...")
                    from genetic_scheduler_v2 import ScheduleGA_V2
                    from utils_v2 import gerar_relatorio_agenda_v2, salvar_agenda_excel
                    
                    ga_v2 = ScheduleGA_V2()
                    agenda, fitness, historico = ga_v2.executar()
                    
                    # Gerar relatório
                    metricas = gerar_relatorio_agenda_v2(agenda, fitness, historico, ga_v2)
                    
                    # Salvar resultado
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"analise_detalhada_v2_{timestamp}.xlsx"
                    caminho_salvo = salvar_agenda_excel(agenda, ga_v2, filename)
                    
                    print(f"\n✅ Análise V2 concluída!")
                    print(f"📄 Resultados salvos em: {caminho_salvo}")
                    print(f"📊 Score de qualidade: {metricas['score_geral']:.1%}")
                    
                except ImportError as e:
                    print(f"❌ Erro de importação: {e}")
                except Exception as e:
                    print(f"❌ Erro durante análise V2: {e}")
                
            elif opcao == "0":
                print("\n👋 Obrigado por usar o sistema!")
                break
                
            else:
                print("❌ Opção inválida! Tente novamente.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

def main():
    """Função principal do sistema integrado"""
    print("🚀 SISTEMA INTEGRADO - HORÁRIOS ACADÊMICOS COM AG")
    print("="*60)
    print(f"📅 Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Verificações iniciais
    print("\n🔍 Verificando sistema...")
    
    if not verificar_dependencias():
        print("❌ Sistema não pode continuar sem as dependências.")
        return 1
    
    if not verificar_arquivos_dados():
        print("❌ Sistema não pode continuar sem os arquivos de dados.")
        print("\n📁 Estrutura esperada:")
        print("   projeto/")
        print("   ├── dados/")
        print("   │   ├── disciplinas.xlsx")
        print("   │   ├── professores.xlsx")
        print("   │   ├── salas.xlsx")
        print("   │   ├── turmas.xlsx")
        print("   │   └── disponibilidade.xlsx")
        print("   ├── genetic_scheduler.py")
        print("   ├── genetic_scheduler_v2.py")
        print("   └── [outros arquivos .py]")
        return 1
    
    # Verificar módulos principais
    modulos_principais = [
        'genetic_scheduler.py',
        'genetic_scheduler_v2.py'
    ]
    
    modulos_faltando = []
    for modulo in modulos_principais:
        if not os.path.exists(modulo):
            modulos_faltando.append(modulo)
    
    if modulos_faltando:
        print(f"⚠️  Módulos principais faltando: {', '.join(modulos_faltando)}")
        print("Algumas funcionalidades podem não estar disponíveis.")
    else:
        print("✅ Todos os módulos principais encontrados.")
    
    # Criar pasta de resultados se não existir
    if not os.path.exists('resultados'):
        os.makedirs('resultados')
        print("📁 Pasta 'resultados/' criada.")
    
    print("\n🎯 Sistema pronto! Escolha uma das opções no menu.")
    
    # Executar menu principal
    menu_principal()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)