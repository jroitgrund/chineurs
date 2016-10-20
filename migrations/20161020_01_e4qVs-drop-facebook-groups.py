"""
drop facebook groups
"""

from yoyo import step

__depends__ = {'20161019_05_NKPra-store-facebook-groups'}

steps = [
    step("DROP TABLE facebook_groups")
]
