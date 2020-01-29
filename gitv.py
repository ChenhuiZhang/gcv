import pandas as pd
import git
import pyecharts.options as opts
from pyecharts.charts import Bar, Timeline

repo = git.Repo(r'~/work/reveal.js', odbt=git.GitCmdObjectDB)
#repo = git.Repo(r'~/django-bootstrap-toolkit', odbt=git.GitCmdObjectDB)
commits = pd.DataFrame(repo.iter_commits('master'), columns=['raw'])

commits['author'] = commits['raw'].apply(lambda x: x.author.name)
commits['committed_date'] = commits['raw'].apply(
    lambda x: x.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'))
commits['lines'] = commits['raw'].apply(lambda x: x.stats.total['lines'])
commits['insert'] = commits['raw'].apply(lambda x: x.stats.total['insertions'])
commits['delete'] = commits['raw'].apply(lambda x: x.stats.total['deletions'])

new = commits.iloc[::-1]

def get_commits_chart(time: str, names: list, c_insert: list, c_delete: list, c_add: list) -> Bar:
    bar = (
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
    return bar


# 生成时间轴的图
timeline = Timeline(init_opts=opts.InitOpts(width="1600px", height="800px"))

authors = []
contributes = []
insert_lines = []
delete_lines = []
top = {}

for row in new.itertuples():
    _, _, author, date, lines, insert, delete = row

    if author not in authors:
        authors.append(author)
        contributes.append(lines)
        top[author] = (insert - delete, insert, delete)
    else:
        contributes[authors.index(author)] += lines
        top[author] = (top[author][0] + insert - delete, top[author][1] + insert, top[author][2] + delete)

    top10 = sorted(top.items(), reverse=True, key=lambda x: x[1][0])[:5]

    c_authors = []
    insert_lines = []
    delete_lines = []
    add_lines = []

    for elem in top10:
        c_authors.append(elem[0])
        add_lines.append(elem[1][0])
        insert_lines.append(elem[1][1])
        delete_lines.append(elem[1][2])

    timeline.add(get_commits_chart(time=date, \
        names=c_authors, \
        c_insert=insert_lines, \
        c_delete=delete_lines, \
        c_add=add_lines), \
        time_point=date)

# 1.0.0 版本的 add_schema 暂时没有补上 return self 所以只能这么写着
timeline.add_schema(is_auto_play=True, play_interval=100)
timeline.render("git.html")
