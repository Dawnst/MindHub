#!/usr/bin/env python3
"""生成虚构演示数据库 /tmp/wbdemo/workbench.db（人设：小北 · 产品经理）。
v3（2026-10-10）：示例数据全面加厚——
- 周视图时刻化：本周每天 3-6 条带 start/deadline 的日程/限时任务进时间轴，每天仅 0-2 条留全天栏；
- 项目 2→4（新增 Q4 规划 + 去年已完成的「搬家整理」，喂统计页项目卡年份切换）；
- 目标 3→6（+写日记[去年已达成]、应急基金[财富]、联系朋友[人际]，覆盖 5 个维度）；
- 统计加料：完成回填扩到 -70 天（已使用天数 71）、热力更密、专注回填 -42 天且时段拉宽、
  新增 5 号标签「学习」、3 条草稿喂「草稿积压」、ai_usage 流水 14 天喂 AI 用量区块。
v2（2026-10-09）：
- 日期全部锚定「今天」动态生成（TODAY = date.today()），任何一天重跑数据都贴当前日期；
- 目标新增月历打卡事件（events 表内 goalId+planId+date，done:true）喂「月历多色格」，
  新增数值 records（{d,v} 一天一条）喂「变化趋势+理论进度线」；
- 回填约 8 周轻量已完成待办 + 近 4 周专注记录，喂统计页热力图/趋势；
- 若 /tmp/wb3prev 有快照库则复制其结构作底子，否则现场建库骨架；无标签时补演示标签；
- 凭据类配置（AI key、CalDAV 账密、备份目录）一律假化清空；清掉分栏/卡片布局旧键；
- 末尾自带泄漏自检：全库不得出现任何真实数据关键词。
绝不触碰 /tmp/wb3prev 原件与 8383 正式库。配套：起 8392 实例后跑 capture.py。"""
import sqlite3, json, random, string, os, shutil
from datetime import date, timedelta, datetime

TODAY = date.today()
random.seed(20261009)
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

def d(off):  # 相对今天的 ISO 日期
    return (TODAY + timedelta(days=off)).isoformat()

m_first = TODAY.replace(day=1)                                   # 本月
m_last = (m_first + timedelta(days=32)).replace(day=1) - timedelta(days=1)

# ── 身份 ────────────────────────────────────────────
put('userName', '小北')
put('birthday', '1995-06-15')

# ── 标签（演示库全量重建，直接覆盖为 5 个演示标签）─────
put('tags', [{"id": "tag_demo1", "name": "产品"}, {"id": "tag_demo2", "name": "销售"},
             {"id": "tag_demo3", "name": "市场"}, {"id": "tag_demo4", "name": "个人"},
             {"id": "tag_demo5", "name": "学习"}])

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
    {"id": "life-demo08", "name": "搬进新家",     "date": f"{TODAY.year}-01-15", "state": "up", "note": ""},
])

# ── 人生之花 ────────────────────────────────────────
put('balanceWheel', {"dims": [
    {"name": "健康", "cur": 6}, {"name": "家庭", "cur": 7}, {"name": "事业", "cur": 5},
    {"name": "财富", "cur": 4}, {"name": "人际", "cur": 6}, {"name": "成长", "cur": 7},
    {"name": "休闲", "cur": 3}, {"name": "爱好", "cur": 4}], "count": 8})

