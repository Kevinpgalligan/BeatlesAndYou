import os
import os.path
import json

class LyricsDatabase:

    def __init__(self, base_dir):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def write(self, song_data):
        with open(self._get_path(song_data), "w") as f:
            json.dump(song_data, f)

    def delete(self, song_data):
        os.remove(self._get_path(song_data))

    def contains(self, song_data):
        return os.path.exists(self._get_path(song_data))

    def _get_path(self, x):
        if isinstance(x, str):
            song_id = x
        else:
            song_id = x["id"]
        return os.path.join(self.base_dir, song_id)

    def load(self, x):
        with open(self._get_path(x), "r") as f:
            return json.load(f)

    def remove(self, x):
        os.remove(self._get_path(x))

    def __iter__(self):
        return iter(self.load(song_id) for song_id in os.listdir(self.base_dir))
