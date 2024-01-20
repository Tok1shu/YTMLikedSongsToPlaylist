import json
import logging
from ytmusicapi import YTMusic
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_playlist_to_json(playlist_id, filename, ytmusic):
    playlist = ytmusic.get_playlist(playlist_id, limit=None)
    songs_data = []

    for track in playlist['tracks']:
        song_info = {
            'title': track['title'],
            'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
            'album': track['album']['name'] if track['album'] else 'Unknown Album',
            'url': f"https://music.youtube.com/watch?v={track['videoId']}"
        }
        songs_data.append(song_info)

    with open(filename, 'w') as json_file:
        json.dump(songs_data, json_file, indent=4)
    logging.info(f"Playlist saved to {filename} with {len(songs_data)} songs.")


def create_playlist_and_add_songs(playlist_name, songs_json_file, ytmusic):
    playlist_id = ytmusic.create_playlist(playlist_name, "Created by script")
    with open(songs_json_file, 'r') as file:
        songs = json.load(file)

    total_songs = len(songs)
    added_songs_count = 0
    for index, song in enumerate(songs, start=1):
        video_id = song['url'].split('=')[-1]
        attempts = 0
        while attempts < 3:
            try:
                ytmusic.add_playlist_items(playlist_id, [video_id])
                logging.info(f"Added ({index}/{total_songs}): {song['title']} - {song['artist']}")
                added_songs_count += 1
                break
            except Exception as e:
                logging.error(f"Error adding ({index}/{total_songs}) {song['title']} - {song['artist']}: {e}")
                attempts += 1
                time.sleep(2)
        if attempts == 3:
            logging.error(f"Skipped ({index}/{total_songs}) {song['title']} - {song['artist']} after 3 attempts")

    logging.info(f"Total songs added to the playlist '{playlist_name}': {added_songs_count}")

if __name__ == "__main__":
    ytmusic = YTMusic('oauth.json')
    generate_playlist_copy = input(
        "Do you want to generate a copy of the 'Liked Songs' playlist? (yes/no): ").strip().lower()

    if generate_playlist_copy == 'yes':
        liked_playlist_id = 'LM'
        playlist_name = input("Enter the name for the new playlist: ").strip()
        save_playlist_to_json(liked_playlist_id, 'liked_songs.json', ytmusic)

        confirm = input(
            f"Do you want to create a new playlist named '{playlist_name}' and add songs to it? (yes/no): ").strip().lower()
        if confirm == 'yes':
            create_playlist_and_add_songs(playlist_name, "liked_songs.json", ytmusic)
        else:
            logging.info("Playlist creation cancelled by user.")
    else:
        logging.info("Operation cancelled by user.")
