import streamlit as st
import random
import string
import time

# Set page configuration
st.set_page_config(page_title="🏦 MyBank - With Smart Assistant", layout="centered")

# Initialize session state
initial_state = {
    'verified': False,
    'balance': 0,
    'name': '',
    'mobile': '',
    'otp': '',
    'setup_complete': False,
    'chat_history': [],  # To store chat messages
}

for key, value in initial_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Function to generate a 6-character OTP
def generate_otp():
    characters = string.digits + string.ascii_uppercase + string.ascii_lowercase
    return ''.join(random.choices(characters, k=6))

# Smart Chatbot Response Function
def get_bot_response(user_input):
    user_input = user_input.lower().strip()
    balance = st.session_state.balance
    name = st.session_state.name or "User"

    # Check balance
    if 'balance' in user_input or 'check balance' in user_input or 'my money' in user_input:
        return (
            f"💰 **Your Current Balance is: ₹{balance:,}**\n\n"
            "You can always see this at the top of your dashboard."
        )

    # Deposit help
    elif 'deposit' in user_input or 'add money' in user_input or 'credit' in user_input:
        return (
            "💵 **To Deposit Money:**\n"
            "1. Go to the **Deposit section** on the screen\n"
            "2. Enter the amount you want to add\n"
            "3. Click the **➕ Deposit** button\n\n"
            "✅ The balance will update instantly!"
        )

    # Withdraw help
    elif 'withdraw' in user_input or 'withdraw money' in user_input or 'take out' in user_input or 'debit' in user_input:
        return (
            "💸 **To Withdraw Money:**\n"
            "1. Go to the **Withdraw section**\n"
            "2. Enter the amount you wish to withdraw\n"
            "3. Click the **➖ Withdraw** button\n\n"
            "⚠️ Make sure you have enough balance to avoid errors."
        )

    # Help / menu
    elif 'help' in user_input or 'menu' in user_input or 'options' in user_input or 'what can you do' in user_input:
        return (
            "📌 **I can help you with:**\n\n"
            "1️⃣ **Check Balance** → Ask: *'What is my balance?'*\n"
            "2️⃣ **Deposit Money** → Ask: *'How do I deposit?'*\n"
            "3️⃣ **Withdraw Money** → Ask: *'How to withdraw cash?'*\n\n"
            "Just type any of these questions, and I’ll guide you step-by-step! 💬"
        )

    # Greeting
    elif 'hello' in user_input or 'hi' in user_input or 'hey' in user_input:
        return (
            f"👋 Hello {name}! I'm your **MyBank Assistant**.\n\n"
            "Need help?\n"
            "Try asking:\n"
            "- *What is my balance?*\n"
            "- *How do I deposit money?*\n"
            "- *How to withdraw?*"
        )

    # Thank you
    elif 'thank' in user_input:
        return "😊 You're very welcome! Feel free to ask anything else."

    # Goodbye
    elif 'bye' in user_input or 'exit' in user_input or 'leave' in user_input:
        return "👋 Goodbye! Come back anytime for help with your banking."

    # Fallback
    else:
        return (
            "😅 I didn't quite get that.\n\n"
            "Try asking about:\n"
            "🔹 *Balance*\n"
            "🔹 *Deposit*\n"
            "🔹 *Withdraw*\n\n"
            "Example: *'How to deposit?'*"
        )

# Title
st.title("🏦 MyBank")
st.subheader("Simple & Secure Banking Simulation")

# --- Sidebar: Chatbot Assistant ---
with st.sidebar:
    st.markdown("### 💬 MyBank Assistant")
    st.markdown("Ask me anything about your account!")

    # Auto-welcome message on first open
    if len(st.session_state.chat_history) == 0:
        st.session_state.chat_history.append({
            "role": "assistant",
            "text": (
                "👋 Hi! I'm here to help you with:\n\n"
                "1️⃣ Check Balance\n"
                "2️⃣ Deposit Money\n"
                "3️⃣ Withdraw Cash\n\n"
                "Type a question above to get started!"
            )
        })

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**🧑 You:** {message['text']}")
        else:
            st.markdown(f"**🤖 Bot:** {message['text']}")

    # User input
    user_question = st.text_input("Ask a question:", key="chat_input")
    if st.button("📤 Send"):
        if user_question.strip() != "":
            # Add user message
            st.session_state.chat_history.append({"role": "user", "text": user_question})
            # Get bot response
            bot_reply = get_bot_response(user_question)
            st.session_state.chat_history.append({"role": "assistant", "text": bot_reply})
            st.rerun()
        else:
            st.warning("Please type a message.")

    # Clear chat button
    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("<small>💡 Powered by smart banking logic</small>", unsafe_allow_html=True)

