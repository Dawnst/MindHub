#!/usr/bin/env python3
"""生成虚构演示数据库 /tmp/wbdemo/workbench.db（人设：小北 · 产品经理）。
- 若 /tmp/wb3prev 有快照库则复制其结构作底子，否则现场建库骨架；
- 随后全量改写为虚构数据：身份 / 纪念日 / 人生节点 / 目标 / 项目 / 待办 / 专注 / AI 对话；
- 凭据类配置（AI key、CalDAV 账密、备份目录）一律假化清空；
- 末尾自带泄漏自检：全库不得出现任何真实数据关键词。
绝不触碰 /tmp/wb3prev 原件与 8383 正式库。配套：起 8392 实例后跑 capture.py。"""
import sqlite3, json, random, string, os, shutil

random.seed(20261007)
DATA_DIR = '/tmp/wbdemo'
DB = os.path.join(DATA_DIR, 'workbench.db')
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(DB):
    src = '/tmp/wb3prev/workbench.db'
    if os.path.exists(src):
        for ext in ['', '-wal', '-shm']:
            if os.path.exists(src + ext):
                shutil.copy(src + ext, DB + ext)
    else:
        shutil.copy(os.devnull, DB)  # 触发 sqlite 新建空库
db = sqlite3.connect(DB)
db.execute("""CREATE TABLE IF NOT EXISTS events(
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TEXT DEFAULT (datetime('now','localtime')))""")
db.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS ai_usage(id TEXT PRIMARY KEY, data TEXT NOT NULL, updated_at TEXT DEFAULT (datetime('now','localtime')))")
db.execute("CREATE TABLE IF NOT EXISTS cache(key TEXT PRIMARY KEY, value TEXT)")
db.commit()

def get(k, default=None):
    row = db.execute("SELECT value FROM settings WHERE key=?", (k,)).fetchone()
    return json.loads(row[0]) if row else default

def put(k, v):
    db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
               (k, json.dumps(v, ensure_ascii=False)))

def rid():  # 模仿原 id 形态：idm + 12 位小写字母数字
    return 'idm' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# ── 身份 ────────────────────────────────────────────
put('userName', '小北')
put('birthday', '1995-06-15')

# ── 纪念日（无照片 bg）───────────────────────────────
put('annivs', [
    {"id": "ann-demo0001", "name": "结婚纪念日", "date": "2022-05-20", "note": "", "cal": "solar"},
    {"id": "ann-demo0002", "name": "爸爸生日",   "date": "1968-03-22", "note": "", "cal": "lunar"},
    {"id": "ann-demo0003", "name": "妈妈生日",   "date": "1970-08-08", "note": "", "cal": "lunar"},
    {"id": "ann-demo0004", "name": "领养小猫芝麻", "date": "2024-04-01", "note": "", "cal": "solar"},
])

# ── 人生时间轴 ──────────────────────────────────────
put('lifeEvs', [
    {"id": "life-demo01", "name": "出生",         "date": "1995-06-15", "state": "flat", "note": ""},
    {"id": "life-demo02", "name": "上大学",       "date": "2013-09-01", "state": "up",   "note": ""},
    {"id": "life-demo03", "name": "第一份工作",   "date": "2017-07-03", "state": "up",   "note": ""},
    {"id": "life-demo04", "name": "转型产品经理", "date": "2020-04-01", "state": "up",   "note": ""},
    {"id": "life-demo05", "name": "买房",         "date": "2021-10-01", "state": "up",   "note": ""},
    {"id": "life-demo06", "name": "结婚",         "date": "2022-05-20", "state": "flat", "note": ""},
    {"id": "life-demo07", "name": "宝宝出生",     "date": "2024-08-12", "state": "flat", "note": ""},
    {"id": "life-demo08", "name": "搬进新家",     "date": "2026-01-15", "state": "up",   "note": ""},
])

