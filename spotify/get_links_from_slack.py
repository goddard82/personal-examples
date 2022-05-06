import requests
import time

slack_channel_id = "CT2D9Q2NT"

slack_token = "blah"


def get_links(slack_channel_id, slack_token):
    url = "https://slack.com/api/conversations.history"
    querystring = {"channel": slack_channel_id}
    payload = ""
    headers = {"Authorization": "Bearer " + slack_token}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    messages = jsonresult.get("messages")
    for message in messages:
        attachments = message.get("attachments")
        if attachments:
            for attachment in attachments:
                service_name = attachment.get("service_name")
                from_url = attachment.get("from_url")
                if service_name != "Spotify":
                    if ".gif" not in from_url:
                        write_links_to_file(service_name, from_url)
                else:
                    write_links_to_file(service_name, from_url)
    response_metadata = jsonresult.get("response_metadata")
    next_cursor = response_metadata.get("next_cursor")
    get_next_links(next_cursor, slack_channel_id, slack_token)


def get_next_links(next_cursor, slack_channel_id, slack_token):
    url = "https://slack.com/api/conversations.history"
    querystring = {"channel": slack_channel_id, "cursor": next_cursor}
    payload = ""
    headers = {"Authorization": "Bearer " + slack_token}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    messages = jsonresult.get("messages")
    if messages:
        for message in messages:
            attachments = message.get("attachments")
            reply_count = message.get("reply_count")
            ts = message.get("ts")
            if reply_count:
                time.sleep(1)
                get_replies(ts)
            else:
                if attachments:
                    for attachment in attachments:
                        service_name = attachment.get("service_name")
                        from_url = attachment.get("from_url")
                        if service_name != "Spotify":
                            write_links_to_file(service_name, from_url)
        # print(response.text)
        response_metadata = jsonresult.get("response_metadata")
        next_cursor = response_metadata.get("next_cursor")
        time.sleep(1)
        get_next_links(next_cursor, slack_channel_id, slack_token)

    else:
        print(jsonresult)


def get_replies(ts, slack_channel_id, slack_token):
    url = "https://slack.com/api/conversations.replies"

    querystring = {"channel": slack_channel_id, "ts": ts}

    payload = ""
    headers = {"Authorization": "Bearer " + slack_token}
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    jsonresult = response.json()
    messages = jsonresult.get("messages")
    if messages:
        for message in messages:
            attachments = message.get("attachments")
            if attachments:
                for attachment in attachments:
                    service_name = attachment.get("service_name")
                    from_url = attachment.get("from_url")
                    if service_name != "Spotify":
                        if from_url and ".gif" not in from_url:
                            write_links_to_file(service_name, from_url)
                        else:
                            print(service_name)
                    else:
                        write_links_to_file(service_name, from_url)
    else:
        print(jsonresult)
    # print(response.text)


def write_links_to_file(service_name, from_url):
    # temp print out
    print({"service": service_name, "link": from_url})



def get_album_tracks(album):
    track_list = []
    url = "https://api.spotify.com/v1/playlists/" + album + "/tracks"
    querystring = {"market": "gb"}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer BQBn71VKjbJLD2ACa0dUtamPO0KFyEdh21FXzADFpV19Ne1dr9Kktdzi1WjDXLxocEopvN-qXFcsqujejZdsnZLnyQi_g4SoPz5XNE3lR5lgZ-SrskDK80Bvn2nydPIqGvX2dOkH5HHmwM2mNQUWInVRM-TmREYMwjdPXH9GDp6yPnTd7iczgt13AZ2MY07Nsd7CpE2TIxWFzrQJSA"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    jsonresult = response.json()
    items = jsonresult.get('items')
    for item in items:
        track = item.get('track')
        uri = track.get('uri')
        if "track" in uri:
            track_list.append(uri)
    print(track_list)


def get_playlist_tracks(playlist):
    track_list = []
    url = "https://api.spotify.com/v1/playlists/" + playlist + "/tracks"
    querystring = {"market": "gb"}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer BQBn71VKjbJLD2ACa0dUtamPO0KFyEdh21FXzADFpV19Ne1dr9Kktdzi1WjDXLxocEopvN-qXFcsqujejZdsnZLnyQi_g4SoPz5XNE3lR5lgZ-SrskDK80Bvn2nydPIqGvX2dOkH5HHmwM2mNQUWInVRM-TmREYMwjdPXH9GDp6yPnTd7iczgt13AZ2MY07Nsd7CpE2TIxWFzrQJSA"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    jsonresult = response.json()
    items = jsonresult.get('items')
    for item in items:
        track = item.get('track')
        uri = track.get('uri')
        if "track" in uri:
            track_list.append(uri)
    print(track_list)

