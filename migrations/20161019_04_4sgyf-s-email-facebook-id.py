"""
s/email/facebook_id
"""

from yoyo import step

__depends__ = {'20161019_03_gZ5KD-make-timestamp-include-tz-info'}

steps = [
    step("ALTER TABLE users RENAME email TO facebook_id")
]
