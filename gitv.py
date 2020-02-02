""" TODO """

from subprocess import Popen, PIPE
import pandas as pd
import pyecharts.options as opts
from pyecharts.charts import Bar, Timeline
import regex as re
#from dateutil.parser import parse


#@profile
def repo_analyze():
    """
    TODO
    """
    commit_info = {}
    index = 0
    #repo = r'/home/chenhuiz/work/reveal.js'
    repo = r'/home/chenhuiz/django-bootstrap-toolkit'
    cmd = [
        r'git', r'log',
        r'--pretty=format:%cn committed %h on %cI',
        r'--shortstat',
        r'--no-merges',
        r'--reverse'
    ]

    with Popen(cmd, cwd=repo, stdout=PIPE, stderr=PIPE) as proc:
        for line in proc.stdout:
            string = line.decode()
            match = re.search(r' committed \w{7} on', string)
            if match:
                author = string[:match.start()]
                date = string[match.end():-7]
                # Too slow way
                #date = parse(string[match.end():-1]).strftime('%Y-%m-%d %H:%M:%S')
                insert = 0
                delete = 0
            elif re.search(r'file|insert|delet', string):
                match = re.match(r".* (?P<insert>\d+) insertion?", string)
                if match:
                    insert = int(match.group('insert'))
                match = re.match(r".* (?P<delete>\d+) deletion?", string)
                if match:
                    delete = int(match.group('delete'))
            else:
                commit_info[index] = {
                    "date": date,
                    "author": author,
                    "add": insert - delete,
                    "insert": insert,
                    "delete": delete
                }
                index += 1

    return pd.DataFrame.from_dict(commit_info, "index")

def get_commits_chart(time: str, names: list, c_insert: list, c_delete: list, c_add: list) -> Bar:
    """
    TODO
    """
    contribute = (
        Bar()
        .add_xaxis(xaxis_data=names)
        .add_yaxis(
            series_name="Insert",
            yaxis_data=c_insert,
            is_selected=True,
            label_opts=opts.LabelOpts(is_show=True),
        )
        .add_yaxis(
            series_name="Delete",
            yaxis_data=c_delete,
            is_selected=True,
            label_opts=opts.LabelOpts(is_show=True),
        )
        .add_yaxis(
            series_name="Add",
            yaxis_data=c_add,
            is_selected=True,
            label_opts=opts.LabelOpts(is_show=True),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="{} Contribution".format(time), subtitle="Git"
            ),
        )
    )
    return contribute

#@profile
def get_topX(top: dict, row: tuple, x: int):
    """
    TODO
    """
    _, _, author, add, insert, delete = row

    if author not in top:
        top[author] = (add, insert, delete)
    else:
        top[author] = (top[author][0] + add, \
                top[author][1] + insert, \
                top[author][2] + delete)

    topX = {k: v for k, v in sorted(top.items(), reverse=True, key=lambda i: i[1][0])[:x]}

    return pd.DataFrame(topX).T.rename_axis("author").add_prefix('v').reset_index()

def gcv_main():
    """
    TODO
    """
    # 生成时间轴的图
    timeline = Timeline(init_opts=opts.InitOpts(width="1600px", height="800px"))

    commit_log = repo_analyze()

    contribute = {}

    for item in commit_log.itertuples():
        top_commiter = get_topX(contribute, item, 5)

        timeline.add(get_commits_chart(time=item[1], \
                names=top_commiter['author'].tolist(), \
                c_insert=top_commiter['v1'].tolist(), \
                c_delete=top_commiter['v2'].tolist(), \
                c_add=top_commiter['v0'].tolist()), \
                time_point=item[1])

    # 1.0.0 版本的 add_schema 暂时没有补上 return self 所以只能这么写着
    timeline.add_schema(is_auto_play=True, play_interval=100)
    timeline.render("git.html")


if __name__ == "__main__":
    gcv_main()
