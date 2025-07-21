import streamlit as st # Importa a biblioteca Streamlit para criar aplicativos web interativos.
import pandas as pd # Importa a biblioteca Pandas para manipulação e análise de dados, especialmente com DataFrames.
import plotly.express as px # Importa a biblioteca Plotly Express para criar gráficos interativos.
from datetime import datetime # Importa o módulo datetime para trabalhar com datas e horas.
import base64 # Importa a biblioteca base64 para codificar e decodificar dados em base64, usado aqui para exibir imagens.

# --- CLASSES ---

# Definição da classe Material.
class Material:
    # O método __init__ é o construtor da classe Material.
    # Ele inicializa um objeto Material com seus atributos.
    def __init__(self, nome, dados):
        self.nome = nome # Nome do material (ex: "Concreto", "Cimento").
        self.desperdicio = dados["desperdicio"] # Taxa de desperdício do material.
        self.co2 = dados["co2"] # Fator de emissão de CO2 por kg de resíduo do material.
        self.consumo_padrao = dados["consumo"] # Consumo padrão do material por m².
        self.unidade = dados["un"] # Unidade de medida do consumo (ex: "m³/m²", "kg/m²").
        self.densidade = dados.get("densidade", 1000) # Densidade do material, com valor padrão de 1000 se não especificado.
        self.descarte = dados["descarte"] # Informações sobre o descarte adequado do material.
        self.reuso = dados["reuso"] # Informações sobre a possibilidade de reuso do material.

    # Método para calcular o consumo, resíduo e emissão de CO2 de um material.
    def calcular(self, consumo, area):
        consumo_total = consumo * area # Calcula o consumo total do material para a área especificada.
        # Ajusta o consumo para kg com base na unidade e densidade.
        if self.unidade == "m³/m²":
            consumo_kg = consumo_total * self.densidade # Converte m³ para kg usando a densidade.
        elif self.unidade == "un/m²":
            consumo_kg = consumo_total * self.densidade # Converte unidades para kg usando a densidade.
        else:
            consumo_kg = consumo_total # Se já estiver em kg/m², mantém o valor.
        residuo = consumo_kg * self.desperdicio # Calcula a quantidade de resíduo gerado.
        co2_total = residuo * self.co2 # Calcula a emissão total de CO2.
        return consumo_total, consumo_kg, residuo, co2_total # Retorna os valores calculados.


# Definição da classe AnalisadorResiduos
class AnalisadorResiduos:
    # O método __init__ é o construtor da classe AnalisadorResiduos.
    # Ele recebe dados dos materiais, área da obra, materiais selecionados e consumos customizados.
    def __init__(self, materiais_dados, area, materiais_selecionados, consumos_customizados):
        # Cria uma lista de objetos Material com base nos materiais selecionados.
        self.materiais = [Material(nome, materiais_dados[nome]) for nome in materiais_selecionados]
        self.area = area # Área total da obra em m².
        self.resultados = [] # Lista para armazenar os resultados da análise de cada material.
        self.consumos_customizados = consumos_customizados # Dicionário com consumos personalizados inseridos pelo usuário.

    # Método para realizar a análise dos materiais.
    def analisar(self):
        for mat in self.materiais: # Itera sobre cada material selecionado.
            # Obtém o consumo real, que pode ser o personalizado ou o padrão.
            consumo_real = self.consumos_customizados.get(mat.nome, mat.consumo_padrao)
            # Calcula os valores para o material usando o método 'calcular' da classe Material.
            consumo_total, consumo_kg, residuo, co2 = mat.calcular(consumo_real, self.area)
            # Adiciona os resultados ao dicionário 'resultados'.
            self.resultados.append({
                "Material": mat.nome,
                "Consumo Total": f"{consumo_total:.2f} {mat.unidade}", # Formata o consumo total com unidade.
                "Consumo (kg)": consumo_kg,
                "Resíduo (kg)": residuo,
                "Emissão CO₂ (kg)": co2,
                "Reutilização": mat.reuso,
                "Descarte": mat.descarte,
                "Excedeu Limite": consumo_real > mat.consumo_padrao # Verifica se o consumo real excedeu o padrão.
            })
        return pd.DataFrame(self.resultados) # Retorna os resultados como um DataFrame do Pandas.

    # Método para gerar um relatório textual da análise.
    def gerar_relatorio(self, df, c1, c2, c3, c3_perc):
        total_residuo = df["Resíduo (kg)"].sum() # Soma total do resíduo gerado.
        total_co2 = df["Emissão CO₂ (kg)"].sum() # Soma total da emissão de CO2.
        selo_concedido = c1 and c2 and c3 # Booleano indicando se o selo verde foi concedido.
        resultado_selo = "✅ CONCEDIDO" if selo_concedido else "❌ NÃO CONCEDIDO" # Mensagem para o resultado do selo.

        linhas = [
            f"Relatório de Análise de Resíduos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", # Cabeçalho do relatório com data e hora.
            f"Área analisada: {self.area:.2f} m²\n", # Área da obra.
            "--- Detalhamento por Material ---", # Seção de detalhamento por material.
            # Converte o DataFrame para string para inclusão no relatório.
            df[['Material', 'Consumo Total', 'Consumo (kg)', 'Resíduo (kg)', 'Emissão CO₂ (kg)', 'Reutilização', 'Descarte']].to_string(index=False),
            "\n\n--- Resumo Geral ---", # Seção de resumo geral.
            f"Total de resíduo gerado: {total_residuo:,.2f} kg", # Total de resíduo.
            f"Total de emissão de CO₂: {total_co2:,.2f} kg\n", # Total de emissão de CO2.
            "--- Resultado do Selo Verde ---", # Seção do resultado do selo verde.
            resultado_selo, # Resultado final do selo.
            "Critérios:", # Lista dos critérios de avaliação.
            f"- {'✅' if c1 else '❌'} Nenhum material ultrapassou o consumo médio.", # Critério 1.
            f"- {'✅' if c2 else '❌'} Emissão de CO₂ por m² ≤ 8 kg (Atual: {total_co2 / self.area:.2f} kg)", # Critério 2.
            f"- {'✅' if c3 else '❌'} {c3_perc:.1f}% dos materiais têm reaproveitamento (Meta: ≥ 70%)" # Critério 3.
        ]
        return "\n".join(linhas) # Retorna o relatório como uma única string, com cada linha separada por quebra de linha.


