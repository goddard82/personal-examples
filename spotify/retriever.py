import requests

token = "{REPLACE}"

req_headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
    }


def last_fifty(after_ts):
    url = "https://api.spotify.com/v1/me/player/recently-played"

    querystring = {"limit": "50", "after": str(after_ts)}

    headers = req_headers

    response = requests.request("GET", url, headers=headers, params=querystring)
    if response.status_code == 200:
        jsonresult = response.json()
        items = jsonresult.get('items')
        if len(items) > 0:
            # todo other keys
            for item in items:
                track = item.get('track')
                # todo other keys
                track_id = track.get('id')
                print(track_id)
        else:
            print("nothing found")
    else:
        print(response.status_code, response.headers)


# print(response.text)


last_fifty(after_ts="1484811043508")


def new_playlist():
    url = "https://api.spotify.com/v1/users/dard/playlists"
    payload = {
        "name": "dsada Playlist",
        "description": "New playlist description",
        "public": False
    }
    headers = req_headers
    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 201:
        jsonresult = response.json()
        playlist_id = jsonresult.get('id')
        add_to_playlist(playlist_id)
        print(response.text)


def add_to_playlist(playlist_id):
    url = "https://api.spotify.com/v1/playlists/" + str(playlist_id) + "/tracks"
    querystring = {"uris": "spotify:track:7euaaij2ohk5MC8xAzHPMO,spotify:track:5tYosD9TicWDYO3kAE4ADp"}
    headers = req_headers

    response = requests.request("POST", url, headers=headers, params=querystring)

    print(response.text)


new_playlist()
