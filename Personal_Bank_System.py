import streamlit as st
import random
import string
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai
from datetime import datetime

# --- 🔐 CONFIGURATION (Update these) ---
OPENAI_API_KEY = "sk-proj-..."           # ← Your OpenAI API key
SENDER_EMAIL = "you@gmail.com"           # ← Your Gmail
SENDER_PASSWORD = "your-app-password"    # ← Gmail App Password

openai.api_key = OPENAI_API_KEY

# Set page config
st.set_page_config(page_title="🏦 MyBank Pro", layout="centered")

# Initialize session state
initial_state = {
    'verified': False,
    'balance': 0,
    'name': '',
    'mobile': '',
    'email': '',
    'otp': '',
    'setup_complete': False,
    'chat_history': [],
    'transaction_history': [],
    'email_sent': False,
    'dark_mode': False,  # New: dark mode toggle
}

for key, value in initial_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Function: Generate OTP
def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

# Function: Send OTP via Email
def send_otp_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = "🔐 Your MyBank OTP Code"

        body = f"""
        Hello {st.session_state.name},

        Your OTP is: **{otp}**

        Thank you,
        MyBank Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {str(e)}")
        return False

# Function: Get AI Response from ChatGPT
def get_ai_response(user_input):
    try:
        context = f"""
        You are MyBank Assistant. User: {st.session_state.name}, Balance: ₹{st.session_state.balance:,}
        Be helpful, short, and clear.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                *[{"role": m["role"], "content": m["text"]} for m in st.session_state.chat_history[-5:]],
                {"role": "user", "content": user_input}
            ],
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# --- 🌙 DARK MODE CSS ---
def inject_dark_mode_css():
    dark_css = """
    <style>
        .stApp {
            background-color: #111 !important;
            color: #eee;
        }
        .css-1d391kg, .css-1v3fvcr, .css-1l02zno {
            background-color: #111 !important;
        }
        .stTextInput > div > div > input,
        .stTextInput > div > div > input:focus {
            color: #fff !important;
            background-color: #333 !important;
            border: 1px solid #555 !important;
        }
        .stButton>button {
            font-size: 18px !important;
            padding: 12px 20px !important;
            border-radius: 10px !important;
        }
        h1, h2, h3, h4, h5, h6, .stMarkdown, label {
            color: #eee !important;
        }
        .stAlert {
            background-color: #222 !important;
            color: #ddd !important;
            border: 1px solid #444 !important;
        }
    </style>
    """
    st.markdown(dark_css, unsafe_allow_html=True)

# Apply dark mode if enabled
if st.session_state.dark_mode:
    inject_dark_mode_css()

# --- HEADER & THEME TOGGLE ---
col_title, col_theme = st.columns([3, 1])

with col_title:
    st.title("🏦 MyBank Pro")
    st.subheader("AI Banking on Mobile")

with col_theme:
    st.write("")
    if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# --- Sidebar: AI Chat + Transactions ---
with st.sidebar:
    st.markdown("### 💬 AI Assistant")

    for message in st.session_state.chat_history:
        role = "🧑 You" if message["role"] == "user" else "🤖 AI"
        st.markdown(f"**{role}:** {message['text']}")
        st.markdown("---")

    user_question = st.text_input("Ask your banker:", key="ai_q")
    if st.button("📤 Send"):
        if user_question.strip():
            st.session_state.chat_history.append({"role": "user", "text": user_question})
            with st.spinner("🧠 Thinking..."):
                reply = get_ai_response(user_question)
            st.session_state.chat_history.append({"role": "assistant", "text": reply})
            st.rerun()
        else:
            st.warning("Type a question.")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")

    # Transaction History
    st.markdown("### 📜 Recent Activity")
    if st.session_state.transaction_history:
        for tx in reversed(st.session_state.transaction_history[-6:]):
            st.markdown(f"- 💹 {tx['type'].title()}: ₹{tx['amount']:,} | {tx['time']}")
    else:
        st.markdown("*No transactions yet.*")

