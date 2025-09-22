
import random
from datetime import datetime, date


class ResultInfo:
    def __init__(self, *, paper_id, title, category_id, category_name,
                 authors, abstract, submit_date, announce_date, version,
                 comments):
        self.paper_id = paper_id
        self.title = title
        self.category_id = category_id
        self.category_name = category_name
        self.authors = authors
        self.abstract = abstract
        self.submit_date = submit_date
        self.announce_date = announce_date
        self.version = version
        self.comments = comments

    @staticmethod
    def remove_const_line(txt, const_end, max_extra=5):
        txt = txt.strip()
        if txt.endswith(const_end):
            splt = txt.split('\n')
            if len(splt[-1].strip()) <= len(const_end) + max_extra:
                return '\n'.join(splt[:-1])
        return txt

    @classmethod
    def from_node(cls, node):
        paper_id = node.find(attrs={'class': 'list-title'}).find('a').text.split('arXiv:')[-1]
        title = node.find(attrs={'class': 'title'}).text.strip()
        category = node.find(attrs={'class': 'tag'})
        category_id = category.text.strip()
        category_name = category.attrs.get('data-tooltip')
        authors = tuple((n.text.strip(), 'https://arxiv.org' + n.attrs.get('href'))
                        for n in node.find(attrs={'class': 'authors'}).find_all('a'))
        abstract = cls.remove_const_line(node.find(attrs={'class': 'abstract-full'}).text, 'Less')

        submit_date = None
        announce_date = None
        for line in node.find(attrs={'class': 'abstract'}).find_next_sibling('p').text.strip().split(';'):
            line = line.strip(' .\r\n\t').lower()
            if line.lower().startswith('submitted'):
                submit_date = datetime.strptime(line.split('submitted')[-1].strip(), '%d %B, %Y').date()
            elif line.lower().startswith('originally announced'):
                announce_date = datetime.strptime(line.split('originally announced')[-1].strip(), '%B %Y').date()
        assert submit_date is not None
        assert announce_date is not None

        version = 'v'+node.find(attrs={'class': 'abstract-full'}).attrs['id'].split('-')[0].split('v')[-1]
        comments_node = node.find(attrs={'class': 'comments'})
        if comments_node is None:
            comments = ()
        else:
            comments = tuple(n.text.strip()
                             for n in comments_node
                                      .find_all('span', attrs={'class': 'mathjax'}))

        return cls(paper_id=paper_id,
                   title=title,
                   category_id=category_id,
                   category_name=category_name,
                   authors=authors,
                   abstract=abstract,
                   submit_date=submit_date,
                   announce_date=announce_date,
                   version=version,
                   comments=comments)

    def pdf_url(self):
        return 'https://arxiv.org/pdf/'+self.paper_id #+self.version

    def abs_url(self):
        return 'https://arxiv.org/abs/'+self.paper_id #+self.version

    def __str__(self):
        announce_str = ''
        if self.version != 'v1':
            announce_str = ', First: {:%Y-%m}'.format(self.announce_date)
        if len(self.comments) > 0:
            comment_list = ', ({})'.format('; '.join(self.comments))
        else:
            comment_list = ''
        return (
'''{self.title}
========
arXiv:{self.paper_id}{self.version}, {self.category_id} ({self.category_name})
{url}
{pdf_url}
Submitted: {self.submit_date:%Y-%m-%d}{announce_str}{comment_list}
Authors: {author_list}

{self.abstract}
'''
        .format(self=self, url=self.abs_url(), pdf_url=self.pdf_url(),
                author_list=', '.join(a[0] for a in self.authors),
                announce_str=announce_str,
                comment_list = comment_list))

    def slack_post(self):
        def escape_slack(text):
            return text.replace('&', '&amp;'
                      ).replace('<', '&lt;'
                      ).replace('>', '&gt;')

        def get_epoch_time(d):
            return (d - date(1970, 1, 1)).total_seconds()

        def rand_color():
            return '#{:06X}'.format(random.randint(0, 2**(8*3)-1))

        author_str = ('_Authors:_ '
                      + ', '.join('<{}|{}>'.format(a[1], escape_slack(a[0]))
                                  for a in self.authors))

        announce_str = ''
        if self.version != 'v1':
            announce_str = ', _First:_ {:%Y-%m}'.format(self.announce_date)
        if len(self.comments) > 0:
            comment_list = '\n({})'.format('; '.join(self.comments))
        else:
            comment_list = ''
        info_str = (
'''{category_id} (_{category_name}_)
<{url}|arXiv:{paper_id}{version}> [<{pdf_url}|pdf>]
_Submitted:_ {submit_date:%Y-%m-%d}{announce_str}{comment_list}'''
            .format(url=escape_slack(self.abs_url()),
                    pdf_url=escape_slack(self.pdf_url()),
                    paper_id=escape_slack(self.paper_id),
                    version=escape_slack(self.version),
                    category_id=escape_slack(self.category_id),
                    category_name=escape_slack(self.category_name),
                    submit_date=self.submit_date,
                    announce_str=announce_str,
                    comment_list=comment_list))

        color=rand_color()

        return dict(
            attachments=[
                dict(
                    fallback=self.title + '\n\n' + self.abstract,
                    color=color,
                    title=escape_slack(self.title),
                    text = '{}\n{}\n\n{}'.format(
                        info_str, author_str, escape_slack(self.abstract)),
                ),
            ],
            unfurl_links=False,
            unfurl_media=False,
            mrkdwn=True)