# ── 人生之花 ────────────────────────────────────────
put('balanceWheel', {"dims": [
    {"name": "健康", "cur": 6}, {"name": "家庭", "cur": 7}, {"name": "事业", "cur": 5},
    {"name": "财富", "cur": 4}, {"name": "人际", "cur": 6}, {"name": "成长", "cur": 7},
    {"name": "休闲", "cur": 3}, {"name": "爱好", "cur": 4}], "count": 8})

# ── 目标（沿用原字段结构）────────────────────────────
put('goals', [
    {"id": "goal_demo01", "title": "养成每周运动习惯", "createdAt": "2026-10-01", "done": False,
     "dim": "健康", "year": 2026, "value": {"start": 0, "target": 12, "unit": "次"},
     "startDate": "2026-10-01", "endDate": "2026-10-31",
     "plan": [
         {"id": "pt_demo011", "title": "跑步 3 公里",   "freq": "daily",  "start": "", "days": [1, 3, 5], "timesPerWeek": 3},
         {"id": "pt_demo012", "title": "健腹轮 4 组",  "freq": "weekly", "start": "", "days": [], "timesPerWeek": 2},
         {"id": "pt_demo013", "title": "户外徒步 10 公里", "freq": "monthly", "start": "", "days": [], "timesPerWeek": 1, "monthDays": [15]}],
     "records": []},
    {"id": "goal_demo02", "title": "每月读完 2 本书", "createdAt": "2026-10-02", "done": False,
     "dim": "成长", "year": 2026, "value": {"start": 0, "target": 2, "unit": "本"},
     "startDate": "2026-10-01", "endDate": "2026-10-31",
     "plan": [{"id": "pt_demo021", "title": "睡前阅读 30 分钟", "freq": "daily", "start": "22:30", "days": [], "timesPerWeek": 5}],
     "records": []},
    {"id": "goal_demo03", "title": "个人网站改版上线", "createdAt": "2026-09-20", "done": False,
     "dim": "事业", "year": 2026, "value": {"start": 0, "target": 100, "unit": "%"},
     "startDate": "2026-09-20", "endDate": "2026-10-23",
     "plan": [{"id": "pt_demo031", "title": "推进开发任务", "freq": "weekly", "start": "", "days": [2, 6], "timesPerWeek": 2}],
     "records": []},
])

