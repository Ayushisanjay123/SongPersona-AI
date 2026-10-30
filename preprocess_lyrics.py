import pandas as pd

input_file = "data/song_lyrics.csv"
output_file = "data/processed_songs.csv"

chunksize = 50000
target_songs = 500

selected_columns = [
    "title",
    "artist",
    "tag",
    "lyrics",
    "year",
    "views"
]

songs = []

print("Processing dataset...")

for chunk in pd.read_csv(input_file, chunksize=chunksize):

    chunk = chunk[selected_columns]

    # Remove missing lyrics
    chunk = chunk.dropna(subset=["lyrics"])

    # Keep useful lyrics only
    chunk = chunk[chunk["lyrics"].str.len() > 50]

    songs.append(chunk)

    total = sum(len(x) for x in songs)
    print("Collected:", total)

    if total >= target_songs:
        break


final_df = pd.concat(songs, ignore_index=True)

# Keep only 20,000 songs
final_df = final_df.head(target_songs)

final_df.to_csv(output_file, index=False)

print("Done!")
print("Saved:", output_file)
print("Total songs:", len(final_df))