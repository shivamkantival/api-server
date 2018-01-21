import os
import json
import requests
import logging


SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
ENDPOINIT = 'https://slack.com/api/users.list'
CONTACTS_FILE = 'contacts.json'


def get_team(title):
    teams = {
        'Engineering': [
            'code', 'engineer', 'frontend', 'backend', 'dev'
        ],
        'Customer Relations': [
            'csi', 'community'
        ],
        'Design': [
            'design', 'art'
        ],
        'Data': [
            'data', 'analytics'
        ],
        'Marketing': [
            'pr ', 'marketing', 'lifestyle', 'global'
        ],
        'Store': [
            'orchard', '90'
        ]

    }
    fallback = 'Manager'  # Pun intended.

    if not title:
        return 'Teamless'

    for name, keys in teams.iteritems():
        if any(ext in title.lower() for ext in keys):
            return name
    return fallback


def main():
    url = '%s?token=%s' % (ENDPOINIT, SLACK_TOKEN)
    r = requests.get(url)
    if not r.ok:
        logging.error('Received Unexpected HTTP %s', r.status_code)
        return -1

    data = r.json()
    if data['ok'] is not True:
        logging.error('Received Slack error: %s', data['error'])
        return -1

    members = {}
    for member in data['members']:

        if member['deleted'] is True \
           or member['is_restricted'] is True \
           or member['is_bot'] is True \
           or 'bot' in member['name']:  # "slackbot" :(
            continue

        profile = member['profile']
        members[member['id']] = {
            "id": member.get('id'),
            "location": member.get('tz'),
            "color": member.get('color'),
            "team": get_team(profile.get('title')),
            "first_name": profile.get('first_name'),
            "last_name": profile.get('last_name'),
            "title": profile.get('title'),
            "image": profile.get('image_512'),
        }

    d = json.dumps(members, sort_keys=True, indent=4, separators=(',', ': '))
    with open(CONTACTS_FILE, 'w') as f:
        l = f.write(d)

    logging.debug('Wrote %s to %s:' % (l, CONTACTS_FILE))
    logging.debug(d)


if __name__ == '__main__':
    main()