# --- DADOS DOS MATERIAIS ---

# Dicionário contendo os dados padrão para diversos materiais de construção.
# Cada material tem atributos como desperdício, CO2, consumo padrão, unidade, densidade, descarte e reuso.
MATERIAIS_DADOS = {
    "Concreto": {"desperdicio": 0.12, "co2": 0.15, "consumo": 0.05, "un": "m³/m²", "densidade": 2400, "descarte": "Descarte em caçambas", "reuso": "Pode ser triturado"},
    "Cimento":  {"desperdicio": 0.10, "co2": 0.85, "consumo": 15,    "un": "kg/m²", "descarte": "Evitar solo e água", "reuso": "Usar em argamassa"},
    "Areia":    {"desperdicio": 0.05, "co2": 0.01, "consumo": 0.006, "un": "m³/m²", "densidade": 1600, "descarte": "Descarte controlado", "reuso": "Pode ser misturada com nova areia"},
    "Tijolo":   {"desperdicio": 0.20, "co2": 0.12, "consumo": 60,    "un": "un/m²", "densidade": 3.5, "descarte": "Descarte autorizado", "reuso": "Reutilizável em calçadas"},
    "Madeira":  {"desperdicio": 0.08, "co2": 0.10, "consumo": 0.01, "un": "m³/m²", "densidade": 600, "descarte": "Reciclagem ou compostagem", "reuso": "Reutilização em pequenas obras"},
    "Aço":      {"desperdicio": 0.07, "co2": 1.80, "consumo": 20,    "un": "kg/m²", "descarte": "Enviar para reciclagem", "reuso": "100% reciclável"},
    "Ferro":    {"desperdicio": 0.08, "co2": 1.80, "consumo": 1,     "un": "kg/m²", "descarte": "Lavar para ferro-velho", "reuso": "Pode ser fundido"},
    "Gesso":    {"desperdicio": 0.30, "co2": 0.18, "consumo": 7,     "un": "kg/m²", "descarte": "Evitar solo e água", "reuso": "Usar em argamassa"},
}


# --- STREAMLIT APP ---

# Configura a página do Streamlit.
st.set_page_config(page_title="Análise de Resíduos", layout="centered")
st.title("♻️ Análise de Resíduos de Materiais de Construção") # Título principal da aplicação.

# Campo de entrada para a área da obra.
area_obra = st.number_input("Área da obra (m²):", min_value=1.0, value=100.0, format="%.2f")
# Campo de seleção múltipla para os materiais a serem analisados.
nomes_materiais = st.multiselect("Materiais a serem analisados:", list(MATERIAIS_DADOS.keys()))

# Verifica se algum material foi selecionado.
if not nomes_materiais:
    st.info("Selecione ao menos um material.") # Exibe uma mensagem informativa se nenhum material for selecionado.
