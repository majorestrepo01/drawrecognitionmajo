import os
import base64
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from openai import OpenAI

# 1. Configuración de la página infantil
st.set_page_config(
    page_title="🎨 Cuentos Mágicos - Fábrica de Historias",
    page_icon="🦄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS Personalizados para Niños (Colores vibrantes y tarjetas lúdicas)
st.markdown("""
    <style>
    /* Fondo e importación de fuente divertida */
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Fredoka', cursive, sans-serif;
    }

    /* Banner Principal */
    .kids-banner {
        background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 50%, #A1C4FD 100%);
        padding: 30px;
        border-radius: 25px;
        color: #2D3748;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(255, 154, 158, 0.3);
    }
    .kids-banner h1 {
        font-size: 2.8rem;
        font-weight: 700;
        color: #4A5568 !important;
        margin-bottom: 10px;
    }
    .kids-banner p {
        font-size: 1.2rem;
        color: #4A5568 !important;
    }

    /* Tarjeta donde aparece la historia */
    .story-card {
        background-color: #FFFFFF;
        border: 3px solid #F6AD55;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 16px rgba(246, 173, 85, 0.2);
        margin-top: 15px;
        font-size: 1.15rem;
        line-height: 1.6;
        color: #2D3748;
    }

    /* Botón Mágico */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 15px 30px !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 18px rgba(255, 107, 107, 0.4) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 8px 22px rgba(255, 107, 107, 0.6) !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Función para codificar la imagen en Base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        return None

# 4. Banner de Encabezado
st.markdown("""
    <div class="kids-banner">
        <h1>✨ 🎨 Cuentos Mágicos 🦄 ✨</h1>
        <p>¡Dibuja lo que quieras en el tablero mágico y transformaremos tu dibujo en una fantástica historia!</p>
    </div>
""", unsafe_allow_html=True)

# 5. Barra Lateral
with st.sidebar:
    st.header("🔑 Clave Mágica & Pinceles")
    
    api_key_input = st.text_input("Ingresa tu OpenAI API Key:", type="password")
    
    st.markdown("---")
    st.subheader("🖍️ Herramientas de Dibujo")
    
    stroke_width = st.slider("Grosor del lápiz", 2, 25, 6)
    stroke_color = st.color_picker("Color de la pintura", "#FF007F")
    
    st.markdown("---")
    st.markdown("### 💡 ¿Cómo jugar?")
    st.markdown("""
    1. Elige tu color preferido.
    2. Dibuja un personaje, animal, objeto o lugar.
    3. Presiona el botón mágico para crear tu cuento.
    """)

# 6. Distribución de Pantalla
col_canvas, col_story = st.columns([1.1, 1], gap="large")

with col_canvas:
    st.subheader("🖍️ Tu Pizarra Mágica")
    
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#FFFFFF",
        height=380,
        width=480,
        drawing_mode="freedraw",
        key="canvas_kids",
    )
    
    st.caption("✨ ¡Usa tu imaginación para crear trazos increíbles!")

with col_story:
    st.subheader("📖 Tu Cuento Fantástico")
    st.write("Presiona el botón cuando tu dibujo esté listo:")
    
    create_story_btn = st.button("✨ ¡Crear mi Cuento Mágico! ✨")

    if create_story_btn:
        if not api_key_input:
            st.warning("⚠️ ¡Ups! Por favor ingresa tu clave API en el menú de la izquierda para comenzar la magia.")
        else:
            # Captura segura de la imagen del lienzo para evitar RuntimeError
            img_data = None
            if canvas_result is not None:
                try:
                    img_data = canvas_result.image_data
                except RuntimeError:
                    img_data = None

            # Verificación si el lienzo tiene dibujos registrados
            has_drawings = False
            if canvas_result is not None and canvas_result.json_data is not None:
                if len(canvas_result.json_data.get("objects", [])) > 0:
                    has_drawings = True

            if has_drawings or (img_data is not None and np.any(img_data)):
                with st.spinner("🧙‍♂️ El duende narrador está leyendo tu dibujo..."):
                    try:
                        # Guardar temporalmente la imagen procesada
                        input_numpy_array = np.array(img_data)
                        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
                        temp_image_path = "dibujo_niño.png"
                        input_image.save(temp_image_path)
                        
                        # Convertir a Base64
                        base64_image = encode_image_to_base64(temp_image_path)
                        
                        # Prompt enfocado en crear una historia infantil
                        prompt_infantil = (
                            "Eres un narrador de cuentos infantiles amable, alegre y muy imaginativo. "
                            "Observa detenidamente el dibujo realizado por un niño/a en la imagen. "
                            "Identifica qué elementos, figuras, personajes o formas dibujó. "
                            "A partir de lo que ves, inventa un cuento infantil corto, entretenido, dulce y lleno de fantasía en español. "
                            "Estructura el cuento con: "
                            "1. Un título creativo con emojis. "
                            "2. Un inicio mágico introduciendo al personaje u objeto dibujado. "
                            "3. Una pequeña aventura o nudo divertido. "
                            "4. Un final feliz y una linda enseñanza o moraleja final."
                        )

                        # Llamada a OpenAI
                        client = OpenAI(api_key=api_key_input)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_infantil},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{base64_image}"
                                            },
                                        },
                                    ],
                                }
                            ],
                            max_tokens=600,
                        )

                        historia = response.choices[0].message.content
                        
                        # Mostrar el resultado en la tarjeta infantil
                        st.markdown(f"""
                        <div class="story-card">
                            {historia}
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()

                    except Exception as e:
                        st.error(f"Hubo un pequeño problema al invocar la magia: {e}")
            else:
                st.warning("🎨 ¡La pizarra está en blanco! Haz un dibujo divertido antes de presionar el botón.")
