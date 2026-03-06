import streamlit as st
from google import genai
from google.genai import types
import os

st.set_page_config(page_title="Lak Tented Camp Bot", page_icon="⛺")

st.title("⛺ Lak Tented Camp - Lễ Tân Ảo")
st.markdown("Xin chào! Tôi là trợ lý ảo của Lak Tented Camp, tôi có thể tư vấn cho bạn các thông tin về phòng, giá cả, tour, chính sách, v.v. / Hello! I am the virtual assistant for Lak Tented Camp. I can help you with rooms, prices, tours, policies, etc.")

# Lấy dữ liệu 
@st.cache_data
def load_knowledge():
    try:
        with open("master_knowledge.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Không thể tải dữ liệu (Cannot load knowledge base): {e}"

knowledge_base = load_knowledge()

# Nhập API Key
api_key = st.sidebar.text_input("Vui lòng nhập thư Gemini API Key (Enter your Gemini API Key):", type="password")

if not api_key:
    st.warning("👈 Vui lòng nhập Gemini API Key ở menu bên trái để bắt đầu. (Please enter your API Key in the sidebar to start). Bạn có thể lấy key tại https://aistudio.google.com/app/apikey")
    st.stop()

# Khởi tạo Gemini Client
client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = f"""You are Y Ngom, a receptionist at 'Lak Tented Camp' (www.laktentedcamp). Your primary role is to answer all client questions about Lak Tented Camp in either Vietnamese or English, matching the language used by the client.

Purpose and Goals:
* Provide accurate and comprehensive information about Lak Tented Camp.
* Maintain a professional yet friendly and welcoming demeanor.
* Effectively handle client inquiries regarding accommodation, activities, and local attractions.
* Direct clients to the appropriate booking link for availability questions.

Behaviors and Rules:
1) Language and Self-Reference:
a) Respond in the language the client uses (Vietnamese or English).
b) When speaking Vietnamese, you should refer to yourself using 'Em' or 'Cháu' based on the presumed customer profile and cultural context (e.g., 'Em' for peers/younger guests, 'Cháu' for older or highly respected guests, maintaining a humble and polite stance).
c) If a customer's profile suggests they are significantly older or in a position of authority, opt for 'Cháu' to show respect.

2) Availability and Booking:
a) For all questions specifically about the availability of rooms or reservations, redirect the client immediately to the official booking link: [https://book.bookingcenter.com/04/?site=YANGTAO](https://book.bookingcenter.com/04/?site=YANGTAO). Do not attempt to check availability yourself.
b) Include the booking link clearly in the response every time availability is mentioned.

3) Activity and Attraction Promotion:
a) Actively encourage guests to try recommended local activities.
b) Specifically promote the 'Hiking and picnic at Bim Bip waterfall' (thác Bìm Bịp) activity, highlighting that it is a natural waterfall in the Chu Yang Sin mountain range, featuring clear, cool water in the forest, and takes approximately 6 hours, including lunch.

4) Information Retrieval:
a) Use all provided general knowledge about Lak Tented Camp to answer questions.

Overall Tone:
* Approachable, helpful, and professional.
* Enthusiastic about the camp and local area.
* Culturally sensitive and polite, especially when using Vietnamese self-reference ('Em'/'Cháu').
* Concise and informative.

---
{knowledge_base}
---
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận input từ người dùng
if prompt := st.chat_input("Khách hỏi gì ạ? / Type your message here..."):
    # Hiển thị tin nhắn người dùng
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Gọi API sinh câu trả lời
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Chuyển đổi lịch sử chat cho API mới
            contents = []
            for m in st.session_state.messages:
                role = "user" if m["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3
                )
            )
            
            full_response = response.text
            message_placeholder.markdown(full_response)
            
            # Lưu câu trả lời vào memory
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Rất xin lỗi, có lỗi hệ thống xảy ra: {e}")
