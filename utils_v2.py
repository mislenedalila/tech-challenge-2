import pandas as pd
import numpy as np
import os
from genetic_scheduler_v2 import ScheduleGA_V2

def salvar_agenda_excel(agenda, ga_v2, filename="agenda_otimizada_v2.xlsx"):
    """Salva a agenda V2 (matriz) em formato Excel"""
    
    # Criar pasta resultados se não existir
    pasta_resultados = 'resultados'
    if not os.path.exists(pasta_resultados):
        os.makedirs(pasta_resultados)
        print(f"📁 Pasta '{pasta_resultados}/' criada.")
    
    # Caminho completo do arquivo
    caminho_arquivo = os.path.join(pasta_resultados, filename)
    
    # Converter agenda para formato tabular
    dados_agenda = []
    
    for dia in range(ga_v2.num_dias):
        for horario in range(ga_v2.num_horarios):
            aula = agenda[dia, horario]
            
            if aula is not None:
                disciplina = ga_v2.disciplinas[aula.disciplina]
                professor = ga_v2.professores[aula.professor]
                
                dados_agenda.append({
                    'Dia': ga_v2.dias[dia],
                    'Horario': ga_v2.horarios[horario],
                    'Disciplina_Codigo': aula.disciplina,
                    'Disciplina_Nome': disciplina.nome,
                    'Professor_Codigo': aula.professor,
                    'Professor_Nome': professor.nome,
                    'Sala': aula.sala,
                    'Carga_Horaria_Disciplina': disciplina.carga_horaria,
                    'Turma': disciplina.turma,
                    'Slot_Posicao': f"{dia}_{horario}"
                })
            else:
                dados_agenda.append({
                    'Dia': ga_v2.dias[dia],
                    'Horario': ga_v2.horarios[horario],
                    'Disciplina_Codigo': None,
                    'Disciplina_Nome': 'LIVRE',
                    'Professor_Codigo': None,
                    'Professor_Nome': 'LIVRE',
                    'Sala': None,
                    'Carga_Horaria_Disciplina': None,
                    'Turma': None,
                    'Slot_Posicao': f"{dia}_{horario}"
                })
    
    df_agenda = pd.DataFrame(dados_agenda)
    
    try:
        with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
            # Agenda completa
            df_agenda.to_excel(writer, sheet_name='Agenda_Completa', index=False)
            
            # Apenas aulas (sem slots livres)
            df_aulas = df_agenda[df_agenda['Disciplina_Nome'] != 'LIVRE']
            df_aulas.to_excel(writer, sheet_name='Apenas_Aulas', index=False)
            
            # Agenda por dia
            for dia_nome in ga_v2.dias:
                df_dia = df_agenda[df_agenda['Dia'] == dia_nome]
                df_dia.to_excel(writer, sheet_name=f'Agenda_{dia_nome}', index=False)
            
            # Criar planilha formato grade visual
            criar_planilha_grade_visual(writer, agenda, ga_v2)
            
            # Estatísticas
            criar_planilha_estatisticas(writer, agenda, ga_v2)
        
        print(f"💾 Agenda V2 salva em: {caminho_arquivo}")
        return caminho_arquivo
        
    except Exception as e:
        print(f"❌ Erro ao salvar agenda: {e}")
        return None

def criar_planilha_grade_visual(writer, agenda, ga_v2):
    """Cria uma planilha com visualização em grade da agenda"""
    
    # Criar matriz visual
    dados_grade = []
    
    # Cabeçalho
    linha_cabecalho = ['HORÁRIO'] + ga_v2.dias
    dados_grade.append(linha_cabecalho)
    
    # Linhas da grade
    for h, horario in enumerate(ga_v2.horarios):
        linha = [horario]
        
        for d in range(ga_v2.num_dias):
            aula = agenda[d, h]
            if aula is not None:
                disciplina = ga_v2.disciplinas[aula.disciplina]
                professor = ga_v2.professores[aula.professor]
                texto = f"{disciplina.nome[:15]}\n({professor.nome})"
                linha.append(texto)
            else:
                linha.append('LIVRE')
        
        dados_grade.append(linha)
    
    df_grade = pd.DataFrame(dados_grade[1:], columns=dados_grade[0])
    df_grade.to_excel(writer, sheet_name='Grade_Visual', index=False)

