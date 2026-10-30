import pandas as pd

from utils.feature_extractor import extract_features
from utils.recommender import recommend_songs

# --------------------------------------------------
# Load Processed Songs
# --------------------------------------------------

songs = pd.read_csv(
    "data/processed_songs.csv"
)


# --------------------------------------------------
# Select Killa Cam
# --------------------------------------------------

song = songs[
    songs["title"] == "Killa Cam"
].iloc[0]


# --------------------------------------------------
# Extract Lyrics
# --------------------------------------------------

lyrics = song["lyrics"]


# --------------------------------------------------
# Generate User Personality
# --------------------------------------------------

user_personality = extract_features(
    lyrics
)


print("\n" + "=" * 60)
print("USER PERSONALITY")
print("=" * 60)

for trait, value in user_personality.items():

    print(
        f"{trait}: {value}"
    )


# --------------------------------------------------
# Generate Recommendations
# --------------------------------------------------

print("\n" + "=" * 60)
print("GENERATING RECOMMENDATIONS...")
print("=" * 60)

recommendations = recommend_songs(
    user_personality
)


# --------------------------------------------------
# Display Recommendations
# --------------------------------------------------

print("\n" + "=" * 60)
print("TOP 5 RECOMMENDATIONS")
print("=" * 60)

print(
    recommendations.to_string(
        index=False
    )
)


print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)