# ── 目标（含月历打卡 + 数值记录；覆盖 健康/成长/事业/财富/人际 5 维 + 1 个去年已达成）──
LY = TODAY.year - 1                                                # 去年（喂统计页年份切换）
G1, G2, G3, G4, G5, G6 = ('goal_demo0%d' % i for i in range(1, 7))
P11, P12, P13 = 'pt_demo011', 'pt_demo012', 'pt_demo013'
P21, P31, P51, P61 = 'pt_demo021', 'pt_demo031', 'pt_demo051', 'pt_demo061'
lyd = lambda mm, dd: f'{LY}-{mm:02d}-{dd:02d}'                     # 去年固定日期
put('goals', [
    {"id": G1, "title": "养成每周运动习惯", "createdAt": d(-8), "done": False,
     "dim": "健康", "year": TODAY.year, "value": {"start": 0, "target": 12, "unit": "次"},
     "startDate": m_first.isoformat(), "endDate": m_last.isoformat(),
     "plan": [
         {"id": P11, "title": "跑步 3 公里",   "freq": "daily",  "start": "", "days": [1, 3, 5], "timesPerWeek": 3},
         {"id": P12, "title": "健腹轮 4 组",  "freq": "weekly", "start": "", "days": [], "timesPerWeek": 2},
         {"id": P13, "title": "户外徒步 10 公里", "freq": "monthly", "start": "", "days": [], "timesPerWeek": 1, "monthDays": [15]}],
     "records": [{"d": d(-7), "v": 1}, {"d": d(-5), "v": 3}, {"d": d(-3), "v": 5},
                 {"d": d(-1), "v": 6}, {"d": d(0), "v": 7}]},
    {"id": G2, "title": "每月读完 2 本书", "createdAt": d(-7), "done": False,
     "dim": "成长", "year": TODAY.year, "value": {"start": 0, "target": 2, "unit": "本"},
     "startDate": m_first.isoformat(), "endDate": m_last.isoformat(),
     "plan": [{"id": P21, "title": "睡前阅读 30 分钟", "freq": "daily", "start": "22:30", "days": [], "timesPerWeek": 5}],
     "records": [{"d": d(-9), "v": 1}]},
    {"id": G3, "title": "个人网站改版上线", "createdAt": d(-19), "done": False,
     "dim": "事业", "year": TODAY.year, "value": {"start": 0, "target": 100, "unit": "%"},
     "startDate": d(-19), "endDate": d(+14),
     "plan": [{"id": P31, "title": "推进开发任务", "freq": "weekly", "start": "", "days": [2, 6], "timesPerWeek": 2}],
     "records": [{"d": d(-17), "v": 5}, {"d": d(-13), "v": 15}, {"d": d(-6), "v": 30}, {"d": d(-2), "v": 45}]},
    {"id": G4, "title": "坚持写日记 90 天", "createdAt": lyd(10, 8), "done": True,
     "dim": "成长", "year": LY, "value": {"start": 0, "target": 90, "unit": "天"},
     "startDate": lyd(10, 8), "endDate": lyd(12, 31),
     "plan": [{"id": "pt_demo041", "title": "写日记 15 分钟", "freq": "daily", "start": "21:30", "days": [], "timesPerWeek": 7}],
     "records": [{"d": lyd(10, 12), "v": 5}, {"d": lyd(10, 26), "v": 19}, {"d": lyd(11, 15), "v": 39},
                 {"d": lyd(11, 30), "v": 54}, {"d": lyd(12, 18), "v": 76}, {"d": lyd(12, 31), "v": 92}]},
    {"id": G5, "title": "攒出 5 万应急基金", "createdAt": d(-30), "done": False,
     "dim": "财富", "year": TODAY.year, "value": {"start": 8000, "target": 50000, "unit": "元"},
     "startDate": d(-30), "endDate": d(+95),
     "plan": [{"id": P51, "title": "记账 + 定期转入", "freq": "weekly", "start": "", "days": [6], "timesPerWeek": 1}],
     "records": [{"d": d(-28), "v": 12000}, {"d": d(-20), "v": 18000},
                 {"d": d(-12), "v": 26000}, {"d": d(-4), "v": 32000}]},
    {"id": G6, "title": "每周联系一位老朋友", "createdAt": d(-21), "done": False,
     "dim": "人际", "year": TODAY.year, "value": {"start": 0, "target": 12, "unit": "次"},
     "startDate": m_first.isoformat(), "endDate": m_last.isoformat(),
     "plan": [{"id": P61, "title": "约电话或见面", "freq": "weekly", "start": "", "days": [0], "timesPerWeek": 1}],
     "records": [{"d": d(-14), "v": 1}, {"d": d(-6), "v": 2}]},
])

# 月历打卡事件（形状对齐 goal-page.js calPaint：type todo + goalId/planId/source:'goal'）
def checkin(day_off, goal, plan, title):
    ds = d(day_off)
    return {"id": rid(), "type": "todo", "title": title, "date": ds, "sdate": "",
            "start": "", "deadline": "", "repeat": "", "repeatDays": [], "priority": "normal",
            "done": True, "doneAt": ds, "note": "", "subs": [],
            "goalId": goal, "planId": plan, "source": "goal"}