# ---- STEP 1: Account Setup ----
if not st.session_state.setup_complete:
    st.markdown("### 📝 Create Your Account")
    name = st.text_input("Full Name:")
    mobile = st.text_input("Mobile (10 digits):")
    email = st.text_input("Email (for OTP):")

    if st.button("🚀 Create Account"):
        name_clean = name.strip()
        if not name_clean.isalpha() and not all(c.isalpha() or c.isspace() for c in name_clean):
            st.error("❌ Name can only have letters and spaces.")
        elif not mobile.isdigit() or len(mobile) != 10:
            st.error("❌ Enter valid 10-digit mobile.")
        elif "@" not in email:
            st.error("❌ Enter valid email.")
        else:
            st.session_state.name = name_clean.title()
            st.session_state.mobile = mobile
            st.session_state.email = email
            st.session_state.setup_complete = True
            st.session_state.balance = 0
            st.success(f"✅ Account created, {st.session_state.name}!")
            st.rerun()

# ---- STEP 2: Email OTP Verification ----
elif not st.session_state.verified:
    st.markdown(f"### 🔐 Verify: {st.session_state.email}")

    if st.button("📨 Send OTP") or st.session_state.email_sent:
        if not st.session_state.email_sent:
            otp = generate_otp()
            st.session_state.otp = otp
            if send_otp_email(st.session_state.email, otp):
                st.session_state.email_sent = True
                st.success("✅ OTP sent!")
                st.info(f"💡 Simulated: `{otp}`")
            else:
                st.session_state.email_sent = False
        else:
            st.info("OTP already sent.")

    user_otp = st.text_input("Enter 6-digit OTP:")
    if st.button("Verify OTP"):
        if user_otp == st.session_state.otp and len(user_otp) == 6:
            st.session_state.verified = True
            st.session_state.email_sent = False
            st.success("✅ Verified! Welcome.")
            st.rerun()
        else:
            st.error("❌ Invalid OTP.")

# ---- STEP 3: Banking Dashboard ----
else:
    st.markdown(f"<h3 style='color:#4CAF50;'>✅ Hi, {st.session_state.name}!</h3>", unsafe_allow_html=True)
    st.markdown(f"📱 {st.session_state.mobile} | ✉️ {st.session_state.email}")
    st.markdown("---")

    st.markdown(f"<h4 style='color:#2196F3;'>💰 Balance: ₹{st.session_state.balance:,}</h4>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 💵 Deposit")
        credit_amount = st.number_input("Amount", min_value=0, step=10, key="dep")
        if st.button("➕ Deposit", use_container_width=True):
            if credit_amount > 0:
                st.session_state.balance += credit_amount
                st.session_state.transaction_history.append({
                    "type": "deposit",
                    "amount": credit_amount,
                    "time": datetime.now().strftime("%H:%M")
                })
                st.success(f"✅ ₹{credit_amount} added!")
                time.sleep(1.2)
                st.rerun()
            else:
                st.warning("⚠️ Enter amount.")

    with col2:
        st.markdown("### 💸 Withdraw")
        debit_amount = st.number_input("Amount", min_value=0, step=10, key="wd")
        if st.button("➖ Withdraw", use_container_width=True):
            if debit_amount > 0:
                if debit_amount <= st.session_state.balance:
                    st.session_state.balance -= debit_amount
                    st.session_state.transaction_history.append({
                        "type": "withdrawal",
                        "amount": debit_amount,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.success(f"✅ ₹{debit_amount} withdrawn!")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error("❌ Low balance!")
            else:
                st.warning("⚠️ Enter amount.")

    st.markdown("---")

    if st.button("🔚 Logout", use_container_width=True):
        for key in initial_state:
            st.session_state[key] = initial_state[key]
        st.success("👋 See you soon!")
        st.rerun()

    st.markdown("<center><small>📱 This app works perfectly on mobile!</small></center>", unsafe_allow_html=True)
