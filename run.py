#!/usr/bin/env python3
import sys
import requests as r
import typing as t
import json

from loguru import logger


class Track(t.NamedTuple):
    id: int
    artist: str
    album: str
    title: str
    now_playing: bool


def to_track(idx: int, track: t.Mapping[str, t.Any]) -> Track:
    return Track(
        id=idx,
        artist=track['artist']['#text'],
        album=track['album']['#text'],
        title=track['name'],
        now_playing=bool(track.get('@attr', {}).get('nowplaying', False)),
    )


def pretty_table(
        tracks: t.Sequence[Track],
        table_format: str,
) -> str:
    from tabulate import tabulate

    rows = [[
        '*' if track.now_playing else '', track.title, track.artist,
        track.album
    ] for track in tracks]

    return tabulate(
        rows,
        headers=['🤘', 'T', 'AR', 'AL'],
        tablefmt=table_format,
    )


if __name__ == '__main__':
    resp = r.get(
        'https://ws.audioscrobbler.com/2.0/',
        params={
            'method': 'user.getrecenttracks',
            'user': str(sys.argv[1]),
            'limit': '50',
            'api_key': str(sys.argv[2]),
            'format': 'json',
        }
    )
    assert resp.ok

    tracks = [
        to_track(idx, track) for idx, track in
        enumerate(resp.json()['recenttracks'].get('track', []))
    ]
    logger.info(
        'Succesfully mapped all tracks={t}',
        t=tracks,
    )

    patch_body = {
        'description': (
            f'{sys.argv[1]} :: '
            f'{"listens now" if any(map(lambda t: t.now_playing, tracks[:5])) else "paused"}'
        ),
        'files': {
            '10_recent.txt': {
                'content': pretty_table(tracks[:10], 'simple'),
                'filename': '10_recent.txt',
            },
            '50_recent.txt': {
                'content': pretty_table(tracks[:50], 'simple'),
                'filename': '50_recent.txt',
            },
            '100_recent.txt': {
                'content': pretty_table(tracks[:100], 'simple'),
                'filename': '100_recent.txt',
            },
            'powered_by.md': {
                'content': '\n'.join([
                    '# Powered by',
                    '* [kornicameister/spogity](https://github.com/kornicameister/spogity)',
                    '* [GH Actions](https://github.com/features/actions)',
                    '* [LastFM](https://www.last.fm/user/kornicameister/library)',
                ]),
                'filename': 'powered_by.md',
            },
        },
    }
    logger.info(
        'Patching gist={gist_id} with body={b}',
        gist_id=sys.argv[3],
        b=patch_body,
    )

    resp = r.patch(
        f'https://api.github.com/gists/{sys.argv[3]}',
        headers={
            'Authorization': f'token {sys.argv[4]}',
        },
        json=patch_body,
    )

    logger.info(
        'gist={gist_id} patched {result}',
        gist_id=sys.argv[3],
        result='successfully' if resp.ok else 'without success',
    )

    logger.info(
        '{r}',
        r=json.dumps(resp.json(), indent=2),
    )
