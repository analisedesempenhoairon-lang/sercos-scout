import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from mplsoccer import Pitch, VerticalPitch
import warnings
import requests
import io
import sys
import subprocess
import os

# --- CORREÇÃO DE AMBIENTE ---
try:
    import graphviz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "graphviz"])
    import graphviz

caminho_bin = r'C:\Program Files\Graphviz\bin'
if os.path.exists(caminho_bin):
    if caminho_bin not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + caminho_bin

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="SERCOS SCOUT 2026", layout="wide")
warnings.filterwarnings("ignore")

# --- LINKS DE DADOS ---
URL_ARQUIVO_GERAL = "https://docs.google.com/spreadsheets/d/1kvs8qoZTeZql99qt_NxTQ2ZsW33V8HEAkjaOdBivrYM/edit?usp=sharing"
URL_MAPA_MENTAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=1682508291&single=true&output=csv"
URL_CLASSIFICACAO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=1057602586&single=true&output=csv"
URL_LOGO = "https://drive.google.com/thumbnail?id=1w2DdLhtdx_ZYKtUoMf1EahvFf5b20Jzc&sz=w1000"
URL_IMG_DESTRO = "https://drive.google.com/thumbnail?id=1SZH8O0MqZog-a13zWl6GYys7--1CjVgr&sz=w200"
URL_IMG_CANHOTO = "https://drive.google.com/thumbnail?id=1UI4bBzGrGU5hmogTCeP4tGBXbSqXzlu2&sz=w200"
URL_NOMES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=340587611&single=true&output=csv"
URL_CARTOES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=1354689566&single=true&output=csv"
URL_CAMPANHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=1241314919&single=true&output=csv"
URL_ASSISTENCIAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZA-C3dpQ4Zr4Htc0X7erIkHS2WrH-pwaKR5IRmdlmZ_AWigkXn8tD0Uuq4EtF2wc9Gg5UA8vMVcNG/pub?gid=0&single=true&output=csv"

