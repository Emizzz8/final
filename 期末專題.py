#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 22:35:52 2025

@author: emi
"""

import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac 中文字體
plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

os.chdir('/Users/emi/Downloads/清華永續基金/excel')
df = pd.read_excel('ETF申購買回清單all.xlsx', dtype={'股票代號': str})
df["股票代號"] = (
    df["股票代號"]
    .astype(str)
    .apply(lambda x: x.zfill(4) if len(x) == 2 
                     else x.zfill(5) if len(x) == 3 
                     else x.zfill(6) if len(x) == 4
                     else x)
)

df = df.loc[:,['日期','股票代號','股票名稱','每受益權單位淨資產價值(元)','基金淨資產價值(千)','已發行受益權單位總數(千)','與前日已發行單位差異數(含加掛ETF)(千)']]
df = df.rename(columns={'基金淨資產價值(千)': '單日AUM（千）', '已發行受益權單位總數(千)':'單位數'})

#%% PART 1 台股AUM
# 台股ETF最新AUM比較


df1 = pd.read_excel('ETF基本資料表.xlsx').drop(columns = ['Cmoney ETF類型','標的區域','追蹤指數中文名稱', '基金成立日期', '是否配息', "股票名稱"])
# df_merged = pd.merge(df1, df, on = ['股票代號','股票名稱'])
df_merged = pd.merge(df1, df, on = ['股票代號'])

df_merged['日期'] = pd.to_datetime(df_merged['日期']).dt.strftime('%Y/%m/%d')
# 先確保排序正確
df_merged = df_merged.sort_values(
    ['股票代號', '日期'],
    ascending=[True, False]
).reset_index(drop=True)

# 同股票代碼內，對齊前一個日期
df_merged['前一交易日'] = (df_merged.groupby('股票代號')['日期'].shift(-1))

df_merged = df_merged[
    [
        '股票代號',
        '股票名稱',
        '日期',
        'ETF類型',
        '每受益權單位淨資產價值(元)',
        '單位數',
        '單日AUM（千）',
        '與前日已發行單位差異數(含加掛ETF)(千)',
        '前一交易日'
    ]
]


#規模排序、篩選
df_merged = df_merged.sort_values(['股票代號', '日期'])
latest_aum = df_merged.groupby('股票代號')[["股票名稱", '單日AUM（千）']].last().reset_index()
latest_aum['單日AUM（千）'] = latest_aum['單日AUM（千）'].replace(['--', '- -', '-'], pd.NA)
latest_aum_sorted = latest_aum.dropna(subset=['單日AUM（千）'])

latest_aum_sorted['AUM(億)'] = latest_aum_sorted['單日AUM（千）'] / 100000 #因為原本單位是(千)
latest_aum_sorted = latest_aum_sorted.loc[
    latest_aum_sorted['AUM(億)'] > 500
].reset_index(drop=True)
latest_aum_sorted = latest_aum_sorted.sort_values('AUM(億)', ascending=False).reset_index(drop=True).iloc[:12]

latest_aum_sorted['ETF顯示名稱'] = (
    latest_aum_sorted['股票代號'].astype(str)
    + ' '
    + latest_aum_sorted['股票名稱'])

plt.figure(figsize=(12, 8))
plt.bar(latest_aum_sorted['ETF顯示名稱'], latest_aum_sorted['AUM(億)'], color='purple')
plt.xlabel('', fontsize=14)
plt.ylabel('AUM (億)', fontsize=14)
plt.title('台股 ETF 最新 AUM 比較', fontsize=18, fontweight='bold')

plt.xticks(rotation=90, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()

bars = plt.bar(
    latest_aum_sorted['ETF顯示名稱'],
    latest_aum_sorted['AUM(億)'],
    color='purple'
)

# 給上方留空間
plt.ylim(0, latest_aum_sorted['AUM(億)'].max() * 1.15)

for bar in bars:
    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height * 1.01,
        f'{height:,.1f}',
        ha='center',
        va='bottom',
        fontsize=14,
        fontweight='bold'
    )
    
plt.show()


#%% 整體台股股票型ETF和債券型ETF AUM 月資料
etf_fund = pd.read_excel("ETF月基金規模.xlsx").loc[:, ["名稱", "代號", "年月", "基金規模(百萬)"]]
selected_funds = etf_fund.loc[
    etf_fund["代號"].isin([
        "AH11",
        "AH13",
        "AH14",
        "AH22",
       
    ])
]

mapping = {
    "AH11": "ETF股票",
    "AH13": "ETF股票",
    "AH14": "ETF股票",
    "AH22": "ETF債券",
}

selected_funds["分類"] = selected_funds["代號"].map(mapping)
mapping_sum = (
    selected_funds
    .groupby(["年月", "分類"])["基金規模(百萬)"]
    .sum()
    .reset_index()
)

mapping_sum["年月"] = pd.to_datetime(mapping_sum["年月"], format="%Y/%m")
mapping_sum = mapping_sum.sort_values("年月")
mapping_sum["月AUM（億）"]= mapping_sum["基金規模(百萬)"] / 100


plt.figure(figsize=(14,7))

for name, group in mapping_sum.groupby("分類"):
    plt.plot(group["年月"], group["月AUM（億）"], label=name, linewidth=2)

plt.xlabel("日期", fontsize=14)
plt.ylabel("AUM（億）", fontsize=14)
plt.title("ETF 月基金規模走勢", fontsize=18, fontweight='bold')
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1,13,1)))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()

#%% 每日AUM整體變化

df_merged["單日AUM（千）"] = pd.to_numeric(df_merged["單日AUM（千）"], errors="coerce")
df_merged["AUM變化"] = (
    df_merged.groupby("股票代號")["單日AUM（千）"]
    .diff()
)


#%% 日AUM總和 

categories = ["市值型", "科技", "高股息", "反1", "正2", "海外股", "商品期貨", "債券型", "主動股票", "主動債券"]
filtered = df_merged[df_merged["ETF類型"].isin(categories)]
daily_sum = filtered.groupby(["日期", "ETF類型"])["單日AUM（千）"].sum().reset_index()
daily_sum["單日AUM（億）"] = daily_sum["單日AUM（千）"] / 100000
daily_pivot = daily_sum.pivot(
    index="日期",
    columns="ETF類型",
    values="單日AUM（億）"
)


daily_pivot.index = pd.to_datetime(daily_pivot.index)

plt.figure(figsize=(14,7))
for col in daily_pivot.columns:
    plt.plot(daily_pivot.index, daily_pivot[col], label=col, linewidth=2)
     
plt.title("2003-2026 台股各類型ETF 日AUM總和 變化", fontsize=18, fontweight='bold')
plt.xlabel("日期", fontsize=12)
plt.ylabel("AUM（億）", fontsize=12)
plt.legend()
plt.grid(True)
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


plt.xticks(rotation=, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()

#%% 日AUM總和 分類型呈現

fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(14,16), sharex=True)
axes = axes.flatten()

fig.suptitle("2003-2026 台股各類型ETF 日AUM總和（分圖）", fontsize=18, fontweight='bold')

for i, col in enumerate(daily_pivot.columns):
    axes[i].plot(daily_pivot.index, daily_pivot[col], linewidth=2)
    axes[i].set_title(col)
    axes[i].set_ylabel("AUM（億）", fontsize=14)
    axes[i].grid(True)

    # x、y軸格式
    axes[i].xaxis.set_major_locator(mdates.YearLocator())
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[i].tick_params(axis='x', rotation=45) 
    axes[i].tick_params(axis='y', labelsize=12)


# 移除多餘空圖
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.xticks()

plt.tight_layout()
plt.show()

#%% 單一ETF的AUM規模走勢

# 0050
target_etf = "006208" #自行輸入
df_aum = df[df["股票代號"] == target_etf].copy()
df_aum["日期"] = pd.to_datetime(df_aum["日期"])
df_aum = df_aum.sort_values("日期")

plt.figure(figsize=(12, 6))

plt.plot(
    df_aum["日期"],
    df_aum["單日AUM（千）"] / 1e5,
    color="purple",
    linewidth=2
)

ax = plt.gca()

# 從資料第一天到最後一天
ax.set_xlim(
    df_aum["日期"].min(),
    df_aum["日期"].max()
)

# 每年顯示一次
ax.xaxis.set_major_locator(mdates.YearLocator(1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

plt.title(f"{target_etf} AUM走勢", fontsize=16)
plt.xticks(rotation=45, fontsize=14, fontweight="bold")
plt.yticks(fontsize=14, fontweight="bold")
plt.xlabel("日期", fontsize=12)
plt.ylabel("AUM（億元）", fontsize=12)
plt.grid(True)

plt.tight_layout()
plt.show()

#%%每日AUM淨資金流入 （單位1-單位0）* 淨值1 (改成累加)
# 手動調整有股票分割的（從ETF申購買回清單改價格）
# 0050 2025/06/12分割的價格要手動調整！！！

df_merged["與前日已發行單位差異數(含加掛ETF)(千)"] = pd.to_numeric(df_merged["與前日已發行單位差異數(含加掛ETF)(千)"], errors="coerce")
df_merged["淨資金流入"] = df_merged["與前日已發行單位差異數(含加掛ETF)(千)"] * df_merged["每受益權單位淨資產價值(元)"]


filtered1 = df_merged[df_merged["ETF類型"].isin(categories)]
daily_sum1 = filtered1.groupby(["日期", "ETF類型"])["淨資金流入"].sum().reset_index()
daily_sum1["淨資金流入（億）"] = daily_sum1["淨資金流入"] / 1e5
daily_pivot1 = daily_sum1.pivot(
    index="日期",
    columns="ETF類型",
    values="淨資金流入（億）"
)
daily_pivot1.index = pd.to_datetime(daily_pivot1.index)
daily_cum = daily_pivot1.cumsum()


plt.figure(figsize=(14,7))
for col in daily_cum.columns:
    plt.plot(daily_cum.index, daily_cum[col], label=col, linewidth=2)
     
plt.title("2003-2026 台股各類型ETF 日淨資金流入 變化", fontsize=18)
plt.xlabel("日期", fontsize=12)
plt.ylabel("淨資金流入（億）", fontsize=12)
plt.legend()
plt.grid(True)

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()


#%%
# 手動調整有股票分割的（從ETF申購買回清單改價格）
# 00632R 2024/12/05反分割！！！

df_merged["與前日已發行單位差異數(含加掛ETF)(千)"] = pd.to_numeric(df_merged["與前日已發行單位差異數(含加掛ETF)(千)"], errors="coerce")
df_merged["淨資金流入"] = df_merged["與前日已發行單位差異數(含加掛ETF)(千)"] * df_merged["每受益權單位淨資產價值(元)"]


filtered1 = df_merged[df_merged["ETF類型"].isin(categories)]
daily_sum1 = filtered1.groupby(["日期", "ETF類型"])["淨資金流入"].sum().reset_index()
daily_sum1["淨資金流入（億）"] = daily_sum1["淨資金流入"] / 100000
daily_pivot1 = daily_sum1.pivot(
    index="日期",
    columns="ETF類型",
    values="淨資金流入（億）"
)
daily_pivot1.index = pd.to_datetime(daily_pivot1.index)
daily_pivot1 = daily_pivot1.loc["2025-01-01":] #自行輸入時間跨度
daily_cum = daily_pivot1.cumsum()


plt.figure(figsize=(14,7))
for col in daily_cum.columns:
    plt.plot(daily_cum.index, daily_cum[col], label=col, linewidth=2)
     
plt.title("2025-2026 台股各類型ETF 日淨資金流入 變化", fontsize=18)
plt.xlabel("日期", fontsize=12)
plt.ylabel("淨資金流入（億）", fontsize=12)
plt.legend()
plt.grid(True)

ax = plt.gca()
# ax.xaxis.set_major_locator(mdates.YearLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()
#%% 分類別呈現 淨資金流入
fig, axes = plt.subplots(nrows=5, ncols=2, figsize=(14,12), sharex=True)
axes = axes.flatten()

fig.suptitle("2003-2026 台股各類型ETF 日淨資金流入（分圖）", fontsize=18)

for i, col in enumerate(daily_cum.columns):
    axes[i].plot(daily_cum.index, daily_cum[col], linewidth=2)
    axes[i].set_title(col)
    axes[i].set_ylabel("淨資金流入（億）", fontsize=14)
    axes[i].grid(True)

    # x、y軸格式
    axes[i].xaxis.set_major_locator(mdates.YearLocator())
    axes[i].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[i].tick_params(axis='x', labelsize=12, rotation=45)
    axes[i].tick_params(axis='y', labelsize=12)

# 移除多餘空圖（如果有）
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.show()


#%% PART 5 主動型ETF
#主動型ETF 單日AUM
df_active = df_merged[df_merged["ETF類型"].str.startswith("主動", na=False)]
df_active["日期"] = pd.to_datetime(df_active["日期"])

latest_aum_active = df_active.groupby(
    ["日期", "ETF類型"]
)["單日AUM（千）"].sum().reset_index()
latest_aum_active['AUM(億)'] = latest_aum_active['單日AUM（千）'] / 1e5

pivot = latest_aum_active.pivot(
    index="日期",
    columns="ETF類型",
    values="AUM(億)"
).fillna(0)

pivot.index = pd.to_datetime(pivot.index) 

plt.figure(figsize=(14,7))

for col in pivot.columns:
    plt.plot(pivot.index, pivot[col], label=col, linewidth=2)

plt.title("2025-2026 主動型ETF 日AUM總和 變化 ", fontsize=18, fontweight='bold')
plt.xlabel("日期", fontsize=14)
plt.ylabel("AUM（億）", fontsize=14)
plt.legend()
plt.grid(True)


ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=range(1,13,1)))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.xticks(rotation=45, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()


#%% 主動型ETF 單日AUM area chart
df_active = df_merged[
    df_merged["ETF類型"].str.startswith("主動", na=False)
].copy()

df_active["日期"] = pd.to_datetime(df_active["日期"])

latest_aum_active = df_active.groupby(
    ["日期", "ETF類型"]
)["單日AUM（千）"].sum().reset_index()

latest_aum_active["AUM(億)"] = (
    latest_aum_active["單日AUM（千）"] / 1e5
)

pivot = latest_aum_active.pivot(
    index="日期",
    columns="ETF類型",
    values="AUM(億)"
)

pivot.index = pd.to_datetime(pivot.index)

plt.figure(figsize=(14, 7))

colors = {
    "主動股票": "#77217C",
    "主動海外股": "#ff7f0e",
    "主動債券": "#2ca02c"
}

# 取得欄位數量
num_columns = len(pivot.columns)

for i, col in enumerate(pivot.columns):
    # 設定層級：第一欄給最高值，之後遞減
    # 這樣第一欄就會永遠在最上面，不會被後面的覆蓋
    current_zorder = num_columns - i 
    
    plt.plot(
        pivot.index,
        pivot[col],
        linewidth=2,
        label=col,
        color=colors[col],
        zorder=current_zorder + 0.1 #
    )

    plt.fill_between(
        pivot.index,
        pivot[col],
        color=colors[col],
        alpha=1,    #透明度
        zorder=current_zorder
    )

plt.title(
    "2025-2026 主動型ETF 日AUM總和變化",
    fontsize=18,
    fontweight="bold"
)

plt.xlabel("日期", fontsize=14)
plt.ylabel("AUM（億）", fontsize=14)

plt.legend(fontsize=12)
plt.grid(True)

ax = plt.gca()
ax.xaxis.set_major_locator(
    mdates.MonthLocator(interval=1)
)

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%Y-%m")
)

plt.xticks(
    rotation=45,
    fontsize=14,
    fontweight="bold"
)

plt.yticks(
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()
plt.show()
#%% 主動式每日AUM淨資金流入 （單位1-單位0）* 淨值1 

active_categories = ["主動債券", "主動股票", "主動海外股"]

filtered1 = df_merged[df_merged["ETF類型"].isin(active_categories)]
daily_sum1 = filtered1.groupby(["日期", "ETF類型"])["淨資金流入"].sum().reset_index()
daily_sum1["淨資金流入（億）"] = daily_sum1["淨資金流入"] / 100000
daily_pivot1 = daily_sum1.pivot(
    index="日期",
    columns="ETF類型",
    values="淨資金流入（億）"
)
daily_pivot1.index = pd.to_datetime(daily_pivot1.index)
daily_cum = daily_pivot1.cumsum()



daily_cum.index = pd.to_datetime(daily_cum.index)

colors = {
    "主動股票": "#77217C",
    "主動海外股": "#ff7f0e",
    "主動債券": "#2ca02c"
}

plt.figure(figsize=(14,7))

     
num_columns = len(daily_cum.columns)

for i, col in enumerate(daily_cum.columns):
    # 設定層級：第一欄給最高值，之後遞減
    # 這樣第一欄就會永遠在最上面，不會被後面的覆蓋
    current_zorder = num_columns - i 
    
    plt.plot(
        daily_cum.index,
        daily_cum[col],
        linewidth=2,
        label=col,
        color=colors[col],
        zorder=current_zorder + 0.1 #
    )

    plt.fill_between(
        daily_cum.index,
        daily_cum[col],
        color=colors[col],
        alpha=1,    #透明度
        zorder=current_zorder
    )

plt.title("2025-2026 主動型ETF 日淨資金流入 變化", fontsize=18)
plt.xlabel("日期", fontsize=12)
plt.ylabel("淨資金流入（億）", fontsize=12)
plt.legend()
plt.grid(True)

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1)) #每月1號
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.xticks(rotation=45, fontsize=14, fontweight='bold')
plt.yticks(fontsize = 14, fontweight='bold')
plt.tight_layout()
plt.show()


#%% 主動型ETF 籌碼

df_active_shares = pd.read_excel("ETF持股.xlsx")

df_active_shares["日期"] = df_active_shares["日期"].dt.strftime('%Y-%m-%d')
df_active_shares = df_active_shares.sort_values(["股票代號", "標的代號", "日期"])
df_active_shares = df_active_shares.rename(columns={'數值': '持有股數', "權重(%)": "持股權重"})

group_obj = df_active_shares.groupby(["股票代號", "標的代號"])
df_active_shares["前一天持股數"] = group_obj["持有股數"].shift(1)
df_active_shares["前一天權重"] = group_obj["持股權重"].shift(1)

# 持股數量變化
df_active_shares["持股數量變化"] = df_active_shares["持有股數"] - df_active_shares["前一天持股數"]

# 比例增減
df_active_shares["加減碼變化幅度"] = df_active_shares["持股數量變化"] / df_active_shares["前一天持股數"]
df_active_shares["加減碼變化幅度"] = df_active_shares["加減碼變化幅度"].replace([float("inf"), -float("inf")], 0).fillna(0)

# 權重變動
df_active_shares["權重變化"] = df_active_shares["持股權重"] - df_active_shares["前一天權重"]

# =
def classify(row):
    if pd.isna(row["前一天持股數"]):
        return np.nan if row["持有股數"] > 0 else "持平"
    elif row["加減碼變化幅度"] > 0:
        return "加碼"
    elif row["加減碼變化幅度"] < 0:
        return "減碼"
    else:
        return "持平"
df_active_shares["動向"] = df_active_shares.apply(classify, axis=1)


df_active_shares = df_active_shares.dropna(subset=["前一天持股數"])
df_active_shares = df_active_shares[df_active_shares["商品種類"] == "股票"]
df_active_shares_result = df_active_shares.loc[:,["日期", "股票代號", "股票名稱", "標的代號", "標的名稱", "持有股數", "持股權重", "持股數量變化", "加減碼變化幅度", "動向"]]
df_active_shares_result["加減碼變化幅度"] = (
    df_active_shares_result["加減碼變化幅度"] * 100
).round(2).astype(str) + "%"

#顏色標示：加碼（紅色）、減碼（綠色）
def color_direction(val):
    if val == "加碼":
        return "background-color: pink"
    elif val == "減碼":
        return "background-color: lightgreen"
    else:
        return ""

df_active_shares_result.style.map(color_direction, subset=["動向"])
styled = df_active_shares_result.style.map(
    color_direction,
    subset=["動向"]
)

styled.to_excel("etf_active_result.xlsx", engine="openpyxl")


#%% 單日所有主動式ETF加減碼個股 張數加總

target_date = "2026-04-29" #自行輸入

df_day = df_active_shares_result[
    df_active_shares_result["日期"] == target_date
].copy()

df_day["加碼股數"] = df_day["持股數量變化"].clip(lower=0)
df_day["減碼股數"] = df_day["持股數量變化"].clip(upper=0)

stock_summary = df_day.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼張數=("加碼股數", lambda x: x.sum()/1000),
    減碼張數=("減碼股數", lambda x: x.sum()/1000),
    淨變動=("持股數量變化", lambda x: x.sum()/1000)
).reset_index()
 
      
#取加減碼前五多的個股（淨變動）
top_buy = stock_summary.sort_values("淨變動", ascending=False).head(5)
top_sell = stock_summary.sort_values("淨變動", ascending=True).head(5)


plot_df = pd.concat([top_buy, top_sell])
plt.figure(figsize=(10, 5))

colors = plot_df["淨變動"].apply(lambda x: "red" if x > 0 else "blue")

bars = plt.bar(
    plot_df["標的名稱"],
    plot_df["淨變動"],
    color=colors
)

plt.bar(plot_df["標的名稱"], plot_df["淨變動"], color=colors)

plt.axhline(0, color="black", linewidth=1)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.0f}",
        ha="center",
        va="bottom" if height > 0 else "top"
    )
    
plt.xticks(rotation=45, fontsize=12)
plt.title(f"{target_date} 投信張數淨加減碼 Top 5", fontsize=14, fontweight='bold')
plt.ylabel("張數變動", fontsize=14)

plt.show()


#%% Same
target_date = "2026-05-08"

df_day = df_active_shares_result[
    df_active_shares_result["日期"] == target_date
].copy()

df_day["加碼股數"] = df_day["持股數量變化"].clip(lower=0)
df_day["減碼股數"] = df_day["持股數量變化"].clip(upper=0)

stock_summary = df_day.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼張數=("加碼股數", lambda x: x.sum()/1000),
    減碼張數=("減碼股數", lambda x: x.sum()/1000),
    淨變動=("持股數量變化", lambda x: x.sum()/1000)
).reset_index()
 
      
#取加減碼前五多的個股（淨變動）
top_buy = stock_summary.sort_values("淨變動", ascending=False).head(5)
top_sell = stock_summary.sort_values("淨變動", ascending=True).head(5)


plot_df = pd.concat([top_buy, top_sell])
plt.figure(figsize=(10, 5))

colors = plot_df["淨變動"].apply(lambda x: "red" if x > 0 else "blue")

bars = plt.bar(
    plot_df["標的名稱"],
    plot_df["淨變動"],
    color=colors
)

plt.bar(plot_df["標的名稱"], plot_df["淨變動"], color=colors)

plt.axhline(0, color="black", linewidth=1)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.0f}",
        ha="center",
        va="bottom" if height > 0 else "top"
    )
    
plt.xticks(rotation=45, fontsize=12)
plt.title(f"{target_date} 投信張數淨加減碼 Top 5", fontsize=14, fontweight='bold')
plt.ylabel("張數變動", fontsize=14)

plt.show()


#%% 單日所有主動式ETF加減碼個股 市值
df_price = pd.read_excel("2026日收盤表.xlsx")
df_price = df_price.loc[:, ["日期", "股票代號", "股票名稱", "收盤價"]]
df_price = df_price.rename(columns={"股票代號":"標的代號"})

df_day["日期"] = pd.to_datetime(
    df_day["日期"],
    errors="coerce"
)

df_price["日期"] = pd.to_datetime(
    df_price["日期"],
    errors="coerce"
).dt.normalize()
df_price["標的代號"] = df_price["標的代號"].astype(str).str.strip()

df_active_shares_result["日期"] = pd.to_datetime(
    df_active_shares_result["日期"],
    errors="coerce"
).dt.normalize()

df_active_shares_result["標的代號"] = (
    df_active_shares_result["標的代號"]
    .astype(str)
    .str.strip()
)

target_date = "2026-04-28" #自行輸入

df_day = df_active_shares_result[
    df_active_shares_result["日期"] == target_date
].copy()

df_day["加碼股數"] = df_day["持股數量變化"].clip(lower=0)
df_day["減碼股數"] = df_day["持股數量變化"].clip(upper=0)


df_day_active_price = pd.merge(
    df_day,
    df_price, 
    on=["日期", "標的代號"], 
    how="left"
)

df_day_active_price["加碼金額"] = df_day_active_price["加碼股數"] * df_day_active_price["收盤價"]
df_day_active_price["減碼金額"] = df_day_active_price["減碼股數"] * df_day_active_price["收盤價"]
df_day_active_price["持有金額變化"] = df_day_active_price["加碼金額"] + df_day_active_price["減碼金額"]

pd.options.display.float_format = '{:.2f}'.format
stock_summary1 = df_day_active_price.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼金額=("加碼金額", "sum"),
    減碼金額=("減碼金額", "sum"),
    淨變動_億=("持有金額變化", lambda x: x.sum()/1e8)
).reset_index()
 
      
#取加減碼前五多的個股（淨變動）
top_buy1 = stock_summary1.sort_values("淨變動_億", ascending=False).head(5)
top_sell1 = stock_summary1.sort_values("淨變動_億", ascending=True).head(5)


plot_df = pd.concat([top_buy1, top_sell1])
plt.figure(figsize=(10, 5))

colors = plot_df["淨變動_億"].apply(lambda x: "red" if x > 0 else "blue")

bars = plt.bar(
    plot_df["標的名稱"],
    plot_df["淨變動_億"],
    color=colors
)

plt.bar(plot_df["標的名稱"], plot_df["淨變動_億"], color=colors)

plt.axhline(0, color="black", linewidth=1)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.2f}",
        ha="center",
        va="bottom" if height > 0 else "top"
    )
    
plt.xticks(rotation=45, fontsize=12)
plt.title(f"{target_date} 投信市值淨加減碼 Top 5", fontsize=14, fontweight='bold')
plt.ylabel("金額變動（億）", fontsize=14)

plt.show()

#%% Same
target_date = "2026-05-07" #自行輸入

df_day["日期"] = pd.to_datetime(
    df_day["日期"],
    errors="coerce"
)

df_price["日期"] = pd.to_datetime(
    df_price["日期"],
    errors="coerce"
).dt.normalize()
df_price["標的代號"] = df_price["標的代號"].astype(str).str.strip()

df_active_shares_result["日期"] = pd.to_datetime(
    df_active_shares_result["日期"],
    errors="coerce"
).dt.normalize()

df_active_shares_result["標的代號"] = (
    df_active_shares_result["標的代號"]
    .astype(str)
    .str.strip()
)

df_day = df_active_shares_result[
    df_active_shares_result["日期"] == target_date
].copy()

df_day["加碼股數"] = df_day["持股數量變化"].clip(lower=0)
df_day["減碼股數"] = df_day["持股數量變化"].clip(upper=0)

df_day_active_price = pd.merge(
    df_day,
    df_price, 
    on=["日期", "標的代號"], 
    how="left"
)

df_day_active_price["加碼金額"] = df_day_active_price["加碼股數"] * df_day_active_price["收盤價"]
df_day_active_price["減碼金額"] = df_day_active_price["減碼股數"] * df_day_active_price["收盤價"]
df_day_active_price["持有金額變化"] = df_day_active_price["加碼金額"] + df_day_active_price["減碼金額"]

pd.options.display.float_format = '{:.2f}'.format
stock_summary1 = df_day_active_price.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼金額=("加碼金額", "sum"),
    減碼金額=("減碼金額", "sum"),
    淨變動_億=("持有金額變化", lambda x: x.sum()/1e8)
).reset_index()
 
      
#取加減碼前五多的個股（淨變動）
top_buy1 = stock_summary1.sort_values("淨變動_億", ascending=False).head(5)
top_sell1 = stock_summary1.sort_values("淨變動_億", ascending=True).head(5)


plot_df = pd.concat([top_buy1, top_sell1])
plt.figure(figsize=(10, 5))

colors = plot_df["淨變動_億"].apply(lambda x: "red" if x > 0 else "blue")

bars = plt.bar(
    plot_df["標的名稱"],
    plot_df["淨變動_億"],
    color=colors
)

plt.bar(plot_df["標的名稱"], plot_df["淨變動_億"], color=colors)

plt.axhline(0, color="black", linewidth=1)

for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height,
        f"{height:.2f}",
        ha="center",
        va="bottom" if height > 0 else "top"
    )
    
plt.xticks(rotation=45, fontsize=12)
plt.title(f"{target_date} 投信市值淨加減碼 Top 5", fontsize=14, fontweight='bold')
plt.ylabel("金額變動（億）", fontsize=14)

plt.show()

#%% 聚焦某一檔ETF和日期 00981A

#00981A
target_date = "2026-04-15" #自行輸入
target_etf = "00981A" #自行輸入

df_981A = df_active_shares_result[
    (df_active_shares_result["股票代號"] == target_etf) &
    (df_active_shares_result["日期"] == target_date)
]

order = ["加碼", "持平", "減碼"]
color_map = {
    "加碼": "lightpink",
    "持平": "lightgrey",
    "減碼": "lightgreen"
}

counts = df_981A["動向"].value_counts().reindex(order, fill_value=0)
colors = [color_map[i] for i in counts.index]

ax = counts.plot(
    kind="bar",
    color=colors,
    figsize=(8, 5),
    rot=0,
    title=f"{target_etf} {target_date} 持股動向分布"
)

ax.set_xlabel("動向", fontsize=12)
ax.set_ylabel("個股標的數", fontsize=12)

for p in ax.patches:
    height = p.get_height()
    ax.annotate(
        f"{int(height)}",
        (p.get_x() + p.get_width()/2, height),
        ha='center',
        va='bottom'
    )

plt.show()

#%%
#00981A
#pie chart

counts = df_981A["動向"].value_counts().reindex(order, fill_value=0)
current_colors = [color_map[label] for label in counts.index]

ax = counts.plot(
    kind="pie", 
    figsize=(8, 8),
    autopct='%1.1f%%',
    startangle=90,
    counterclock=False,   #順時針
    colors=current_colors,
    labels=counts.index,
    textprops={'fontsize': 16}
)

ax.set_title(f"{target_etf} {target_date} 持股動向比例", fontsize=18, fontweight='bold', pad=20)
ax.set_ylabel("")

plt.axis('equal')
plt.show()

#顏色標示：加碼（紅色）、減碼（綠色）
def color_direction(val):
    if val == "加碼":
        return "background-color: pink"
    elif val == "減碼":
        return "background-color: lightgreen"
    else:
        return ""

df_981A.style.map(color_direction, subset=["動向"])
styled = df_981A.style.map(
    color_direction,
    subset=["動向"]
)

styled.to_excel("00981A.xlsx", engine="openpyxl")

#%% 聚焦某一檔ETF和日期 00985A

# 00985A
target_date = "2026-04-16" #自行輸入
target_etf = "00985A" #自行輸入

df_985A = df_active_shares_result[
    (df_active_shares_result["股票代號"] == target_etf) &
    (df_active_shares_result["日期"] == target_date)
]

order = ["加碼", "持平", "減碼"]
color_map = {
    "加碼": "lightpink",
    "持平": "lightgrey",
    "減碼": "lightgreen"
}

counts = df_985A["動向"].value_counts().reindex(order, fill_value=0)
colors = [color_map[i] for i in counts.index]

ax = counts.plot(
    kind="bar",
    color=colors,
    figsize=(8, 5),
    rot=0,
    title=f"{target_etf} {target_date} 持股動向分布"
)

ax.set_xlabel("動向", fontsize=12)
ax.set_ylabel("個股標的數", fontsize=12)

for p in ax.patches:
    height = p.get_height()
    ax.annotate(
        f"{int(height)}",
        (p.get_x() + p.get_width()/2, height),
        ha='center',
        va='bottom'
    )

plt.show()

df_985A.style.map(color_direction, subset=["動向"])
styled = df_985A.style.map(
    color_direction,
    subset=["動向"]
)

styled.to_excel("{target_etf}.xlsx", engine="openpyxl")

#%%
#00985A
#pie chart

counts = df_985A["動向"].value_counts().reindex(order, fill_value=0)
current_colors = [color_map[label] for label in counts.index]

ax = counts.plot(
    kind="pie", 
    figsize=(8, 8),
    autopct='%1.1f%%',
    startangle=90,
    counterclock=False,   #順時針
    colors=current_colors,
    labels=counts.index,
    textprops={'fontsize': 16}
)

ax.set_title(f"{target_etf} {target_date} 持股動向比例", fontsize=18, fontweight='bold', pad=20)
ax.set_ylabel("")

plt.axis('equal')
plt.show()


#%% 觀察主動式ETF「加碼」 vs 個股股價

target_stock = "3665" #自行輸入

df_price["標的代號"] = df_price["標的代號"].astype(str)
df_stock = df_price[
    df_price["標的代號"] == target_stock
].copy()

df_stock["日期"] = pd.to_datetime(df_stock["日期"])
df_stock = df_stock.sort_values("日期")
stock_name = df_stock["股票名稱"].iloc[0]

plt.figure(figsize=(12, 6))

# 用索引畫圖（交易日等距）
plt.plot(
    range(len(df_stock)),
    df_stock["收盤價"],
    color="red",
    linewidth=2
)

# 每2筆顯示一次日期
tick_positions = range(0, len(df_stock), 2)
tick_labels = df_stock["日期"].dt.strftime("%Y-%m-%d")[::2]

plt.xticks(tick_positions, tick_labels, rotation=45, fontsize=12)
plt.yticks(fontsize=12)

plt.title(f"{target_stock} {stock_name} 股價走勢圖", fontsize=18, fontweight='bold')
plt.xlabel("交易日", fontsize=12, fontweight='bold')
plt.ylabel("收盤價", fontsize=12, fontweight='bold')
plt.grid(True)

plt.tight_layout()
plt.show()

#%% 觀察主動式ETF「減碼」 vs 個股股價
target_stock = "2408" #自行輸入

df_price["標的代號"] = df_price["標的代號"].astype(str)
df_stock = df_price[
    df_price["標的代號"] == target_stock
].copy()

df_stock["日期"] = pd.to_datetime(df_stock["日期"])
df_stock = df_stock.sort_values("日期")
stock_name = df_stock["股票名稱"].iloc[0]

plt.figure(figsize=(12, 6))

# 用索引畫圖（交易日等距）
plt.plot(
    range(len(df_stock)),
    df_stock["收盤價"],
    color="blue",
    linewidth=2
)

# 每2筆顯示一次日期
tick_positions = range(0, len(df_stock), 2)
tick_labels = df_stock["日期"].dt.strftime("%Y-%m-%d")[::2]

plt.xticks(tick_positions, tick_labels, rotation=45, fontsize=12)
plt.yticks(fontsize=12)

plt.title(f"{target_stock} {stock_name} 股價走勢圖", fontsize=18, fontweight='bold')
plt.xlabel("交易日", fontsize=12, fontweight='bold')
plt.ylabel("收盤價", fontsize=12, fontweight='bold')
plt.grid(True)

plt.tight_layout()
plt.show()

#%% 0056 換股籌碼「新增」
# 2026/06/18 生效
# 2026/06/21-2026/06/25 過渡生效日期

target_dates = [
    "20210617", "20210618", "20210621", "20210622",
    "20210623", "20210624", "20210625", "20210628"
]

add_stock = ["2409", "3481", "2603", "2108", "2441"]

df_0056 = pd.read_excel("0056換股籌碼.xlsx")
df_0056["股票代號"] = df_0056["股票代號"].astype(str).str.strip()

all_data = []

for date in target_dates:
    temp = df_0056[[
        "股票代號",
        "股票名稱",
        f"{date}收盤價",
        f"{date}成交量",
        f"{date}投信買賣超",
        f"{date}外資買賣超",
        "20210517-20210617日平均:成交量"
    ]].copy()

    temp.columns = [
        "股票代號",
        "股票名稱",
        "收盤價",
        "成交量",
        "投信買賣超",
        "外資買賣超",
        "過去一個月的日平均成交量"
    ]

    temp = temp[temp["股票代號"].isin(add_stock)]
    temp.insert(0, "日期", pd.to_datetime(date))

    all_data.append(temp)

add_result = pd.concat(all_data, ignore_index=True)
add_result = add_result.sort_values(["日期", "股票代號"])
add_result["日期"] = pd.to_datetime(
    add_result["日期"],
    errors="coerce"
)
add_result["日期"] = add_result["日期"].dt.strftime('%Y-%m-%d')


target_stock = "2441" #自行輸入
df_add = add_result[add_result["股票代號"] == target_stock]

#%% 0056 換股籌碼「刪除」
# 2026/06/18 生效
# 2026/06/21-2026/06/25 過渡生效日期


target_dates = [
    "20210617", "20210618", "20210621", "20210622",
    "20210623", "20210624", "20210625", "20210628"
]

delete_stock = ["2347", "3005"]

df_0056 = pd.read_excel("0056換股籌碼.xlsx")
df_0056["股票代號"] = df_0056["股票代號"].astype(str).str.strip()

all_data = []

for date in target_dates:
    temp = df_0056[[
        "股票代號",
        "股票名稱",
        f"{date}收盤價",
        f"{date}成交量",
        f"{date}投信買賣超",
        f"{date}外資買賣超",
        "20210517-20210617日平均:成交量"
    ]].copy()

    temp.columns = [
        "股票代號",
        "股票名稱",
        "收盤價",
        "成交量",
        "投信買賣超",
        "外資買賣超",
        "過去一個月的日平均成交量"
    ]

    temp = temp[temp["股票代號"].isin(delete_stock)]
    temp.insert(0, "日期", pd.to_datetime(date))

    all_data.append(temp)

delete_result = pd.concat(all_data, ignore_index=True)
delete_result = delete_result.sort_values(["日期", "股票代號"])
delete_result["日期"] = pd.to_datetime(
    delete_result["日期"],
    errors="coerce"
)
delete_result["日期"] = delete_result["日期"].dt.strftime('%Y-%m-%d')

target_stock = "3005"
df_delete= delete_result[delete_result["股票代號"] == target_stock]

#%% 回測觀察 進入市值加碼TOP 5

# 2454聯發科
target_stock = "2327"

marketprice = pd.read_excel("2026日收盤表.xlsx")
marketprice = marketprice.loc[:, ["日期", "股票代號", "收盤價"]]
marketprice = marketprice.rename(columns={"股票代號":"標的代號"})
marketprice["日期"] = pd.to_datetime(marketprice["日期"], errors="coerce").dt.normalize()
marketprice["標的代號"] = marketprice["標的代號"].astype(str).str.strip()
marketprice["日期"] = marketprice["日期"].dt.strftime('%Y-%m-%d')


df_active_shares_result["日期"] = pd.to_datetime(df_active_shares_result["日期"], errors="coerce").dt.normalize()
df_active_shares_result["日期"] = df_active_shares_result["日期"].dt.strftime('%Y-%m-%d')
df_active_shares_result["標的代號"] = df_active_shares_result["標的代號"].astype(str).str.strip()


# 加減碼
df_active_shares_result["加碼股數"] = df_active_shares_result["持股數量變化"].clip(lower=0)
df_active_shares_result["減碼股數"] = df_active_shares_result["持股數量變化"].clip(upper=0)

print(df_active_shares_result[["日期", "標的代號"]].head(10))
print(marketprice[["日期", "標的代號"]].head(10))


df_stock_price = pd.merge(
    df_active_shares_result,
    marketprice,
    on=["日期", "標的代號"],
    how="left"
)

df_stock_price["加碼金額"] = df_stock_price["加碼股數"] * df_stock_price["收盤價"]
df_stock_price["減碼金額"] = df_stock_price["減碼股數"] * df_stock_price["收盤價"]
df_stock_price["持有金額變化"] = df_stock_price["加碼金額"] + df_stock_price["減碼金額"]

pd.options.display.float_format = '{:.2f}'.format
stock_summary2 = df_stock_price.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼金額=("加碼金額", "sum"),
    減碼金額=("減碼金額", "sum"),
    淨變動_億=("持有金額變化", lambda x: x.sum() / 1e8),
    收盤價=("收盤價", "first")
).reset_index()
      
# 每日市值加碼Top 5（淨變動）
top5_buy_daily = (
    stock_summary2
    .sort_values(["日期", "淨變動_億"], ascending=[True, False])
    .groupby("日期")
    .head(5)
    .copy()
)

test = top5_buy_daily[
    top5_buy_daily["標的代號"].astype(str).str.strip() == target_stock
].copy()
test = test[test["淨變動_億"] != 0].copy()

stock_name = test["標的名稱"].iloc[0]

plt.figure(figsize=(6, 5))

plt.bar(
    test["日期"],
    test["淨變動_億"],
    color="purple"
)

plt.axhline(0, color="black", linewidth=1)

for x, y in zip(test["日期"], test["淨變動_億"]):
    plt.text(
        x,
        y,
        f"{y:.2f}",
        ha="center",
        va="bottom" if y > 0 else "top"
    )

plt.xticks(rotation=45, fontsize=10)
plt.title(f"{target_stock} {stock_name} 市值加碼進入TOP天數", fontsize=14, fontweight="bold")
plt.ylabel("金額變動（億）", fontsize=12)
plt.xlabel("日期", fontsize=12)

plt.tight_layout()
plt.show()

#%% #%% 回測觀察 市值加碼>3億

target_stock = "3665"

marketprice = pd.read_excel("2026日收盤表.xlsx")
marketprice = marketprice.loc[:, ["日期", "股票代號", "收盤價"]]
marketprice = marketprice.rename(columns={"股票代號":"標的代號"})
marketprice["日期"] = pd.to_datetime(marketprice["日期"], errors="coerce").dt.normalize()
marketprice["標的代號"] = marketprice["標的代號"].astype(str).str.strip()
marketprice["日期"] = marketprice["日期"].dt.strftime('%Y-%m-%d')


df_active_shares_result["日期"] = pd.to_datetime(df_active_shares_result["日期"], errors="coerce").dt.normalize()
df_active_shares_result["日期"] = df_active_shares_result["日期"].dt.strftime('%Y-%m-%d')
df_active_shares_result["標的代號"] = df_active_shares_result["標的代號"].astype(str).str.strip()


# 加減碼
df_active_shares_result["加碼股數"] = df_active_shares_result["持股數量變化"].clip(lower=0)
df_active_shares_result["減碼股數"] = df_active_shares_result["持股數量變化"].clip(upper=0)

print(df_active_shares_result[["日期", "標的代號"]].head(10))
print(marketprice[["日期", "標的代號"]].head(10))


df_stock_price = pd.merge(
    df_active_shares_result,
    marketprice,
    on=["日期", "標的代號"],
    how="left"
)

df_stock_price["加碼金額"] = df_stock_price["加碼股數"] * df_stock_price["收盤價"]
df_stock_price["減碼金額"] = df_stock_price["減碼股數"] * df_stock_price["收盤價"]
df_stock_price["持有金額變化"] = df_stock_price["加碼金額"] + df_stock_price["減碼金額"]

pd.options.display.float_format = '{:.2f}'.format
stock_summary2 = df_stock_price.groupby(
    ["日期", "標的代號"]
).agg(
    標的名稱=("標的名稱", "first"),
    加碼金額=("加碼金額", "sum"),
    減碼金額=("減碼金額", "sum"),
    淨變動_億=("持有金額變化", lambda x: x.sum() / 1e8),
    收盤價=("收盤價", "first")
).reset_index()
stock_summary2 = stock_summary2[stock_summary2["淨變動_億"] != 0].copy()

      
# 每日市值加碼Top 5（淨變動）
buy3_daily = stock_summary2[
    stock_summary2["淨變動_億"] > 3
].copy()

test = buy3_daily[
    buy3_daily["標的代號"].astype(str).str.strip() == target_stock
].copy()
test = test[test["淨變動_億"] != 0].copy()

stock_name = test["標的名稱"].iloc[0]

plt.figure(figsize=(6, 5))

plt.bar(
    test["日期"],
    test["淨變動_億"],
    color="purple"
)

plt.axhline(0, color="black", linewidth=1)

for x, y in zip(test["日期"], test["淨變動_億"]):
    plt.text(
        x,
        y,
        f"{y:.2f}",
        ha="center",
        va="bottom" if y > 0 else "top"
    )

plt.xticks(rotation=45, fontsize=10)
plt.title(f"{target_stock} {stock_name} 市值加碼 > 3億天數", fontsize=14, fontweight="bold")
plt.ylabel("金額變動（億）", fontsize=12)
plt.xlabel("日期", fontsize=12)

plt.tight_layout()
plt.show()