# get_links(next_cursor, slack_channel_id, slack_token)

list_of_things = [{"service": "Songkick", "link": "https://www.songkick.com/artists/555278-ulrich-schnauss"},
                  {"service": "Spotify",
                   "link": "https://open.spotify.com/album/79ac2jNgieeKzrkzcGaa3l?si=cjMkRt-UTJ6HQzlt1lY0Bg"},
                  {"service": "Spotify",
                   "link": "https://open.spotify.com/track/1pyXSvT0Sj5uWSJbwMdZC7?si=cfe3000d797d4fea"},
                  {"service": "Spotify",
                   "link": "https://open.spotify.com/track/325VVodN2bVcByGxLyybTK?si=a353f16ec7334b28"},
                  {"service": "Spotify",
                   "link": "https://open.spotify.com/track/7rID1ForJ2U3YT6N8oVMbO?si=3d1c88ade3734624"},
                  {"service": "Spotify",
                   "link": "https://open.spotify.com/track/4VGa1by1qnmiV4JSde3mnz?si=3dd4ba18b03743d1"}]


# https://open.spotify.com/playlist/7ETZxiqxrhQAKcrRh2NqZn?si=eb95a27db0ed4290
albums = ['6o7nGNxjcQF04D6epk1vOf', '0bS5uOkhs1NjqAX79aHjSr', '0lCo5xt78SBDop9pm56E76', '1ijkFiMeHopKkHyvQCWxUa', '79ac2jNgieeKzrkzcGaa3l', '1SY37ob6pYF2mBBhONNKmL', '5atrOg1aO4d5KEcYo4UBIA', '08Ihv2AKcGRwxd0M9xoQ6S', '3qaW8k2mtG3p9tiOVNRkYh', '4gj8h7CymDda5DWulyVJey', '2No3jXDWQWuWlose3dJbgv', '4iqRgUboK84tJjN2prm9JP', '7GdeIkHAyeOJDPpg34hNAg', '0oNB7NzIM3UQT40saIZIK2', '1j3GYTPdoHkyOp3ALlyRfc', '5xp8nj4Uji2Kr1nkm3CLFC', '5BOhq1PafML6DPA09wygcD', '3erYafFxS957wtwrwXC583', '3vm1Ph1arV4EH2zfzl8xvR', '1Zpy29XOWBR42YeNymwmZ5', '0Dy6UqW0NHe80kBDvSc5JH', '7hHWviZ8Gqrve9WBMLC8Qe', '24pYEynNi6D7T0rj5WQqpQ', '07igNBjUqmgregGtDpnTNg', '3frlnKF0J7CZ2oXRJwHOZV', '5g2FK1ZEYRvr1aQIqdcM1Z', '6gcAUc2LUZfbHwZZJLgvtm', '4KNOQdMgMdSgyBMUtzPT02', '7sVUd1xQtfCkt7JDSfqpTn', '7yiKaSJBhzriJgp5w09X58', '012oKUlmu9qA84z4kYrOAj', '4yssWRZcdhnkbrIKbjZMdy', '18fqUiIpf0XaFy60VmidAr', '3HpFr2EeE38hr706Rxtmjy', '1ijkFiMeHopKkHyvQCWxUa', '2No3jXDWQWuWlose3dJbgv', '6tR5Kg1s8OT9zrrr0ZWNaR', '7d1lZrhDxWYInTDOMhrUfh', '7zdCHghAWjaRBVwqIDYx7v', '2IOYwdDRXs6dJ8Dz7JDG6K', '12EHjKDsfCdj2cejAdX7PA', '5gIa8hTQGPwVeNYjDwrraZ', '5Rr2NMSWTD6F7rsKAbhTXb', '2T64N96AVfsrRFJCUXQEoZ']