CHECKINS = [
    # 运动目标：跑步一三五 / 健腹轮二四；昨天两项同天（月历出多色格），今天健腹轮
    checkin(-7, G1, P11, '跑步 3 公里'), checkin(-5, G1, P11, '跑步 3 公里'),
    checkin(-3, G1, P11, '跑步 3 公里'), checkin(-1, G1, P11, '跑步 3 公里'),
    checkin(-6, G1, P12, '健腹轮 4 组'), checkin(-4, G1, P12, '健腹轮 4 组'),
    checkin(-1, G1, P12, '健腹轮 4 组'), checkin(0,  G1, P12, '健腹轮 4 组'),
    # 阅读目标：近两周隔天打卡，含今天
    *[checkin(o, G2, P21, '睡前阅读 30 分钟') for o in (-9, -7, -6, -4, -3, -1, 0)],
    # 网站目标：每周两次推进
    checkin(-17, G3, P31, '推进开发任务'), checkin(-13, G3, P31, '推进开发任务'),
    checkin(-6,  G3, P31, '推进开发任务'), checkin(-2,  G3, P31, '推进开发任务'),
    # 应急基金：每周六记账；联系朋友：上周 done 一次
    checkin(-7, G5, P51, '记账 + 定期转入'), checkin(0,  G5, P51, '记账 + 定期转入'),
    checkin(-6, G6, P61, '约电话或见面'),
]

