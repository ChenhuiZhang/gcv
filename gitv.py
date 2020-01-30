""" TODO """

import pandas as pd
import git
import pyecharts.options as opts
from pyecharts.charts import Bar, Timeline

def get_repo():
    """
    TODO
    """
    #repo = git.Repo(r'~/work/reveal.js', odbt=git.GitCmdObjectDB)
    repo = git.Repo(r'~/django-bootstrap-toolkit', odbt=git.GitCmdObjectDB)
    commits = pd.DataFrame(repo.iter_commits('master'), columns=['raw'])

    commits['author'] = commits['raw'].apply(lambda x: x.author.name)
    commits['committed_date'] = commits['raw'].apply(\
            lambda x: x.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'))
    commits['lines'] = commits['raw'].apply(lambda x: x.stats.total['lines'])
    commits['insert'] = commits['raw'].apply(lambda x: x.stats.total['insertions'])
    commits['delete'] = commits['raw'].apply(lambda x: x.stats.total['deletions'])

    return commits.iloc[::-1]

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

def get_topX(top: dict, row: tuple, x: int):
    """
    TODO
    """
    _, _, author, *_, insert, delete = row

    contribute = pd.DataFrame(columns=['author', 'add', 'insert', 'delete'])

    if author not in top:
        top[author] = (insert - delete, insert, delete)
    else:
        top[author] = (top[author][0] + insert - delete, \
                top[author][1] + insert, \
                top[author][2] + delete)

    topX = sorted(top.items(), reverse=True, key=lambda x: x[1][0])[:x]

    for elem in topX:
        rec = pd.Series(\
                {'author': elem[0], 'add': elem[1][0], 'insert': elem[1][1], 'delete': elem[1][2]})
        contribute = contribute.append(rec, ignore_index=True)

    return contribute

def gcv_main():
    """
    TODO
    """
    # 生成时间轴的图
    timeline = Timeline(init_opts=opts.InitOpts(width="1600px", height="800px"))

    commit_hist = get_repo()

    contribute = {}

    for item in commit_hist.itertuples():
        top_commiter = get_topX(contribute, item, 5)

        timeline.add(get_commits_chart(time=item[3], \
                names=top_commiter['author'].tolist(), \
                c_insert=top_commiter['insert'].tolist(), \
                c_delete=top_commiter['delete'].tolist(), \
                c_add=top_commiter['add'].tolist()), \
                time_point=item[3])

    # 1.0.0 版本的 add_schema 暂时没有补上 return self 所以只能这么写着
    timeline.add_schema(is_auto_play=True, play_interval=100)
    timeline.render("git.html")

if __name__ == "__main__":
    gcv_main()
