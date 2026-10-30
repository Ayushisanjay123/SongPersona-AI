import pandas as pd

from sklearn.metrics.pairwise import cosine_similarity


def recommend_songs(
    user_personality,
    songs_file="data/song_features.csv",
    emotions_file="data/song_emotions.csv"
):

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    songs = pd.read_csv(
        songs_file
    )

    emotions = pd.read_csv(
        emotions_file
    )

    emotions = emotions[
        [
            "title",
            "artist",
            "emotion",
            "emotion_score"
        ]
    ]

    songs = songs.merge(
        emotions,
        on=[
            "title",
            "artist"
        ],
        how="left"
    )

    # --------------------------------------------------
    # PERSONALITY TRAITS
    # --------------------------------------------------

    traits = [
        "Introversion",
        "Emotional Intensity",
        "Romanticism",
        "Energy Preference",
        "Optimism",
        "Independence"
    ]

    user_vector = [
        float(
            user_personality.get(
                trait,
                0.0
            )
        )
        for trait in traits
    ]

    # --------------------------------------------------
    # EMOTION PREFERENCES
    # --------------------------------------------------

    emotion_preferences = {

        "Introversion": {
            "neutral": 1.0,
            "sadness": 0.7,
            "fear": 0.4,
            "joy": 0.4,
            "surprise": 0.3,
            "anger": 0.2,
            "disgust": 0.2,
        },

        "Emotional Intensity": {
            "sadness": 1.0,
            "fear": 0.9,
            "anger": 0.8,
            "joy": 0.7,
            "surprise": 0.6,
            "disgust": 0.5,
            "neutral": 0.3,
        },

        "Romanticism": {
            "joy": 0.9,
            "sadness": 0.8,
            "surprise": 0.5,
            "neutral": 0.4,
            "fear": 0.3,
            "anger": 0.2,
            "disgust": 0.1,
        },

        "Energy Preference": {
            "joy": 1.0,
            "anger": 0.9,
            "surprise": 0.7,
            "neutral": 0.4,
            "fear": 0.4,
            "sadness": 0.3,
            "disgust": 0.3,
        },

        "Optimism": {
            "joy": 1.0,
            "surprise": 0.6,
            "neutral": 0.5,
            "anger": 0.3,
            "sadness": 0.2,
            "fear": 0.2,
            "disgust": 0.1,
        },

        "Independence": {
            "surprise": 0.7,
            "joy": 0.7,
            "anger": 0.6,
            "neutral": 0.5,
            "fear": 0.4,
            "sadness": 0.3,
            "disgust": 0.3,
        },
    }

    # --------------------------------------------------
    # TOTAL PERSONALITY
    # --------------------------------------------------

    total_personality = sum(
        abs(
            float(
                user_personality.get(
                    trait,
                    0.0
                )
            )
        )
        for trait in traits
    )

    if total_personality == 0:

        total_personality = 1.0

    recommendations = []

    # --------------------------------------------------
    # SCORE EACH SONG
    # --------------------------------------------------

    for _, song in songs.iterrows():

        song_vector = [
            float(
                song.get(
                    trait,
                    0.0
                )
            )
            for trait in traits
        ]

        # Personality similarity
        personality_score = (
            cosine_similarity(
                [user_vector],
                [song_vector]
            )[0][0]
        )

        personality_score = max(
            0.0,
            min(
                1.0,
                personality_score
            )
        )

        # --------------------------------------------------
        # EMOTION
        # --------------------------------------------------

        emotion = str(
            song.get(
                "emotion",
                "neutral"
            )
        ).lower().strip()

        try:

            emotion_score = float(
                song.get(
                    "emotion_score",
                    0.0
                )
            )

        except (
            ValueError,
            TypeError
        ):

            emotion_score = 0.0

        emotion_score = max(
            0.0,
            min(
                1.0,
                emotion_score
            )
        )

        # --------------------------------------------------
        # EMOTION COMPATIBILITY
        # --------------------------------------------------

        emotion_compatibility = 0.0

        for trait in traits:

            trait_value = float(
                user_personality.get(
                    trait,
                    0.0
                )
            )

            trait_weight = (
                abs(trait_value)
                / total_personality
            )

            compatibility = (
                emotion_preferences
                .get(trait, {})
                .get(
                    emotion,
                    0.2
                )
            )

            emotion_compatibility += (
                trait_weight
                * compatibility
            )

        emotion_component = (
            emotion_compatibility
            * emotion_score
        )

        # --------------------------------------------------
        # FINAL SCORE
        # --------------------------------------------------

        final_score = (
            personality_score * 0.80
        ) + (
            emotion_component * 0.20
        )

        recommendations.append(
            {
                "title": song["title"],

                "artist": song["artist"],

                "emotion": song["emotion"],

                "emotion_score": round(
                    emotion_score,
                    4
                ),

                "similarity": round(
                    final_score,
                    4
                ),
            }
        )

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------

    recommendations = sorted(
        recommendations,
        key=lambda x: x["similarity"],
        reverse=True
    )

    # --------------------------------------------------
    # STEP 2
    #
    # Return top 20 instead of top 5.
    #
    # The app displays only 5 at a time.
    # "Recommend Again" changes the batch.
    # --------------------------------------------------

    return pd.DataFrame(
        recommendations[:20]
    )