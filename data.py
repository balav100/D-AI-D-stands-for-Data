import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime
import json, os, warnings
import ollama
import speech_recognition as sr
from gtts import gTTS
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import IsolationForest
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

# Firebase
import pyrebase

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
ollama_client = ollama.Client(host=OLLAMA_HOST)

warnings.filterwarnings("ignore")
sns.set_style("whitegrid")


def df_to_dict_safe(df):
    df_copy = df.copy()
    for col in df_copy.select_dtypes(include=['datetime', 'datetimetz']).columns:
        df_copy[col] = df_copy[col].astype(str)
    return df_copy.to_dict(orient='records')


st.set_page_config(page_title="D-AI, D stands for Data", layout="wide")
st.title("D-AI, D stands for Data")


firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
db = firebase.database()


st.sidebar.header("Login / Sign Up")
auth_action = st.sidebar.radio("Action", ["Login", "Sign Up"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_action == "Sign Up" and st.sidebar.button("Sign Up"):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.success("User created! Please log in.")
    except Exception as e:
        st.error(f"Error: {e}")

if auth_action == "Login" and st.sidebar.button("Login"):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state.user = user
        st.success(f"Logged in as {email}")
    except Exception as e:
        st.error(f"Login failed: {e}")

if "user" not in st.session_state:
    st.info("Please login or sign up to continue.")
    st.stop()


st.sidebar.header("Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=['csv','xlsx','xls'])
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.df_clean = df.copy()
        # store in Firebase
        db.child("users").child(st.session_state.user['localId']).child("uploaded_datasets").push({
            "filename": uploaded_file.name,
            "uploaded_at": str(datetime.now()),
            "data_preview": df.head(100).to_json(orient='records')
        }, st.session_state.user['idToken'])
        st.success("Dataset uploaded and saved!")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()
else:
    st.info("Upload a CSV or Excel file to begin.")
    st.stop()

df = st.session_state.df_clean


st.sidebar.header("Data Preprocessing")

# Handle duplicates
dup_action = st.sidebar.selectbox("Duplicates", ["None", "Drop duplicates"])
if dup_action == "Drop duplicates":
    before = df.shape[0]
    df = df.drop_duplicates()
    after = df.shape[0]
    st.sidebar.success(f"Dropped {before-after} duplicate rows")
    st.session_state.df_clean = df.copy()

# Handle missing
mv_strategy = st.sidebar.selectbox("Missing values", ["None","Drop rows","Drop columns","Fill mean","Fill median","KNN Impute"])
if mv_strategy != "None":
    if mv_strategy == "Drop rows":
        df = df.dropna()
    elif mv_strategy == "Drop columns":
        df = df.dropna(axis=1)
    elif mv_strategy == "Fill mean":
        for c in df.select_dtypes(include=[np.number]).columns:
            df[c] = df[c].fillna(df[c].mean())
    elif mv_strategy == "Fill median":
        for c in df.select_dtypes(include=[np.number]).columns:
            df[c] = df[c].fillna(df[c].median())
    elif mv_strategy == "KNN Impute":
        num_cols = df.select_dtypes(include=[np.number]).columns
        imputer = KNNImputer(n_neighbors=5)
        df[num_cols] = imputer.fit_transform(df[num_cols])
    st.session_state.df_clean = df.copy()
    st.sidebar.success("Missing values handled")

st.subheader("Dataset Preview")
st.dataframe(df.head())


st.subheader("Dataset Summary")
def dataset_summary(df):
    rows, cols = df.shape
    numeric = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical = df.select_dtypes(exclude=[np.number]).columns.tolist()
    missing_counts = df.isna().sum().to_dict()
    return {"rows": rows, "cols": cols, "numeric": numeric, "categorical": categorical, "missing": missing_counts}

summary = dataset_summary(df)
st.json(summary)


st.subheader("Visualizations")
plot_type = st.selectbox("Plot type", ["Histogram","Box","Bar","Pie","Scatter","Line","Correlation Heatmap","Pairplot","PCA"])
x_col = st.selectbox("X column", df.columns)
y_col = None
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
y_options = [c for c in numeric_cols if c != x_col]
if plot_type in ["Scatter","Line","Bar"] and y_options:
    y_col = st.selectbox("Y column", y_options)

fig = None
try:
    if plot_type == "Histogram" and x_col in numeric_cols:
        fig, ax = plt.subplots()
        df[x_col].hist(ax=ax, bins=20)
        ax.set_title(f"Histogram of {x_col}")
    elif plot_type == "Box" and x_col in numeric_cols:
        fig, ax = plt.subplots()
        sns.boxplot(x=df[x_col], ax=ax)
        ax.set_title(f"Boxplot of {x_col}")
    elif plot_type == "Bar":
        fig, ax = plt.subplots()
        if y_col:
            sns.barplot(x=df[x_col].astype(str), y=df[y_col], ax=ax)
        else:
            df[x_col].value_counts().plot(kind='bar', ax=ax)
    elif plot_type == "Pie":
        fig, ax = plt.subplots()
        df[x_col].value_counts().head(6).plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")
    elif plot_type == "Scatter" and y_col:
        fig, ax = plt.subplots()
        ax.scatter(df[x_col], df[y_col])
    elif plot_type == "Line" and y_col:
        fig, ax = plt.subplots()
        ax.plot(df[x_col], df[y_col])
    elif plot_type == "Correlation Heatmap" and len(numeric_cols)>=2:
        fig, ax = plt.subplots()
        sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    elif plot_type == "Pairplot" and len(numeric_cols)>=2:
        fig = sns.pairplot(df[numeric_cols].sample(min(500, df.shape[0]))).fig
    elif plot_type == "PCA" and len(numeric_cols)>=2:
        scaler = StandardScaler()
        X = scaler.fit_transform(df[numeric_cols].dropna())
        pca = PCA(n_components=2)
        comps = pca.fit_transform(X)
        fig, ax = plt.subplots()
        ax.scatter(comps[:,0], comps[:,1])
        ax.set_title("PCA first two components")
except Exception as e:
    st.error(f"Plot error: {e}")

if fig:
    st.pyplot(fig)


st.subheader("D-AI's Chatbot")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

chat_input = st.text_input("Ask a question about the dataset:")
if st.button("Ask AI"):
    if chat_input:
        prompt = f"Dataset facts: {summary}\nQuestion: {chat_input}\nAnswer concisely."
        try:
            resp = ollama_client.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}],
                
            )
            answer = resp["message"]["content"].strip()
            st.write(answer)
            st.session_state.chat_history.append({"question": chat_input, "answer": answer, "timestamp": str(datetime.now())})
            # store in Firebase
            db.child("users").child(st.session_state.user['localId']).child("chat_history").push({
                "question": chat_input,
                "answer": answer,
                "timestamp": str(datetime.now())
            }, st.session_state.user['idToken'])

        except Exception as e:
            st.error(f"LLM error: {e}")

