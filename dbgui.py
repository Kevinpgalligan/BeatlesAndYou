import PySimpleGUI as sg
import pyperclip
from storage import LyricsDatabase

COLUMNS = [
    "id",
    "name",
    "artist"
]

def create_window(header, data):
    done = sum(1 if cell[-1] else 0 for cell in data)
    layout = [
        [
            sg.Table(
                values=data,
                headings=header,
                max_col_width=25,
                auto_size_columns=True,
                justification="right",
                enable_events=True,
                num_rows=min(len(data), 10),
                row_colors=[(i, "Green" if data[i][-1] else "Red")
                            for i in range(len(data))],
                key="TABLE")
        ],
        [sg.Text(
            "Coverage: {}%; {} total, {} done, {} remaining.".format(
                round(done/len(data)*100., 2),
                len(data),
                done,
                len(data)-done))]
    ]
    return sg.Window("Table", layout, grab_anywhere=False)

def main():
    db = LyricsDatabase("./lyrics/charts/")
    header = COLUMNS + ["has-lyrics"]
    data = []
    song_by_id = {}
    for song in db:
        song_by_id[song["id"]] = song
        data.append(
            [song[field] for field in COLUMNS] + [True if "lyrics" in song else False])
    data.sort(key=lambda cell: cell[-1])
    sg.theme("Black")
    window = create_window(header, data)
    while True:
        event, values = window.read()
        if event in (None, "Exit"):
            break
        if event == "TABLE":
            row_index = values["TABLE"][0]
            song = song_by_id[data[row_index][0]]
            pyperclip.copy(song["artist"] + " " + song["name"] + " " + "lyrics")
            lyrics = sg.PopupGetText("Input lyrics of {}".format(song["name"]))
            if lyrics is not None and len(lyrics) > 0:
                song["lyrics"] = lyrics.strip()
                db.write(song)
                data[row_index][-1] = True
                data.sort(key=lambda cell: cell[-1])
                window.close()
                window = create_window(header, data)
    window.close()

if __name__ == "__main__":
    main()
