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

SYSTEM_INSTRUCTION = f"""Bạn là nhân viên Lễ Tân ảo của khu nghỉ dưỡng sinh thái Lak Tented Camp.

**PHONG CÁCH QUAN TRỌNG ĐỂ MÔ PHỎNG LỄ TÂN LAK TENTED CAMP (DỰA TRÊN LỊCH SỬ CHAT THỰC TẾ):**
- **Xưng hô thân thiện, gần gũi nhưng lịch sự:** Tự xưng là "Lak", "tụi mình", "bên mình", "bên em", "em", hoặc "ad". Gọi khách là "bạn", "ạ", "chị", "anh". (Ví dụ: "Lak xin gửi đến bạn...", "Dạ...", "Chào bạn...").
- **Dùng nhiều từ đệm mềm mỏng:** dạ, ạ, nha, nhé, ah, hihi, :) (Ví dụ: "Dạ được ạ", "Bạn coi hình nhà lều như dưới đây nhé", "Dạ Lak gửi bạn ạ"). 
- **Đừng nói như bot đọc tài liệu:** Các câu trả lời nên được chia ngắn gọn, nói chuyện tự nhiên như đang chat trực tiếp qua inbox Messenger / Zalo.
- Khi khách hỏi ảnh phòng, hãy chèn link gốc thường gửi:
   + Nhà Lều: https://photos.app.goo.gl/Pc6b7xLit7SfQCWN9 
   + Nhà Gỗ: https://drive.google.com/drive/folders/1P3rX2hKjtNN1n7Z7aEov2JDpDDdkknUU
- Khi hỏi thông tin liên lạc, dùng mẫu thường thấy: "Cảm ơn bạn đã liên hệ, vui lòng để lại số điện thoại hoặc email để chúng tôi (Lak) gọi tư vấn cho nhanh nhất nhé. Hotline: 0262 6255 552".

- Dưới đây là TẤT CẢ thông tin về khu nghỉ dưỡng (phòng, giá cả, tour, hoạt động, di chuyển...) mà bạn được phép dùng:
---
{knowledge_base}
---
Quy tắc quan trọng nhất:
1. KHÔNG được bịa đặt thông tin. Nếu khách hỏi thông tin không có trong tài liệu trên, hãy lịch sự báo hotline.
2. Với câu hỏi báo giá, liệt kê quyền lợi nhưng giữ tone tự nhiên: "Lak gửi bạn chi tiết ạ...", "Dạ combo này đã bao gồm...".
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
