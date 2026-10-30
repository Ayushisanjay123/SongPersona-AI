def generate_personality_emotion(profile):

    emotional_intensity = profile["Emotional Intensity"]
    romanticism = profile["Romanticism"]
    energy = profile["Energy Preference"]
    optimism = profile["Optimism"]
    introversion = profile["Introversion"]
    independence = profile["Independence"]


    if romanticism >= 7 and emotional_intensity >= 7:
        emotion_type = "Romantic Soul 💙"
        description = (
            "You connect deeply with emotional lyrics, "
            "love themes, and meaningful songs."
        )

    elif energy >= 7 and optimism >= 7:
        emotion_type = "Energetic Explorer ⚡"
        description = (
            "You enjoy uplifting, powerful, and "
            "high-energy music."
        )

    elif introversion >= 7 and emotional_intensity >= 6:
        emotion_type = "Deep Thinker 🌙"
        description = (
            "You prefer reflective songs with deep "
            "emotions and personal stories."
        )

    elif independence >= 7:
        emotion_type = "Free Spirit 🦋"
        description = (
            "You enjoy unique music experiences "
            "and independent expressions."
        )

    else:
        emotion_type = "Balanced Listener 🎵"
        description = (
            "You enjoy different emotions and "
            "a variety of musical experiences."
        )


    return {
        "emotion_type": emotion_type,
        "description": description
    }