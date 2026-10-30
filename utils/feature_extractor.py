from transformers import pipeline
import re


# --------------------------------------------------
# Emotion Model
# --------------------------------------------------

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)


# --------------------------------------------------
# Romantic Vocabulary
# --------------------------------------------------

ROMANTIC_WORDS = [
    "love", "loved", "loving", "lover",
    "heart", "hearts", "kiss", "kisses", "kissed",
    "romance", "romantic", "darling", "sweetheart",
    "forever", "together", "relationship",
    "girlfriend", "boyfriend", "husband", "wife",
    "beautiful", "miss you", "need you",
    "want you", "my love"
]


# --------------------------------------------------
# Split Lyrics into Chunks
# --------------------------------------------------

def split_lyrics(lyrics, chunk_size=400):

    words = lyrics.split()

    chunks = []

    for i in range(0, len(words), chunk_size):

        chunk = " ".join(
            words[i:i + chunk_size]
        )

        if chunk.strip():
            chunks.append(chunk)

    return chunks


# --------------------------------------------------
# Extract Features
# --------------------------------------------------

def extract_features(lyrics):

    if not lyrics:
        lyrics = ""

    lyrics = str(lyrics).strip()

    if not lyrics:

        return {
            "Introversion": 0.0,
            "Emotional Intensity": 0.0,
            "Romanticism": 0.0,
            "Energy Preference": 0.0,
            "Optimism": 0.0,
            "Independence": 0.0
        }


    # --------------------------------------------------
    # Split Lyrics
    # --------------------------------------------------

    chunks = split_lyrics(
        lyrics,
        chunk_size=400
    )


    # --------------------------------------------------
    # Emotion Totals
    # --------------------------------------------------

    emotion_totals = {
        "anger": 0.0,
        "disgust": 0.0,
        "fear": 0.0,
        "joy": 0.0,
        "neutral": 0.0,
        "sadness": 0.0,
        "surprise": 0.0
    }


    analyzed_chunks = 0


    # --------------------------------------------------
    # Transformer Emotion Analysis
    # --------------------------------------------------

    for chunk in chunks:

        try:

            emotions = emotion_classifier(
                chunk,
                truncation=True,
                max_length=512
            )[0]

            chunk_scores = {
                emotion["label"].lower():
                emotion["score"]
                for emotion in emotions
            }

            for emotion in emotion_totals:

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
    # Average Transformer Scores
    # --------------------------------------------------

    if analyzed_chunks > 0:

        emotion_scores = {
            emotion:
            score / analyzed_chunks
            for emotion, score
            in emotion_totals.items()
        }

    else:

        emotion_scores = emotion_totals


    # --------------------------------------------------
    # Emotion Values
    # --------------------------------------------------

    anger = emotion_scores["anger"]
    disgust = emotion_scores["disgust"]
    fear = emotion_scores["fear"]
    joy = emotion_scores["joy"]
    neutral = emotion_scores["neutral"]
    sadness = emotion_scores["sadness"]
    surprise = emotion_scores["surprise"]


    # --------------------------------------------------
    # Romantic Keyword Analysis
    # --------------------------------------------------

    text = lyrics.lower()

    romantic_count = 0

    for word in ROMANTIC_WORDS:

        if " " in word:

            romantic_count += text.count(word)

        else:

            romantic_count += len(
                re.findall(
                    r"\b"
                    + re.escape(word)
                    + r"\b",
                    text
                )
            )


    # Normalize romantic keywords

    romantic_keyword_score = min(
        romantic_count / 20,
        1.0
    )


    # --------------------------------------------------
    # Personality Mapping
    # --------------------------------------------------

    # Introversion:
    # sadness + fear + neutral
    introversion = (
        sadness * 0.40
        + fear * 0.30
        + neutral * 0.30
    )


    # Emotional Intensity:
    # strong negative + surprise + anger
    emotional_intensity = (
        anger * 0.30
        + sadness * 0.25
        + fear * 0.20
        + surprise * 0.15
        + disgust * 0.10
    )


    # Romanticism:
    # romantic vocabulary + emotional expression
    romanticism = (
        romantic_keyword_score * 0.60
        + joy * 0.20
        + sadness * 0.10
        + surprise * 0.10
    )


    # Energy Preference:
    # joy + anger + surprise
    energy_preference = (
        joy * 0.40
        + anger * 0.30
        + surprise * 0.30
    )


    # Optimism:
    # joy is the strongest signal,
    # while fear/sadness reduce optimism.
    optimism = (
        joy * 0.70
        + neutral * 0.15
        + surprise * 0.15
        - sadness * 0.10
        - fear * 0.10
    )


    # Independence:
    # neutral + anger + surprise
    independence = (
        neutral * 0.40
        + anger * 0.30
        + surprise * 0.20
        + disgust * 0.10
    )


    # --------------------------------------------------
    # Keep Values Between 0 and 1
    # --------------------------------------------------

    def clamp(value):

        return max(
            0.0,
            min(1.0, value)
        )


    introversion = clamp(introversion)

    emotional_intensity = clamp(
        emotional_intensity
    )

    romanticism = clamp(
        romanticism
    )

    energy_preference = clamp(
        energy_preference
    )

    optimism = clamp(
        optimism
    )

    independence = clamp(
        independence
    )


    # --------------------------------------------------
    # Convert 0–1 → 0–10
    # --------------------------------------------------

    features = {

        "Introversion": round(
            introversion * 10,
            2
        ),

        "Emotional Intensity": round(
            emotional_intensity * 10,
            2
        ),

        "Romanticism": round(
            romanticism * 10,
            2
        ),

        "Energy Preference": round(
            energy_preference * 10,
            2
        ),

        "Optimism": round(
            optimism * 10,
            2
        ),

        "Independence": round(
            independence * 10,
            2
        )
    }


    return features