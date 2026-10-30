# 🎵 SongPersona AI

### AI-Powered Music Recommendation Based on Personality and Emotions

SongPersona AI is an NLP-based music recommendation system that combines **user personality traits and emotional analysis of song lyrics** to generate personalized music recommendations.

Unlike traditional recommendation systems that rely mainly on listening history or popularity, SongPersona AI explores the connection between a listener's personality, emotional preferences, and the emotions expressed in song lyrics.

---

## ✨ Key Features

- **Personality Quiz:** Evaluates users across six characteristics: Introversion, Emotional Intensity, Romanticism, Energy Preference, Optimism, and Independence.
- **Emotion Detection:** Uses a pretrained Transformer model to identify emotions expressed in song lyrics.
- **Personalized Recommendations:** Combines personality similarity and emotional compatibility to recommend songs.
- **Match Percentage:** Displays recommendation match scores to help users understand how closely songs align with their preferences.
- **Confidence Score:** Provides a confidence indicator alongside recommendations.
- **User Authentication:** Includes account registration, login, and password reset functionality.
- **Saved Songs:** Allows users to save recommended songs and revisit their selections.
- **Interactive Interface:** Built with Streamlit for an accessible and interactive experience.

---

## 🧠 How It Works

SongPersona AI combines personality-based matching with NLP-based emotion analysis.

### 1. Personality Assessment
Users complete a personality quiz covering six personality characteristics.

### 2. Emotion Analysis
Song lyrics are analyzed using the pretrained Hugging Face model:

`j-hartmann/emotion-english-distilroberta-base`

The model identifies emotions such as:
- Joy
- Sadness
- Anger
- Fear
- Disgust
- Surprise
- Neutral

### 3. Similarity Calculation
The system uses cosine similarity to compare personality preferences and song characteristics.

### 4. Recommendation Generation
The recommendation score combines:

- 80% Personality Similarity
- 20% Emotion Compatibility

The system then generates personalized song recommendations based on the combined score.

---

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Natural Language Processing | Hugging Face Transformers, NLTK |
| Deep Learning Framework | PyTorch |
| Data Visualization | Matplotlib, Seaborn |
| Database | SQLite |
| Similarity Measurement | Cosine Similarity |

---

## 📂 Project Structure

```text
SongPersona-AI/
│
├── assets/
│   └── style.css
│
├── data/
│   └── Local song datasets (not included in this repository)
│
├── utils/
│   ├── emotion_analyzer.py
│   ├── feature_extractor.py
│   ├── personality_emotion.py
│   ├── quiz_mapper.py
│   └── recommender.py
│
├── app.py
├── database.py
├── generate_song_features.py
├── preprocess_lyrics.py
├── requirements.txt
├── test_features.py
├── test_recommender.py
└── .gitignore
```

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.11 or a compatible Python version
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Ayushisanjay123/SongPersona-AI.git
```

### 2. Navigate to the project directory

```bash
cd SongPersona-AI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

**Note:** Local datasets and generated files are not included in this repository. The required project data must be prepared separately. Email-based password reset functionality also requires the appropriate environment variables to be configured.

---

## 🔬 Core Concepts

This project explores the practical application of:

- Natural Language Processing (NLP)
- Transformer-based emotion classification
- Personality-based recommendation
- Feature extraction
- Cosine similarity
- Hybrid recommendation techniques
- Data preprocessing and analysis

---

## 🚀 Future Improvements

- Expand the song dataset.
- Improve recommendation personalization.
- Explore additional personality and emotion features.
- Integrate Spotify API for richer music discovery.
- Enhance recommendation evaluation and performance.

---

## 👩‍💻 Developer

**Ayushi Sanjaykumar**

Integrated MCA Graduate | Aspiring Data Scientist

GitHub: [Ayushisanjay123](https://github.com/Ayushisanjay123)

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, NLP, Machine Learning, and a love for music.** 🎶