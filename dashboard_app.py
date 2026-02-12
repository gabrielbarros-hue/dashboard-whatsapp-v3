import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Dashboard WhatsApp - Hub X Genesys",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Diretório para armazenar dados
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "base_leads.xlsx"

# Senha admin (use variável de ambiente em produção)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin2026")

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: bold;
        background: linear-gradient(120deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 2.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1.1rem;
        opacity: 0.95;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .success-metric {
        background: linear-gradient(135deg, #00c853 0%, #64dd17 100%);
    }
    .warning-metric {
        background: linear-gradient(135deg, #ff6f00 0%, #ff8f00 100%);
    }
    .info-metric {
        background: linear-gradient(135deg, #0091ea 0%, #00b0ff 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        border: none;
        font-size: 1.05rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #45a049 0%, #3d8b40 100%);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .download-btn>button {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
    }
    .download-btn>button:hover {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .filter-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Carrega dados do arquivo Excel"""
    if DATA_FILE.exists():
        try:
            df = pd.read_excel(DATA_FILE)
            
            # Converter data para datetime se necessário
            if 'Data de criação do Lead Raiz' in df.columns:
                df['Data de criação do Lead Raiz'] = pd.to_datetime(df['Data de criação do Lead Raiz'], errors='coerce')
            
            return df
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados: {str(e)}")
            return None
    return None

def calculate_metrics(df):
    """Calcula métricas do dashboard"""
    total_leads = len(df)
    
    # Análise de Info Disparo
    disparados = len(df[df['Info Disparo'].str.strip().str.lower() == 'disparado'])
    nao_disparados = len(df[df['Info Disparo'].str.strip().str.lower() == 'não disparado'])
    taxa_disparo = (disparados / total_leads * 100) if total_leads > 0 else 0
    
    return {
        'total_leads': total_leads,
        'disparados': disparados,
        'nao_disparados': nao_disparados,
        'taxa_disparo': taxa_disparo
    }

def format_number(num):
    """Formata números com separador de milhares"""
    return f"{num:,}".replace(",", ".")

def admin_mode():
    """Modo administrador - permite upload de dados"""
    st.markdown("<div class='main-header'>🔐 Modo Administrador</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Gestão e Atualização da Base de Dados</div>", unsafe_allow_html=True)
    
    # Verificação de senha
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("### 🔑 Autenticação Necessária")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                password = st.text_input("Senha de Administrador", type="password", placeholder="Digite a senha")
                submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
                
                if submit:
                    if password == ADMIN_PASSWORD:
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Senha incorreta! Tente novamente.")
        return
    
    st.success("✅ Autenticado como Administrador")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Upload de arquivo
    st.markdown("### 📤 Upload de Nova Base de Dados")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Selecione o arquivo Excel (.xlsx)",
            type=['xlsx'],
            help="Arquivo deve conter as colunas: Data de criação do Lead Raiz, Colégio de Interesse, Info Disparo, Status"
        )
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Validar colunas essenciais
            required_cols = ['Info Disparo', 'Status', 'Colégio de Interesse', 'Data de criação do Lead Raiz']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                st.error(f"❌ Colunas obrigatórias ausentes: {', '.join(missing_cols)}")
            else:
                st.success(f"✅ Arquivo válido carregado!")
                
                # Estatísticas do arquivo
                col1, col2, col3 = st.columns(3)
                col1.metric("📊 Total de Linhas", format_number(len(df)))
                col2.metric("📋 Total de Colunas", len(df.columns))
                
                disparados = len(df[df['Info Disparo'].str.strip().str.lower() == 'disparado'])
                taxa = (disparados / len(df) * 100) if len(df) > 0 else 0
                col3.metric("📈 Taxa de Disparo", f"{taxa:.1f}%")
                
                # Preview dos dados
                st.markdown("### 👀 Preview dos Dados")
                st.dataframe(df.head(10), use_container_width=True, height=350)
                
                # Informações das colunas
                with st.expander("📑 Estrutura de Colunas Detectadas"):
                    col1, col2 = st.columns(2)
                    mid_point = len(df.columns) // 2
                    
                    with col1:
                        for i, col in enumerate(df.columns[:mid_point], 1):
                            st.text(f"{i}. {col}")
                    
                    with col2:
                        for i, col in enumerate(df.columns[mid_point:], mid_point + 1):
                            st.text(f"{i}. {col}")
                
                # Botão para salvar
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 SALVAR E ATUALIZAR DASHBOARD", type="primary", use_container_width=True):
                        df.to_excel(DATA_FILE, index=False, engine='openpyxl')
                        st.success("🎉 Base de dados atualizada com sucesso!")
                        st.balloons()
                        st.info("💡 Os usuários visualizadores já podem acessar os novos dados.")
                
        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {str(e)}")
            st.info("💡 Verifique se o arquivo não está corrompido e possui o formato correto.")
    
    # Informações do arquivo atual
    st.markdown("---")
    st.markdown("### 📊 Base de Dados Atual")
    
    if DATA_FILE.exists():
        df = load_data()
        if df is not None:
            file_stats = DATA_FILE.stat()
            last_modified = datetime.fromtimestamp(file_stats.st_mtime)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📈 Total de Leads", format_number(len(df)))
            col2.metric("📋 Colunas", len(df.columns))
            col3.metric("🕐 Última Atualização", last_modified.strftime("%d/%m/%Y"))
            col4.metric("⏰ Horário", last_modified.strftime("%H:%M"))
            
            # Distribuição por Status de Disparo
            st.markdown("#### 📊 Distribuição Atual")
            col1, col2 = st.columns(2)
            
            with col1:
                disparo_counts = df['Info Disparo'].value_counts()
                fig = px.pie(
                    values=disparo_counts.values,
                    names=disparo_counts.index,
                    title="Distribuição de Disparos",
                    color_discrete_sequence=['#00c853', '#ff6f00'],
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                colegio_counts = df['Colégio de Interesse'].value_counts().head(8)
                fig = px.bar(
                    x=colegio_counts.values,
                    y=colegio_counts.index,
                    orientation='h',
                    title="Top 8 Colégios",
                    color=colegio_counts.values,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False, xaxis_title="Quantidade", yaxis_title="")
                st.plotly_chart(fig, use_container_width=True)
            
            # Preview da base atual
            with st.expander("🔍 Visualizar Primeiras Linhas da Base Atual"):
                st.dataframe(df.head(20), use_container_width=True, height=400)
    else:
        st.warning("⚠️ Nenhuma base de dados encontrada. Faça upload para começar.")

def viewer_mode():
    """Modo visualizador - permite filtros, visualização e exportação"""
    st.markdown("<div class='main-header'>📊 Dashboard de Análise</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Hub X Genesys - Disparos de WhatsApp</div>", unsafe_allow_html=True)
    
    df = load_data()
    
    if df is None or df.empty:
        st.warning("⚠️ Nenhum dado disponível. Entre em contato com o administrador para atualização da base.")
        st.info("💡 Acesse o modo Administrador para fazer upload da base de dados.")
        return
    
    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("## 🎯 Filtros de Análise")
        st.markdown("---")
        
        # Filtro de Colégio
        st.markdown("### 🏫 Colégio de Interesse")
        colegios_disponiveis = sorted(df['Colégio de Interesse'].dropna().unique().tolist())
        colegios_selecionados = st.multiselect(
            "Selecione um ou mais colégios:",
            colegios_disponiveis,
            default=colegios_disponiveis,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filtro de Data
        st.markdown("### 📅 Período")
        df_dates = df['Data de criação do Lead Raiz'].dropna()
        
        if not df_dates.empty:
            min_date = df_dates.min().date()
            max_date = df_dates.max().date()
            
            date_range = st.date_input(
                "Selecione o intervalo:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                label_visibility="collapsed"
            )
            
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date = end_date = date_range if date_range else min_date
        else:
            start_date = end_date = None
        
        st.markdown("---")
        
        # Filtro de Status de Disparo
        st.markdown("### 🎯 Status de Disparo")
        status_disparo_options = ['Disparado', 'Não disparado']
        status_disparo_selecionados = st.multiselect(
            "Selecione um ou mais status:",
            status_disparo_options,
            default=status_disparo_options,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Filtro de Status do Lead
        st.markdown("### 📋 Status do Lead")
        status_disponiveis = sorted(df['Status'].dropna().unique().tolist())
        status_selecionados = st.multiselect(
            "Selecione um ou mais status:",
            status_disponiveis,
            default=status_disponiveis,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; padding: 1rem; background: #f0f2f6; border-radius: 10px;'>
        <small><b>Dashboard WhatsApp</b><br>
        Análise de Disparos de Leads</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    # Filtro de Colégio (múltipla escolha)
    if colegios_selecionados:
        df_filtered = df_filtered[df_filtered['Colégio de Interesse'].isin(colegios_selecionados)]
    
    # Filtro de Data
    if start_date and end_date:
        df_filtered = df_filtered[
            (df_filtered['Data de criação do Lead Raiz'] >= pd.Timestamp(start_date)) &
            (df_filtered['Data de criação do Lead Raiz'] <= pd.Timestamp(end_date))
        ]
    
    # Filtro de Status de Disparo (múltipla escolha)
    if status_disparo_selecionados:
        df_filtered = df_filtered[
            df_filtered['Info Disparo'].str.strip().str.lower().isin([s.lower() for s in status_disparo_selecionados])
        ]
    
    # Filtro de Status do Lead (múltipla escolha)
    if status_selecionados:
        df_filtered = df_filtered[df_filtered['Status'].isin(status_selecionados)]
    
    # Métricas
    metrics = calculate_metrics(df_filtered)
    
    st.markdown("### 📈 Indicadores Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card info-metric'>
            <div class='metric-label'>Total de Leads</div>
            <div class='metric-value'>{format_number(metrics['total_leads'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card success-metric'>
            <div class='metric-label'>✅ Disparados</div>
            <div class='metric-value'>{format_number(metrics['disparados'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card warning-metric'>
            <div class='metric-label'>❌ Não Disparados</div>
            <div class='metric-value'>{format_number(metrics['nao_disparados'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        taxa_color = 'success-metric' if metrics['taxa_disparo'] >= 80 else 'warning-metric' if metrics['taxa_disparo'] >= 60 else 'metric-card'
        st.markdown(f"""
        <div class='metric-card {taxa_color}'>
            <div class='metric-label'>Taxa de Disparo</div>
            <div class='metric-value'>{metrics['taxa_disparo']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos
    st.markdown("### 📊 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza - Distribuição de Disparos
        disparo_counts = df_filtered['Info Disparo'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=disparo_counts.index,
            values=disparo_counts.values,
            hole=0.5,
            marker=dict(colors=['#00c853', '#ff6f00']),
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Distribuição de Disparos",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de barras - Leads por Colégio
        colegio_counts = df_filtered['Colégio de Interesse'].value_counts().head(10)
        
        fig = px.bar(
            x=colegio_counts.values,
            y=colegio_counts.index,
            orientation='h',
            title="Top 10 Colégios por Volume de Leads",
            color=colegio_counts.values,
            color_continuous_scale='Viridis',
            labels={'x': 'Quantidade de Leads', 'y': 'Colégio'}
        )
        
        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis_title="Quantidade de Leads",
            yaxis_title="",
            margin=dict(t=50, b=20, l=20, r=20)
        )
        
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Leads: %{x}<extra></extra>'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline
    st.markdown("### 📅 Evolução Temporal de Leads")
    
    df_timeline = df_filtered.copy()
    df_timeline['Data'] = df_timeline['Data de criação do Lead Raiz'].dt.date
    timeline_data = df_timeline.groupby('Data').size().reset_index(name='Quantidade')
    
    fig = px.area(
        timeline_data,
        x='Data',
        y='Quantidade',
        title="Volume de Leads ao Longo do Tempo",
        color_discrete_sequence=['#1f77b4']
    )
    
    fig.update_traces(
        fill='tozeroy',
        line=dict(width=2),
        hovertemplate='<b>Data:</b> %{x}<br><b>Leads:</b> %{y}<extra></extra>'
    )
    
    fig.update_layout(
        height=350,
        hovermode='x unified',
        xaxis_title="Data de Criação",
        yaxis_title="Quantidade de Leads",
        margin=dict(t=50, b=20, l=20, r=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise por Status (somente para não disparados)
    nao_disparados_df = df_filtered[df_filtered['Info Disparo'].str.strip().str.lower() == 'não disparado']
    
    if len(nao_disparados_df) > 0:
        st.markdown("### 🔍 Análise de Leads Não Disparados")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            status_counts = nao_disparados_df['Status'].value_counts().head(8)
            
            fig = px.bar(
                x=status_counts.values,
                y=status_counts.index,
                orientation='h',
                title="Distribuição por Status (Leads Não Disparados)",
                color=status_counts.values,
                color_continuous_scale='Reds'
            )
            
            fig.update_layout(
                height=350,
                showlegend=False,
                xaxis_title="Quantidade",
                yaxis_title="Status",
                margin=dict(t=50, b=20, l=20, r=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Resumo")
            st.metric("Total Não Disparados", format_number(len(nao_disparados_df)))
            st.metric("Status Diferentes", nao_disparados_df['Status'].nunique())
            
            if len(nao_disparados_df) > 0:
                status_mais_comum = nao_disparados_df['Status'].mode()[0] if not nao_disparados_df['Status'].mode().empty else "N/A"
                st.info(f"**Status mais comum:**\n\n{status_mais_comum}")
    
    # Detalhes dos dados
    st.markdown("---")
    st.markdown("### 📋 Detalhamento Completo dos Dados")
    
    # Preparar DataFrame para exibição
    df_display = df_filtered.copy()
    
    # Criar coluna condicional para Status
    df_display['Status (Detalhado)'] = df_display.apply(
        lambda row: row['Status'] if row['Info Disparo'].strip().lower() == 'não disparado' else '—',
        axis=1
    )
    
    # Selecionar colunas para exibição
    cols_to_display = [
        'Data de criação do Lead Raiz',
        'Nome',
        'Colégio de Interesse',
        'Número de telefone',
        'E-mail',
        'Info Disparo',
        'Status (Detalhado)'
    ]
    
    # Filtrar apenas colunas que existem
    cols_to_display = [col for col in cols_to_display if col in df_display.columns]
    df_display = df_display[cols_to_display]
    
    # Formatar data
    if 'Data de criação do Lead Raiz' in df_display.columns:
        df_display['Data de criação do Lead Raiz'] = df_display['Data de criação do Lead Raiz'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Opções de visualização
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        show_all = st.checkbox("Mostrar todos os registros", value=False)
    
    with col2:
        records_to_show = st.selectbox(
            "Registros por página:",
            [20, 50, 100, 500],
            index=0,
            disabled=show_all
        )
    
    # Mostrar tabela
    if show_all:
        st.dataframe(
            df_display,
            use_container_width=True,
            height=500,
            hide_index=True
        )
    else:
        st.dataframe(
            df_display.head(records_to_show),
            use_container_width=True,
            height=500,
            hide_index=True
        )
        
        if len(df_display) > records_to_show:
            st.info(f"ℹ️ Mostrando {records_to_show} de {format_number(len(df_display))} registros. Marque 'Mostrar todos' para ver a lista completa.")
    
    # Botão de exportação
    st.markdown("---")
    st.markdown("### 💾 Exportar Dados Filtrados")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.metric("📊 Registros Filtrados", format_number(len(df_display)))
    
    with col2:
        st.metric("📋 Colunas Exportadas", len(df_display.columns))
    
    with col3:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_whatsapp_{timestamp}.xlsx"
        
        # Preparar arquivo para download
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Restaurar formato de data para Excel
            df_export = df_filtered.copy()
            
            # Criar coluna Status condicional
            df_export['Status (Detalhado)'] = df_export.apply(
                lambda row: row['Status'] if row['Info Disparo'].strip().lower() == 'não disparado' else '—',
                axis=1
            )
            
            # Selecionar e ordenar colunas
            export_cols = [col for col in cols_to_display if col in df_export.columns]
            if 'Status (Detalhado)' not in export_cols:
                export_cols.append('Status (Detalhado)')
            
            df_export[export_cols].to_excel(writer, index=False, sheet_name='Leads Filtrados')
            
            # Adicionar aba com resumo
            summary_data = {
                'Métrica': ['Total de Leads', 'Disparados', 'Não Disparados', 'Taxa de Disparo (%)'],
                'Valor': [
                    metrics['total_leads'],
                    metrics['disparados'],
                    metrics['nao_disparados'],
                    round(metrics['taxa_disparo'], 2)
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Resumo')
        
        buffer.seek(0)
        
        st.download_button(
            label="📥 Baixar Excel",
            data=buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
    
    with col4:
        st.info(f"**Arquivo:** {filename[:20]}...")

def main():
    """Função principal"""
    
    # Menu de seleção de modo
    mode = st.sidebar.radio(
        "🎛️ Modo de Acesso",
        ["📊 Visualizador", "🔐 Administrador"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    if mode == "🔐 Administrador":
        admin_mode()
    else:
        viewer_mode()

if __name__ == "__main__":
    main()
