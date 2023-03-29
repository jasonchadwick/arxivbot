#!/usr/bin/env python3

import sys
import traceback
import requests
from datetime import datetime

import scrape
from config import ID_LOGS, SLACK_POSTS

THEORY_URL = 'https://arxiv.org/search/advanced?advanced=&terms-0-term=cs.CC&terms-0-operator=AND&terms-0-field=all&terms-1-term=cs.DS&terms-1-operator=OR&terms-1-field=all&terms-2-term=quantum&terms-2-operator=AND&terms-2-field=all&terms-3-term=cs.DS&terms-3-operator=OR&terms-3-field=all&terms-4-term=graphs&terms-4-operator=AND&terms-4-field=all&classification-computer_science=y&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=100&order=-announced_date_first'


def main(url=None):
    try:
        run(url)
    except Exception as e:
        msg = traceback.format_exc()
        print(msg)
        print(e)
        # TODO: right now if there's an error, it just prints


def run(url=None):
    try:
        with open(ID_LOG, 'r') as f:
            known_ids = set(l.strip() for l in f if len(l)>2)
    except FileNotFoundError:
        known_ids = set()

    s = scrape.Scraper.with_search_query(url=url)
    s.scrape()

    results = tuple(r for r in s.results if r.paper_id not in known_ids)

    print('{} new results'.format(len(results)))

    if len(results) > 0:
        with open(ID_LOG, 'a') as f:
            f.write('# {:%Y-%m-%d}\n'.format(datetime.now().date()))
            for r in reversed(results):
                f.write(r.paper_id)
                f.write('\n')
            f.write('\n')

        txt = '{} new paper{} on arXiv.\n\n\n'.format(
                    len(results), 's'*(len(results)!=1))
        slack_post_header(s, results)
        for r in reversed(results):
            rr = str(r)
            txt += rr
            txt += '\n'*3

            slack_post_result(r)

        subject = 'arXiv update ({} new paper{})'.format(
                        len(results), 's'*(len(results)!=1))


def slack_post_header(s, results):
    slack_post_raw(
        as_user=False,
        icon_emoji=':books:',
        text='@channel\n:books: <{}|{} new paper{} on arXiv>'.format(
                s.url, len(results), 's'*(len(results) != 1)),
        link_names=True,
        unfurl_links=False,
        unfurl_media=False,
        mrkdwn=True)


def slack_post_result(r):
    slack_post_raw(**r.slack_post())


def slack_post_raw(**msg):
    headers = {'content-type': 'application/json'}
    response = requests.post(SLACK_POST, headers=headers, json=msg)
    print(response.status_code)


if __name__ == '__main__':
    print("Running script at", datetime.now())
    print(sys.argv)
    if sys.argv[1] == 'theory':
        ID_LOG = ID_LOGS['theory']
        SLACK_POST = SLACK_POSTS['theory']
        main(url=THEORY_URL)
    elif sys.argv[1] == 'quantum':
        ID_LOG = ID_LOGS['quantum']
        SLACK_POST = SLACK_POSTS['quantum']
        main()
    else:
        print("bad argument; which query do I use?")
