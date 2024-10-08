import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
import openpyxl
import seaborn as sns

import base64
import os

st.set_page_config(layout="wide")

def main():

    ####Desabilitar tela de login
    #st.session_state['logged_in'] = True
    ####
    
    # Verificar se o usuário está logado
    if not is_user_logged_in():
        show_login_page()
    else:
        run_main_program()

def is_user_logged_in():
    # Verificar se o usuário está logado
    return st.session_state.get('logged_in', False)

def show_login_page():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button = st.button("Login")

    if login_button:
        if username == "admin" and password == "admin":
            st.session_state['logged_in'] = True
            st.experimental_rerun()  # Re-executar o aplicativo para atualizar a tela
        else:
            st.error("Invalid username or password")

@st.cache_data
def ler_nomes_das_planilhas(caminho_arquivo):
    workbook = openpyxl.load_workbook(caminho_arquivo)
        
    # Obtém os nomes das planilhas
    nomes_planilhas = workbook.sheetnames
        
    # Fecha o arquivo Excel
    workbook.close()
            
    return nomes_planilhas

@st.cache_data
def read_sheet(name, sheet):
        df = pd.read_excel(name, sheet, header=0)
        return df


@st.cache_data
def read_table(_connection, sheet):
    #df = pd.read_excel(name, sheet, header=0)
    cursor = _connection.cursor()
    cursor.execute(f"SELECT * FROM {sheet}")
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()
    cursor.close()
            
    return df
    
@st.cache_data
def get_table_names(connection):
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    return table_names

    
@st.cache_data
def connect_to_mysql(user, password, host, database):
    try:
        connection = mysql.connector.connect(user=user, password=password,
                                            host=host,
                                            database=database)
        return connection
    except mysql.connector.Error as error:
        print("Erro ao conectar ao banco de dados MySQL:", error)
        return None


@st.cache_data
def download_link_excel(df, filename):
    # Salvar o DataFrame em um arquivo Excel temporário
    temp_file = f"{filename}.xlsx"
    df.to_excel(temp_file, index=False)
            
    # Ler o arquivo Excel em bytes
    with open(temp_file, 'rb') as f:
        excel_data = f.read()
            
    # Excluir o arquivo temporário
    os.remove(temp_file)
            
    # Codificar em base64
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Baixar tabela para o excel</a>'
    return href

#@st.cache_data
def pag1():
    st.title("Página 1")
    with st.sidebar:
        database = st.checkbox('Utilizar banco de dados')

    ######################
    #adaptar com o nome de usuario e nome do banco de dados
    ################
    
    if database:
        user = 'luan'
        password = 'luan'
        host = 'localhost'
        database = 'cantodeminas'
        connection = connect_to_mysql(user, password, host, database)

        
        # Obter nomes das tabelas
        name = get_table_names(connection)
        
        # Usar os nomes das tabelas para seleção
        with st.sidebar:
            selected_graficos = st.selectbox("Tabela:", name)
        df = read_table(connection, selected_graficos)
                       
        
        if connection is None:
            st.error("Não foi possível conectar ao banco de dados MySQL. Verifique as credenciais.")
            return
    if not database:
        name = st.file_uploader("Escolha o arquivo Excel", type=['xlsx'])

    #verificar se possui um arquivo presente
    if name is not None:
        # Criação do menu lateral
        # Obtenção dos dados da interface do streamlit
        if not database:
            with st.sidebar:
                selected_graficos = st.selectbox("Planilha:", ler_nomes_das_planilhas(name))
                
            df = read_sheet(name, selected_graficos)
    with st.sidebar:
        linhas = st.slider("Quantidade de linhas", 1, 20)
    if st.button("Mostrar linhas"):
        col1, col2 = st.columns(2)

        with col1:
            df = df.head(linhas)
            st.write("Tabela")
            st.write(df)
            st.markdown(download_link_excel(df, 'dados'), unsafe_allow_html=True)
        
        #segundo gráfico
        with col2:
            # Manter apenas as colunas desejadas
            df = df[['NumeroSemana', 'QUANTIDADE']]
            
            # Exibir a tabela
            st.write("Tabela filtrada:")
            st.write(df)
        with col1:
            # Plotar o gráfico
            plt.figure(figsize=(10, 5))
            plt.plot(df['NumeroSemana'], df['QUANTIDADE'], marker='o')
            plt.title('Quantidade por Número da Semana')
            plt.xlabel('Número da Semana')
            plt.ylabel('Quantidade')
            plt.grid()
            plt.xticks(df['NumeroSemana'])  # Para mostrar todos os números de semana
            
            # Exibir o gráfico no Streamlit
            st.pyplot(plt)
     
