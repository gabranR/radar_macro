import streamlit as st
import pandas as pd
from pandas.api.types import CategoricalDtype
import altair as alt

# st.set_page_config(layout="wide")

# Carregando os dados
d23 = pd.read_csv("Base_Chegadas_2023.csv", sep=";", encoding="cp1252")
d24 = pd.read_csv("Base_Chegadas_2024_Acum_05_maio.csv", sep=";", encoding="cp1252")


data = pd.concat([d23, d24])
data["mes"] = data["mes"].replace("Marco", "Março")

meses = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
custom_dtype = CategoricalDtype(categories=meses, ordered=True)
data["mes"] = data["mes"].astype(custom_dtype)

vias = ["Aéreo", "Terrestre", "Marítimo", "Fluvial"]
custom_via = CategoricalDtype(categories=vias, ordered=True)
data["Via_de_acesso"] = data["Via_de_acesso"].astype(custom_via)


st.title("Análise de Chegadas de Turistas Internacionais no Brasil")


data_year1 = data[data["ano"] == 2023].groupby("mes")["Chegadas"].sum()
data_year2 = data[data["ano"] == 2024].groupby("mes")["Chegadas"].sum()


# Plotar o gráfico de linhas com Streamlit native

data_to_plot = pd.DataFrame({"2023": data_year1, "2024": data_year2[:5]})

# Plotar o gráfico de linhas com Streamlit native
st.subheader("Comparação de Chegadas por Mês")
st.line_chart(data_to_plot, color=["#0068c9", "#ff8700"])

data_year2_ = data_year2
data_year2_[5:] = "-"


percentage_variation = ((data_year2[:5] - data_year1[:5]) / data_year1) * 100

percentage_variation[5:13] = "-"

# st.subheader("Tabela de Chegadas por Mês")
table_data = {
    str(2023): data_year1,
    str(2024): data_year2_,
    "Variação (%)": percentage_variation,
}
df_table = pd.DataFrame(table_data)
st.dataframe(df_table.transpose(), height=150, use_container_width=True)

tri1 = sum(data_year1[:5])
tri2 = sum(data_year2[:5])

var = round(((tri2 - tri1) / tri1) * 100, 2)

st.write(
    f"Houve um aumento de **{var}%** do número de chegadas de turistas internacionais no primeiro quadrimestre de 2024 comparado ao mesmo período de 2023."
)

st.divider()

#####
access_proportions = data.groupby(["ano", "Via_de_acesso"]).size().unstack(fill_value=0)
access_proportions = access_proportions.div(access_proportions.sum(axis=1), axis=0)

# Reset index to make 'ano' a column
access_proportions = access_proportions.reset_index()

# Melt DataFrame to long format for Altair plotting
access_proportions_melted = access_proportions.melt(
    id_vars="ano", var_name="Via_de_acesso", value_name="Proporção"
)


access_proportions_melted["Proporção"] = round(
    access_proportions_melted["Proporção"] * 100, 2
)

access_proportions_melted["Via_de_acesso"] = pd.Categorical(
    access_proportions_melted["Via_de_acesso"], categories=vias
)

st.subheader("Proporção da Via de Acesso para cada Ano")
# Create Altair chart object
chart = (
    alt.Chart(access_proportions_melted)
    .mark_bar()
    .encode(
        x=alt.X("ano:O", title="Mês", axis=alt.Axis(labelAngle=0)),
        order=alt.Order(
            "Proporção:Q",
            sort="ascending",
        ),
        y=alt.Y(
            "Proporção:Q",
            stack="normalize",
            axis=alt.Axis(format="%"),
            title="Proporção",
        ),
        color=alt.Color("Via_de_acesso:N", legend=alt.Legend(title="Via de Acesso")),
        tooltip=["Via_de_acesso", "Proporção"],
    )
    .properties(height=400)
)

access_proportions_melted["altext"] = access_proportions_melted["Proporção"] / 100

text = chart.mark_text(
    align="center",
    size=15,
    baseline="middle",
    dx=0,  # Adjust the horizontal position of the text
    dy=-5,  # Adjust the vertical position of the text
    color="black",  # Text color
    fontWeight="bold",
).encode(
    text=alt.Text("altext:Q", format=".2%")
    # Display proportion values with two decimal places
)

# Combine chart and annotations
chart = chart + text


# Display Altair chart using st.altair_chart
st.altair_chart(chart, use_container_width=True)

# Select unique years
years = sorted(data["ano"].unique())
st.divider()
# Display tables for each year side by side
st.subheader("Ranking dos principais países emissores de turistas para o Brasil")
col1, col2 = st.columns(2)

# Iterate through each year and display table
for year, col in zip(years, [col1, col2]):
    with col:
        st.subheader(f"{year}")

        # Filter data for the current year
        year_data = data[data["ano"] == year]

        # Group data by country and calculate total arrivals
        top_countries = year_data.groupby("nome_pais_correto")["Chegadas"].sum()

        # Sort countries by total arrivals in descending order
        top_countries = top_countries.sort_values(ascending=False)

        # Select top 10 countries
        top_10_countries = top_countries.head(10)

        # Create DataFrame for top 10 countries
        top_10_df = pd.DataFrame(
            {"País": top_10_countries.index, "Chegadas": top_10_countries.values},
            index=list(range(1, 11)),
        )

        # Display table for the current year
        st.dataframe(top_10_df)

################


st.divider()
st.subheader("Ranking de UFs que mais receberam Turistas Internacionais")
col3, col4 = st.columns(2)


# Iterate through each year and display table
for year, col in zip(years, [col3, col4]):
    with col:
        st.subheader(f"{year}")

        # Filter data for the current year
        year_data = data[data["ano"] == year]

        # Group data by country and calculate total arrivals
        top_countries = year_data.groupby("UF")["Chegadas"].sum()

        # Sort countries by total arrivals in descending order
        top_countries = top_countries.sort_values(ascending=False)

        # Select top 10 countries
        top_10_countries = top_countries.head(10)

        # Create DataFrame for top 10 countries
        top_10_df = pd.DataFrame(
            {
                "UF de Desembarque": top_10_countries.index,
                "Chegadas": top_10_countries.values,
            },
            index=list(range(1, 11)),
        )

        # Display table for the current year
        st.dataframe(top_10_df)

#############


st.divider()

st.write(
    "_Fonte: Dados dispoinibilizados pela Polícia Federal com tratamento e cálculo feitos pela CGINT/SNPTur/Mtur._"
)
