import pandas as pd

from utils.feature_extractor import extract_features


# Load actual processed songs
songs = pd.read_csv(
    "data/processed_songs.csv"
)


# Select Killa Cam
song = songs[
    songs["title"] == "Killa Cam"
].iloc[0]


# Extract lyrics
lyrics = song["lyrics"]


# Generate personality features
result = extract_features(lyrics)


print("\nSong:")
print(song["title"])

print("\nArtist:")
print(song["artist"])

print("\nPersonality Features:")
print(result)