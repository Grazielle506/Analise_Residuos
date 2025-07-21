# === IMPORTAÇÃO DE BIBLIOTECAS ===
import streamlit as st             # Para criar interface web interativa
import pandas as pd               # Para manipulação de tabelas (DataFrames)
import plotly.express as px       # Para criar gráficos interativos com visual moderno
from datetime import datetime     # Para registrar data e hora no relatório
import base64                     # Para converter imagem do selo em base64 e exibir no app

# === DEFINIÇÃO DOS DADOS DOS MATERIAIS ===
# Cada material tem: consumo padrão, unidade, densidade (se m³), fator de emissão de CO₂, percentual de desperdício, instruções de reuso e descarte
materiais = {
    "Concreto": {
        "consumo": 0.05, "un": "m³/m²", "densidade": 2400, "co2": 0.15,
        "desperdicio": 0.12, "reuso": "Pode ser triturado", "descarte": "Descarte em caçambas"
    },
    "Cimento": {
        "consumo": 15, "un": "kg/m²", "co2": 0.85,
        "desperdicio": 0.10, "reuso": "Usar em argamassa", "descarte": "Evitar solo e água"
    },
    "Aço": {
        "consumo": 20, "un": "kg/m²", "co2": 1.80,
        "desperdicio": 0.07, "reuso": "100% reciclável", "descarte": "Enviar para reciclagem"
    }
}

# === CONFIGURAÇÃO INICIAL DA PÁGINA STREAMLIT ===
st.set_page_config(page_title="Análise Preliminar", layout="centered")
st.title("♻️ Análise Preliminar de Resíduos e CO₂")

# === ENTRADA DE DADOS PELO USUÁRIO ===
# Solicita ao usuário a área da obra em m²
area = st.number_input("Área da obra (m²):", min_value=1.0, value=100.0)

# Permite que o usuário selecione os materiais a serem analisados
selecionados = st.multiselect("Materiais:", list(materiais.keys()))

