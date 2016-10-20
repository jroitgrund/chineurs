"""
store facebook groups
"""

from yoyo import step

__depends__ = {'20161019_04_4sgyf-s-email-facebook-id'}

steps = [
    step("CREATE TABLE facebook_groups ("
         "user_id INT REFERENCES users (id), group_name TEXT, group_id TEXT, "
         "PRIMARY KEY (user_id, group_id))")
]
