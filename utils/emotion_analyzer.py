import pandas as pd
from transformers import pipeline


# --------------------------------------------------
# Input and Output Files
# --------------------------------------------------

input_file = "data/processed_songs.csv"
output_file = "data/song_emotions.csv"


# --------------------------------------------------
# Load Dataset
# --------------------------------------------------

print("Loading dataset...")

df = pd.read_csv(input_file)

print(f"Total songs: {len(df)}")


# --------------------------------------------------
# Load Hugging Face Emotion Model
# --------------------------------------------------

print("Loading emotion model...")

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)


# --------------------------------------------------
# Emotion Labels
# --------------------------------------------------

EMOTIONS = [
    "anger",
    "disgust",
    "fear",
    "joy",
    "neutral",
    "sadness",
    "surprise"
]


# --------------------------------------------------
# Split Lyrics into Chunks
# --------------------------------------------------

def split_lyrics(lyrics, chunk_size=400):

    words = str(lyrics).split()

    chunks = []

    for i in range(
        0,
        len(words),
        chunk_size
    ):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


# --------------------------------------------------
# Analyze Song Emotion
# --------------------------------------------------

def analyze_emotion(lyrics):

    lyrics = str(lyrics).strip()

    if not lyrics:

        return pd.Series(
            ["neutral", 0.0]
        )


    # --------------------------------------------------
    # Split Full Lyrics
    # --------------------------------------------------

    chunks = split_lyrics(
        lyrics,
        chunk_size=400
    )


    # --------------------------------------------------
    # Store Emotion Scores
    # --------------------------------------------------

    emotion_totals = {
        emotion: 0.0
        for emotion in EMOTIONS
    }


    analyzed_chunks = 0


    # --------------------------------------------------
    # Analyze Each Chunk
    # --------------------------------------------------

    for chunk in chunks:

        try:

            result = emotion_classifier(
                chunk,
                truncation=True,
                max_length=512
            )[0]


            chunk_scores = {
                emotion["label"].lower():
                emotion["score"]
                for emotion in result
            }


            for emotion in EMOTIONS:

                emotion_totals[emotion] += (
                    chunk_scores.get(
                        emotion,
                        0.0
                    )
                )


            analyzed_chunks += 1


        except Exception as e:

            print(
                f"Warning: Could not analyze chunk: {e}"
            )


    # --------------------------------------------------
    # Handle Failed Analysis
    # --------------------------------------------------

    if analyzed_chunks == 0:

        return pd.Series(
            ["neutral", 0.0]
        )


    # --------------------------------------------------
    # Average Emotion Scores
    # --------------------------------------------------

    emotion_scores = {

        emotion:
        score / analyzed_chunks

        for emotion, score
        in emotion_totals.items()
    }


    # --------------------------------------------------
    # Select Dominant Emotion
    # --------------------------------------------------

    dominant_emotion = max(
        emotion_scores,
        key=emotion_scores.get
    )


    dominant_score = emotion_scores[
        dominant_emotion
    ]


    return pd.Series(
        [
            dominant_emotion,
            round(dominant_score, 6)
        ]
    )


# --------------------------------------------------
# Analyze All Songs
# --------------------------------------------------

print("\nStarting emotion analysis...")

df[
    [
        "emotion",
        "emotion_score"
    ]
] = df["lyrics"].apply(
    analyze_emotion
)


# --------------------------------------------------
# Save Results
# --------------------------------------------------

df.to_csv(
    output_file,
    index=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\nEmotion analysis completed successfully!")

print(
    "Saved:",
    output_file
)


print("\nEmotion distribution:")

print(
    df["emotion"].value_counts()
)