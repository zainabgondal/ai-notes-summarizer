# 🧠 AI Notes Summarizer & Knowledge Extraction System

> **Transform raw lecture notes into structured summaries, key concepts, and study questions — instantly.**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=flat-square&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=flat-square)

**Created by Zainab Gondal**

---

## 📌 Overview

The **AI Notes Summarizer & Knowledge Extraction System** is an intelligent web application that helps students and researchers turn raw lecture notes into structured, exam-ready study material. Powered by OpenAI's GPT-3.5 and built with Streamlit, it processes text in seconds and delivers:

- Concise and detailed summaries
- Extracted key concepts, definitions, and facts
- Auto-generated study questions (conceptual, MCQ, and short-answer)
- NLP-based keyword extraction
- Downloadable output as a `.txt` file

---

## ✨ Features

| Feature | Description |
|---|---|
| 📋 Multi-Input | Paste text directly or upload PDF / DOCX / TXT files |
| ⚡ Quick Summary | 3–5 sentence high-level overview |
| 📖 Detailed Summary | In-depth explanation with sub-headings |
| 🎯 Key Points | Bullet-point list of the most important concepts |
| 🧩 Concept Extraction | Identifies and explains major ideas |
| 📖 Definitions | Pulls out all defined terms with explanations |
| 📌 Important Facts | Notable statements, stats, and facts |
| ❓ Study Questions | 5 conceptual + 5 MCQ + 3 short-answer questions |
| 🏷️ Keyword Extraction | NLTK-powered frequency-based keyword detection |
| ⬇️ Download | Export the entire analysis as a plain-text file |

---

## 🗂️ Project Structure

```
ai-notes-summarizer/
│
├── app.py                  # Main Streamlit application (UI + orchestration)
├── summarizer.py           # Quick summary, detailed summary, key points
├── extractor.py            # Concepts, definitions, key terms, facts
├── question_generator.py   # Conceptual, MCQ, short-answer questions
├── file_handler.py         # PDF / DOCX / TXT text extraction
├── utils.py                # Text cleaning, keyword extraction (NLTK)
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

### Module Interaction

```
app.py
  ├── file_handler.py   →  extracts text from uploaded files
  ├── utils.py          →  cleans text, counts words, extracts keywords
  ├── summarizer.py     →  sends text to OpenAI → returns summaries
  ├── extractor.py      →  sends text to OpenAI → returns knowledge items
  └── question_generator.py → sends text to OpenAI → returns questions
```

---

## 🛠️ Technology Stack

- **Language:** Python 3.9+
- **Web Framework:** Streamlit
- **AI:** OpenAI GPT-3.5 Turbo (via `openai` SDK)
- **PDF Parsing:** pdfplumber
- **DOCX Parsing:** python-docx
- **NLP / Keywords:** NLTK (punkt tokenizer + stopwords)
- **Data:** pandas (available for future tabular extensions)

---

## ⚙️ Installation & Setup

### 1. Prerequisites

Ensure you have Python 3.9 or higher installed:

```bash
python --version
```

### 2. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/ai-notes-summarizer.git
cd ai-notes-summarizer
```

### 3. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS / Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Your OpenAI API Key

**Option A — Environment Variable (recommended for local dev):**

```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=sk-your-key-here

# macOS / Linux
export OPENAI_API_KEY=sk-your-key-here
```

**Option B — Streamlit Secrets (recommended for deployment):**

Create the file `.streamlit/secrets.toml`:

```toml
OPENAI_API_KEY = "sk-your-key-here"
```

**Option C — Sidebar input:**

Paste your API key directly into the sidebar text box when the app opens (useful for quick testing).

### 6. Run the Application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 🚀 Usage Guide

1. **Open the app** in your browser at `http://localhost:8501`.
2. **Provide notes** — either paste text into the text area or upload a PDF / DOCX / TXT file.
3. **Click "🔍 Analyse Notes"**.
4. **View results** across five sections:
   - 📝 Summaries (tabbed: Quick / Detailed / Key Points)
   - 🔬 Knowledge Extraction (Concepts, Definitions, Terms, Facts)
   - ❓ Study Questions (Conceptual / MCQ / Short Answer)
   - 🏷️ NLP Keywords
   - ⬇️ Download
5. **Download** your full analysis as a `.txt` file.

---

## 📤 Deployment on Streamlit Community Cloud

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: AI Notes Summarizer"
git remote add origin https://github.com/YOUR-USERNAME/ai-notes-summarizer.git
git push -u origin main
```

### Step 2 — Deploy

1. Visit [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"New app"**.
3. Select your repository and set the main file to `app.py`.
4. Click **"Advanced settings"** → **"Secrets"** and add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   ```
5. Click **"Deploy"** — your app will be live within minutes.

---

## 📸 Screenshots

> Add screenshots here after deploying.

| Section | Preview |
|---|---|
| Main Interface | *(screenshot)* |
| Summaries Tab | *(screenshot)* |
| Knowledge Extraction | *(screenshot)* |
| Study Questions | *(screenshot)* |
| NLP Keywords | *(screenshot)* |

---

## 🔮 Example Output

### Quick Summary
> "This lecture covers the fundamental principles of machine learning, focusing on supervised learning algorithms. The notes explain gradient descent optimisation and how it minimises loss functions. Key applications in image classification and natural language processing are discussed. The material highlights the bias-variance trade-off as a central challenge in model generalisation."

### Key Points
```
• Supervised learning requires labelled training data
• Gradient descent iteratively minimises the loss function
• Overfitting occurs when a model memorises training data
• Regularisation techniques (L1/L2) reduce overfitting
• Cross-validation provides an unbiased performance estimate
```

### Conceptual Questions
```
1. Explain how gradient descent converges to a minimum. What are its limitations?
2. What is the bias-variance trade-off and why does it matter in model selection?
3. How does regularisation prevent overfitting without reducing training data?
4. Compare supervised and unsupervised learning with practical examples.
5. Why is cross-validation preferred over a simple train/test split?
```

---

## 📄 License

This project is licensed under the **MIT License**. See `LICENSE` for details.

---

## 👩‍💻 Author

**Zainab Gondal**

- 🌐 [LinkedIn](https://linkedin.com/in/zainab-gondal)
- 💻 [GitHub](https://github.com/zainabgondal)

---

*AI Notes Summarizer — making studying smarter, not harder.*