CORES_EQUIPES = {
    "A.A. Serrana/FZ": "#90EE90", "ACM/Estacaville": "#006400", "América FC": "#FF4500",
    "Aviação F.C.": "#1E90FF", "Caxias F.C.": "#F8F8F8", "E.C. Panagua": "#0000FF",
    "G.E. Pirabeiraba": "#8B0000", "Pará FC": "#00BFFF", "Serbi": "#32CD32", "Sercos": "#FF0000"
}

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    h1, h2, h3, h4 { color: #e3e1e1 !important; font-family: 'Roboto', sans-serif; text-transform: uppercase; font-weight: 800; }
    section[data-testid="stSidebar"] { background-color: #11131a !important; border-right: 1px solid #333; }
    div[data-testid="stMetric"] { background-color: #1c1f26 !important; border-left: 5px solid #CC0000 !important; padding: 15px; border-radius: 8px; }
    div[data-testid="stMetricValue"] { color: #fff !important; font-size: 26px; }
    div[data-testid="stLinkButton"] > a { background-color: #CC0000 !important; color: white !important; border: 1px solid #FF3333 !important; font-weight: bold !important; text-transform: uppercase !important; }
    div[data-testid="stLinkButton"] > a:hover { background-color: #FF0000 !important; border-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def get_export_url(url):
    if "/d/" not in url: return url
    file_id = url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"

def converter_link_drive(url):
    if pd.isna(url): return url
    url_str = str(url).strip()
    if "docs.google.com/spreadsheets" in url_str:
        if "/d/" in url_str:
            file_id = url_str.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=xlsx"
    if "drive.google.com" in url_str:
        if "/d/" in url_str:
            file_id = url_str.split("/d/")[1].split("/")[0]
            return f"https://docs.google.com/uc?export=download&id={file_id}"
    return url_str

def corrigir_link_drive(url):
    if pd.isna(url): return None
    url_str = str(url).strip()
    if "drive.google.com" in url_str and "/d/" in url_str:
        try:
            file_id = url_str.split("/d/")[1].split("/")[0]
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
        except: return url_str
    return url_str

@st.cache_data(ttl=60)
def carregar_planilha_csv(url):
    try: 
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def processar_planilha_mestra(url_mestra):
    try:
        export_url = get_export_url(url_mestra)
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(export_url, headers=headers)
        if r.status_code != 200: return None, None, None
        xls = pd.ExcelFile(io.BytesIO(r.content), engine='openpyxl')
        
        try:
            df_linha = pd.read_excel(xls, sheet_name='PAINEL DE CONTROLE')
            if not df_linha.empty:
                df_linha = df_linha.dropna(subset=[df_linha.columns[0]])
                df_linha = df_linha.drop_duplicates(subset=[df_linha.columns[0]])
                df_linha.set_index(df_linha.columns[0], inplace=True)
                df_linha.index = df_linha.index.astype(str).str.strip()
        except: df_linha = pd.DataFrame()

        try:
            df_goleiros = pd.read_excel(xls, sheet_name='GOLEIROS PAINEL DE CONTROLE')
            if not df_goleiros.empty:
                df_goleiros = df_goleiros.dropna(subset=[df_goleiros.columns[0]])
                df_goleiros = df_goleiros.drop_duplicates(subset=[df_goleiros.columns[0]])
                df_goleiros.set_index(df_goleiros.columns[0], inplace=True)
                df_goleiros.index = df_goleiros.index.astype(str).str.strip()
        except: df_goleiros = pd.DataFrame()

        return df_linha, df_goleiros
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

def separar_dados_atleta(df, atleta, tipo='linha'):
    if df is None or atleta not in df.index: return None, None, None
    try:
        row = df.loc[atleta]
        if isinstance(row, pd.DataFrame): row = row.iloc[0]
    except: return None, None, None
    cols = df.columns.tolist()
    if tipo == 'goleiro':
        try:
            dados_assert = row.iloc[0:15]
            dados_volume = row.iloc[15:30]
            dados_minutos = row.iloc[30:]
        except: return None, None, None
    else: 
        idx_jogo = -1
        for i, c in enumerate(cols):
            if str(c).upper().strip().startswith('JOGO'):
                idx_jogo = i
                break
        if idx_jogo == -1: return None, None, None
        dados_minutos = row.iloc[idx_jogo:]
        dados_metricas = row.iloc[:idx_jogo]
        meio = len(dados_metricas) // 2
        dados_assert = dados_metricas.iloc[:meio]
        dados_volume = dados_metricas.iloc[meio:]
    try:
        dados_assert.index = [str(c).split('.')[0] for c in dados_assert.index]
        dados_volume.index = [str(c).split('.')[0] for c in dados_volume.index]
    except: pass
    return dados_assert, dados_volume, dados_minutos

# --- O EXECUTOR (v6) - COM REGRAS EXATAS DAS ABAS ---
@st.cache_data(ttl=300)
def carregar_scouts_dinamico_v6(links_selecionados, nomes_jogos):
    if not links_selecionados: return pd.DataFrame()
    dfs = []
    headers_req = {'User-Agent': 'Mozilla/5.0'}

    dic_nomes = {}
    nomes_reais_validos = []
    if URL_NOMES:
        df_nomes_temp = carregar_planilha_csv(URL_NOMES)
        if not df_nomes_temp.empty:
            dic_nomes = dict(zip(df_nomes_temp['Nome_Arquivo'].astype(str).str.strip(), df_nomes_temp['Nome_Real'].astype(str).str.strip()))
            nomes_reais_validos = list(set([str(v).strip() for v in dic_nomes.values() if str(v).strip() != 'nan']))

    for url, nome_exibicao in zip(links_selecionados, nomes_jogos):
        if pd.isna(url) or str(url).strip() == "": continue
        try:
            final_url = converter_link_drive(url)
            r = requests.get(final_url, headers=headers_req)
            if r.status_code == 200:
                xls = pd.ExcelFile(io.BytesIO(r.content), engine='openpyxl')
                for sheet in xls.sheet_names:
                    if any(x in str(sheet).upper() for x in ["RESUMO", "DASHBOARD", "INFO", "GERAL"]): continue
                    
                    df_s = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=50)
                    h_idx = -1
                    
                    for i, row in df_s.iterrows():
                        linha_arr = [str(val).strip().upper() for val in row.values if pd.notna(val)]
                        # Garante que acha o cabeçalho pelas palavras chaves comuns
                        if any(c in linha_arr for c in ['X', 'FIELD X', 'FIELDX', 'EVENTO', 'EVENT', 'ACTION', 'CATEGORIA', 'TIPO', 'TEMPO']):
                            h_idx = i
                            break
                            
                    if h_idx != -1:
                        data = pd.read_excel(xls, sheet_name=sheet, header=h_idx)
                        cols_novas = {}
                        for c in data.columns:
                            c_str = str(c).strip().upper()
                            if c_str in ['X', 'FIELD X', 'FIELDX']: cols_novas[c] = 'FieldX'
                            elif c_str in ['Y', 'FIELD Y', 'FIELDY']: cols_novas[c] = 'FieldY'
                            elif c_str in ['TIME', 'TEMPO (S)', 'TEMPO']: cols_novas[c] = 'Tempo'
                            elif c_str in ['PLAYER', 'ATLETA', 'JOGADOR', 'JOGADORES']: cols_novas[c] = 'Jogadores'
                            elif c_str in ['EVENTO', 'EVENT', 'ACTION', 'AÇÃO', 'CATEGORIA', 'TIPO']: cols_novas[c] = 'Evento'
                        
                        data.rename(columns=cols_novas, inplace=True)
                        data['Jogo'] = nome_exibicao
                        data['Categoria_Acao_Aba'] = str(sheet).strip().upper() # Padronizado pra maiúsculo
                        dfs.append(data)
        except: continue
            
    if not dfs: return pd.DataFrame()
    df = pd.concat(dfs, ignore_index=True)
    df.columns = [str(c).strip() for c in df.columns]

    def traduzir_nome(x):
        x_str = str(x).strip()
        if x_str in dic_nomes: return dic_nomes[x_str]
        return x_str

    # Traduz os nomes onde eles aparecerem
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(traduzir_nome)
    
    if 'FieldX' not in df.columns and 'X' in df.columns: df.rename(columns={'X':'FieldX'}, inplace=True)
    if 'FieldY' not in df.columns and 'Y' in df.columns: df.rename(columns={'Y':'FieldY'}, inplace=True)
    
    if 'Tempo' in df.columns:
        def t_min(t):
            try:
                t = str(t).strip()
                if ':' in t:
                    p = t.split(':')
                    if len(p) == 2: return float(p[0]) + float(p[1])/60
                    elif len(p) == 3: return float(p[0])*60 + float(p[1]) + float(p[2])/60
                return 0.0
            except: return 0.0
        df['Minuto'] = df['Tempo'].apply(t_min)
        
    if 'Jogadores' in df.columns:
        def proc_passador(x):
            if pd.isna(x) or str(x) == 'nan': return None
            x_str = str(x)
            for sep in ['|', '>', ',']:
                if sep in x_str: return x_str.split(sep)[0].strip()
            return x_str.strip()
            
        def proc_receptor(x):
            if pd.isna(x) or str(x) == 'nan': return None
            x_str = str(x)
            for sep in ['|', '>', ',']:
                if sep in x_str:
                    parts = x_str.split(sep)
                    if len(parts) > 1 and parts[1].strip() != "": return parts[1].strip()
            return None

        df['Passador'] = df['Jogadores'].apply(proc_passador)
        df['Receptor'] = df['Jogadores'].apply(proc_receptor)
        df['Jogadores'] = df['Passador'] 
        
        # Caça receptores que ficaram nas colunas secretas
        colunas_busca = [c for c in df.columns if c not in ['Jogo', 'Categoria_Acao_Aba', 'Tempo', 'Minuto', 'FieldX', 'FieldY', 'Evento', 'Passador', 'Receptor', 'Jogadores']]
        for idx, row in df.iterrows():
            rec_atual = row.get('Receptor')
            if pd.isna(rec_atual) or str(rec_atual).strip() in ['', 'None', 'nan']:
                for c in colunas_busca:
                    val = str(row[c]).strip()
                    passador_atual = str(row.get('Passador')).strip()
                    if val in nomes_reais_validos and val != passador_atual:
                        df.at[idx, 'Receptor'] = val
                        break

    if 'FieldX' in df.columns:
        df['FieldX'] = pd.to_numeric(df['FieldX'].astype(str).str.replace(',', '.').str.extract(r'([0-9.]+)')[0], errors='coerce')
        df['FieldY'] = pd.to_numeric(df['FieldY'].astype(str).str.replace(',', '.').str.extract(r'([0-9.]+)')[0], errors='coerce')
        
        max_x = df['FieldX'].max()
        if max_x <= 1.1: 
            df['FieldX'] *= 120
            df['FieldY'] *= 80
        elif max_x <= 100: 
            df['FieldX'] = (df['FieldX']/100)*120
            df['FieldY'] = (df['FieldY']/100)*80
            
    return df

def plot_radar_simples(categorias, valores, titulo, max_escala=None):
    if max_escala is None: range_max = 100
    else:
        v_max = max(valores) if len(valores) > 0 else 0
        range_max = v_max * 1.1 if v_max > 0 else 5
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=valores, theta=categorias, fill='toself', fillcolor='rgba(255, 0, 0, 0.5)', line=dict(color='red', width=2), name=titulo))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, range_max], color='white', gridcolor='#444'), bgcolor='#1a1c24'), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), title=dict(text=titulo, x=0.5), margin=dict(l=20, r=20, t=30, b=20), showlegend=False, height=300)
    return fig

