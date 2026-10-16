import streamlit as st
from PIL import Image
import pandas as pd
import google.generativeai as genai
import json
import os

# Pega a chave de API configurada no painel de Segredos do Streamlit
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

st.title("Captura de Dados para Excel")

img_file_buffer = st.camera_input("Tire uma foto do item/documento")

if img_file_buffer is not None:
    image = Image.open(img_file_buffer)
    st.image(image, caption="Foto Capturada", use_column_width=True)
    
    with st.spinner("Analisando com IA..."):
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Analise esta imagem e extraia APENAS o 'Nome' e o 'Código'.
        Retorne a resposta estritamente no formato JSON:
        {
            "nome": "Texto do Nome",
            "codigo": "Texto do Codigo"
        }
        """
        response = model.generate_content([prompt, image])
        
        try:
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(cleaned_response)
            
            st.success("Dados Extraídos!")
            st.json(data)
            
            # Salva ou atualiza a planilha
            file_path = "dados_extraidos.xlsx"
            new_entry = pd.DataFrame([data])
            
            if os.path.exists(file_path):
                df_existing = pd.read_excel(file_path)
                df_final = pd.concat([df_existing, new_entry], ignore_index=True)
            else:
                df_final = new_entry
                
            df_final.to_excel(file_path, index=False)
            
            st.download_button(
                label="Baixar Excel Atualizado",
                data=open(file_path, "rb"),
                file_name="dados_extraidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
