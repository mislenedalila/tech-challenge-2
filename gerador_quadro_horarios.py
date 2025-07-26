#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📅 GERADOR DE QUADRO DE HORÁRIOS VISUAL
Tech Challenge - FIAP

Gera quadros de horário em PNG/PDF a partir dos resultados do algoritmo genético.
Suporta diferentes formatos e estilos de visualização.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import seaborn as sns
from datetime import datetime
import os

class GeradorQuadroHorarios:
    """📅 Gerador de quadros de horário visual"""
    
    def __init__(self):
        self.horarios = ['18:50', '19:40', '20:30', '21:20']
        self.dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        
        # Cores para disciplinas (palette vibrante)
        self.cores_disciplinas = {
            'CULTURA E SOCIEDADE': '#FF6B6B',
            'ALGORITMOS E TÉCNICAS DE PROGRAMAÇÃO II': '#4ECDC4',
            'ORGANIZAÇÃO E ARQUITETURA DE COMPUTADORES': '#45B7D1',
            'SISTEMAS DE INFORMAÇÃO': '#96CEB4',
            'CÁLCULO DIFERENCIAL E INTEGRAL': '#FFEAA7',
            'PROJETO INTEGRADOR I': '#DDA0DD',
            'ESTRUTURAS DE DADOS E ALGORITMOS': '#98D8C8',
            'SISTEMAS OPERACIONAIS II': '#F7DC6F',
            'SISTEMAS DE BANCO DE DADOS': '#BB8FCE',
            'ENGENHARIA DE SOFTWARE II': '#85C1E9',
            'TÓPICOS ESPECIAIS I': '#F8C471',
            'PROJETO INTEGRADOR III': '#82E0AA'
        }
        
        # Estilo padrão com fontes compatíveis
        plt.style.use('default')
        
        # Configurar fontes compatíveis com diferentes sistemas
        try:
            # Tentar usar fontes específicas por sistema
            import platform
            system = platform.system().lower()
            
            if system == 'windows':
                plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans', 'sans-serif']
            elif system == 'darwin':  # macOS
                plt.rcParams['font.family'] = ['Helvetica', 'Arial', 'DejaVu Sans', 'sans-serif']
            else:  # Linux e outros
                plt.rcParams['font.family'] = ['DejaVu Sans', 'Liberation Sans', 'sans-serif']
        except:
            # Fallback para fonte padrão do sistema
            plt.rcParams['font.family'] = 'sans-serif'
        
        plt.rcParams['font.size'] = 8
    
    def carregar_dados_exemplo(self):
        """📊 Cria dados de exemplo baseados na estrutura real"""
        dados_exemplo = [
            {'dia': 'Segunda', 'horario': '18:50', 'turma': 'SIN-2A-N', 'disciplina': 'CULTURA E SOCIEDADE', 'professor': 'ALTAMIR', 'sala': '201'},
            {'dia': 'Segunda', 'horario': '19:40', 'turma': 'SIN-2A-N', 'disciplina': 'ALGORITMOS E TÉCNICAS DE PROGRAMAÇÃO II', 'professor': 'SANDRO', 'sala': '201'},
            {'dia': 'Segunda', 'horario': '20:30', 'turma': 'SIN-2A-N', 'disciplina': 'ORGANIZAÇÃO E ARQUITETURA DE COMPUTADORES', 'professor': 'LILIS', 'sala': '201'},
            {'dia': 'Segunda', 'horario': '21:20', 'turma': 'SIN-2A-N', 'disciplina': 'SISTEMAS DE INFORMAÇÃO', 'professor': 'BARROS', 'sala': '201'},
            
            {'dia': 'Terça', 'horario': '18:50', 'turma': 'SIN-2A-N', 'disciplina': 'CÁLCULO DIFERENCIAL E INTEGRAL', 'professor': 'GERALDO', 'sala': '201'},
            {'dia': 'Terça', 'horario': '19:40', 'turma': 'SIN-2A-N', 'disciplina': 'PROJETO INTEGRADOR I', 'professor': 'DIANE', 'sala': '201'},
            {'dia': 'Terça', 'horario': '20:30', 'turma': 'SIN-2A-N', 'disciplina': 'CULTURA E SOCIEDADE', 'professor': 'ALTAMIR', 'sala': '201'},
            {'dia': 'Terça', 'horario': '21:20', 'turma': 'SIN-2A-N', 'disciplina': 'ALGORITMOS E TÉCNICAS DE PROGRAMAÇÃO II', 'professor': 'SANDRO', 'sala': '201'},
            
            {'dia': 'Quarta', 'horario': '18:50', 'turma': 'SIN-2A-N', 'disciplina': 'ESTRUTURAS DE DADOS E ALGORITMOS', 'professor': 'SANDRO', 'sala': '201'},
            {'dia': 'Quarta', 'horario': '19:40', 'turma': 'SIN-2A-N', 'disciplina': 'SISTEMAS OPERACIONAIS II', 'professor': 'BARROS', 'sala': '201'},
            {'dia': 'Quarta', 'horario': '20:30', 'turma': 'SIN-2A-N', 'disciplina': 'SISTEMAS DE BANCO DE DADOS', 'professor': 'ALEXANDRE', 'sala': '201'},
            {'dia': 'Quarta', 'horario': '21:20', 'turma': 'SIN-2A-N', 'disciplina': 'ENGENHARIA DE SOFTWARE II', 'professor': 'LILIS', 'sala': '201'},
            
            {'dia': 'Quinta', 'horario': '18:50', 'turma': 'SIN-2A-N', 'disciplina': 'TÓPICOS ESPECIAIS I', 'professor': 'MARINHO', 'sala': '201'},
            {'dia': 'Quinta', 'horario': '19:40', 'turma': 'SIN-2A-N', 'disciplina': 'PROJETO INTEGRADOR III', 'professor': 'DALILA', 'sala': '201'},
            {'dia': 'Quinta', 'horario': '20:30', 'turma': 'SIN-2A-N', 'disciplina': 'ORGANIZAÇÃO E ARQUITETURA DE COMPUTADORES', 'professor': 'LILIS', 'sala': '201'},
            {'dia': 'Quinta', 'horario': '21:20', 'turma': 'SIN-2A-N', 'disciplina': 'SISTEMAS DE INFORMAÇÃO', 'professor': 'BARROS', 'sala': '201'},
            
            {'dia': 'Sexta', 'horario': '18:50', 'turma': 'SIN-2A-N', 'disciplina': 'ESTRUTURAS DE DADOS E ALGORITMOS', 'professor': 'SANDRO', 'sala': '201'},
            {'dia': 'Sexta', 'horario': '19:40', 'turma': 'SIN-2A-N', 'disciplina': 'SISTEMAS DE BANCO DE DADOS', 'professor': 'ALEXANDRE', 'sala': '201'},
            {'dia': 'Sexta', 'horario': '20:30', 'turma': 'SIN-2A-N', 'disciplina': 'CÁLCULO DIFERENCIAL E INTEGRAL', 'professor': 'GERALDO', 'sala': '201'},
            {'dia': 'Sexta', 'horario': '21:20', 'turma': 'SIN-2A-N', 'disciplina': 'PROJETO INTEGRADOR I', 'professor': 'DIANE', 'sala': '201'},
        ]
        
        return pd.DataFrame(dados_exemplo)
    
    def gerar_quadro_estilo_moderno(self, df_horarios, turma=None, salvar_como='quadro_horarios_moderno.png'):
        """🎨 Gera quadro de horários estilo moderno"""
        
        # Filtrar por turma se especificado
        if turma:
            df_filtrado = df_horarios[df_horarios['turma'] == turma].copy()
            titulo = f"Horário da Turma {turma}"
        else:
            df_filtrado = df_horarios.copy()
            titulo = "Horário Geral"
        
        # Criar figura
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Configurar grid
        cell_width = 2.8
        cell_height = 1.8
        
        # Desenhar cabeçalho
        ax.text(cell_width * 2.5, cell_height * 5.5, titulo, 
                fontsize=20, fontweight='bold', ha='center',
                color='#2C3E50')
        
        ax.text(cell_width * 2.5, cell_height * 5.2, 
                f"FIAP - Sistemas de Informação - Período Noturno", 
                fontsize=12, ha='center', color='#7F8C8D')
        
        ax.text(cell_width * 2.5, cell_height * 5.0, 
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                fontsize=10, ha='center', color='#95A5A6')
        
        # Desenhar cabeçalhos dos dias
        for i, dia in enumerate(self.dias):
            rect = patches.Rectangle((i * cell_width + cell_width, cell_height * 4), 
                                   cell_width, cell_height/2, 
                                   linewidth=2, edgecolor='#34495E', 
                                   facecolor='#3498DB', alpha=0.8)
            ax.add_patch(rect)
            
            ax.text(i * cell_width + cell_width + cell_width/2, 
                   cell_height * 4 + cell_height/4,
                   dia, fontsize=12, fontweight='bold', 
                   ha='center', va='center', color='white')
        
        # Desenhar cabeçalhos dos horários
        for i, horario in enumerate(self.horarios):
            rect = patches.Rectangle((0, cell_height * (3-i)), 
                                   cell_width, cell_height, 
                                   linewidth=2, edgecolor='#34495E', 
                                   facecolor='#2980B9', alpha=0.8)
            ax.add_patch(rect)
            
            ax.text(cell_width/2, cell_height * (3-i) + cell_height/2,
                   horario, fontsize=11, fontweight='bold', 
                   ha='center', va='center', color='white')
        
        # Preencher células com aulas
        for _, aula in df_filtrado.iterrows():
            try:
                # Converter todos os valores para string de forma segura
                dia = str(aula['dia']) if pd.notna(aula['dia']) else 'Segunda'
                horario = str(aula['horario']) if pd.notna(aula['horario']) else '18:50'
                disciplina = str(aula['disciplina']) if pd.notna(aula['disciplina']) else 'DISCIPLINA'
                professor = str(aula['professor']) if pd.notna(aula['professor']) else 'PROFESSOR'
                sala = str(aula['sala']) if pd.notna(aula['sala']) else '000'
                
                dia_idx = self.dias.index(dia)
                horario_idx = self.horarios.index(horario)
                
                x = (dia_idx + 1) * cell_width
                y = cell_height * (3 - horario_idx)
                
                # Cor da disciplina
                disciplina_curta = disciplina.split(' ')[0] if disciplina else 'DISCIPLINA'
                cor = self.cores_disciplinas.get(disciplina, '#95A5A6')
                
                # Desenhar célula
                rect = patches.Rectangle((x, y), cell_width, cell_height, 
                                       linewidth=1, edgecolor='#34495E', 
                                       facecolor=cor, alpha=0.7)
                ax.add_patch(rect)
                
                # Texto da disciplina (abreviado)
                disciplina_abrev = self.abreviar_disciplina(disciplina)
                ax.text(x + cell_width/2, y + cell_height * 0.75,
                       disciplina_abrev, fontsize=9, fontweight='bold', 
                       ha='center', va='center', color='white',
                       bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.6))
                
                # Professor
                ax.text(x + cell_width/2, y + cell_height * 0.5,
                       f"Prof. {professor}", fontsize=8, 
                       ha='center', va='center', color='#2C3E50')
                
                # Sala
                ax.text(x + cell_width/2, y + cell_height * 0.25,
                       f"Sala {sala}", fontsize=8, 
                       ha='center', va='center', color='#2C3E50')
                
            except (ValueError, KeyError) as e:
                print(f"⚠️ Erro ao processar aula: {e}")
                print(f"   Dados da aula: dia={aula.get('dia', 'N/A')}, horario={aula.get('horario', 'N/A')}")
                continue
            except Exception as e:
                print(f"❌ Erro inesperado ao processar aula: {e}")
                print(f"   Tipo do erro: {type(e).__name__}")
                print(f"   Dados da aula: {aula.to_dict()}")
                continue
        
        # Configurar eixos
        ax.set_xlim(0, (len(self.dias) + 1) * cell_width)
        ax.set_ylim(0, cell_height * 5.5)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Adicionar legenda das cores
        self.adicionar_legenda_cores(ax, df_filtrado, cell_width, cell_height)
        
        plt.tight_layout()
        
        # Salvar
        if not os.path.exists('resultados'):
            os.makedirs('resultados')
        
        caminho_completo = f'resultados/{salvar_como}'
        plt.savefig(caminho_completo, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"📅 Quadro de horários salvo em: {caminho_completo}")
        
        plt.show()
        return fig
    
    def abreviar_disciplina(self, nome_completo):
        """✂️ Abrevia nome da disciplina para caber na célula"""
        
        # Converter para string se for Series ou outro tipo
        if hasattr(nome_completo, 'iloc'):
            # Se for Series, pegar o primeiro valor
            nome_completo = str(nome_completo.iloc[0]) if len(nome_completo) > 0 else str(nome_completo)
        else:
            # Converter para string de qualquer forma
            nome_completo = str(nome_completo)
        
        # Verificar se é NaN ou vazio
        if nome_completo in ['nan', 'None', ''] or pd.isna(nome_completo):
            return "DISCIPLINA"
        
        palavras = nome_completo.split()
        
        if len(palavras) <= 2:
            return nome_completo
        
        # Regras de abreviação específicas
        abreviacoes = {
            'ALGORITMOS': 'ALG',
            'TÉCNICAS': 'TÉC',
            'PROGRAMAÇÃO': 'PROG',
            'ORGANIZAÇÃO': 'ORG',
            'ARQUITETURA': 'ARQ',
            'COMPUTADORES': 'COMP',
            'SISTEMAS': 'SIST',
            'INFORMAÇÃO': 'INFO',
            'CÁLCULO': 'CALC',
            'DIFERENCIAL': 'DIF',
            'INTEGRAL': 'INT',
            'PROJETO': 'PROJ',
            'INTEGRADOR': 'INTEG',
            'EXTENSÃO': 'EXT',
            'CURRICULARIZADA': 'CURR',
            'ESTRUTURAS': 'ESTR',
            'DADOS': 'DADOS',
            'OPERACIONAIS': 'OPER',
            'BANCO': 'BD',
            'ENGENHARIA': 'ENG',
            'SOFTWARE': 'SW',
            'TÓPICOS': 'TÓP',
            'ESPECIAIS': 'ESP',
            'CULTURA': 'CULT',
            'SOCIEDADE': 'SOC'
        }
        
        palavras_abrev = []
        for palavra in palavras:
            palavra_upper = str(palavra).upper()
            if palavra_upper in abreviacoes:
                palavras_abrev.append(abreviacoes[palavra_upper])
            else:
                palavras_abrev.append(str(palavra)[:4])  # Primeiras 4 letras
        
        resultado = ' '.join(palavras_abrev)
        
        # Se ainda muito longo, pegar só as primeiras 3 palavras
        if len(resultado) > 25:
            resultado = ' '.join(palavras_abrev[:3])
        
        return resultado
    
    def adicionar_legenda_cores(self, ax, df_horarios, cell_width, cell_height):
        """🎨 Adiciona legenda das cores das disciplinas"""
        disciplinas_unicas = df_horarios['disciplina'].unique()
        
        # Posição da legenda
        x_legenda = (len(self.dias) + 1.5) * cell_width
        y_inicio = cell_height * 4
        
        ax.text(x_legenda, y_inicio + 0.3, "Legenda:", 
               fontsize=12, fontweight='bold', color='#2C3E50')
        
        for i, disciplina in enumerate(disciplinas_unicas[:8]):  # Máximo 8 para caber
            y_pos = y_inicio - (i * 0.4)
            
            cor = self.cores_disciplinas.get(disciplina, '#95A5A6')
            
            # Quadradinho colorido
            rect = patches.Rectangle((x_legenda, y_pos - 0.1), 0.2, 0.2, 
                                   facecolor=cor, alpha=0.7, edgecolor='black')
            ax.add_patch(rect)
            
            # Nome abreviado
            nome_abrev = self.abreviar_disciplina(disciplina)
            ax.text(x_legenda + 0.3, y_pos, nome_abrev, 
                   fontsize=8, va='center', color='#2C3E50')
    
    def gerar_quadro_por_turma_pdf(self, df_horarios, salvar_como='quadros_todas_turmas.pdf'):
        """📋 Gera PDF com quadro de todas as turmas"""
        turmas_unicas = sorted(df_horarios['turma'].unique())
        
        caminho_completo = f'resultados/{salvar_como}'
        
        with PdfPages(caminho_completo) as pdf:
            for turma in turmas_unicas:
                print(f"Gerando quadro para turma: {turma}")
                
                fig = self.gerar_quadro_individual_turma(df_horarios, turma)
                pdf.savefig(fig, bbox_inches='tight', dpi=300)
                plt.close(fig)
        
        print(f"📄 PDF com todas as turmas salvo em: {caminho_completo}")
    
    def gerar_quadro_individual_turma(self, df_horarios, turma):
        """📅 Gera quadro individual para uma turma"""
        df_turma = df_horarios[df_horarios['turma'] == turma].copy()
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Título
        ax.text(0.5, 0.95, f"Horário da Turma {turma}", 
                transform=ax.transAxes, fontsize=16, fontweight='bold', 
                ha='center', color='#2C3E50')
        
        ax.text(0.5, 0.92, "FIAP - Sistemas de Informação - Noturno", 
                transform=ax.transAxes, fontsize=12, ha='center', color='#7F8C8D')
        
        # Criar tabela
        tabela_data = []
        
        for horario in self.horarios:
            linha = [horario]
            for dia in self.dias:
                aula = df_turma[(df_turma['dia'] == dia) & (df_turma['horario'] == horario)]
                
                if not aula.empty:
                    aula_info = aula.iloc[0]
                    disciplina_abrev = self.abreviar_disciplina(aula_info['disciplina'])
                    celula = f"{disciplina_abrev}\nProf. {aula_info['professor']}\nSala {aula_info['sala']}"
                else:
                    celula = "---"
                
                linha.append(celula)
            
            tabela_data.append(linha)
        
        # Criar tabela matplotlib
        colunas = ['Horário'] + self.dias
        
        table = ax.table(cellText=tabela_data, colLabels=colunas,
                        cellLoc='center', loc='center',
                        bbox=[0.1, 0.1, 0.8, 0.75])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Estilizar tabela
        for i in range(len(colunas)):
            table[(0, i)].set_facecolor('#3498DB')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        for i in range(len(tabela_data)):
            table[(i+1, 0)].set_facecolor('#2980B9')
            table[(i+1, 0)].set_text_props(weight='bold', color='white')
        
        ax.axis('off')
        
        return fig
    
    def gerar_a_partir_de_csv(self, caminho_csv, formato='png'):
        """📊 Gera quadro a partir do CSV de resultados"""
        try:
            df = pd.read_csv(caminho_csv)
            
            print(f"📊 Dados carregados: {len(df)} aulas")
            print(f"Colunas encontradas: {list(df.columns)}")
            
            # Mapear colunas se necessário
            mapeamento_colunas = {
                'nome_disciplina': 'disciplina',
                'NOME': 'disciplina',
                'DISCIPLINA': 'disciplina',
                'CODPROF': 'professor',
                'professor_id': 'professor',
                'id_professor': 'professor',
                'CODSALA': 'sala',
                'sala_id': 'sala',
                'id_sala': 'sala',
                'CODTURMA': 'turma',
                'turma_id': 'turma',
                'DIADASEMANA': 'dia',
                'dia_semana': 'dia',
                'HORARIO': 'horario'
            }
            
            df = df.rename(columns=mapeamento_colunas)
            
            # Verificar se temos as colunas necessárias
            colunas_necessarias = ['disciplina', 'professor', 'sala', 'turma', 'dia', 'horario']
            colunas_faltando = [col for col in colunas_necessarias if col not in df.columns]
            
            if colunas_faltando:
                print(f"⚠️ Colunas faltando: {colunas_faltando}")
                print(f"Colunas disponíveis: {list(df.columns)}")
                
                # Tentar inferir colunas faltando
                if 'disciplina' not in df.columns:
                    disciplina_cols = [col for col in df.columns if 'disciplina' in col.lower() or 'nome' in col.lower()]
                    if disciplina_cols:
                        df['disciplina'] = df[disciplina_cols[0]]
                
                if 'professor' not in df.columns:
                    prof_cols = [col for col in df.columns if 'prof' in col.lower()]
                    if prof_cols:
                        df['professor'] = df[prof_cols[0]]
                
                if 'sala' not in df.columns:
                    sala_cols = [col for col in df.columns if 'sala' in col.lower()]
                    if sala_cols:
                        df['sala'] = df[sala_cols[0]]
                
                if 'turma' not in df.columns:
                    turma_cols = [col for col in df.columns if 'turma' in col.lower()]
                    if turma_cols:
                        df['turma'] = df[turma_cols[0]]
                
                if 'dia' not in df.columns:
                    dia_cols = [col for col in df.columns if 'dia' in col.lower()]
                    if dia_cols:
                        df['dia'] = df[dia_cols[0]]
                
                if 'horario' not in df.columns:
                    horario_cols = [col for col in df.columns if 'horario' in col.lower()]
                    if horario_cols:
                        df['horario'] = df[horario_cols[0]]
            
            # Converter todas as colunas para string para evitar erros
            for col in ['disciplina', 'professor', 'sala', 'turma', 'dia', 'horario']:
                if col in df.columns:
                    df[col] = df[col].astype(str)
            
            # Limpar dados nulos ou inválidos
            df = df.dropna(subset=['disciplina', 'turma', 'dia', 'horario'])
            
            # Mostrar sample dos dados processados
            print(f"\n📋 Sample dos dados processados:")
            if len(df) > 0:
                print(df[['disciplina', 'professor', 'sala', 'turma', 'dia', 'horario']].head(3))
                print(f"\nTurmas encontradas: {sorted(df['turma'].unique())}")
            else:
                print("❌ Nenhum dado válido encontrado após processamento")
                raise ValueError("Dados insuficientes após limpeza")
            
            if formato == 'png':
                # Quadro geral
                self.gerar_quadro_estilo_moderno(df, salvar_como='quadro_geral.png')
                
                # Quadros por turma
                for turma in sorted(df['turma'].unique()):
                    nome_arquivo = f'quadro_{turma.replace("-", "_").replace(" ", "_")}.png'
                    self.gerar_quadro_estilo_moderno(df, turma, nome_arquivo)
            
            elif formato == 'pdf':
                self.gerar_quadro_por_turma_pdf(df)
            
        except Exception as e:
            print(f"❌ Erro ao gerar quadro: {e}")
            print(f"🔍 Tipo do erro: {type(e).__name__}")
            
            # Debug adicional
            if 'df' in locals():
                print(f"📊 Debug - Colunas do DataFrame: {list(df.columns)}")
                if len(df) > 0:
                    print(f"📊 Debug - Primeiro registro: {df.iloc[0].to_dict()}")
                    print(f"📊 Debug - Tipos de dados: {df.dtypes}")
            
            print("💡 Usando dados de exemplo...")
            df_exemplo = self.carregar_dados_exemplo()
            self.gerar_quadro_estilo_moderno(df_exemplo, 'SIN-2A-N', 'exemplo_quadro_horarios.png')

    def debug_csv(self, caminho_csv):
        """🔍 Debug do conteúdo do CSV"""
        try:
            print("🔍 ANÁLISE DO CSV:")
            print("=" * 40)
            
            df = pd.read_csv(caminho_csv)
            
            print(f"📊 Linhas: {len(df)}")
            print(f"📊 Colunas: {len(df.columns)}")
            print(f"📊 Nomes das colunas: {list(df.columns)}")
            
            print(f"\n📋 Primeiras 3 linhas:")
            print(df.head(3))
            
            print(f"\n🔍 Tipos de dados:")
            print(df.dtypes)
            
            print(f"\n📊 Valores únicos por coluna:")
            for col in df.columns:
                unique_vals = df[col].unique()
                if len(unique_vals) <= 10:
                    print(f"  {col}: {list(unique_vals)}")
                else:
                    print(f"  {col}: {len(unique_vals)} valores únicos (sample: {list(unique_vals[:5])})")
            
            # Verificar valores nulos
            print(f"\n❓ Valores nulos:")
            nulls = df.isnull().sum()
            print(nulls[nulls > 0])
            
            return df
            
        except Exception as e:
            print(f"❌ Erro ao analisar CSV: {e}")
            return None

