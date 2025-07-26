import pandas as pd
import os
import sys
from collections import defaultdict

# Adicione o caminho do seu módulo de validação se necessário
# sys.path.append('caminho/para/seu/modulo')

def teste_rapido_validacao():
    """🧪 Teste rápido da validação de dados"""
    
    print("🧪 TESTE RÁPIDO - VALIDAÇÃO DE DADOS")
    print("=" * 50)
    
    try:
        # Verifica se pasta dados existe
        if not os.path.exists('dados'):
            print("❌ Pasta 'dados' não encontrada!")
            print("💡 Crie a pasta e coloque os arquivos Excel necessários")
            return False
        
        # Lista arquivos na pasta dados
        arquivos_necessarios = [
            'disciplinas.xlsx',
            'professores.xlsx', 
            'salas.xlsx',
            'turmas.xlsx',
            'disponibilidadeProfessor.xlsx'
        ]
        
        print("📁 Verificando arquivos necessários...")
        arquivos_faltando = []
        
        for arquivo in arquivos_necessarios:
            caminho = os.path.join('dados', arquivo)
            if os.path.exists(caminho):
                print(f"   ✅ {arquivo}")
            else:
                print(f"   ❌ {arquivo} - FALTANDO")
                arquivos_faltando.append(arquivo)
        
        if arquivos_faltando:
            print(f"\n❌ Arquivos faltando: {arquivos_faltando}")
            return False
        
        # Carrega dados
        print(f"\n📂 Carregando dados...")
        disciplinas = pd.read_excel('dados/disciplinas.xlsx')
        professores = pd.read_excel('dados/professores.xlsx')
        salas = pd.read_excel('dados/salas.xlsx')
        turmas = pd.read_excel('dados/turmas.xlsx')
        disponibilidade = pd.read_excel('dados/disponibilidadeProfessor.xlsx')
        
        # Estatísticas básicas
        print(f"\n📊 ESTATÍSTICAS BÁSICAS:")
        print(f"   📚 Disciplinas: {len(disciplinas)}")
        print(f"   👨‍🏫 Professores: {len(professores)}")
        print(f"   🏫 Salas: {len(salas)}")
        print(f"   🎓 Turmas: {len(turmas)}")
        print(f"   🕒 Registros disponibilidade: {len(disponibilidade)}")
        
        # Verifica colunas essenciais
        print(f"\n🔍 VERIFICANDO ESTRUTURA DOS DADOS:")
        
        # Disciplinas
        colunas_disciplinas = ['codigo_disciplina', 'nome_disciplina', 'numero_aulas_semanais']
        colunas_faltando = set(colunas_disciplinas) - set(disciplinas.columns)
        if colunas_faltando:
            print(f"   ❌ Disciplinas - faltam colunas: {list(colunas_faltando)}")
        else:
            print(f"   ✅ Disciplinas - estrutura OK")
        
        # Professores
        colunas_professores = ['id_professor', 'nome_professor']
        colunas_faltando = set(colunas_professores) - set(professores.columns)
        if colunas_faltando:
            print(f"   ❌ Professores - faltam colunas: {list(colunas_faltando)}")
        else:
            print(f"   ✅ Professores - estrutura OK")
        
        # Análise rápida de capacidade
        print(f"\n⚖️ ANÁLISE RÁPIDA DE CAPACIDADE:")
        
        if 'numero_aulas_semanais' in disciplinas.columns:
            total_aulas_por_turma = disciplinas['numero_aulas_semanais'].sum()
            total_aulas_necessarias = total_aulas_por_turma * len(turmas)
            
            # Assumindo horários 18:50-22:20 (4 slots) x 5 dias x N salas
            slots_por_semana = 4 * 5 * len(salas)
            ocupacao_percent = (total_aulas_necessarias / slots_por_semana) * 100
            
            print(f"   📖 Aulas por turma: {total_aulas_por_turma}")
            print(f"   📖 Total aulas necessárias: {total_aulas_necessarias}")
            print(f"   🕒 Slots disponíveis/semana: {slots_por_semana}")
            print(f"   📊 Ocupação máxima: {ocupacao_percent:.1f}%")
            
            if ocupacao_percent > 100:
                print(f"   ❌ PROBLEMA: Ocupação > 100% - IMPOSSÍVEL!")
            elif ocupacao_percent > 90:
                print(f"   ⚠️ ATENÇÃO: Ocupação muito alta - DIFÍCIL!")
            elif ocupacao_percent > 75:
                print(f"   ⚠️ CUIDADO: Ocupação alta - DESAFIADOR!")
            else:
                print(f"   ✅ Ocupação adequada - VIÁVEL!")
        
        # Análise de habilitações (se coluna existir)
        print(f"\n👨‍🏫 ANÁLISE DE HABILITAÇÕES:")
        
        if 'habilitacoes' in professores.columns:
            disciplinas_sem_professor = []
            
            for _, disciplina in disciplinas.iterrows():
                nome_disc = disciplina['nome_disciplina']
                tem_professor = False
                
                for _, professor in professores.iterrows():
                    habilitacoes = str(professor.get('habilitacoes', '')).split(';')
                    habilitacoes = [h.strip() for h in habilitacoes if h.strip()]
                    
                    if nome_disc in habilitacoes:
                        tem_professor = True
                        break
                
                if not tem_professor:
                    disciplinas_sem_professor.append(nome_disc)
            
            if disciplinas_sem_professor:
                print(f"   ❌ PROBLEMA: {len(disciplinas_sem_professor)} disciplinas sem professor habilitado:")
                for disc in disciplinas_sem_professor[:5]:  # Mostra só as primeiras 5
                    print(f"      - {disc}")
                if len(disciplinas_sem_professor) > 5:
                    print(f"      ... e mais {len(disciplinas_sem_professor) - 5}")
            else:
                print(f"   ✅ Todas as disciplinas têm professores habilitados!")
        else:
            print(f"   ⚠️ Coluna 'habilitacoes' não encontrada - não foi possível validar")
        
        # Análise de disponibilidade
        print(f"\n🕒 ANÁLISE DE DISPONIBILIDADE:")
        
        if 'disponivel' in disponibilidade.columns:
            total_registros = len(disponibilidade)
            registros_disponiveis = len(disponibilidade[disponibilidade['disponivel'] == True])
            percent_disponivel = (registros_disponiveis / total_registros) * 100
            
            print(f"   📊 {registros_disponiveis}/{total_registros} registros disponíveis ({percent_disponivel:.1f}%)")
            
            if percent_disponivel < 30:
                print(f"   ❌ PROBLEMA: Pouquíssima disponibilidade!")
            elif percent_disponivel < 50:
                print(f"   ⚠️ ATENÇÃO: Baixa disponibilidade!")
            else:
                print(f"   ✅ Disponibilidade adequada!")
        
        print(f"\n" + "=" * 50)
        print(f"🎯 RESUMO DO TESTE:")
        print(f"   📁 Arquivos: OK")
        print(f"   📊 Estrutura: Verificada")
        print(f"   ⚖️ Capacidade: Analisada")
        print(f"   👨‍🏫 Habilitações: Verificadas")
        print(f"   🕒 Disponibilidade: Analisada")
        
        print(f"\n💡 PRÓXIMOS PASSOS:")
        print(f"   1. Execute o algoritmo genético completo")
        print(f"   2. Se fitness for alto, use a validação detalhada")
        print(f"   3. Ajuste dados conforme recomendações")
        
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def verificar_dados_especificos():
    """🔎 Verificações específicas mais detalhadas"""
    
    print(f"\n🔎 VERIFICAÇÕES ESPECÍFICAS DETALHADAS")
    print("=" * 50)
    
    try:
        # Carrega dados
        disciplinas = pd.read_excel('dados/disciplinas.xlsx')
        professores = pd.read_excel('dados/professores.xlsx')
        
        # Mostra algumas disciplinas
        print(f"📚 SAMPLE DAS DISCIPLINAS:")
        for i, row in disciplinas.head(3).iterrows():
            print(f"   {row.get('codigo_disciplina', 'N/A')}: {row.get('nome_disciplina', 'N/A')} ({row.get('numero_aulas_semanais', 'N/A')} aulas)")
        
        # Mostra alguns professores
        print(f"\n👨‍🏫 SAMPLE DOS PROFESSORES:")
        for i, row in professores.head(3).iterrows():
            habilitacoes = str(row.get('habilitacoes', 'N/A'))[:50] + "..." if len(str(row.get('habilitacoes', ''))) > 50 else str(row.get('habilitacoes', 'N/A'))
            print(f"   {row.get('id_professor', 'N/A')}: {row.get('nome_professor', 'N/A')}")
            print(f"      Habilitações: {habilitacoes}")
        
        # Detecta possíveis problemas específicos
        print(f"\n🚨 DETECÇÃO DE PROBLEMAS ESPECÍFICOS:")
        
        # Problema 1: Disciplinas com muitas aulas
        disciplinas_muitas_aulas = disciplinas[disciplinas['numero_aulas_semanais'] >= 4]
        if not disciplinas_muitas_aulas.empty:
            print(f"   ⚠️ {len(disciplinas_muitas_aulas)} disciplinas com 4+ aulas por semana:")
            for _, disc in disciplinas_muitas_aulas.iterrows():
                print(f"      - {disc['nome_disciplina']}: {disc['numero_aulas_semanais']} aulas")
        
        # Problema 2: Valores nulos críticos
        print(f"\n🔍 VERIFICAÇÃO DE VALORES NULOS:")
        for col in ['numero_aulas_semanais']:
            if col in disciplinas.columns:
                nulos = disciplinas[col].isnull().sum()
                if nulos > 0:
                    print(f"   ❌ {nulos} valores nulos em disciplinas.{col}")
                else:
                    print(f"   ✅ disciplinas.{col} sem valores nulos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação específica: {e}")
        return False

def main():
    """🚀 Função principal do teste"""
    
    print("🧪 SCRIPT DE TESTE - VALIDAÇÃO DE DADOS")
    print("Tech Challenge - FIAP")
    print("=" * 60)
    
    # Teste básico
    if teste_rapido_validacao():
        print(f"\n✅ Teste básico passou!")
        
        # Teste específico
        verificar_dados_especificos()
        
        print(f"\n🎉 VALIDAÇÃO CONCLUÍDA!")
        print(f"💡 Execute agora o algoritmo genético completo para ver os resultados")
        
    else:
        print(f"\n❌ Teste básico falhou!")
        print(f"🔧 Corrija os problemas identificados antes de continuar")

if __name__ == "__main__":
    main()