# ── 项目（4 个：2 进行中 + 1 进行中规划 + 1 去年已完成，喂统计页项目卡年份切换）──
put('projects', [
    {"id": "pj_demo01", "title": "个人网站改版", "start": d(-19), "end": d(+14),
     "note": "年度改版：新版视觉 + 博客 + 订阅", "createdAt": d(-19), "tasks": [
        {"id": "pt_d101", "title": "需求梳理与信息架构", "sdate": d(-19), "date": d(-15), "done": True,  "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d102", "title": "视觉稿与设计系统",   "sdate": d(-15), "date": d(-9),  "done": True,  "dep": ["pt_d101"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d103", "title": "首页开发",           "sdate": d(-11), "date": d(+2),  "done": False, "dep": ["pt_d102"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d104", "title": "文章页与归档",       "sdate": "", "date": d(+7),  "done": False, "dep": ["pt_d103"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d105", "title": "订阅功能上线",       "sdate": "", "date": d(+9),  "done": False, "dep": ["pt_d104"], "subs": [], "ms": True,  "note": "里程碑", "owner": ""},
        {"id": "pt_d106", "title": "性能优化与备案",     "sdate": "", "date": d(+13), "done": False, "dep": ["pt_d105"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d107", "title": "正式上线",           "sdate": "", "date": d(+14), "done": False, "dep": ["pt_d106"], "subs": [], "ms": True,  "note": "", "owner": ""}]},
    {"id": "pj_demo02", "title": "厨房改造", "start": d(-14), "end": d(+15),
     "note": "", "createdAt": d(-14), "tasks": [
        {"id": "pt_d201", "title": "定预算与风格",       "sdate": d(-14), "date": d(-11), "done": True,  "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d202", "title": "选橱柜与电器",       "sdate": d(-3),  "date": d(+3),  "done": False, "dep": ["pt_d201"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d203", "title": "拆旧与清运",         "sdate": "", "date": d(+4),  "done": False, "dep": ["pt_d202"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d204", "title": "水电改造",           "sdate": d(+5),  "date": d(+7),  "done": False, "dep": ["pt_d203"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d205", "title": "橱柜安装完成",       "sdate": "", "date": d(+12), "done": False, "dep": ["pt_d204"], "subs": [], "ms": True,  "note": "", "owner": ""},
        {"id": "pt_d206", "title": "验收与保洁",         "sdate": "", "date": d(+15), "done": False, "dep": ["pt_d205"], "subs": [], "ms": False, "note": "", "owner": ""}]},
    {"id": "pj_demo03", "title": "Q4 产品规划", "start": d(-9), "end": d(+25),
     "note": "四季度路线图与资源排期", "createdAt": d(-9), "tasks": [
        {"id": "pt_d301", "title": "回顾 Q3 数据与反馈", "sdate": d(-9),  "date": d(-5),  "done": True,  "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d302", "title": "确定 Q4 三大主题",   "sdate": d(-4),  "date": d(+1),  "done": False, "dep": ["pt_d301"], "subs": [], "ms": True,  "note": "里程碑", "owner": ""},
        {"id": "pt_d303", "title": "排期与人力预估",     "sdate": "", "date": d(+8),  "done": False, "dep": ["pt_d302"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d304", "title": "向管理层汇报",       "sdate": "", "date": d(+15), "done": False, "dep": ["pt_d303"], "subs": [], "ms": False, "note": "", "owner": ""}]},
    {"id": "pj_demo04", "title": "搬家整理", "start": lyd(11, 5), "end": lyd(11, 25),
     "note": "去年完成的旧项目（已全部交付）", "createdAt": lyd(11, 5), "tasks": [
        {"id": "pt_d401", "title": "打包与断舍离",   "sdate": lyd(11, 5),  "date": lyd(11, 9),  "done": True, "dep": [], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d402", "title": "联系搬家公司",   "sdate": lyd(11, 8),  "date": lyd(11, 12), "done": True, "dep": ["pt_d401"], "subs": [], "ms": False, "note": "", "owner": ""},
        {"id": "pt_d403", "title": "搬家日",         "sdate": lyd(11, 15), "date": lyd(11, 16), "done": True, "dep": ["pt_d402"], "subs": [], "ms": True,  "note": "里程碑", "owner": ""},
        {"id": "pt_d404", "title": "归置与收纳",     "sdate": lyd(11, 17), "date": lyd(11, 25), "done": True, "dep": ["pt_d403"], "subs": [], "ms": False, "note": "", "owner": ""}]},
])

# ── 待办（虚构全量重建）─────────────────────────────
TAGS = {t['name']: t['id'] for t in get('tags')}
def todo(date, title, *, start="", deadline="", tag='', pri='normal', note='', place='',
         done=False, doneAt='', repeat='', repeatDays=None, source='manual', sched=False):
    dd = {"type": "todo", "date": date, "title": title, "start": start, "deadline": deadline,
          "repeat": repeat, "repeatDays": repeatDays or [], "tag": TAGS.get(tag, ''),
          "priority": pri, "note": note, "place": place, "subs": [], "id": rid(),
          "source": source, "done": done, "doneAt": doneAt if done else '', "sdate": ""}
    if sched:
        dd["sched"] = True
    return dd

T = list(CHECKINS)
# 今天（0，周六）：日程/限时任务进时间轴，仅 2 条留全天栏
t_review = todo(d(0), '产品评审会', start='15:00', deadline='16:00', tag='产品', place='会议室 A', sched=True)
t_review['subs'] = [{'t': '过订阅功能交互稿', 'd': True}, {'t': '确认性能优化范围', 'd': False}, {'t': '定审稿结论与分工', 'd': False}]
T += [todo(d(0), '晨会：本周排期对齐', start='09:30', deadline='10:00', tag='产品', done=True, doneAt=d(0), sched=True),
      todo(d(0), '项目周会', start='10:00', deadline='10:45', place='会议室 B', sched=True),
      todo(d(0), '写 PRD：订阅功能', start='11:00', deadline='12:00', tag='产品', done=True, doneAt=d(0)),
      t_review,
      todo(d(0), '整理竞品调研笔记', start='16:30', deadline='17:00', tag='产品', note='先补交互细节部分'),
      todo(d(0), '羽毛球队局', start='17:30', deadline='19:00', tag='个人', place='活力体育馆'),
      todo(d(0), '预约体检', tag='个人', pri='low', note='挂号 App 上约下周三'),
      todo(d(0), '跑步 3 公里', tag='个人', pri='high'),
      todo(d(0), '周报', tag='产品', repeat='weekly', repeatDays=[5])]
# 本周已过天（-5 周一 ~ -1 周五）：大部分带时刻，每天至多 1-2 条留全天
T += [todo(d(-5), '周会：改版排期', start='10:00', deadline='10:45', tag='产品', done=True, doneAt=d(-5), sched=True),
      todo(d(-5), '回产品群反馈 x6', start='14:00', deadline='14:30', tag='产品', done=True, doneAt=d(-5)),
      todo(d(-4), '和小林过首页交互', start='10:00', deadline='10:30', tag='产品', done=True, doneAt=d(-4)),
      todo(d(-4), '厨房改造：看橱柜样品', start='14:00', deadline='15:30', tag='个人', done=True, doneAt=d(-4), place='红星美凯龙'),
      todo(d(-3), '用户访谈 x1', start='10:00', deadline='11:00', tag='产品', done=True, doneAt=d(-3), sched=True),
      todo(d(-3), '写 9 月复盘', start='15:00', deadline='16:00', tag='产品', done=True, doneAt=d(-3)),
      todo(d(-2), '需求评审：订阅功能', start='14:00', deadline='15:00', tag='产品', done=True, doneAt=d(-2), sched=True),
      todo(d(-2), '健腹轮 4 组', start='19:00', deadline='19:20', tag='个人', done=True, doneAt=d(-2)),
      todo(d(-1), '发周报给团队', start='17:00', deadline='17:30', tag='产品', done=True, doneAt=d(-1)),
      todo(d(-1), '和家庭复盘本周开支', start='20:30', deadline='21:00', tag='个人', done=True, doneAt=d(-1)),
      # 草稿箱（无日期）：喂统计页「草稿积压」，不进周视图
      todo('', '整理相册备份到 NAS', tag='个人', pri='low'),
      todo('', '研究年终旅行路线', tag='个人'),
      todo('', '更新简历', tag='产品', pri='low')]
# 超期未完成
T += [todo(d(-4), '缴物业费', tag='个人', pri='low'),
      todo(d(-5), '寄秋茶给爸妈', tag='个人')]
# 过去两周（已完成 + 少量未完成）
past = [
    (-15, '写季度 OKR 草案', '产品', 'high', True, ('10:00', '11:00')),
    (-14, '竞品功能矩阵初稿', '产品', 'normal', True, ('', '')),
    (-14, '和小林对齐改版视觉稿', '产品', 'normal', True, ('16:00', '16:30')),
    (-13, '周报', '产品', 'low', True, ('', '')),
    (-13, '给小猫买猫粮', '个人', 'low', True, ('', '')),
    (-12, '徒步 10 公里', '个人', 'high', True, ('', '')),
    (-11, '需求评审会', '产品', 'normal', True, ('14:00', '15:00')),
    (-11, '读《产品设计心理学》第 3 章', '个人', 'normal', True, ('', '')),
    (-10, '用户访谈 x2', '产品', 'high', True, ('10:00', '12:00')),
    (-10, '整理访谈纪要', '产品', 'normal', True, ('', '')),
    (-9,  '9 月数据分析', '产品', 'normal', True, ('', '')),
    (-9,  '和小林过视觉稿细节', '产品', 'normal', True, ('15:30', '16:00')),
    (-8,  '家庭日：公园野餐', '个人', 'normal', True, ('', '')),
    (-7,  '首页开发：导航与 Hero', '产品', 'high', True, ('', '')),
    (-6,  '朋友来家聚餐', '个人', 'normal', True, ('18:00', '21:00')),
    (-5,  '跑步 3 公里', '个人', 'normal', True, ('07:30', '08:05')),
    (-4,  '读《产品设计心理学》第 4 章', '个人', 'normal', True, ('21:30', '22:00')),
    (-4,  '厨房改造：量尺寸', '个人', 'normal', True, ('16:00', '16:40')),
    (-3,  '首页开发：文章列表', '产品', 'high', True, ('09:30', '11:30')),
    (-3,  '给爸妈打电话', '个人', 'normal', True, ('20:00', '20:15')),
    (-3,  '报销 9 月差旅', '市场', 'low', False, ('', '')),
]
SCHED_PAST = {(-15, '写季度 OKR 草案'), (-11, '需求评审会'), (-10, '用户访谈 x2'), (-6, '朋友来家聚餐')}
for off, t, tg, p, dn, (s, e) in past:
    T.append(todo(d(off), t, tag=tg, pri=p, start=s, deadline=e, done=dn, doneAt=d(off) if dn else '',
                  sched=(off, t) in SCHED_PAST))
# 未来一周
T += [todo(d(+1), '晨跑 5 公里', tag='个人', start='08:00', deadline='08:40'),
      todo(d(+1), '设计评审：改版视觉稿', tag='产品', start='14:00', deadline='15:00', sched=True),
      todo(d(+1), '和小林对齐开发排期', tag='产品', start='16:00', deadline='16:30'),
      todo(d(+1), '睡前阅读 30 分钟', tag='个人', start='22:00', deadline='22:30'),
      todo(d(+2), '写周复盘', tag='产品', pri='low'),
      todo(d(+3), '家庭日：植物园', tag='个人'),
      todo(d(+7), '缴车险', tag='个人', pri='low'),
      todo(d(+160), '车辆年检', tag='个人', repeat='yearly')]
# 回填年初以来的已完成小任务（喂统计页热力图/趋势/已使用天数；起点=1 月中，热力图铺满大半年）
POOL = [('整理周报', '产品'), ('回复用户反馈', '产品'), ('需求文档更新', '产品'), ('数据周报整理', '市场'),
        ('给爸妈打电话', '个人'), ('采购日用品', '个人'), ('读书 30 分钟', '个人'), ('慢跑 2 公里', '个人'),
        ('整理 Inbox', '个人'), ('和同事 1:1', '产品'), ('健身 30 分钟', '个人'), ('写周复盘', '产品'),
        ('背单词 30 分钟', '学习'), ('上网课 1 节', '学习'), ('整理学习笔记', '学习'), ('写技术周记', '学习')]
BACKFILL_START = date(TODAY.year, 1, 12)                           # 今年 1 月 12 日开始使用
SPAN = (TODAY - BACKFILL_START).days
T.append(todo(BACKFILL_START.isoformat(), '注册 MindHub，开始记录', tag='个人', done=True,
              doneAt=BACKFILL_START.isoformat()))                  # 最早活动日 → 已使用天数
for off in range(-SPAN + 1, -15):
    if random.random() < 0.85:
        for _ in range(1 + (random.random() < 0.45) + (random.random() < 0.15)):
            t, tg = random.choice(POOL)
            T.append(todo(d(off), t, tag=tg, done=True, doneAt=d(off)))

db.execute("DELETE FROM events")
for t in T:
    db.execute("INSERT INTO events(id,data,updated_at) VALUES(?,?,datetime('now','localtime'))",
               (t['id'], json.dumps(t, ensure_ascii=False)))

# ── 专注记录（近两周实感 + 近 4 周回填）──────────────
FL = []
focus_src = [(-15, '10:04', '写季度 OKR 草案', 1500),
             (-14, '09:12', '竞品功能矩阵初稿', 1500),
             (-11, '14:22', '需求评审材料', 1500),
             (-11, '20:31', '读《产品设计心理学》', 900),
             (-10, '10:02', '用户访谈准备', 1500),
             (-9,  '16:40', '9 月数据分析', 1500),
             (-7,  '09:40', '首页开发：导航与 Hero', 1500),
             (-7,  '15:10', '首页开发：导航与 Hero', 1500),
             (-5,  '08:30', '跑步 3 公里', 1500),
             (-4,  '21:05', '睡前阅读', 1200),
             (-3,  '09:35', '首页开发：文章列表', 1500),
             (-3,  '14:00', '首页开发：文章列表', 1500),
             (-2,  '09:58', '晨会材料', 1500),
             (0,   '09:20', '写 PRD：订阅功能', 1500),
             (0,   '13:40', '整理竞品调研笔记', 760),
             (0,   '16:10', '产品评审准备', 1200)]
for off, s, title, sec in focus_src:
    FL.append({"id": rid(), "evId": "", "evTitle": title, "date": d(off), "startAt": s,
               "mode": "down", "target": 25, "seconds": sec, "finished": sec >= 1500})
for off in range(-42, -14):
    if random.random() < 0.55:
        t, _ = random.choice(POOL)
        FL.append({"id": rid(), "evId": "", "evTitle": t, "date": d(off),
                   "startAt": f"{random.choice(['08','09','10','11','14','15','16','20','21'])}:{random.choice(['05','20','35','50'])}",
                   "mode": "down", "target": 25, "seconds": 1500, "finished": True})
put('focusLogs', FL)

# ── AI 对话（虚构问答）──────────────────────────────
ts1 = int((datetime.now() - timedelta(days=2)).timestamp() * 1000)
ts2 = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
put('aiChats', [
    {"id": "ac_demo01", "title": "总结下我上周的工作", "ts": ts1, "agent": "hermes", "msgs": [
        {"role": "user", "content": "总结下我上周的工作"},
        {"role": "assistant", "content":
         "## 上周工作总结\n\n**整体：完成 14 项待办、6 个专注段（约 2.5 小时）；改版项目是绝对主线，运动与阅读习惯也在稳步推进。**\n\n### 一、网站改版（主线）\n- 视觉稿收尾：和小林过细节后定稿\n- 首页开发启动：导航与 Hero（两个专注段）、文章列表（两个专注段）\n\n### 二、产品节奏\n- 需求评审会、用户访谈 x2 + 纪要、9 月数据分析\n\n### 三、个人与家庭\n- 徒步 10 公里、家庭日野餐、跑步按一三五节奏推进\n- 阅读推进 1 章（《产品设计心理学》）\n\n### 节奏观察\n- 专注段集中在上午 9–10 点与下午 2–4 点，午后利用率还有空间\n- 高优先级事项全部完成，低优先级「报销」「物业费」连续两周顺延\n\n### 本周建议\n- 把「报销」「缴物业费」合并到周五下午统一清掉\n- 改版进入开发深水区，建议每天留一个不受扰的上午专注段。"}],
     "plan": None},
    {"id": "ac_demo02", "title": "帮我安排周六的时间", "ts": ts2, "agent": "hermes", "msgs": [
        {"role": "user", "content": "帮我安排周六的时间"},
        {"role": "assistant", "content":
         "周六已有 1 条待办：**家庭日：植物园**。\n\n建议这样排：\n- **上午 9:30–11:30** 植物园（避开人流，光线也适合拍照）\n- **午休后 14:00–15:30** 一个专注段：推进「文章页与归档」\n- **16:00** 顺手清掉「缴物业费」（2 分钟）\n- **晚上** 睡前阅读 30 分钟，保住阅读习惯的连续性\n\n周日只留了「写周复盘」，弹性充足。"}]},
])

# ── 凭据与隐私位清空/假化 ────────────────────────────
put('ai', {"base": "https://api.demo.invalid", "key": "sk-demo-000000000000000000000000",
           "model": "deepseek-flash", "mem": []})
put('caldav', {"on": False, "url": "", "user": "", "pass": ""})
put('backup', {"freq": "daily", "dir": "/tmp/wbdemo-backups"})
put('trash', [])

# ── 清掉会带走旧布局的键（让 v3.8.99/108 的新默认值生效）──
for k in ('cardGrid', 'ovSplit', 'gfSplit', 'todoSbW', 'pjSbW', 'gfMonth'):
    db.execute("DELETE FROM settings WHERE key=?", (k,))

# ── 清空运行痕迹表，再灌入虚构 AI 用量流水（喂统计页 AI 用量区块）──
db.execute("DELETE FROM ai_usage")
db.execute("DELETE FROM cache")
AIMS = ['deepseek-chat', 'deepseek-chat', 'deepseek-reasoner']
for off in range(-13, 1):
    for _ in range(random.randint(2, 6)):
        pt = random.randint(180, 900); ct = random.randint(120, 900)
        db.execute("INSERT INTO ai_usage VALUES(?,?,?,?,?,?,?)",
                   (f"{d(off)} {random.randint(9,21):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}",
                    random.choice(AIMS), pt, ct, pt + ct, random.randint(900, 6000),
                    1 if random.random() > 0.06 else 0))

# ── 页面停留用时流水（v3.8.120 app_usage，喂统计页「使用·时间」）──
PAGES = ['overview', 'action', 'project', 'goal', 'life', 'focus', 'stat']
for off in range(-27, 1):
    for pg in random.sample(PAGES, random.randint(3, 5)):
        db.execute("INSERT INTO app_usage VALUES(?,?,?,?)",
                   (d(off), pg, random.randint(60, 1800),
                    f"{d(off)} {random.randint(8,22):02d}:{random.randint(0,59):02d}:00"))

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
print('TODAY:', TODAY.isoformat(), '| todos+checkins:', len(T), '| focus:', len(FL))
db.close()