# === VERIFICA SE ALGUM MATERIAL FOI SELECIONADO ===
if selecionados:
    st.subheader("🔧 Personalize o consumo (ou use o padrão)")

    resultados = []  # Lista para armazenar os dados calculados

    # === LOOP PARA CADA MATERIAL SELECIONADO ===
    for mat in selecionados:
        info = materiais[mat]
        consumo_padrao = info["consumo"]
        un = info["un"]
        densidade = info.get("densidade", 1)

        # Permite ao usuário ajustar o consumo manualmente
        valor = st.number_input(
            f"{mat} ({un}, padrão: {consumo_padrao})",
            min_value=0.0, value=float(consumo_padrao), key=mat
        )

        # Cálculo do consumo total com base na área
        consumo_total = valor * area

        # Conversão para kg se a unidade for m³
        consumo_kg = consumo_total * densidade if un == "m³/m²" else consumo_total

        # Cálculo do resíduo gerado com base no desperdício
        residuo = consumo_kg * info["desperdicio"]

        # Cálculo da emissão de CO₂ associada ao resíduo
        co2_total = residuo * info["co2"]

        # Verifica se o consumo foi maior que o padrão
        excedeu = valor > consumo_padrao

        unidade_total = un.split("/")[0]  # Ex: "m³", "kg"

        # Armazena todos os resultados em formato de dicionário
        resultados.append({
            "Material": mat,
            "Consumo Total (un)": f"{consumo_total:,.2f} {unidade_total}",
            "Consumo (kg)": f"{consumo_kg:,.2f} kg",
            "Resíduo (kg)": f"{residuo:,.2f} kg",
            "CO₂ (kg)": f"{co2_total:,.2f} kg",
            "Reutilização": info["reuso"],
            "Descarte": info["descarte"],
            "Excedeu": excedeu,
            "CO2_ValorBruto": co2_total  # usado internamente para cálculo
        })

    # === CRIAÇÃO DO DATAFRAME COM OS RESULTADOS ===
    df = pd.DataFrame(resultados)

    # === EXIBIÇÃO DA TABELA NA TELA ===
    st.subheader("📊 Resultado com Unidades")
    st.dataframe(df[["Material", "Consumo Total (un)", "Consumo (kg)", "Resíduo (kg)", "CO₂ (kg)", "Reutilização", "Descarte"]])

    # === GRÁFICO DE RESÍDUO E CO₂ ===
    st.subheader("📈 Gráfico de Resíduos e CO₂")

    # Prepara os dados para o gráfico em formato "long"
    df_plot = df[["Material", "Resíduo (kg)", "CO₂ (kg)"]].copy()
    df_plot = df_plot.melt(id_vars="Material", var_name="variable", value_name="value")
    df_plot["value"] = df_plot["value"].str.replace(" kg", "").str.replace(",", "").astype(float)

    # Gera o gráfico de colunas agrupadas com tema escuro
    fig = px.bar(
        df_plot,
        x="Material",
        y="value",
        color="variable",
        barmode="group",
        template="plotly_dark",
        color_discrete_map={
            "Resíduo (kg)": "#87CEFA",  # azul claro
            "CO₂ (kg)": "#0066CC"       # azul escuro
        }
    )

    # Ajusta rótulos e estilo do gráfico
    fig.update_layout(
        yaxis_title=None,
        xaxis_title="Material",
        legend_title="variable",
        font=dict(size=14),
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
    )

    # Exibe o gráfico na aplicação
    st.plotly_chart(fig, use_container_width=True)

    # === AVALIAÇÃO DO SELO VERDE ===
    st.subheader("🌱 Critérios do Selo Verde")

    total_co2 = df["CO2_ValorBruto"].sum()

    c1 = not df["Excedeu"].any()  # Nenhum material ultrapassou consumo padrão
    c2 = (total_co2 / area) <= 8  # CO₂ por m² está abaixo de 8
    c3 = df["Reutilização"].str.contains("reutil|recicl|usar", case=False).sum() / len(df) >= 0.7  # ≥ 70% reaproveitáveis

    # Se todos os critérios forem atendidos, exibe selo verde com imagem
    if c1 and c2 and c3:
        st.success("✅ Selo Verde Concedido!")
        try:
            with open("SJG.png", "rb") as img:
                img_base64 = base64.b64encode(img.read()).decode()
                st.markdown(f"""
                    <div style="text-align:center;">
                        <img src="data:image/png;base64,{img_base64}" width="140"/>
                        <p><strong>Selo Verde Concedido</strong></p>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.warning("⚠ Imagem 'SJG.png' não encontrada.")
    else:
        st.error("❌ Selo Verde NÃO Concedido")

    # Exibe quais critérios foram ou não cumpridos
    st.markdown("### ✅ Avaliação dos Critérios:")
    st.markdown(f"- {'✅' if c1 else '❌'} Nenhum material ultrapassou o consumo padrão")
    st.markdown(f"- {'✅' if c2 else '❌'} CO₂ por m² ≤ 8 kg (Atual: {total_co2 / area:.2f} kg)")
    st.markdown(f"- {'✅' if c3 else '❌'} Pelo menos 70% dos materiais são reaproveitáveis")

    # === RELATÓRIO FINAL EM TXT PARA DOWNLOAD ===
    st.subheader("📄 Baixar Relatório")

    # Cria texto linha a linha com os dados da análise
    texto_materiais = "\n".join([
        f"- {row['Material']}: {row['Consumo Total (un)']}, {row['Consumo (kg)']}, Resíduo: {row['Resíduo (kg)']}, CO₂: {row['CO₂ (kg)']}"
        for _, row in df.iterrows()
    ])

    resumo = f"""Relatório - Análise de Resíduos
Data: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Área analisada: {area:.2f} m²

--- Materiais ---
{texto_materiais}

--- Critérios do Selo Verde ---
- {'✅' if c1 else '❌'} Nenhum material excedeu o consumo padrão
- {'✅' if c2 else '❌'} Emissão de CO₂ por m² ≤ 8 kg (Atual: {total_co2 / area:.2f} kg)
- {'✅' if c3 else '❌'} Mínimo de 70% de reaproveitamento

Resultado final: {'✅ Selo CONCEDIDO' if c1 and c2 and c3 else '❌ Selo NÃO CONCEDIDO'}
"""

    # Botão para o usuário baixar o relatório como .txt
    st.download_button("📥 Baixar .txt", data=resumo, file_name="relatorio_residuos.txt", mime="text/plain")

else:
    # Se nenhum material for selecionado, exibe aviso
    st.info("Selecione pelo menos um material para continuar.")
