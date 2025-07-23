
# 🏗️ Análise de Resíduos e Emissão de CO₂ na Construção Civil

Aplicação web interativa desenvolvida com Streamlit para estimar a geração de **resíduos** e **emissão de CO₂** em obras civis. O sistema avalia o impacto ambiental de diferentes materiais e verifica se a construção cumpre os critérios para receber um **Selo Verde** sustentável.

---

## 📌 Funcionalidades

- Cálculo de consumo, resíduo gerado e emissão de CO₂ por material.
- Interface intuitiva com gráficos e tabelas.
- Entrada de consumo personalizado.
- Avaliação automática do **Selo Verde**, com base em:
  - ✅ Nenhum material ultrapassou o consumo médio;
  - ✅ Emissão ≤ 8 kg CO₂ por m²;
  - ✅ ≥ 70% dos materiais com potencial de reuso ou reciclagem.
- Geração de relatório `.txt` detalhado com dados e critérios.

---

### 💻 Executar localmente

```bash
# Clone o repositório
git clone https://github.com/Grazielle506/analise-residuos-co2.git
cd analise-residuos-co2

# Instale as dependências
pip install -r requirements.txt

# Execute o app com Streamlit
streamlit run codigo_final.py
```

Isso abrirá automaticamente o app em seu navegador padrão.

---

- Python 3.8 ou superior
- Bibliotecas:
  - `streamlit`
  - `pandas`
  - `plotly`

Instale com:

```bash
pip install streamlit pandas plotly

```

## 🚀 Como usar
1. Adicionar a área da obra
2. Selecionar os materias utilizados
3. (Opcional) Editar a quantidade de cada material selecionado
4. (Opcional) Salvar relatório em .txt

## 📦 Requisitos

## 📂 Documentação e recursos

- 📄 [Documento de proposta técnica](https://www.overleaf.com/read/rjpnvmcbxvyq#49fcab)
- 🧑‍🏫 [Apresentação em LaTeX (slides)](https://www.overleaf.com/read/hrsqdfrmqnkk#684bc7)
- 🕸️ [Rede de Petri (normal)](https://drive.google.com/file/d/1MY0T63ELn8W_ZRVRhC-5RyLNm5gPAF8u/view?usp=sharing)
- 🎨 [Rede de Petri (colorida)](https://drive.google.com/file/d/1gwv8XoTsnVfUDbF2SAB93mW4EbUC-tCM/view?usp=sharing)

> **Nota:** Os arquivos de rede de Petri devem ser abertos com softwares compatíveis, como CPN Tools ou similares.

---

## 📄 Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).

---

## 👨‍💻 Autores

Sauán Mendes / Jéssica Ribeiro / Grazielle Santana 

GitHub: [@Grazielle506](https://github.com/Grazielle506)  
E-mail: graziellegpssantana@email.com
