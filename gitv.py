import pandas as pd
import git
import pyecharts.options as opts
from pyecharts.charts import Bar, Timeline

repo = git.Repo(r'~/django-bootstrap-toolkit', odbt=git.GitCmdObjectDB)
commits = pd.DataFrame(repo.iter_commits('master'), columns=['raw'])

commits['author'] = commits['raw'].apply(lambda x: x.author.name)
commits['committed_date'] = commits['raw'].apply(
    lambda x: x.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'))
commits['lines'] = commits['raw'].apply(lambda x: x.stats.total['lines'])
commits['insert'] = commits['raw'].apply(lambda x: x.stats.total['insertions'])
commits['delete'] = commits['raw'].apply(lambda x: x.stats.total['deletions'])

new = commits.iloc[::-1]

def get_commits_chart(time: str, names: list, c_insert: list, c_delete: list) -> Bar:
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

for row in new.itertuples():
    _, _, author, date, lines, insert, delete = row

    if author not in authors:
        authors.append(author)
        contributes.append(lines)
        insert_lines.append(insert)
        delete_lines.append(delete)
    else:
        contributes[authors.index(author)] += lines
        insert_lines[authors.index(author)] += insert
        delete_lines[authors.index(author)] += delete

    timeline.add(get_commits_chart(time=date,
        names=authors.copy(),
        c_insert=insert_lines.copy(),
        c_delete=delete_lines.copy()),
        time_point=date)

# 1.0.0 版本的 add_schema 暂时没有补上 return self 所以只能这么写着
timeline.add_schema(is_auto_play=True, play_interval=100)
timeline.render("git.html")
