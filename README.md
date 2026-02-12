# 📊 Dashboard WhatsApp - Hub X Genesys

## 🎯 Visão Geral

Dashboard interativo desenvolvido em Python com Streamlit para análise avançada de disparos de WhatsApp no contexto de gestão de leads educacionais (Hub X Genesys).

**Base de Dados Real:** 9.440 leads | 87,2% disparados | 13 colégios

---

## ✨ Funcionalidades Principais

### 👁️ Modo Visualizador (Acesso Público)

#### Filtros Dinâmicos
- **🏫 Colégio de Interesse**: Seletor com todos os colégios cadastrados
- **📅 Período**: Seletor de calendário para análise temporal
- **🎯 Status de Disparo**: Filtro por "Disparado", "Não Disparado" ou "Todos"

#### Métricas e KPIs
- Total de Leads (filtrados)
- Quantidade de Disparados (✅)
- Quantidade de Não Disparados (❌)
- Taxa de Disparo Percentual (%)

#### Visualizações Interativas
1. **Gráfico de Pizza**: Distribuição Disparado vs Não Disparado
2. **Gráfico de Barras**: Top 10 colégios por volume de leads
3. **Timeline**: Evolução do volume de leads ao longo do tempo
4. **Análise Específica**: Status detalhado apenas para leads "Não Disparados"

#### Tabela Detalhada
- Exibição completa dos dados filtrados
- Coluna "Status" exibida **APENAS** para leads "Não Disparados"
- Paginação configurável (20, 50, 100, 500 registros)
- Opção de visualizar todos os registros

#### Exportação
- **Formato**: Excel (.xlsx)
- **Conteúdo**: 
  - Aba 1: Dados filtrados com todas as colunas
  - Aba 2: Resumo com métricas principais
- **Nome do arquivo**: `leads_whatsapp_AAAAMMDD_HHMMSS.xlsx`

---

### 🔐 Modo Administrador (Acesso Restrito)

#### Autenticação
- Proteção por senha configurável
- Senha padrão: `admin2026`
- Pode ser alterada via variável de ambiente `ADMIN_PASSWORD`

#### Gestão de Dados
- **Upload de Nova Base**: Interface para substituir o arquivo .xlsx
- **Validação Automática**: Verifica colunas obrigatórias
- **Preview**: Visualização prévia antes de confirmar
- **Estatísticas**: Informações sobre a base atual e nova

#### Dashboard Administrativo
- Informações da base atual (linhas, colunas, última atualização)
- Gráficos de distribuição
- Preview das primeiras 20 linhas

---

## 📋 Estrutura de Dados Esperada

### Colunas Obrigatórias

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `Data de criação do Lead Raiz` | datetime | Data de criação do lead (formato: YYYY-MM-DD) |
| `Colégio de Interesse` | string | Nome do colégio/unidade de interesse |
| `Info Disparo` | string | Status do disparo (**penúltima coluna**) |
| `Status` | string | Status detalhado do lead (**última coluna**) |

### Valores Esperados

**Info Disparo:**
- `"Disparado"`
- `"Não disparado"`

**Status** (exemplos da base real):
- Leads (LEADS RAIZ 2026)
- Agendamento Realizado (LEADS RAIZ 2026)
- Leads contatados (LEADS RAIZ 2026)
- Visita Realizada (LEADS RAIZ 2026)
- Declinado (LEADS RAIZ 2026)
- Matriculado Total (LEADS RAIZ 2026)
- E outros...

### Regra de Negócio Crítica

> ⚠️ A coluna `Status` **SOMENTE** é exibida e considerada nas análises quando o valor de `Info Disparo` for `"Não disparado"`.

---

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Preparar o Ambiente

```bash
# Clone ou extraia o projeto
cd dashboard-whatsapp

# (Opcional mas recomendado) Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Passo 2: Instalar Dependências

```bash
pip install -r requirements.txt
```

**Bibliotecas instaladas:**
- `streamlit` - Framework web para dashboards
- `pandas` - Manipulação de dados
- `openpyxl` - Leitura/escrita de arquivos Excel
- `plotly` - Gráficos interativos
- `python-dateutil` - Manipulação de datas

### Passo 3: Configurar Senha Admin (Opcional)

**Método 1 - Variável de Ambiente (Recomendado para Produção):**

```bash
# Linux/Mac
export ADMIN_PASSWORD="sua_senha_super_segura_2026"

# Windows CMD
set ADMIN_PASSWORD=sua_senha_super_segura_2026

# Windows PowerShell
$env:ADMIN_PASSWORD="sua_senha_super_segura_2026"
```

**Método 2 - Editar o Código (Desenvolvimento):**

Abra `dashboard_app.py` e modifique a linha 19:

```python
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sua_senha_aqui")
```

### Passo 4: Preparar os Dados Iniciais

**Opção A - Usar a base fornecida (já incluída):**
```bash
# A base já está em data/base_leads.xlsx
# Nenhuma ação necessária
```

**Opção B - Usar sua própria base:**
```bash
# Copie seu arquivo para o diretório data/
cp /caminho/para/seu/arquivo.xlsx data/base_leads.xlsx
```

---

## ▶️ Executando o Dashboard

### Execução Local

```bash
streamlit run dashboard_app.py
```

O navegador abrirá automaticamente em: `http://localhost:8501`

### Execução em Servidor/Cloud

```bash
streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0
```

### Opções Avançadas de Execução