# ---- STEP 1: Account Creation ----
if not st.session_state.setup_complete:
    st.markdown("### 📝 Create Your Account")
    name = st.text_input("Enter your full name (letters and spaces only):")
    mobile = st.text_input("Enter your 10-digit mobile number:")

    if st.button("Create Account"):
        name_stripped = name.strip()
        if not name_stripped:
            st.error("❌ Name cannot be empty.")
        elif not all(c.isalpha() or c.isspace() for c in name_stripped):
            st.error("❌ Name can only contain letters and spaces (no numbers/symbols).")
        elif not mobile.isdigit() or len(mobile) != 10:
            st.error("❌ Please enter a valid 10-digit mobile number.")
        else:
            st.session_state.name = name_stripped.title()
            st.session_state.mobile = mobile
            st.session_state.setup_complete = True
            st.session_state.balance = 0
            st.success(f"✅ Account created successfully, {st.session_state.name}!")
            st.rerun()

# ---- STEP 2: Verification (PIN or OTP) ----
elif not st.session_state.verified:
    st.markdown(f"### 🔐 Hello, {st.session_state.name}!")
    st.write("Please verify your identity to access your account.")

    method = st.radio("Choose Verification Method:", ("🔐 PIN", "📨 OTP"))

    if method == "🔐 PIN":
        pin = st.text_input("Enter PIN", type="password", placeholder="Try 1234")
        if st.button("Verify PIN"):
            if pin == "1234":
                st.session_state.verified = True
                st.success("✅ PIN Verified! Welcome to your dashboard.")
                st.rerun()
            else:
                st.error("❌ Incorrect PIN. Try again.")

    elif method == "📨 OTP":
        if st.button("Send OTP"):
            otp = generate_otp()
            st.session_state.otp = otp
            st.info(f"💡 OTP sent! → Your OTP is: **`{otp}`**")

        user_otp = st.text_input("Enter the OTP you received:")
        if st.button("Verify OTP"):
            if user_otp == st.session_state.otp and user_otp.strip() != '':
                st.session_state.verified = True
                st.success("✅ OTP Verified! Welcome back.")
                st.rerun()
            else:
                st.error("❌ Invalid or expired OTP.")

# ---- STEP 3: Banking Dashboard ----
else:
    st.markdown(f"<h3 style='color:#1f77b4;'>✅ Welcome, {st.session_state.name}!</h3>", unsafe_allow_html=True)
    st.markdown(f"📱 **Mobile:** {st.session_state.mobile}")
    st.markdown("---")

    # Display Balance
    st.markdown(f"<h4>💰 Current Balance: ₹{st.session_state.balance:,}</h4>", unsafe_allow_html=True)

    # Transaction Columns
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 💵 Deposit (Credit)")
        credit_amount = st.number_input("Amount to deposit", min_value=0, step=10, key="credit_in")
        if st.button("➕ Deposit"):
            if credit_amount > 0:
                st.session_state.balance += credit_amount
                st.success(f"✅ ₹{credit_amount} credited successfully!")
                time.sleep(1.5)
                st.rerun()
            else:
                st.warning("⚠️ Enter a valid amount.")

    with col2:
        st.markdown("### 💸 Withdraw (Debit)")
        debit_amount = st.number_input("Amount to withdraw", min_value=0, step=10, key="debit_in")
        if st.button("➖ Withdraw"):
            if debit_amount > 0:
                if debit_amount <= st.session_state.balance:
                    st.session_state.balance -= debit_amount
                    st.success(f"✅ ₹{debit_amount} debited successfully!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Insufficient balance!")
            else:
                st.warning("⚠️ Enter a valid amount.")

    st.markdown("---")

    # Logout Button
    if st.button("🔚 Logout"):
        for key in initial_state:
            st.session_state[key] = initial_state[key]
        st.success("👋 Logged out successfully. Redirecting...")
        st.rerun()

    # Footer hint
    st.markdown("<center><small>💡 Need help? Use the <b>chatbot</b> in the sidebar!</small></center>", unsafe_allow_html=True)