def criar_planilha_estatisticas(writer, agenda, ga_v2):
    """Cria planilha com estatísticas da agenda"""
    
    # Estatísticas por dia
    stats_dia = []
    for d, dia_nome in enumerate(ga_v2.dias):
        aulas_dia = sum(1 for h in range(ga_v2.num_horarios) if agenda[d, h] is not None)
        stats_dia.append({
            'Dia': dia_nome,
            'Aulas_Agendadas': aulas_dia,
            'Slots_Livres': ga_v2.num_horarios - aulas_dia,
            'Utilizacao_Pct': (aulas_dia / ga_v2.num_horarios) * 100
        })
    
    df_stats_dia = pd.DataFrame(stats_dia)
    df_stats_dia.to_excel(writer, sheet_name='Stats_Por_Dia', index=False)
    
    # Estatísticas por disciplina
    stats_disciplina = []
    aulas_por_disciplina = {}
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        professor = None
        for prof in ga_v2.professores.values():
            if prof.disciplina == disc_codigo:
                professor = prof.nome
                break
        
        stats_disciplina.append({
            'Disciplina_Codigo': disc_codigo,
            'Disciplina_Nome': disciplina.nome,
            'Professor': professor,
            'Carga_Prevista': disciplina.carga_horaria,
            'Aulas_Alocadas': aulas_alocadas,
            'Status': 'COMPLETA' if aulas_alocadas >= disciplina.carga_horaria else 'INCOMPLETA',
            'Diferenca': aulas_alocadas - disciplina.carga_horaria
        })
    
    df_stats_disc = pd.DataFrame(stats_disciplina)
    df_stats_disc.to_excel(writer, sheet_name='Stats_Por_Disciplina', index=False)
    
    # Estatísticas por professor
    stats_professor = []
    aulas_por_professor = {}
    dias_por_professor = {}
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                prof = aula.professor
                aulas_por_professor[prof] = aulas_por_professor.get(prof, 0) + 1
                if prof not in dias_por_professor:
                    dias_por_professor[prof] = set()
                dias_por_professor[prof].add(d)
    
    for prof_codigo, professor in ga_v2.professores.items():
        aulas_total = aulas_por_professor.get(prof_codigo, 0)
        dias_trabalhados = len(dias_por_professor.get(prof_codigo, set()))
        disciplina = ga_v2.disciplinas[professor.disciplina]
        
        stats_professor.append({
            'Professor_Codigo': prof_codigo,
            'Professor_Nome': professor.nome,
            'Disciplina': disciplina.nome,
            'Total_Aulas': aulas_total,
            'Dias_Trabalhados': dias_trabalhados,
            'Media_Aulas_Por_Dia': aulas_total / max(dias_trabalhados, 1),
            'Concentracao': 'ALTA' if dias_trabalhados <= 2 else 'MEDIA' if dias_trabalhados <= 3 else 'BAIXA'
        })
    
    df_stats_prof = pd.DataFrame(stats_professor)
    df_stats_prof.to_excel(writer, sheet_name='Stats_Por_Professor', index=False)

def analisar_qualidade_agenda(agenda, ga_v2):
    """Analisa a qualidade da agenda V2 e retorna métricas"""
    
    metricas = {}
    
    # 1. Completude das disciplinas
    aulas_por_disciplina = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
    
    disciplinas_completas = 0
    total_disciplinas = len(ga_v2.disciplinas)
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        if aulas_alocadas >= disciplina.carga_horaria:
            disciplinas_completas += 1
    
    metricas['completude_disciplinas'] = disciplinas_completas / total_disciplinas
    
    # 2. Respeito à disponibilidade
    total_aulas = sum(1 for d in range(ga_v2.num_dias) for h in range(ga_v2.num_horarios) 
                     if agenda[d, h] is not None)
    aulas_com_disponibilidade = 0
    
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                if ga_v2._professor_disponivel(aula.professor, d, h):
                    aulas_com_disponibilidade += 1
    
    metricas['respeito_disponibilidade'] = aulas_com_disponibilidade / max(total_aulas, 1)
    
    # 3. Distribuição equilibrada
    aulas_por_dia = []
    for d in range(ga_v2.num_dias):
        aulas_dia = sum(1 for h in range(ga_v2.num_horarios) if agenda[d, h] is not None)
        aulas_por_dia.append(aulas_dia)
    
    if len(aulas_por_dia) > 0:
        media_aulas = np.mean(aulas_por_dia)
        variacao_aulas = np.std(aulas_por_dia)
        metricas['equilibrio_distribuicao'] = max(0, (3.0 - variacao_aulas) / 3.0)  # Normalizar para 0-1
    else:
        metricas['equilibrio_distribuicao'] = 0
    
    # 4. Utilização de slots
    slots_utilizados = total_aulas
    slots_totais = ga_v2.num_dias * ga_v2.num_horarios
    metricas['utilizacao_slots'] = slots_utilizados / slots_totais
    
    # 5. Concentração por professor
    dias_por_professor = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                prof = aula.professor
                if prof not in dias_por_professor:
                    dias_por_professor[prof] = set()
                dias_por_professor[prof].add(d)
    
    concentracao_media = 0
    if dias_por_professor:
        total_concentracao = sum(max(0, (4 - len(dias))) / 4 for dias in dias_por_professor.values())
        concentracao_media = total_concentracao / len(dias_por_professor)
    
    metricas['concentracao_professores'] = concentracao_media
    
    # 6. Score geral (média ponderada)
    pesos = {
        'completude_disciplinas': 0.3,
        'respeito_disponibilidade': 0.25,
        'equilibrio_distribuicao': 0.2,
        'utilizacao_slots': 0.1,
        'concentracao_professores': 0.15
    }
    
    score_geral = sum(metricas[metrica] * peso for metrica, peso in pesos.items())
    metricas['score_geral'] = score_geral
    
    return metricas

