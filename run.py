#!/usr/bin/env python3
import sys
import os
import requests as r
import typing as t


class Track(t.NamedTuple):
    id: int
    artist: str
    album: str
    title: str


def to_track(arg: t.Tuple[int, t.Mapping[str, t.Any]]) -> Track:
    idx = arg[0]
    track = arg[1]
    return Track(
        id=idx,
        artist=track['artist']['#text'],
        album=track['album']['#text'],
        title=track['name'],
    )


if __name__ == '__main__':
    resp = r.get(
        'https://ws.audioscrobbler.com/2.0/',
        params={
            'method': 'user.getrecenttracks',
            'user': sys.argv[1],
            'limit': 10,
            'api_key': sys.argv[2],
            'format': 'json',
        }
    )
    assert resp.ok

    tracks = map(
        to_track,
        enumerate(
            sorted(
                resp.json()['recenttracks'].get('track', []),
                key=lambda track: int(track['date']['uts']),
                reverse=True,
            )
        )
    )