# show history
if st.session_state.chat_history:
    with st.expander("Chat history"):
        for h in reversed(st.session_state.chat_history):
            st.markdown(f"**Q:** {h['question']}")
            st.write(h['answer'])


st.subheader("D-AI's Voice Assistant")
if st.button("Record Question"):
    try:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Speak now...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        query = r.recognize_google(audio)
        st.write("You said:", query)
        prompt = f"Dataset facts: {summary}\nQuestion: {query}\nAnswer concisely."
        resp = ollama_client.chat(
            model="llama3",
            messages=[{"role":"user","content":prompt}],
            
        )
        answer = resp["message"]["content"].strip()
        st.write(answer)
        temp_audio = "temp.mp3"
        gTTS(answer).save(temp_audio)
        st.audio(temp_audio, format="audio/mp3")
        # store voice chat
        db.child("users").child(st.session_state.user['localId']).child("voice_history").push({
            "question": query,
            "answer": answer,
            "timestamp": str(datetime.now())
        }, st.session_state.user['idToken'])

    except Exception as e:
        st.error(f"Voice error: {e}")


st.subheader("What-If Simulator")
df_sim = df.copy()
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
simulated_values = {}
for col in numeric_cols:
    simulated_values[col] = st.slider(f"{col} adjustment factor", -100.0, 100.0, 0.0)

if st.button("Generate Simulated Dataset"):
    for col in numeric_cols:
        df_sim[col] = df_sim[col] + simulated_values[col]
    st.dataframe(df_sim.head())
    db.child("users").child(st.session_state.user['localId']).child("simulated_datasets").push({
        "data_preview": df_sim.head(100).to_json(orient='records'),
        "simulated_at": str(datetime.now()),
        "adjustments": simulated_values
    }, st.session_state.user['idToken'])
    csv_buffer = df_sim.to_csv(index=False).encode('utf-8')
    st.download_button("Download Simulated CSV", csv_buffer, "simulated_dataset.csv", "text/csv")


st.subheader("Anomaly Detection (IsolationForest)")
if numeric_cols and st.button("Detect Anomalies"):
    iso = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    sub = df[numeric_cols].dropna()
    iso.fit(sub)
    scores = iso.decision_function(sub)
    st.dataframe(pd.DataFrame({"index": sub.index, "anomaly_score": scores}).sort_values("anomaly_score"))


st.subheader("Generate PDF Report")
include_visualization = st.checkbox("Include visualization in the PDF")
if st.button("Generate PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height-50, "D-AI Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, height-70, f"Generated: {datetime.now().isoformat()}")
    text_obj = c.beginText(50, height-90)
    for line in json.dumps(summary, indent=2).splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)

    if include_visualization:
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height-50, "Visualization")
        if fig:
            img_buffer = BytesIO()
            fig.tight_layout()
            fig.savefig(img_buffer, format="PNG", bbox_inches='tight')
            img_buffer.seek(0)
            image = ImageReader(img_buffer)
            image_width = width - 100
            image_height = height - 150
            c.drawImage(image, 50, 80, width=image_width, height=image_height, preserveAspectRatio=True, mask='auto')
        else:
            c.setFont("Helvetica", 10)
            c.drawString(50, height-80, "No visualization has been generated yet. Please create a plot first.")

    c.save()
    buffer.seek(0)
    st.download_button("Download PDF Report", buffer, "report.pdf", "application/pdf")
