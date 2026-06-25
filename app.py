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
    /* Hide default headers and footers */
    header, footer, [data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    
    /* Logo styling */
    .logo-container-landing {
        text-align: center;
        margin-top: 22vh;
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
    }
    .bot-bubble {
        background-color: transparent;
        color: #ECECF1;
        padding: 12px 0px;
        max-width: 85%;
        font-size: 16px;
    }
    
    /* Style custom error card */
    .error-card {
        background-color: rgba(255, 75, 75, 0.1);
        border: 1px solid #FF4B4B;
        color: #FF4B4B;
        padding: 15px;
        border-radius: 12px;
        margin-top: 10px;
        font-weight: 500;
    }

    /* PREMIUM OVAL CAPSULE INPUT WITH REMOVED BORDERS */
    [data-testid="stChatInput"] {
        border-radius: 35px !important;
        overflow: hidden !important;
        background-color: #2F2F2F !important;
        padding: 4px 10px !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 35px !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Completely kill focused red outlines when clicking inside the input box */
    [data-testid="stChatInput"]:focus-within {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. AUTOMATIC SECRET KEY DETECTION
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # 4. DYNAMIC LOGO HANDLING
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

        # 5. RENDER CUSTOM ALIGNED BUBBLES WITH NO ICONS
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
                    st.write(message["content"])
                    st.markdown('</div></div>', unsafe_allow_html=True)
                elif message["type"] == "image":
                    img = Image.open(io.BytesIO(message["content"]))
                    st.image(img, use_container_width=True)

        # 6. INTEGRATE THE ANCHORED CHAT INPUT
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
                except Exception as img_err:
                    st.error(f"Image Engine Error: {img_err}")
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
                            '<div class="error-card">⚠️ Overloaded cloud channels. Please wait 5 seconds and click send again.</div>', 
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