def main():
        """🚀 Função principal para gerar quadros"""
        print("📅 GERADOR DE QUADRO DE HORÁRIOS")
        print("=" * 50)
        
        gerador = GeradorQuadroHorarios()
        
        # Verificar se existe CSV de resultados
        caminho_csv = 'resultados/horario_otimizado.csv'
        
        if os.path.exists(caminho_csv):
            print(f"✅ Encontrado arquivo de resultados: {caminho_csv}")
            
            # Debug primeiro para ver o problema
            print("\n🔍 Analisando estrutura do CSV...")
            df_debug = gerador.debug_csv(caminho_csv)
            
            if df_debug is not None:
                resposta_debug = input("\nDeseja continuar com a geração de quadros? (s/n): ").lower()
                if resposta_debug != 's':
                    return
            
            # Perguntar formato
            print("\nFormatos disponíveis:")
            print("1. PNG (quadros individuais)")
            print("2. PDF (todas as turmas)")
            print("3. Ambos")
            
            try:
                escolha = input("Escolha o formato (1/2/3): ").strip()
                
                if escolha == '1':
                    gerador.gerar_a_partir_de_csv(caminho_csv, 'png')
                elif escolha == '2':
                    gerador.gerar_a_partir_de_csv(caminho_csv, 'pdf')
                elif escolha == '3':
                    gerador.gerar_a_partir_de_csv(caminho_csv, 'png')
                    gerador.gerar_a_partir_de_csv(caminho_csv, 'pdf')
                else:
                    print("Opção inválida, gerando PNG...")
                    gerador.gerar_a_partir_de_csv(caminho_csv, 'png')
                    
            except KeyboardInterrupt:
                print("\n⚠️ Operação cancelada")
            
        else:
            print(f"⚠️ Arquivo {caminho_csv} não encontrado")
            print("💡 Gerando exemplo com dados simulados...")
            
            # Gerar exemplo
            df_exemplo = gerador.carregar_dados_exemplo()
            gerador.gerar_quadro_estilo_moderno(df_exemplo, 'SIN-2A-N', 'exemplo_quadro_horarios.png')
            
            print("\n📋 Para usar com seus dados reais:")
            print("1. Execute: python genetic_algorithm.py")
            print("2. Execute: python gerador_quadro_horarios.py")

if __name__ == "__main__":
    main()
    