def gerar_relatorio_agenda_v2(agenda, fitness, historico, ga_v2):
    """Gera relatório completo para agenda V2"""
    
    print("\n" + "="*80)
    print("📊 RELATÓRIO COMPLETO - AGENDA V2 (PONTUAÇÃO)")
    print("="*80)
    
    # Métricas de qualidade
    metricas = analisar_qualidade_agenda(agenda, ga_v2)
    
    print(f"\n🎯 MÉTRICAS GERAIS:")
    print(f"   • Fitness final: {fitness:.0f} pontos")
    print(f"   • Score geral de qualidade: {metricas['score_geral']:.1%}")
    print(f"   • Gerações executadas: {len(historico)}")
    print(f"   • Melhoria total: {historico[-1] - historico[0]:.0f} pontos")
    
    print(f"\n📚 ANÁLISE ACADÊMICA:")
    print(f"   • Completude das disciplinas: {metricas['completude_disciplinas']:.1%}")
    print(f"   • Disponibilidade respeitada: {metricas['respeito_disponibilidade']:.1%}")
    print(f"   • Equilíbrio na distribuição: {metricas['equilibrio_distribuicao']:.1%}")
    print(f"   • Utilização de slots: {metricas['utilizacao_slots']:.1%}")
    print(f"   • Concentração dos professores: {metricas['concentracao_professores']:.1%}")
    
    # Análise por disciplina
    print(f"\n📋 STATUS DAS DISCIPLINAS:")
    aulas_por_disciplina = {}
    for d in range(ga_v2.num_dias):
        for h in range(ga_v2.num_horarios):
            aula = agenda[d, h]
            if aula is not None:
                disc = aula.disciplina
                aulas_por_disciplina[disc] = aulas_por_disciplina.get(disc, 0) + 1
    
    for disc_codigo, disciplina in ga_v2.disciplinas.items():
        aulas_alocadas = aulas_por_disciplina.get(disc_codigo, 0)
        status = "✅" if aulas_alocadas >= disciplina.carga_horaria else "❌"
        print(f"   {status} {disciplina.nome[:35]:35} | {aulas_alocadas}/{disciplina.carga_horaria}h")
    
    # Distribuição por dia
    print(f"\n📅 DISTRIBUIÇÃO SEMANAL:")
    for d, dia_nome in enumerate(ga_v2.dias):
        aulas_dia = sum(1 for h in range(ga_v2.num_horarios) if agenda[d, h] is not None)
        utilizacao = (aulas_dia / ga_v2.num_horarios) * 100
        print(f"   • {dia_nome}: {aulas_dia} aulas ({utilizacao:.0f}% utilização)")
    
    return metricas

# Exemplo de uso
if __name__ == "__main__":
    print("🛠️  Utilitários V2 - Teste de Funcionalidades")
    
    # Testar criação e salvamento de agenda
    ga_v2 = ScheduleGA_V2()
    agenda_teste, fitness_teste, historico_teste = ga_v2.executar()
    
    # Salvar agenda
    caminho_salvo = salvar_agenda_excel(agenda_teste, ga_v2, "teste_agenda_v2.xlsx")
    
    # Gerar relatório
    metricas = gerar_relatorio_agenda_v2(agenda_teste, fitness_teste, historico_teste, ga_v2)
    
    print(f"\n✅ Teste concluído. Agenda salva em: {caminho_salvo}")
    print(f"📊 Score geral de qualidade: {metricas['score_geral']:.1%}")