"""
Add date to playlist_inserts
"""

from yoyo import step

__depends__ = {'20161018_01_vCSKP'}

steps = [
    step("ALTER TABLE playlist_inserts ADD COLUMN datetime timestamp")
]