#@st.cache_data
def pag2():
    col1, col2 = st.columns(2)
    with col1:
        # Carregar o conjunto de dados Iris
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        df = pd.read_csv(url, header=None, names=['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species'])
        
        # Título do aplicativo
        st.title("Análise do Conjunto de Dados Iris")
        
        # Mostrar os dados
        st.subheader("Dados do Conjunto Iris")
        st.write(df)
        
        # Gráfico de dispersão
        st.subheader("Gráfico de Dispersão")
        with st.sidebar:
            st.subheader("Gráfico de Dispersão")
            x_axis = st.selectbox("Escolha a variável no eixo X", df.columns[:-1])  # Excluindo a coluna de espécie
            y_axis = st.selectbox("Escolha a variável no eixo Y", df.columns[:-1])
        plt.figure(figsize=(10, 5))
        sns.scatterplot(data=df, x=x_axis, y=y_axis, hue='species', style='species')
        plt.title("Gráfico de Dispersão")
        st.pyplot(plt)

    with col2:
        # Histograma
        st.subheader("Histograma")
        with st.sidebar:
            st.subheader("Histograma")
            hist_col = st.selectbox("Escolha a variável para o histograma", df.columns[:-1])
        plt.figure(figsize=(10, 5))
        sns.histplot(df[hist_col], bins=20, kde=True)
        plt.title(f"Histograma de {hist_col}")
        st.pyplot(plt)
        
        # Gráfico de caixa
        st.subheader("Gráfico de Caixa")
        with st.sidebar:
            st.subheader("Gráfico de Caixa")
            box_col = st.selectbox("Escolha a variável para o gráfico de caixa", df.columns[:-1])
        plt.figure(figsize=(10, 5))
        sns.boxplot(data=df, x='species', y=box_col)
        plt.title(f"Gráfico de Caixa de {box_col} por Espécie")
        st.pyplot(plt)

def pag3():
    # Carregar o conjunto de dados Titanic
    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
    df = pd.read_csv(url)
    
    # Título do aplicativo
    st.title("Análise do Conjunto de Dados Titanic")
    
    # Mostrar os dados
    st.subheader("Dados do Conjunto Titanic")
    st.write(df)

    col1, col2 = st.columns(2)
    with col1:
        # Gráfico de barras para sobreviventes
        st.subheader("Gráfico de Barras: Sobreviventes por Classe")
        df['Survived'] = df['Survived'].replace({0: 'No', 1: 'Yes'})  # Substitui 0 e 1 por No e Yes
        sns.countplot(data=df, x='Pclass', hue='Survived')
        plt.title("Sobreviventes por Classe")
        st.pyplot(plt)
        
        # Gráfico de dispersão
        st.subheader("Gráfico de Dispersão: Idade vs. Preço da Passagem")
        plt.figure(figsize=(10, 5))
        sns.scatterplot(data=df, x='Age', y='Fare', hue='Survived', alpha=0.6)
        plt.title("Idade vs. Preço da Passagem")
        st.pyplot(plt)
    with col2:
        # Gráfico de caixa
        st.subheader("Gráfico de Caixa: Preço da Passagem por Classe")
        plt.figure(figsize=(10, 5))
        sns.boxplot(data=df, x='Pclass', y='Fare')
        plt.title("Preço da Passagem por Classe")
        plt.xlabel("Classe")
        plt.ylabel("Preço Médio da Passagem")
        st.pyplot(plt)


        
def run_main_program():
    pd.options.mode.chained_assignment = None
    ######### caminho direto ou escokha
    #name = "D:\OneDrive\Área de Trabalho\CantoDeMinas\Dados semanais com gráficos.xlsx"

    #0 para só aparecer o menu ao ter os dados, 1 para sempre ter o menu
    #menu = '0'
    menu = '1'
            
    ######        
    #bootstrap-icons
    #####
    
    if menu=='1':
        with st.sidebar:
            selecao = option_menu(
                "Menu",
                ["Página 1", "Página 2", "Página 3"],
                icons=['1-circle', '2-circle', '3-circle'],
                menu_icon="cast",
                default_index=0,
            )
            
        
        if selecao == 'Página 1':
            pag1()
        elif selecao == 'Página 2':
            pag2()
        elif selecao == 'Página 3':
            pag3()

if __name__ == "__main__":
    main()