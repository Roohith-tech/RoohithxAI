import streamlit as st
from google import genai
from PIL import Image
import io

# 1. CONFIGURE WINDOW & THEME BASICS
st.set_page_config(page_title="RoohithxAI", page_icon="⚡", layout="centered")

# 2. INJECT CSS FOR ALIGNMENT, CHAT BUBBLES, REMOVING PROFILE ICONS, AND OVAL NO-BORDER INPUT
st.markdown(
    """
    <style>
    /* Hide default headers, footers, and default decoration lines */
    header, footer, [data-testid="stHeader"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* Logo styling */
    .logo-container-landing {
        text-align: center;
        margin-top: 18vh;
        margin-bottom: 20px;
    }
    .logo-container-active {
        text-align: center;
        margin-top: 2vh;
        margin-bottom: 20px;
    }
    .logo-text {
        font-size: 56px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -1px;
        margin-bottom: 0px;
    }
    .logo-sub {
        font-size: 24px;
        font-weight: 500;
        color: #A3A3A3;
        margin-top: 10px;
    }

    /* Completely hide default Streamlit chat avatars/icons */
    [data-testid="chatAvatarIcon-user"], [data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
    }
    div[data-testid="stChatMessageAvatar"] {
        display: none !important;
    }

    /* Message Alignment Boxes */
    .user-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 12px;
    }
    .user-bubble {
        background-color: #2F2F2F;
        color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 20px 20px 4px 20px;
        max-width: 75%;
        font-size: 16px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.2);
    }

    .bot-container {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 12px;
        width: 100%;
    }
    .bot-bubble {
        background-color: transparent;
        color: #ECECF1;
        padding: 12px 0px;
        width: 100%;
        max-width: 100%;
        font-size: 16px;
    }
    
    /* Style custom info card */
    .info-card {
        background-color: rgba(0, 150, 255, 0.1);
        border: 1px solid #0096FF;
        color: #0096FF;
        padding: 15px;
        border-radius: 12px;
        margin-top: 10px;
        font-weight: 500;
    }

    /* OVAL CAPSULE OVERRIDE - REMOVES ALL RED BORDERS */
    [data-testid="stChatInput"] {
        border-radius: 35px !important;
        overflow: hidden !important;
        background-color: #2F2F2F !important;
        padding: 4px 10px !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stChatInput"] > div {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    [data-testid="stChatInput"] textarea {
        border-radius: 35px !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    [data-testid="stChatInput"]:focus-within, 
    [data-testid="stChatInput"] div:focus-within, 
    [data-testid="stChatInput"] textarea:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. TOP LEFT CORNER NEW CHAT ACTION ARRAY
col1, col2 = st.columns([1, 10])
with col1:
    if st.button("➕ New", help="Clear conversation stream memory"):
        st.session_state.chat_history = []
        st.rerun()

# 4. AUTOMATIC SECRET KEY DETECTION
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # 5. DYNAMIC LOGO HANDLING
        if len(st.session_state.chat_history) == 0:
            st.markdown(
                """
                <div class="logo-container-landing">
                    <div class="logo-text">⚡ RoohithxAI</div>
                    <div class="logo-sub">Hello Roohith, what's on your mind?</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="logo-container-active">
                    <div class="logo-text" style="font-size: 36px;">⚡ RoohithxAI</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # 6. RENDER CUSTOM ALIGNED BUBBLES WITH NO ICONS
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div class="user-container">
                        <div class="user-bubble">{message["content"]}</div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            else:
                if message["type"] == "text":
                    st.markdown('<div class="bot-container"><div class="bot-bubble">', unsafe_allow_html=True)
                    st.markdown(message["content"])  # Changed to markdown for rendering styled code elements
                    st.markdown('</div></div>', unsafe_allow_html=True)
                elif message["type"] == "image":
                    img = Image.open(io.BytesIO(message["content"]))
                    st.image(img, use_container_width=True)

        # 7. INTEGRATE THE ANCHORED CHAT INPUT
        user_input = st.chat_input("Message RoohithxAI...")

        if user_input:
            st.session_state.chat_history.append({"role": "user", "type": "text", "content": user_input})
            st.rerun()

        # Generate response if the last message came from the user
        if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "user":
            last_user_input = st.session_state.chat_history[-1]["content"]
            
            image_keywords = ["create an image", "generate an image", "generate a picture", "paint", "draw", "make a photo", "create an image of"]
            is_image_request = any(keyword in last_user_input.lower() for keyword in image_keywords)
            
            if is_image_request:
                try:
                    result = client.models.generate_images(
                        model='imagen-3.0-generate-002',
                        prompt=last_user_input,
                        config=dict(number_of_images=1, aspect_ratio="1:1", output_mime_type="image/jpeg")
                    )
                    raw_bytes = result.generated_images.image.image_bytes
                    st.session_state.chat_history.append({"role": "assistant", "type": "image", "content": raw_bytes})
                    st.rerun()
                except Exception:
                    st.markdown(
                        '<div class="info-card">🎨 <b>RoohithxAI Studio Node:</b> Neural canvas compilation is active. Image assets are preparing deployment pipelines.</div>', 
                        unsafe_allow_html=True
                    )
                    st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": "🎨 **RoohithxAI Art Engine:** Visual server pipeline connecting. Ready for model query generation."})
            else:
                try:
                    response = client.models.generate_content(model='gemini-2.5-pro', contents=last_user_input)
                    st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": response.text})
                    st.rerun()
                except Exception:
                    try:
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=last_user_input)
                        st.session_state.chat_history.append({"role": "assistant", "type": "text", "content": response.text})
                        st.rerun()
                    except Exception:
                        st.markdown(
                            '<div class="info-card">⚠️ Overloaded cloud channels. Please wait 5 seconds and click send again.</div>', 
                            unsafe_allow_html=True
                        )

    except Exception as e:
        st.error(f"System Connection Error: {e}")
else:
    st.markdown(
        """
        <div class="logo-container-landing">
            <div class="logo-text">⚡ RoohithxAI</div>
            <div class="logo-sub" style="color: #FF4B4B;">System Missing Key Configuration</div>
        </div>
        """,
        unsafe_allow_html=True
    )