else:
    consumos_input = {} # Dicionário para armazenar os consumos personalizados.
    st.subheader("Consumo personalizado (opcional)") # Subtítulo para a seção de consumo personalizado.
    # Loop para permitir que o usuário personalize o consumo de cada material selecionado.
    for nome in nomes_materiais:
        dados = MATERIAIS_DADOS[nome] # Obtém os dados padrão do material.
        valor = st.number_input(
            f"{nome} ({dados['un']}, padrão: {dados['consumo']}):", # Label do campo de entrada com unidade e valor padrão.
            min_value=0.0, step=0.1, format="%.4f", key=nome # Configurações do campo de entrada numérico.
        )
        # Se o valor inserido for maior que zero, usa-o; caso contrário, usa o consumo padrão.
        consumos_input[nome] = valor if valor > 0 else dados["consumo"]

    # Cria uma instância da classe AnalisadorResiduos com os dados fornecidos.
    analise = AnalisadorResiduos(MATERIAIS_DADOS, area_obra, nomes_materiais, consumos_input)
    df = analise.analisar() # Executa a análise e obtém o DataFrame de resultados.

    st.subheader("Resumo dos Cálculos") # Subtítulo para o resumo dos cálculos.
    # Exibe o DataFrame de resultados, formatando as colunas numéricas.
    st.dataframe(df[["Material", "Consumo Total", "Consumo (kg)", "Resíduo (kg)", "Emissão CO₂ (kg)", "Reutilização", "Descarte"]].style.format({
        "Consumo (kg)": "{:,.2f}",
        "Resíduo (kg)": "{:,.2f}",
        "Emissão CO₂ (kg)": "{:,.2f}"
    }))

    total_co2 = df["Emissão CO₂ (kg)"].sum() # Calcula a soma total de CO2 emitido.
    total_residuo = df["Resíduo (kg)"].sum() # Calcula a soma total de resíduo gerado.

    st.markdown(f"*Total de resíduo:* {total_residuo:,.2f} kg") # Exibe o total de resíduo.
    st.markdown(f"*Total de CO₂ emitido:* {total_co2:,.2f} kg") # Exibe o total de CO2.

    # Cria um gráfico de barras interativo usando Plotly Express.
    fig = px.bar(df, x="Material", y=["Resíduo (kg)", "Emissão CO₂ (kg)"], barmode="group")
    st.plotly_chart(fig, use_container_width=True) # Exibe o gráfico no Streamlit.

    # --- SELO VERDE ---
    st.subheader("🌱 Resultado do Selo Verde") # Subtítulo para a seção do Selo Verde.
    # Critério 1: Verifica se nenhum material excedeu o consumo padrão.
    c1 = not df["Excedeu Limite"].any()
    # Critério 2: Verifica se a emissão de CO2 por m² é menor ou igual a 8 kg.
    c2 = (total_co2 / area_obra) <= 8
    # Calcula o número de materiais que podem ser reutilizados ou reciclados.
    reaproveitaveis = df["Reutilização"].str.contains("reutil|recicl|usar", case=False).sum()
    # Calcula o percentual de materiais reaproveitáveis.
    perc_reaproveit = (reaproveitaveis / len(df)) * 100
    # Critério 3: Verifica se o percentual de materiais reaproveitáveis é maior ou igual a 70%.
    c3 = perc_reaproveit >= 70

    # Verifica se todos os critérios para o Selo Verde foram atendidos.
    if c1 and c2 and c3:
        st.success("✅ Selo Verde garantido!") # Mensagem de sucesso.
        try:
            # Tenta abrir e codificar a imagem do selo.
            with open("SJG.png", "rb") as img:
                img_base64 = base64.b64encode(img.read()).decode()
                # Exibe a imagem do selo usando HTML e base64.
                st.markdown(f"""
                    <div style="text-align:center;">
                        <img src="data:image/png;base64,{img_base64}" width="140"/>
                        <p><strong>Selo Verde Concedido</strong></p>
                    </div>
                """, unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("⚠ Imagem 'SJG.png' não encontrada. Verifique se o arquivo está no diretório correto.")
        except Exception as e:
            st.warning(f"⚠ Ocorreu um erro ao carregar a imagem: {e}")
    else:
        st.error("❌ Selo Verde não concedido.") # Mensagem de falha.

    st.markdown("### Critérios de Avaliação:") # Subtítulo para os critérios.
    # Exibe o status de cada critério.
    st.markdown(f"{'✅' if c1 else '❌'} Nenhum material ultrapassou o consumo médio.")
    st.markdown(f"{'✅' if c2 else '❌'} Emissão de CO₂ por m² ≤ 8 kg (Atual: {total_co2 / area_obra:.2f} kg)")
    st.markdown(f"{'✅' if c3 else '❌'} {perc_reaproveit:.1f}% dos materiais reaproveitáveis (Meta: ≥ 70%)")

    # Botão para baixar o relatório completo.
    st.download_button(
        label="Salvar Relatório (.txt)", # Texto do botão.
        data=analise.gerar_relatorio(df, c1, c2, c3, perc_reaproveit), # Dados do relatório.
        file_name=f"relatorio_residuos_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt", # Nome do arquivo.
        mime="text/plain" # Tipo MIME do arquivo.
    )