def exibir_bump_chart(url):
    df_raw = carregar_planilha_csv(url)
    if df_raw.empty:
        st.info("Aguardando preenchimento da tabela de classificação...")
        return

    df_raw.columns = df_raw.columns.str.strip()
    colunas_rodadas = [c for c in df_raw.columns if "Rodada" in c]
    if not colunas_rodadas:
        st.warning("Nenhuma coluna de 'Rodada' encontrada na aba CLASSIFICACAO.")
        return

    df_plot = df_raw.melt(id_vars=['Equipes'], value_vars=colunas_rodadas, var_name='Rodada', value_name='Posicao')
    df_plot['Rodada_Num'] = df_plot['Rodada'].str.replace('Rodada ', '').astype(int)

    col_legenda, col_grafico = st.columns([1.1, 4])

    with col_legenda:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        rodada_inicial = colunas_rodadas[0]
        df_ordem_inicial = df_raw.sort_values(by=rodada_inicial)
        
        for _, row in df_ordem_inicial.iterrows():
            equipe = row['Equipes']
            link_logo = row.get('Link Logo')
            cor = CORES_EQUIPES.get(equipe, "#ffffff")
            img_html = ""
            if pd.notna(link_logo) and str(link_logo).strip() != "":
                url_final = corrigir_link_drive(link_logo)
                img_html = f'<img src="{url_final}" width="28" style="margin-right: 10px; border-radius: 4px; object-fit: contain;">'
            else:
                img_html = f'<div style="width: 15px; height: 15px; background-color: {cor}; border-radius: 50%; margin-right: 15px; border: 1px solid white;"></div>'

            st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 9px; height: 32px;">
                    {img_html}
                    <span style="color: white; font-size: 13px; font-weight: 800; font-family: 'Roboto', sans-serif; white-space: nowrap;">{equipe}</span>
                </div>
            """, unsafe_allow_html=True)

    with col_grafico:
        fig = px.line(df_plot, x="Rodada_Num", y="Posicao", color="Equipes", markers=True,
                      title="EVOLUÇÃO NA TABELA - RODADA A RODADA", 
                      color_discrete_map=CORES_EQUIPES)
        
        fig.update_traces(line=dict(width=5), marker=dict(size=14, line=dict(width=2, color='white')))

        ultima_rodada = df_plot['Rodada_Num'].max()
        for equipe in df_plot['Equipes'].unique():
            df_eq = df_plot[df_plot['Equipes'] == equipe]
            pos_f = df_eq[df_eq['Rodada_Num'] == ultima_rodada]['Posicao'].iloc[0]
            fig.add_annotation(
                x=ultima_rodada, y=pos_f, text=f" {equipe}",
                showarrow=False, xanchor="left", xshift=10,
                font=dict(color=CORES_EQUIPES.get(equipe, "white"), size=13, family="Arial Black")
            )

        fig.update_yaxes(autorange="reversed", dtick=1, showgrid=True, gridcolor='#333', title="POSIÇÃO")
        fig.update_xaxes(dtick=1, title="RODADA", gridcolor='#333', range=[1, ultima_rodada + 0.8])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=650, showlegend=False, margin=dict(l=0, r=120, t=50, b=50), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

# --- EXECUÇÃO ---
if 'tela' not in st.session_state: st.session_state.tela = 'Home'
if 'atleta_sel' not in st.session_state: st.session_state.atleta_sel = None

df_cartoes = carregar_planilha_csv(URL_CARTOES)
df_campanha = carregar_planilha_csv(URL_CAMPANHA)
df_assistencias = carregar_planilha_csv(URL_ASSISTENCIAS)
df_elenco = carregar_planilha_csv(URL_NOMES)
df_linha, df_goleiros = processar_planilha_mestra(URL_ARQUIVO_GERAL)

col_link = "Link do Arquivo LongoMatch (.xlsx)"
if not df_campanha.empty and col_link in df_campanha.columns:
    df_campanha['Nome_Exibicao'] = "Jogo " + df_campanha.index.astype(str) + " - " + df_campanha['Adversário'].astype(str)
    opcoes_jogos = ["Todos"] + df_campanha['Nome_Exibicao'].tolist()
else:
    opcoes_jogos = ["Nenhum jogo encontrado"]

try: st.sidebar.image(URL_LOGO, use_container_width=True)
except: pass
st.sidebar.title("SERCOS")

if st.sidebar.button("HOME PAGE"): st.session_state.tela = 'Home'
if st.sidebar.button("VISÃO GERAL"): st.session_state.tela = 'Equipe'
if st.sidebar.button("ATLETAS"): st.session_state.tela = 'Grid'

filtro = st.sidebar.selectbox("Selecionar Jogo", opcoes_jogos)

if not df_campanha.empty and col_link in df_campanha.columns:
    if filtro == "Todos":
        links = df_campanha[col_link].tolist()
        nomes = df_campanha['Nome_Exibicao'].tolist()
    else:
        selecao = df_campanha[df_campanha['Nome_Exibicao'] == filtro]
        links = selecao[col_link].tolist()
        nomes = selecao['Nome_Exibicao'].tolist()
    
    df_master = carregar_scouts_dinamico_v6(links, nomes)
else:
    df_master = pd.DataFrame()

df_jogo = df_master 

# --- TELAS ---
if st.session_state.tela == 'Home':
    st.title("NAP - Núcleo de Análise e Performance")
    st.markdown("### Bem-vindo ao Departamento de Inteligência da Sercos.")
    st.write("Desenvolvido por Airon Ramos.")

elif st.session_state.tela == 'Equipe':
    st.title("VISÃO GERAL DA EQUIPE")
    
    if not df_campanha.empty:
        df_campanha.columns = df_campanha.columns.str.strip()
        vitorias = len(df_campanha[df_campanha['Resultado'].str.contains('Vitória', na=False)])
        empates = len(df_campanha[df_campanha['Resultado'].str.contains('Empate', na=False)])
        jogos = len(df_campanha); gols_pro = pd.to_numeric(df_campanha['Gols Pro'], errors='coerce').sum()
        aprov = ((vitorias * 3 + empates) / (jogos * 3)) * 100 if jogos > 0 else 0
        media = gols_pro / jogos if jogos > 0 else 0
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Aproveitamento", f"{aprov:.1f}%"); k2.metric("Vitórias", vitorias); k3.metric("Total Gols Pró", int(gols_pro)); k4.metric("Média p/ Jogo", f"{media:.2f}")
        st.dataframe(df_campanha[['Resultado', 'Placar', 'Adversário']], use_container_width=True, hide_index=True)
    
    st.divider()
    st.subheader("CLASSIFICAÇÃO DO CAMPEONATO")
    exibir_bump_chart(URL_CLASSIFICACAO)

    st.divider(); st.subheader("Líderes de Estatística")
    if not df_assistencias.empty: st.dataframe(df_assistencias, use_container_width=True, hide_index=True)
    st.divider(); st.subheader("Controle de Cartões")
    if not df_cartoes.empty: st.dataframe(df_cartoes, use_container_width=True, hide_index=True)

    if not df_jogo.empty and 'Receptor' in df_jogo.columns:
        st.divider(); st.header("Conexões de Passes")
        
        # 1. Filtra APENAS pelas abas específicas de Passe
        abas_passes = ['PASSE', 'PASSE ULT TERCO', 'PASSE CHAVE', 'PASSE PROGRESSAO']
        mask_passe = df_jogo['Categoria_Acao_Aba'].isin(abas_passes)
        
        # 2. Filtra APENAS os passes marcados como "CERTO"
        colunas_texto = df_jogo.select_dtypes(include=['object']).columns
        mask_certo = pd.Series(False, index=df_jogo.index)
        for c in colunas_texto:
            mask_certo = mask_certo | df_jogo[c].astype(str).str.upper().str.contains('CERTO', na=False)
            
        df_passes_validos = df_jogo[mask_passe & mask_certo].dropna(subset=['Receptor', 'FieldX', 'FieldY'])

        if not df_passes_validos.empty:
            locs = df_passes_validos.groupby('Passador').agg({'FieldX':'mean','FieldY':'mean','Jogadores':'count'})
            p_net = df_passes_validos.groupby(['Passador','Receptor']).size().reset_index(name='q')
            pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e1e1e', line_color='#444')
            fig, ax = pitch.draw(figsize=(12, 8))
            if not p_net.empty:
                p_net_plot = p_net.merge(locs, left_on='Passador', right_index=True).merge(locs, left_on='Receptor', right_index=True, suffixes=['','_d'])
                pitch.lines(p_net_plot.FieldX, 80 - p_net_plot.FieldY, p_net_plot.FieldX_d, 80 - p_net_plot.FieldY_d, lw=p_net_plot.q*1.5, color='#CC0000', alpha=0.5, ax=ax, zorder=1)
            pitch.scatter(locs.FieldX, 80 - locs.FieldY, s=locs.Jogadores*50, color='white', edgecolors='#CC0000', linewidth=2, ax=ax, zorder=2)
            for n, r in locs.iterrows(): pitch.annotate(n, (r.FieldX, 80 - r.FieldY), c='white', size=10, weight='bold', ax=ax, ha='center', zorder=3)
            st.pyplot(fig)
            st.write("**Matriz de Passes**")
            matriz = pd.crosstab(df_passes_validos['Passador'], df_passes_validos['Receptor'])
            st.dataframe(matriz.style.background_gradient(cmap="Reds", axis=None), use_container_width=True)
        else:
            st.info("Nenhum passe com o marcador 'CERTO' registrado neste jogo.")

    st.divider(); st.header("Análise Tática do Jogo")
    if not df_jogo.empty:
        tempo = st.sidebar.slider("Minutos do Jogo", 0, 90, (0, 90))
        df_f = df_jogo[(df_jogo['Minuto'] >= tempo[0]) & (df_jogo['Minuto'] <= tempo[1])]
        df_f_coords = df_f.dropna(subset=['FieldX', 'FieldY'])
        
        m1, m2, m3 = st.columns(3)
        p_cfg = dict(pitch_type='statsbomb', pitch_color='#1e1e1e', line_color='#444')
        
        with m1:
            st.write("Mapa de Calor")
            p_map = VerticalPitch(**p_cfg); f, a = p_map.draw()
            if len(df_f_coords)>0: p_map.kdeplot(df_f_coords.FieldX, df_f_coords.FieldY, ax=a, cmap='Reds', fill=True, alpha=0.7)
            st.pyplot(f)
            
        with m2:
            st.write("Mapa de Ações (Total)")
            p_map = VerticalPitch(**p_cfg); f, a = p_map.draw()
            if len(df_f_coords)>0: p_map.scatter(df_f_coords.FieldX, df_f_coords.FieldY, ax=a, c='#CC0000', alpha=0.5)
            st.pyplot(f)
            
        with m3:
            st.write("Ofensivo (Finalizações)")
            p_map = VerticalPitch(**p_cfg); f, a = p_map.draw()
            if len(df_f_coords)>0:
                # Agora procura exclusivamente pela aba FINALIZACAO
                mask_fin = df_f_coords['Categoria_Acao_Aba'] == 'FINALIZACAO'
                fins = df_f_coords[mask_fin]
                if len(fins) == 0: 
                    # Se não achar nada na aba, cai no backup de X>80
                    fins = df_f_coords[df_f_coords['FieldX'] > 80]
                
                if len(fins) > 0:
                    p_map.scatter(fins.FieldX, fins.FieldY, ax=a, c='white', marker='*')
            st.pyplot(f)

    st.divider()
    with st.expander("🛠️ DEPURADOR DE DADOS"):
        if df_jogo.empty: st.error("Nenhum dado encontrado.")
        else:
            st.write("**Abas lidas do Excel:**", df_jogo['Categoria_Acao_Aba'].unique().tolist())
            st.write("**Total de ações:**", len(df_jogo))

elif st.session_state.tela == 'Grid':
    st.title("ELENCO")
    if not df_elenco.empty:
        atletas = df_elenco[df_elenco['Status'] != 'Inativo'].to_dict('records')
        cols = st.columns(5)
        for i, atleta in enumerate(atletas):
            with cols[i % 5]:
                foto_grid = atleta.get('Foto_URL')
                if pd.notna(foto_grid):
                    st.image(corrigir_link_drive(foto_grid), width=100)
                else:
                    st.markdown("👤", unsafe_allow_html=True)
                st.markdown(f"**{atleta['Nome_Real']}**")
                if st.button(f"Ver", key=f"btn_{i}"):
                    st.session_state.atleta_sel = atleta['Nome_Real']; st.session_state.tela = 'Player'; st.rerun()

elif st.session_state.tela == 'Player':
    p = st.session_state.atleta_sel
    info_atleta = {}
    if not df_elenco.empty:
        filtro_p = df_elenco[df_elenco['Nome_Real'] == p]
        if not filtro_p.empty: info_atleta = filtro_p.iloc[0].to_dict()

    if st.button("⬅️ VOLTAR"): st.session_state.tela = 'Grid'; st.rerun()

    st.title(f"DASHBOARD: {p}")
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        foto_url = info_atleta.get('Foto_URL')
        if pd.notna(foto_url) and len(str(foto_url)) > 10:
            st.image(corrigir_link_drive(foto_url), width=150)
        else: st.info("Sem foto")
        
        links_jogos_p = []
        for chave, valor in info_atleta.items():
            if str(chave).lower().startswith('jogo') and pd.notna(valor) and len(str(valor)) > 5:
                links_jogos_p.append((chave, valor))
        links_jogos_p.sort(key=lambda x: x[0])

        if links_jogos_p:
            st.markdown("##### JOGOS")
            cols_v = st.columns(3)
            for i, (nome_coluna, link) in enumerate(links_jogos_p):
                with cols_v[i % 3]:
                    st.link_button(str(nome_coluna).title(), str(link).strip(), use_container_width=True)

    with c2: st.metric("Número", info_atleta.get('Numero', '-')); st.metric("Posição", info_atleta.get('Posicao', '-'))
    with c3:
        st.markdown("**Pé Dominante**")
        pe_dom = str(info_atleta.get('Pe_Dominante', '')).strip().title()
        if 'Destro' in pe_dom: st.markdown(f"""<div style="background-color: white; padding: 5px; border-radius: 8px; width: 80px; display: flex; justify-content: center;"><img src="{URL_IMG_DESTRO}" width="65"></div>""", unsafe_allow_html=True); st.caption("Destro")
        elif 'Canhoto' in pe_dom: st.markdown(f"""<div style="background-color: white; padding: 5px; border-radius: 8px; width: 80px; display: flex; justify-content: center;"><img src="{URL_IMG_CANHOTO}" width="65"></div>""", unsafe_allow_html=True); st.caption("Canhoto")
        else: st.info("-")
    
    st.divider()
    
    dados_a, dados_v, dados_m = None, None, None
    if not df_goleiros.empty and p in df_goleiros.index:
        dados_a, dados_v, dados_m = separar_dados_atleta(df_goleiros, p, 'goleiro')
    elif not df_linha.empty and p in df_linha.index:
        dados_a, dados_v, dados_m = separar_dados_atleta(df_linha, p, 'linha')
        
    col_rad1, col_rad2 = st.columns(2)
    with col_rad1:
        st.markdown("### Assertividade (%)")
        if dados_a is not None:
            vals = pd.to_numeric(dados_a, errors='coerce').fillna(0)
            st.plotly_chart(plot_radar_simples(vals.index, vals.values, "Assertividade", None), use_container_width=True)
        else: st.warning("Sem dados de Assertividade.")
    with col_rad2:
        st.markdown("### Volume (Ações)")
        if dados_v is not None:
            vals_v = pd.to_numeric(dados_v, errors='coerce').fillna(0)
            st.plotly_chart(plot_radar_simples(vals_v.index, vals_v.values, "Volume", vals_v.max()), use_container_width=True)
        else: st.warning("Sem dados de Volume.")
            
    st.markdown("### Histórico de Minutagem")
    if dados_m is not None:
        dados_m_p = pd.to_numeric(dados_m, errors='coerce').dropna()
        if not dados_m_p.empty:
            fig = px.line(x=dados_m_p.index, y=dados_m_p.values, markers=True)
            fig.update_traces(line_color='red', marker=dict(size=8, color='white', line=dict(width=2, color='red')))
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    k1, k2, k3, k4 = st.columns(4)
    acoes_total = len(df_jogo[df_jogo['Jogadores'] == p]) if not df_jogo.empty else 0
    k1.metric("Ações Totais no Jogo", acoes_total)
    
    if not df_jogo.empty:
        df_p_scout = df_jogo[df_jogo['Jogadores'] == p]
        c_a, c_b = st.columns([1, 2])
        with c_a:
            st.markdown("### Perfil Técnico")
            df_rec_scout = df_jogo[df_jogo['Receptor'] == p]
            if not df_rec_scout.empty:
                st.write("**Quem mais passou para ele:**")
                st.dataframe(df_rec_scout['Passador'].value_counts().reset_index(name='Passes').head(5), hide_index=True, use_container_width=True)
        with c_b:
            st.markdown("### Mapa de Calor (Scout)")
            p_pitch = Pitch(pitch_type='statsbomb', pitch_color='#1e1e1e', line_color='#444')
            f_pitch, a_pitch = p_pitch.draw(figsize=(10, 6))
            
            df_p_coords = df_p_scout.dropna(subset=['FieldX', 'FieldY'])
            if len(df_p_coords) > 2:
                p_pitch.kdeplot(df_p_coords.FieldX, 80 - df_p_coords.FieldY, ax=a_pitch, cmap='Reds', fill=True, alpha=0.6, levels=50)
                p_pitch.scatter(df_p_coords.FieldX, 80 - df_p_coords.FieldY, ax=a_pitch, c='white', alpha=0.2, s=10)
            elif len(df_p_coords) > 0:
                p_pitch.scatter(df_p_coords.FieldX, 80 - df_p_coords.FieldY, ax=a_pitch, c='#CC0000', s=50)
            st.pyplot(f_pitch)

    st.divider()
    st.markdown("### Mapa de Vulnerabilidade sob Estresse (MVE)")
    
    if URL_MAPA_MENTAL:
        try:
            import graphviz
            df_mental = carregar_planilha_csv(URL_MAPA_MENTAL)
            
            if not df_mental.empty and 'Atleta' in df_mental.columns:
                df_mental['Atleta'] = df_mental['Atleta'].astype(str).str.strip()
                p_limpo = str(p).strip()
                df_atleta_mental = df_mental[df_mental['Atleta'] == p_limpo]
                
                if not df_atleta_mental.empty:
                    dot = graphviz.Digraph(graph_attr={'rankdir':'LR', 'bgcolor':'transparent'})
                    dot.node('R', p, shape='doubleoctagon', fillcolor='#CC0000', style='filled', fontcolor='white', fontname='Arial')

                    for index, row in df_atleta_mental.iterrows():
                        uid = str(index)
                        caos_val = str(row.get('Caos', '1')).strip()
                        cor_bola = '#808080'
                        if '2' in caos_val: cor_bola = '#FFD700'
                        if '3' in caos_val: cor_bola = '#FF0000'

                        dot.node(f'a{uid}', str(row.get('Ação', 'Ação')), shape='box', style='rounded,filled', fillcolor='#222', fontcolor='white', color='white')
                        dot.node(f'c{uid}', caos_val, shape='circle', style='filled', fillcolor=cor_bola, fontcolor='black', width='0.4', fixedsize='true', fontname='Arial Bold')
                        dot.node(f'i{uid}', str(row.get('Indicador', 'Indicador')), shape='note', style='filled', fillcolor='#444', fontcolor='white', fontname='Arial')
                        dot.node(f'd{uid}', str(row.get('Detalhe', '...')), shape='plaintext', fontcolor='#aaa', fontname='Arial Italic')

                        dot.edge('R', f'a{uid}', color='#666')
                        dot.edge(f'a{uid}', f'c{uid}', color='#666')
                        dot.edge(f'c{uid}', f'i{uid}', color='#666')
                        dot.edge(f'i{uid}', f'd{uid}', color='#666')

                    st.graphviz_chart(dot)
                else:
                    st.info(f"Nenhum mapeamento MVE registrado para {p}.")
            else:
                st.error("Erro: A coluna 'Atleta' não foi encontrada ou a planilha está vazia.")
        except ImportError:
            st.warning("⚠️ Biblioteca 'graphviz' não encontrada no Python. O mapa não pode ser gerado.")