```bash
# Desabilitar auto-reload
streamlit run dashboard_app.py --server.runOnSave false

# Mudar porta
streamlit run dashboard_app.py --server.port 8080

# Modo headless (sem abrir navegador)
streamlit run dashboard_app.py --server.headless true
```

---

## 🎨 Interface do Usuário

### Modo Visualizador

1. **Sidebar Esquerda**: 
   - Seleção de modo (Visualizador/Admin)
   - Filtros (Colégio, Período, Status)
   - Informações do dashboard

2. **Área Principal**:
   - Header com título
   - Cards com 4 métricas principais
   - 2 gráficos lado a lado (Pizza + Barras)
   - Timeline de evolução temporal
   - Análise de não disparados (se aplicável)
   - Tabela detalhada com paginação
   - Botão de exportação

### Modo Administrador

1. **Tela de Login**:
   - Campo de senha
   - Botão de autenticação

2. **Painel Admin**:
   - Botão de logout
   - Área de upload
   - Preview de dados
   - Estatísticas da base atual
   - Gráficos de distribuição

---

## 📊 Análise de Dados Incluída

### Métricas Calculadas

```python
Total de Leads = Quantidade total de registros filtrados
Disparados = Leads onde Info Disparo == "Disparado"
Não Disparados = Leads onde Info Disparo == "Não disparado"
Taxa de Disparo = (Disparados / Total de Leads) × 100
```

### Visualizações

1. **Distribuição de Disparos**: Comparação percentual
2. **Volume por Colégio**: Ranking dos top 10
3. **Evolução Temporal**: Série histórica diária
4. **Status Detalhado**: Apenas para não disparados

---

## 🔒 Segurança e Controle de Acesso

### Níveis de Acesso

| Nível | Pode Visualizar | Pode Filtrar | Pode Exportar | Pode Atualizar Base |
|-------|-----------------|--------------|---------------|---------------------|
| Visualizador | ✅ | ✅ | ✅ | ❌ |
| Administrador | ✅ | ✅ | ✅ | ✅ |

### Recomendações de Segurança

1. **Produção**: SEMPRE usar variável de ambiente para senha
2. **Cloud**: Configurar firewall para restringir acesso ao modo admin
3. **Logs**: Monitorar tentativas de login
4. **Backup**: Manter backup da base antes de atualizações

---

## 📁 Estrutura de Arquivos do Projeto

```
dashboard-whatsapp/
│
├── dashboard_app.py          # Aplicação principal Streamlit
├── requirements.txt          # Dependências Python
├── README.md                 # Este arquivo
│
├── data/                     # Diretório de dados (criado automaticamente)
│   └── base_leads.xlsx       # Base de dados ativa
│
└── .streamlit/               # (Opcional) Configurações do Streamlit
    └── config.toml           # Temas e configurações
```

---

## 🛠️ Solução de Problemas

### Erro: "No module named 'streamlit'"

```bash
pip install -r requirements.txt
```

### Erro: "Permission denied" ao salvar dados

```bash
# Linux/Mac
chmod 755 data/
chmod 644 data/base_leads.xlsx
```

### Dashboard não abre automaticamente

Acesse manualmente: `http://localhost:8501`

### Senha admin não funciona

Verifique se a variável de ambiente está configurada:
```bash
echo $ADMIN_PASSWORD  # Linux/Mac
echo %ADMIN_PASSWORD% # Windows CMD
```

### Erro ao carregar Excel

- Verifique se o arquivo está em formato `.xlsx` (não `.xls`)
- Confirme que as colunas obrigatórias existem
- Teste se o arquivo abre no Excel/LibreOffice

---

## 🚀 Deploy em Produção

### Streamlit Cloud (Recomendado)

1. Criar conta em https://streamlit.io/cloud
2. Conectar repositório GitHub
3. Configurar `ADMIN_PASSWORD` nos Secrets
4. Deploy automático

### Heroku

```bash
# Criar Procfile
echo "web: streamlit run dashboard_app.py --server.port $PORT" > Procfile

# Deploy
heroku create seu-app-dashboard
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard_app.py"]
```

---

## 📈 Exemplo de Uso

### Cenário 1: Análise de Desempenho de um Colégio

1. Selecionar "Colégio São Paulo" no filtro
2. Definir período: Última semana
3. Observar taxa de disparo específica
4. Exportar dados para relatório

### Cenário 2: Identificar Leads Não Disparados

1. Filtro de Status: "Não disparado"
2. Analisar distribuição por Status
3. Identificar motivos principais
4. Exportar para ação corretiva

### Cenário 3: Atualização Mensal da Base

1. Acessar modo Administrador
2. Fazer upload do arquivo atualizado
3. Verificar preview e estatísticas
4. Confirmar atualização
5. Notificar equipe

---

## 📝 Notas Importantes

- ✅ O dashboard é responsivo e funciona em mobile
- ✅ Todos os filtros são cumulativos
- ✅ A exportação respeita os filtros ativos
- ✅ A base de dados persiste entre sessões
- ⚠️ Recarregar a página limpa os filtros
- ⚠️ Upload de nova base sobrescreve a anterior

---

## 🤝 Suporte

Para dúvidas ou problemas:

1. Verifique este README
2. Consulte a documentação do Streamlit: https://docs.streamlit.io
3. Entre em contato com o administrador do sistema

---

## 📄 Licença

Projeto proprietário - Hub X Genesys

---

**Desenvolvido com ❤️ usando Python + Streamlit**

*Última atualização: Fevereiro 2026*
