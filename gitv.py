import pandas as pd
import git
import pyecharts.options as opts
from pyecharts.charts import Line,Bar,Timeline

repo = git.Repo(r'~/django-bootstrap-toolkit', odbt=git.GitCmdObjectDB)
commits = pd.DataFrame(repo.iter_commits('master'), columns=['raw'])
print(commits.head())

commits['author'] = commits['raw'].apply(lambda x: x.author.name)
commits['committed_date'] = commits['raw'].apply(lambda x: pd.to_datetime(x.committed_datetime))
#commits['committed_date'] = commits['raw'].apply(lambda x: pd.to_datetime(x.committed_datetime, format='%Y/%m/%d'))
#commits['committed_date'] = commits['raw'].apply(lambda x: x.committed_datetime.strftime("%Y %B W%w"))
commits['lines'] = commits['raw'].apply(lambda x: x.stats.total['lines'])
commits['insert'] = commits['raw'].apply(lambda x: x.stats.total['insertions'])
commits['delete'] = commits['raw'].apply(lambda x: x.stats.total['deletions'])

#date = commits["committed_date"].apply(lambda x: str(x)).tolist()

#print(commits.head())
#print(commits.tail())
#print(commits.info())

new = commits.iloc[::-1]

#date = new["committed_date"].apply(lambda x: str(x)).tolist()
#print(commits.groupby(['author', 'committed_date'], as_index=False).agg({'lines' : sum, 'raw' : 'first'}))
#df.groupby('ID', as_index=False).agg({'NAME' : ' '.join, 'AGE' : 'first'})

#l = Line()
#l.add_xaxis(xaxis_data=date)
#l.add_yaxis(series_name="", y_axis=new['lines'])
#l.set_global_opts(title_opts=opts.TitleOpts(title="某商场销售情况"))
#l.render()

def get_year_overlap_chart(time: int, names: list, value: list) -> Bar:
    bar = (
        Bar()
        .add_xaxis(xaxis_data=names)
        .add_yaxis(
            series_name="Lines",
            yaxis_data=value,
            is_selected=True,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="{}contribution".format(time), subtitle="Git"
            ),
            tooltip_opts=opts.TooltipOpts(
                is_show=True, trigger="axis", axis_pointer_type="shadow"
            ),
        )
    )
    return bar


# 生成时间轴的图
timeline = Timeline(init_opts=opts.InitOpts(width="1600px", height="800px"))

authors = []
contributes = []

for row in new.itertuples():
    author = row[2]
    date = row[3]
    line = row[4]
    if author not in authors:
        authors.append(author)
        contributes.append(line)
    else:
        contributes[authors.index(author)] += line

    timeline.add(get_year_overlap_chart(time=date, names=authors.copy(), value=contributes.copy()), time_point=date)

# 1.0.0 版本的 add_schema 暂时没有补上 return self 所以只能这么写着
timeline.add_schema(is_auto_play=True, play_interval=1000)
timeline.render("git.html")
