#!/usr/bin/env python3

import traceback
import requests
from datetime import datetime

import scrape
from config import ID_LOG, SLACK_POST


def main():
    try:
        run()
    except Exception as e:
        msg = traceback.format_exc()
        print(msg)
        print(e)
        # TODO: right now if there's an error, it just prints


def run():
    try:
        with open(ID_LOG, 'r') as f:
            known_ids = set(l.strip() for l in f if len(l)>2)
    except FileNotFoundError:
        known_ids = set()

    s = scrape.Scraper.with_search_query()
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
    # response = requests.post(SLACK_POST, headers=headers, json=msg)
    # print(response.status_code)


if __name__ == '__main__':
    main()
