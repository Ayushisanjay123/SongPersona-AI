import pandas as pd
from utils.feature_extractor import extract_features

# Input and output files
input_file = "data/processed_songs.csv"
output_file = "data/song_features.csv"

print("Loading dataset...")

songs = pd.read_csv(input_file)

feature_data = []

total = len(songs)

print(f"Total songs: {total}")

for index, song in songs.iterrows():

    lyrics = str(song["lyrics"])

    # Extract personality features
    features = extract_features(lyrics)

    feature_data.append({
        "title": song["title"],
        "artist": song["artist"],
        "Introversion": features["Introversion"],
        "Emotional Intensity": features["Emotional Intensity"],
        "Romanticism": features["Romanticism"],
        "Energy Preference": features["Energy Preference"],
        "Optimism": features["Optimism"],
        "Independence": features["Independence"]
    })

    # Progress update every 100 songs
    if (index + 1) % 100 == 0:
        print(f"Processed {index + 1}/{total} songs")

# Save features
feature_df = pd.DataFrame(feature_data)
feature_df.to_csv(output_file, index=False)

print("Done!")
print(f"Saved features to: {output_file}")