playlists_and_albums = ['https://open.spotify.com/album/6o7nGNxjcQF04D6epk1vOf?si=a_NvGOTTTUaPn9jYrNOA_Q',
                        'https://open.spotify.com/album/0bS5uOkhs1NjqAX79aHjSr?si=K-tHiLxQQ0WYI7RangmyHg',
                        'https://open.spotify.com/album/0lCo5xt78SBDop9pm56E76?si=oURJH8BPT9y9V-EHoI7E8Q',
                        'https://open.spotify.com/album/1ijkFiMeHopKkHyvQCWxUa?si=91PZUj7ZQoGvve0ianIYPQ',
                        'https://open.spotify.com/playlist/37i9dQZF1DWZtZ8vUCzche?si=1540173288484e91',
                        'https://open.spotify.com/playlist/6FMcjpl45ol3yDmpZGYTvF?si=f738ecd2ec1b496b',
                        'https://open.spotify.com/playlist/1IM2CTSU3nsw94nqHcPf1D?si=9739e46af452419d',
                        'https://open.spotify.com/playlist/4Ib4Bx1zQxzL0YwV1WCO3q?si=6afe3f70c3c04c52',
                        'https://open.spotify.com/album/79ac2jNgieeKzrkzcGaa3l?si=cjMkRt-UTJ6HQzlt1lY0Bg',
                        'https://open.spotify.com/playlist/37i9dQZF1DXa71eg5j9dKZ?si=5fdc8db0e56345b5',
                        'https://open.spotify.com/playlist/37i9dQZF1DXa71eg5j9dKZ?si=fbb92c528e7f48e5',
                        'https://open.spotify.com/album/1SY37ob6pYF2mBBhONNKmL?si=hF3rvoHvSSqkB9Zhims6Ag&amp;dl_branch=1',
                        'https://open.spotify.com/album/5atrOg1aO4d5KEcYo4UBIA?si=xQMIeSO5Q3KVlEEyBIZhnw&amp;dl_branch=1',
                        'https://open.spotify.com/album/08Ihv2AKcGRwxd0M9xoQ6S?si=VkNSYX30RI6Owy-mGreL_g&amp;dl_branch=1',
                        'https://open.spotify.com/playlist/2sqzezv8t9VuCnLZ1cKzuF?si=5161288fbe564e51',
                        'https://open.spotify.com/playlist/2HhUApXeqLfssYtMb1Jk2V?si=m4vfGmF_RCm2w4JC-FQcPQ&amp;utm_source=copy-link&amp;dl_branch=1',
                        'https://open.spotify.com/album/3qaW8k2mtG3p9tiOVNRkYh?si=Wa-z0pyDQ128171b2d6tkA&amp;dl_branch=1',
                        'https://open.spotify.com/album/4gj8h7CymDda5DWulyVJey?si=loDEodpMSwWVSAZcLM3ufA&amp;dl_branch=1',
                        'https://open.spotify.com/album/2No3jXDWQWuWlose3dJbgv?si=LuVZGT2FSl6L_B0P8BnYiQ&amp;dl_branch=1',
                        'https://open.spotify.com/album/4iqRgUboK84tJjN2prm9JP?si=DjGsK8QBRiSGp5xi0_qHQg&amp;dl_branch=1',
                        'https://open.spotify.com/playlist/37i9dQZF1DX9WbnZpHWMaI?si=ec6e82fd86b0482a',
                        'https://open.spotify.com/album/7GdeIkHAyeOJDPpg34hNAg?si=tpez6YBvS-GMAMLZq8YbwA&amp;dl_branch=1',
                        'https://open.spotify.com/artist/04jj7dljPI0ixtNsz2pXWK?si=oheN2XFuS0qKy5q4Bh6Abw&amp;dl_branch=1',
                        'https://open.spotify.com/album/0oNB7NzIM3UQT40saIZIK2?si=rsVld42OT0WLaiiuJmsptw',
                        'https://open.spotify.com/playlist/37i9dQZF1DXa71eg5j9dKZ?si=NVYvUo2XScm6Ww4D7WavAw',
                        'https://open.spotify.com/album/1j3GYTPdoHkyOp3ALlyRfc?si=-kvMcS27QOiVT3DJ5beRRg',
                        'https://open.spotify.com/album/5xp8nj4Uji2Kr1nkm3CLFC?si=E3AGP0-eQfCqVAugVbkbVA',
                        'https://open.spotify.com/album/5BOhq1PafML6DPA09wygcD?si=hlMCdzo1RSiszYk6PdC7xQ',
                        'https://open.spotify.com/album/3erYafFxS957wtwrwXC583?si=fK4WrvoqRXmnvSXzciN4dQ',
                        'https://open.spotify.com/album/3vm1Ph1arV4EH2zfzl8xvR?si=dRrUiv51Q5y23DVftc8-aA',
                        'https://open.spotify.com/album/1Zpy29XOWBR42YeNymwmZ5?si=uHXVsKjZSOChalw1-Xr4BA',
                        'https://open.spotify.com/album/0Dy6UqW0NHe80kBDvSc5JH?si=BfA8SXYXTFectOdNjhOR_w',
                        'https://open.spotify.com/album/7hHWviZ8Gqrve9WBMLC8Qe?si=LUGlWTncRVesNe0--IrNMw',
                        'https://open.spotify.com/album/24pYEynNi6D7T0rj5WQqpQ?si=kJEGlW20Q3mNoldH73t1FA',
                        'https://open.spotify.com/playlist/5aL9jeGMCA7uiH8MviKDSQ?si=8AuxWZzxRPS1TxtKwJkRzQ',
                        'https://open.spotify.com/album/07igNBjUqmgregGtDpnTNg?si=Ru7ShCS4S0GuMq5_Jftbjg',
                        'https://open.spotify.com/album/3frlnKF0J7CZ2oXRJwHOZV?si=AHV0Jo5SRrKhyB0TyFlSNw',
                        'https://open.spotify.com/album/5g2FK1ZEYRvr1aQIqdcM1Z?si=lC6VY7KWSpmEgvInxeA5Qg',
                        'https://open.spotify.com/album/6gcAUc2LUZfbHwZZJLgvtm?si=G_hW8RSDRcCH0Ce6i5SXcQ',
                        'https://open.spotify.com/album/4KNOQdMgMdSgyBMUtzPT02?si=9Go4TuwSTFO4TvE6T_ITyQ',
                        'https://open.spotify.com/album/7sVUd1xQtfCkt7JDSfqpTn?si=oct5eNR0RJ2c4Iphn_dVdw',
                        'https://open.spotify.com/album/7yiKaSJBhzriJgp5w09X58?si=adQN4iqASQq6XIEEZuZRlw',
                        'https://open.spotify.com/album/012oKUlmu9qA84z4kYrOAj?si=4P02PjcVRYeYE-ejFegJEw',
                        'https://open.spotify.com/album/4yssWRZcdhnkbrIKbjZMdy?si=SonNKlvpSr2un3nhyFPQAg',
                        'https://open.spotify.com/album/18fqUiIpf0XaFy60VmidAr?si=9RNvs39yTIWu0DRh0aTFFw',
                        'https://open.spotify.com/album/3HpFr2EeE38hr706Rxtmjy?si=_67fYjZiREyt9I_aeRRwUw',
                        'https://open.spotify.com/playlist/1cQ4wFFjPdxVGgazzFK5LW?si=KC6othIdT1KNlX3ADI2vSA',
                        'https://open.spotify.com/album/1ijkFiMeHopKkHyvQCWxUa?si=AMb932SbTDGk9Wxrv8LuzQ',
                        'https://open.spotify.com/album/2No3jXDWQWuWlose3dJbgv?si=JQmYJsdaR1iGd1zbtj3G2w',
                        'https://open.spotify.com/album/6tR5Kg1s8OT9zrrr0ZWNaR?si=IpzV2OUpR82hDexlYF3fBQ',
                        'https://open.spotify.com/playlist/3jl3CyKtRhSWvKBLuGnohT?si=kU7hqApUQp-tpWjlJQj_Qw',
                        'https://open.spotify.com/album/7d1lZrhDxWYInTDOMhrUfh?si=RUR0r17aR52esh2XHrKoWA',
                        'https://open.spotify.com/album/7zdCHghAWjaRBVwqIDYx7v?si=7EZDmgwmTnqz1YWHRDy7hA',
                        'https://open.spotify.com/album/2IOYwdDRXs6dJ8Dz7JDG6K?si=hBNGgcDCSWWBmWs31zga4A',
                        'https://open.spotify.com/artist/4XK2N5qsj8FUVZHeIL3ilM',
                        'https://open.spotify.com/artist/0y91rhzvi0xhkvdcjiAXmA',
                        'https://open.spotify.com/album/12EHjKDsfCdj2cejAdX7PA',
                        'https://open.spotify.com/album/5gIa8hTQGPwVeNYjDwrraZ?si=0vE-tx8eTve_SCGXcomyvg',
                        'https://open.spotify.com/album/5Rr2NMSWTD6F7rsKAbhTXb?si=cxMVUtZTT4WOYDPVcV6MTg',
                        'https://open.spotify.com/album/2T64N96AVfsrRFJCUXQEoZ?si=jtdSLnUYToCaO0c8WrC1Kg']

# for thing in albums:
#     get_album_tracks(thing)


playlists = ['37i9dQZF1DWZtZ8vUCzche', '6FMcjpl45ol3yDmpZGYTvF', '1IM2CTSU3nsw94nqHcPf1D', '4Ib4Bx1zQxzL0YwV1WCO3q', '37i9dQZF1DXa71eg5j9dKZ', '37i9dQZF1DXa71eg5j9dKZ', '2sqzezv8t9VuCnLZ1cKzuF', '2HhUApXeqLfssYtMb1Jk2V', '37i9dQZF1DX9WbnZpHWMaI', '37i9dQZF1DXa71eg5j9dKZ', '5aL9jeGMCA7uiH8MviKDSQ', '1cQ4wFFjPdxVGgazzFK5LW', '3jl3CyKtRhSWvKBLuGnohT']
for thing in playlists:
 get_playlist_tracks(thing)