# ── 项目（2 个，带依赖与里程碑）──────────────────────
put('projects', [
    {"id": "pj_demo01", "title": "个人网站改版", "start": "2026-09-20", "end": "2026-10-23",
     "note": "年度改版：新版视觉 + 博客 + 订阅", "createdAt": "2026-09-20", "tasks": [
        {"id": "pt_d101", "title": "需求梳理与信息架构", "sdate": "2026-09-20", "date": "2026-09-24", "done": True,  "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d102", "title": "视觉稿与设计系统",   "sdate": "2026-09-24", "date": "2026-09-30", "done": True,  "dep": ["pt_d101"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d103", "title": "首页开发",           "sdate": "2026-09-28", "date": "2026-10-09", "done": False, "dep": ["pt_d102"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d104", "title": "文章页与归档",       "sdate": "", "date": "2026-10-14", "done": False, "dep": ["pt_d103"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d105", "title": "订阅功能上线",       "sdate": "", "date": "2026-10-16", "done": False, "dep": ["pt_d104"], "subs": [], "ms": True,  "note": "里程碑", "owner": ""},
        {"id": "pt_d106", "title": "性能优化与备案",     "sdate": "", "date": "2026-10-20", "done": False, "dep": ["pt_d105"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d107", "title": "正式上线",           "sdate": "", "date": "2026-10-23", "done": False, "dep": ["pt_d106"], "subs": [], "ms": True,  "note": "", "owner": ""}]},
    {"id": "pj_demo02", "title": "厨房改造", "start": "2026-09-25", "end": "2026-10-24",
     "note": "", "createdAt": "2026-09-25", "tasks": [
        {"id": "pt_d201", "title": "定预算与风格",       "sdate": "2026-09-25", "date": "2026-09-28", "done": True,  "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d202", "title": "选橱柜与电器",       "sdate": "2026-10-06", "date": "2026-10-12", "done": False, "dep": ["pt_d201"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d203", "title": "拆旧与清运",         "sdate": "", "date": "2026-10-13", "done": False, "dep": ["pt_d202"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d204", "title": "水电改造",           "sdate": "2026-10-14", "date": "2026-10-16", "done": False, "dep": ["pt_d203"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d205", "title": "橱柜安装完成",       "sdate": "", "date": "2026-10-21", "done": False, "dep": ["pt_d204"], "subs": [], "ms": True,  "note": "", "owner": ""},
        {"id": "pt_d206", "title": "验收与保洁",         "sdate": "", "date": "2026-10-24", "done": False, "dep": ["pt_d205"], "subs": [], "ms": False, "note": "", "owner": ""}]},
])

# ── 待办（虚构全量重建）─────────────────────────────
TAGS = {t['name']: t['id'] for t in get('tags')}   # 沿用现有标签：产品/销售/市场/个人
def todo(date, title, *, start="", deadline="", tag='', pri='normal', note='', place='',
         done=False, doneAt='', repeat='', repeatDays=None, source='manual', sched=False):
    d = {"type": "todo", "date": date, "title": title, "start": start, "deadline": deadline,
         "repeat": repeat, "repeatDays": repeatDays or [], "tag": TAGS.get(tag, ''),
         "priority": pri, "note": note, "place": place, "subs": [], "id": rid(),
         "source": source, "done": done, "doneAt": doneAt if done else '', "sdate": ""}
    if sched:
        d["sched"] = True
    return d

T = []
# 今天 2026-10-07（周三）
T += [todo('2026-10-07', '晨会：本周排期对齐', start='09:30', deadline='10:00', tag='产品', done=True, doneAt='2026-10-07', sched=True),
      todo('2026-10-07', '产品评审会', start='15:00', deadline='16:00', tag='产品', place='会议室 A', sched=True),
      todo('2026-10-07', '整理竞品调研笔记', tag='产品', note='先补交互细节部分'),
      todo('2026-10-07', '跑步 3 公里', tag='个人', pri='high'),
      todo('2026-10-07', '预约体检', tag='个人', pri='low', note='挂号 App 上约下周三')]
# 超期未完成
T += [todo('2026-10-05', '缴物业费', tag='个人', pri='low'),
      todo('2026-10-04', '寄秋茶给爸妈', tag='个人')]
# 过去两周（已完成 + 少量未完成）
past = [
    ('2026-09-24', '写季度 OKR 草案', '产品', 'high', True, ('10:00', '11:00')),
    ('2026-09-25', '竞品功能矩阵初稿', '产品', 'normal', True, ('', '')),
    ('2026-09-25', '和小林对齐改版视觉稿', '产品', 'normal', True, ('16:00', '16:30')),
    ('2026-09-26', '周报', '产品', 'low', True, ('', '')),
    ('2026-09-26', '给小猫买猫粮', '个人', 'low', True, ('', '')),
    ('2026-09-27', '徒步 10 公里', '个人', 'high', True, ('', '')),
    ('2026-09-28', '需求评审会', '产品', 'normal', True, ('14:00', '15:00')),
    ('2026-09-28', '读《产品设计心理学》第 3 章', '个人', 'normal', True, ('', '')),
    ('2026-09-29', '用户访谈 x2', '产品', 'high', True, ('10:00', '12:00')),
    ('2026-09-29', '整理访谈纪要', '产品', 'normal', True, ('', '')),
    ('2026-09-30', '9 月数据分析', '产品', 'normal', True, ('', '')),
    ('2026-09-30', '和小林过视觉稿细节', '产品', 'normal', True, ('15:30', '16:00')),
    ('2026-10-01', '家庭日：公园野餐', '个人', 'normal', True, ('', '')),
    ('2026-10-02', '首页开发：导航与 Hero', '产品', 'high', True, ('', '')),
    ('2026-10-03', '朋友来家聚餐', '个人', 'normal', True, ('18:00', '21:00')),
    ('2026-10-04', '跑步 3 公里', '个人', 'normal', True, ('', '')),
    ('2026-10-05', '读《产品设计心理学》第 4 章', '个人', 'normal', True, ('', '')),
    ('2026-10-05', '厨房改造：量尺寸', '个人', 'normal', True, ('', '')),
    ('2026-10-06', '首页开发：文章列表', '产品', 'high', True, ('', '')),
    ('2026-10-06', '给爸妈打电话', '个人', 'normal', True, ('', '')),
    ('2026-10-06', '报销 9 月差旅', '市场', 'low', False, ('', '')),
]
SCHED_PAST = {('2026-09-24', '写季度 OKR 草案'), ('2026-09-28', '需求评审会'),
              ('2026-09-29', '用户访谈 x2'), ('2026-10-03', '朋友来家聚餐')}
for d, t, tg, p, dn, (s, e) in past:
    T.append(todo(d, t, tag=tg, pri=p, start=s, deadline=e, done=dn, doneAt=d if dn else '',
                  sched=(d, t) in SCHED_PAST))
# 未来一周
T += [todo('2026-10-08', '设计评审：改版视觉稿', tag='产品', start='14:00', deadline='15:00', sched=True),
      todo('2026-10-08', '和小林对齐开发排期', tag='产品', start='16:00', deadline='16:30'),
      todo('2026-10-09', '项目周会', tag='产品', start='10:00', deadline='10:45', place='会议室 B', sched=True),
      todo('2026-10-09', '宝宝疫苗复诊', tag='个人', pri='high', start='15:00', deadline='16:00', note='带上疫苗本', sched=True),
      todo('2026-10-10', '周六家庭日：植物园', tag='个人'),
      todo('2026-10-11', '写周复盘', tag='产品', pri='low'),
      todo('2026-10-16', '缴车险', tag='个人', pri='low')]
# 重复任务
T += [todo('2026-10-09', '周报', tag='产品', repeat='weekly', repeatDays=[5]),
      todo('2027-03-18', '车辆年检', tag='个人', repeat='yearly')]

db.execute("DELETE FROM events")
for t in T:
    db.execute("INSERT INTO events(id,data,updated_at) VALUES(?,?,datetime('now','localtime'))",
               (t['id'], json.dumps(t, ensure_ascii=False)))

# ── 专注记录（引用虚构待办标题）──────────────────────
FL = []
focus_src = [('2026-09-24', '10:04', '写季度 OKR 草案', 25, 1500, True),
             ('2026-09-25', '09:12', '竞品功能矩阵初稿', 25, 1500, True),
             ('2026-09-28', '14:22', '需求评审材料', 25, 1500, True),
             ('2026-09-28', '20:31', '读《产品设计心理学》', 25, 900, False),
             ('2026-09-29', '10:02', '用户访谈准备', 25, 1500, True),
             ('2026-09-30', '16:40', '9 月数据分析', 25, 1500, True),
             ('2026-10-02', '09:40', '首页开发：导航与 Hero', 25, 1500, True),
             ('2026-10-02', '15:10', '首页开发：导航与 Hero', 25, 1500, True),
             ('2026-10-04', '08:30', '跑步 3 公里', 25, 1500, True),
             ('2026-10-05', '21:05', '睡前阅读', 25, 1200, False),
             ('2026-10-06', '09:35', '首页开发：文章列表', 25, 1500, True),
             ('2026-10-06', '14:00', '首页开发：文章列表', 25, 1500, True),
             ('2026-10-07', '09:58', '晨会材料', 25, 1500, True),
             ('2026-10-07', '13:40', '整理竞品调研笔记', 25, 760, False)]
for d, s, title, tg, sec, fin in focus_src:
    FL.append({"id": rid(), "evId": "", "evTitle": title, "date": d, "startAt": s,
               "mode": "down", "target": tg, "seconds": sec, "finished": fin})
put('focusLogs', FL)

# ── AI 对话（虚构问答）──────────────────────────────
put('aiChats', [
    {"id": "ac_demo01", "title": "总结下我上周的工作", "ts": 1791371600000, "agent": "hermes", "msgs": [
        {"role": "user", "content": "总结下我上周的工作"},
        {"role": "assistant", "content":
         "## 上周工作总结（9/28 – 10/04）\n\n**整体：完成 12 项待办、7 个专注段（约 2.9 小时）；改版项目是绝对主线，个人习惯线也在稳步推进。**\n\n### 一、网站改版（主线）\n- 视觉稿收尾：和小林过细节（9/30）后定稿\n- 首页开发启动：导航与 Hero（10/2，两个专注段）、文章列表（10/6，两个专注段）\n\n### 二、产品节奏\n- 需求评审会（9/28）、用户访谈 x2 + 纪要（9/29）、9 月数据分析（9/30）\n\n### 三、个人与家庭\n- 徒步 10 公里（9/27）、家庭日野餐（10/1）、跑步 1 次（10/4）\n- 阅读 1 章（《产品设计心理学》9/28、10/5 各一章）\n\n### 节奏观察\n- 专注段集中在上午 9–10 点与下午 2–4 点，午后利用率还有空间\n- 高优先级事项全部完成，低优先级「报销」「物业费」连续两周顺延\n\n### 本周建议\n- 把「报销」「缴物业费」合并到周五下午统一清掉\n- 改版进入开发深水区，建议每天留一个不受扰的上午专注段。"}],
     "plan": None},
    {"id": "ac_demo02", "title": "帮我安排周六的时间", "ts": 1791544400000, "agent": "muse", "msgs": [
        {"role": "user", "content": "帮我安排周六的时间"},
        {"role": "assistant", "content":
         "周六（10/10）已有 1 条待办：**周六家庭日：植物园**。\n\n建议这样排：\n- **上午 9:30–11:30** 植物园（避开人流，光线也适合拍照）\n- **午休后 14:00–15:30** 一个专注段：推进「文章页与归档」\n- **16:00** 顺手清掉「缴物业费」（2 分钟）\n- **晚上** 睡前阅读 30 分钟，保住阅读习惯的连续性\n\n周日只留了「写周复盘」，弹性充足。"}]},
])

# ── 凭据与隐私位清空/假化 ────────────────────────────
put('ai', {"base": "https://api.demo.invalid", "key": "sk-demo-000000000000000000000000",
           "model": "deepseek-flash", "mem": []})
put('caldav', {"on": False, "url": "", "user": "", "pass": ""})
put('backup', {"freq": "daily", "dir": "/tmp/wbdemo-backups"})
put('trash', [])

# ── 清空运行痕迹表 ──────────────────────────────────
db.execute("DELETE FROM ai_usage")
db.execute("DELETE FROM cache")

db.commit()

# ── 自检：全库文本不得再出现真实人名/公司/旧标题关键词 ──
leak_words = ['Shang', '宥宥', '李瑞满', '王利群', '嵊州', '彩谱', '托普', '中非', '岳父',
              '无人机', '水稻', '植保', '高光谱', '妙算', '卖房', '1993-10-01', 'sk-990']
bad = []
rows = db.execute("SELECT data FROM events").fetchall()
for (txt,) in rows:
    for w in leak_words:
        if w in (txt or ''):
            bad.append(('events', w))
for k in ['userName','birthday','annivs','lifeEvs','goals','projects','aiChats','focusLogs','trash','ai','caldav','backup','balanceWheel']:
    v = db.execute("SELECT value FROM settings WHERE key=?", (k,)).fetchone()[0]
    for w in leak_words:
        if w in v:
            bad.append(('settings:' + k, w))
print('LEAK:', bad if bad else 'none')
print('todos:', len(T), '| focus:', len(FL))
db.close()
