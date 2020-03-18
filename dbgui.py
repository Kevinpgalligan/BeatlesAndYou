import PySimpleGUI as sg
from storage import LyricsDatabase

COLUMNS = [
    "name",
    "artist"
]

def create_window(header, data):
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
                row_colors=[(i, "Green" if data[i][2] else "Red")
                            for i in range(len(data))],
                key="TABLE")
        ],
        [sg.Text(
            "Coverage: {}%".format(round(sum(1 if cell[2] else 0 for cell in data)/len(data)*100., 2)))]
    ]
    return sg.Window("Table", layout, grab_anywhere=False)

def main():
    db = LyricsDatabase("./lyrics/charts/")
    header = COLUMNS + ["has-lyrics"]
    data = []
    songs = []
    for song in db:
        songs.append(song)
        data.append(
            [song[field] for field in COLUMNS] + [True if "lyrics" in song else False])
    sg.theme("Black")
    window = create_window(header, data)
    while True:
        event, values = window.read()
        if event in (None, "Exit"):
            break
        if event == "TABLE":
            row_index = values["TABLE"][0]
            song = songs[row_index]
            lyrics = sg.PopupGetText("Input lyrics of {}".format(song["name"])).strip()
            if lyrics is not None and len(lyrics) > 0:
                song["lyrics"] = lyrics
                db.write(song)
                data[row_index][2] = True
                window.close()
                window = create_window(header, data)
    window.close()

if __name__ == "__main__":
    main()
