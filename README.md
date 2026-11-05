# 🎵 SongPersona AI

### AI-Powered Music Recommendation Based on Personality and Emotions

SongPersona AI is an intelligent music recommendation system that combines **personality-based matching and NLP-powered emotion analysis** to generate personalized song recommendations.

Unlike traditional recommendation systems that primarily rely on listening history or popularity, SongPersona AI explores the relationship between a listener's personality, emotional preferences, and the emotions expressed in song lyrics.

The project demonstrates how Natural Language Processing (NLP), Machine Learning, and recommendation techniques can work together to create a more personalized music discovery experience.

---

## ✨ Key Features

- **Personality Assessment:** Evaluates users across six characteristics: Introversion, Emotional Intensity, Romanticism, Energy Preference, Optimism, and Independence.
- **Emotion Detection:** Uses a pretrained Transformer model to identify emotions expressed in song lyrics.
- **Personalized Recommendations:** Combines personality similarity and emotional compatibility to recommend songs.
- **Match Percentage:** Displays how closely recommended songs align with user preferences.
- **Confidence Score:** Provides a confidence indicator alongside recommendations.
- **User Authentication:** Supports account registration, login, and password reset.
- **Secure Password Storage:** Uses salted PBKDF2-HMAC-SHA256 password hashing with automatic migration of legacy password hashes.
- **Saved Songs:** Allows users to save and manage their favourite recommendations.
- **Persistent Song Feedback:** Users can mark recommendations as "Love it" or "Not for me". Feedback is stored in the database.
- **Interactive Interface:** Provides a personalized experience through a Streamlit application.

---

## 🧠 How It Works

SongPersona AI combines personality-based matching with emotion analysis of song lyrics.

### 1. Personality Assessment

Users complete an interactive personality quiz covering six characteristics:

- Introversion
- Emotional Intensity
- Romanticism
- Energy Preference
- Optimism
- Independence

The quiz responses are used to build a personality preference profile.

### 2. Emotion Analysis

Song lyrics are analyzed using the pretrained Hugging Face Transformer model:

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

The system uses cosine similarity to compare user personality preferences with extracted song characteristics.

### 4. Recommendation Generation

The final recommendation score combines two components:

| Component | Weight |
|---|---:|
| Personality Similarity | 80% |
| Emotion Compatibility | 20% |

The combined score is used to rank songs and generate personalized recommendations.

---

## 🛠️ Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Natural Language Processing | Hugging Face Transformers, NLTK |
| Deep Learning | PyTorch |
| Data Visualization | Matplotlib, Seaborn, Plotly |
| Database | SQLite |
| Similarity Measurement | Cosine Similarity |
| Version Control | Git, GitHub |

---

## 📂 Project Structure

```text
SongPersona-AI/
│
├── assets/
│   └── style.css
│
├── data/
│   ├── processed_songs.csv
│   ├── song_emotions.csv
│   ├── song_features.csv
│   └── song_lyrics.csv          # Local dataset, not uploaded
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

- Python 3.11
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

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Prepare the dataset

The repository includes the following processed datasets:

- `processed_songs.csv`
- `song_emotions.csv`
- `song_features.csv`

The original `song_lyrics.csv` dataset is excluded from GitHub because of its large file size (approximately 9 GB).

Place the original lyrics dataset in the `data/` directory if required for preprocessing or dataset regeneration.

### 7. Run the application

```bash
python -m streamlit run app.py
```

The application will open in your default web browser.

**Note:** The pretrained emotion model may need to download its files from Hugging Face during its first use. Email-based password reset functionality requires the appropriate environment variables to be configured.

---

## 🔬 Core Concepts

This project explores the practical application of:

- Natural Language Processing (NLP)
- Transformer-based emotion classification
- Personality-based recommendation systems
- Feature extraction
- Cosine similarity
- Hybrid recommendation techniques
- Data preprocessing and analysis
- Secure user authentication
- SQLite database management

---

## 🚀 Future Improvements

- Expand the song dataset.
- Improve recommendation personalization using stored user feedback.
- Explore additional personality and emotion features.
- Integrate the Spotify API for richer music discovery.
- Enhance recommendation evaluation and performance.

---

## 👩‍💻 Developer

**Ayushi Sanjaykumar**

Integrated MCA Graduate | Aspiring Data Scientist

- **GitHub:** [Ayushisanjay123](https://github.com/Ayushisanjay123)
- **Repository:** [SongPersona AI](https://github.com/Ayushisanjay123/SongPersona-AI)

---

⭐ If you find this project interesting, consider giving the repository a star!

**Built with Python, NLP, Machine Learning, and a love for music.** 🎶