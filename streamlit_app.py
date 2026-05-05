# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import math
from datetime import datetime

# ══════════════════════════════════════════════════════════════
#  頁面設定
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PChome 商品價格分析",
    page_icon="🖥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
#  Session State
# ══════════════════════════════════════════════════════════════
for key, default in {
    "selected_items": set(),
    "df_result": pd.DataFrame(),
    "last_keyword": "",
    "search_mode": "keyword",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
html,body,[class*="css"]{font-family:'Noto Sans TC',sans-serif;}
.stApp{background:linear-gradient(135deg,#0a0a1a,#1a1040,#0d1b2a);min-height:100vh;}
.main-header{background:linear-gradient(90deg,#6C5CE7,#00CEC9);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;font-size:2.6rem;font-weight:700;text-align:center;
  padding:.5rem 0;letter-spacing:2px;}
.sub-header{text-align:center;color:rgba(255,255,255,.5);font-size:.95rem;
  margin-top:-.5rem;margin-bottom:1.5rem;letter-spacing:1px;}
hr{border:none;height:1px;background:linear-gradient(90deg,transparent,#6C5CE7,transparent);margin:1.5rem 0;}
[data-testid="metric-container"]{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
  border-radius:16px;padding:1.2rem 1rem;backdrop-filter:blur(10px);
  transition:transform .2s ease,box-shadow .2s ease;box-shadow:0 4px 20px rgba(0,0,0,.3);}
[data-testid="metric-container"]:hover{transform:translateY(-4px);
  box-shadow:0 8px 30px rgba(108,92,231,.25);border-color:rgba(108,92,231,.4);}
[data-testid="metric-container"] label{color:rgba(255,255,255,.6)!important;font-size:.82rem!important;font-weight:500!important;}
[data-testid="metric-container"] [data-testid="stMetricValue"]{color:#00CEC9!important;font-size:1.8rem!important;font-weight:700!important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0e2e 0%,#0d1b2a 100%)!important;
  border-right:1px solid rgba(255,255,255,.07);}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#6C5CE7,#00CEC9)!important;
  color:white!important;border:none!important;border-radius:12px!important;
  padding:.65rem 2.5rem!important;font-size:1rem!important;font-weight:600!important;
  letter-spacing:1px!important;transition:all .3s ease!important;
  box-shadow:0 4px 15px rgba(108,92,231,.4)!important;width:100%;}
.stButton>button[kind="primary"]:hover{transform:translateY(-2px)!important;
  box-shadow:0 8px 25px rgba(108,92,231,.6)!important;}
.stButton>button[kind="secondary"]{background:rgba(255,255,255,.06)!important;
  color:rgba(255,255,255,.8)!important;border:1px solid rgba(255,255,255,.2)!important;
  border-radius:10px!important;transition:all .2s ease!important;width:100%;}
.stButton>button[kind="secondary"]:hover{background:rgba(255,255,255,.12)!important;
  border-color:rgba(0,206,201,.5)!important;}
.stDownloadButton>button{background:rgba(255,255,255,.07)!important;color:#00CEC9!important;
  border:1px solid rgba(0,206,201,.4)!important;border-radius:10px!important;
  font-weight:500!important;transition:all .2s ease!important;}
.stDownloadButton>button:hover{background:rgba(0,206,201,.15)!important;border-color:#00CEC9!important;}
.chart-container{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
  border-radius:16px;padding:1rem 1.2rem;margin:.5rem 0;}
.selected-card{background:linear-gradient(135deg,rgba(108,92,231,.12),rgba(0,206,201,.12));
  border:1px solid rgba(0,206,201,.35);border-radius:14px;padding:.9rem 1.1rem;
  margin:.4rem 0;transition:all .2s ease;}
.selected-card:hover{border-color:#00CEC9;box-shadow:0 4px 16px rgba(0,206,201,.2);}
.selected-card .card-name{color:rgba(255,255,255,.88);font-size:.85rem;line-height:1.4;margin-bottom:.3rem;}
.selected-card .card-price{color:#00CEC9;font-size:1.15rem;font-weight:700;}
.selected-card .card-meta{color:rgba(255,255,255,.4);font-size:.75rem;margin-top:.2rem;}
.special-badge{display:inline-block;background:linear-gradient(135deg,#e17055,#d63031);
  border-radius:6px;padding:2px 10px;font-size:.72rem;color:white;font-weight:700;
  margin-left:6px;vertical-align:middle;letter-spacing:.5px;}
.discount-badge{display:inline-block;background:linear-gradient(135deg,#00b894,#00CEC9);
  border-radius:6px;padding:2px 10px;font-size:.72rem;color:white;font-weight:700;
  margin-left:4px;vertical-align:middle;}
.stat-badge{display:inline-block;background:linear-gradient(135deg,rgba(108,92,231,.2),rgba(0,206,201,.2));
  border:1px solid rgba(0,206,201,.3);border-radius:20px;padding:2px 12px;
  font-size:.78rem;color:#00CEC9;margin:2px;}
.special-header{background:linear-gradient(90deg,rgba(214,48,49,.2),rgba(225,112,85,.2));
  border:1px solid rgba(214,48,49,.4);border-radius:14px;padding:1rem 1.5rem;margin-bottom:1rem;}
.empty-state{text-align:center;padding:4rem 2rem;color:rgba(255,255,255,.3);}
.empty-state .icon{font-size:4rem;margin-bottom:1rem;}
.empty-state p{font-size:1.1rem;}
.keyword-confirm{background:rgba(0,206,201,.1);border:1px solid rgba(0,206,201,.3);
  border-radius:8px;padding:6px 12px;margin-top:4px;font-size:.82rem;color:rgba(255,255,255,.5);}
.keyword-confirm b{color:#00CEC9;}
.stTabs [data-baseweb="tab-list"]{background:rgba(255,255,255,.04);border-radius:12px;padding:4px;gap:4px;}
.stTabs [data-baseweb="tab"]{border-radius:8px;color:rgba(255,255,255,.6)!important;font-weight:500;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#6C5CE7,#00CEC9)!important;color:white!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  常數
# ══════════════════════════════════════════════════════════════
PLOTLY_TEMPLATE = "plotly_dark"
COLOR_PRIMARY   = "#6C5CE7"
COLOR_SECONDARY = "#00CEC9"
COLOR_ACCENT    = "#FD79A8"
COLOR_WARNING   = "#FDCB6E"
COLOR_PALETTE   = ["#6C5CE7","#00CEC9","#FD79A8","#FDCB6E","#55EFC4",
                   "#74B9FF","#A29BFE","#FF7675","#FAB1A0","#81ECEC"]

PRICE_BINS   = [0, 500, 1000, 2000, 5000, float("inf")]
PRICE_LABELS = ["超值區 <500","經濟區 500-999","中價區 1000-1999",
                "高價區 2000-4999","頂級區 5000+"]

SPECIAL_CATEGORIES = {
    "DSAA31":"🎧 耳機音響特賣","DSAB2C":"💻 筆電特賣","DSAB1T":"🖥 桌機/螢幕特賣",
    "DSABC8":"📱 手機特賣","DSAB5T":"⌨️ 鍵鼠週邊特賣","DSAB6T":"🖨 印表機特賣",
    "DSAA5T":"📷 相機特賣","DSAB9T":"🎮 電競周邊特賣","DSABD8":"📦 行動電源特賣",
    "DSABFT":"⌚ 穿戴裝置特賣","DSAB7T":"🔊 喇叭特賣","DSABGT":"🧹 智慧家電特賣",
    "DXAA0T":"🏠 家電特賣","DXAB0T":"❄️ 冷氣特賣",
}

PRESET_KEYWORDS = [
    "✏️ 自行輸入…","🎧 耳機","💻 筆電","🖱 滑鼠","⌨️ 鍵盤",
    "📱 手機","📷 相機","🖥 螢幕","🎮 遊戲手把","📦 行動電源",
    "🔊 藍牙喇叭","⌚ 智慧手錶","🧹 掃地機器人","❄️ 空氣清淨機",
    "🖨 印表機","📡 路由器","🎙 麥克風","💡 智慧燈泡",
]

# ══════════════════════════════════════════════════════════════
#  輔助函數
# ══════════════════════════════════════════════════════════════
def apply_chart_style(fig, title="", height=480):
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=title, font=dict(size=16, color="#00CEC9", family="Noto Sans TC"), x=0.02),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(color="rgba(255,255,255,0.75)", family="Noto Sans TC"),
        height=height, margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(bgcolor="rgba(255,255,255,0.05)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.1)")
    return fig

def categorize_price(price):
    for i, upper in enumerate(PRICE_BINS[1:]):
        if price < upper:
            return PRICE_LABELS[i]
    return PRICE_LABELS[-1]

def analyze_data(df):
    return {
        "總商品數":   len(df),
        "平均價格":   df["price"].mean(),
        "最高價格":   df["price"].max(),
        "最低價格":   df["price"].min(),
        "價格標準差": df["price"].std(),
        "中位數價格": df["price"].median(),
    }

# ══════════════════════════════════════════════════════════════
#  爬蟲
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=600, show_spinner=False)
def fetch_keyword(keyword: str, total_items: int) -> pd.DataFrame:
    rows, pages = [], math.ceil(total_items / 20)
    bar = st.progress(0, text="準備中…")
    for i in range(1, pages + 1):
        try:
            r = requests.get(
                f"https://ecshweb.pchome.com.tw/search/v3.3/all/results"
                f"?q={keyword}&page={i}&sort=sale/dc", timeout=10)
            for p in r.json().get("prods", []):
                if len(rows) >= total_items:
                    break
                rows.append({"name": p.get("name",""), "price": p.get("price",0),
                              "id": p.get("Id",""), "brand": p.get("brandName",""),
                              "is_special": False})
        except Exception as e:
            st.warning(f"第 {i} 頁失敗：{e}")
        bar.progress(min(i/pages, 1.0), text=f"⏳ 第 {i}/{pages} 頁 · {len(rows)} 筆")
        if i < pages:
            time.sleep(0.8)
    bar.empty()
    return pd.DataFrame(rows[:total_items])

@st.cache_data(ttl=600, show_spinner=False)
def fetch_special(code: str, total_items: int) -> pd.DataFrame:
    rows, pages = [], math.ceil(total_items / 20)
    bar = st.progress(0, text="準備中…")
    for i in range(1, pages + 1):
        try:
            r = requests.get(
                f"https://ecshweb.pchome.com.tw/search/v3.3/all/results"
                f"?cateid={code}&page={i}&sort=sale/dc", timeout=10)
            prods = r.json().get("prods", [])
            if not prods:
                r2 = requests.get(
                    f"https://ecshweb.pchome.com.tw/search/v3.3/all/results"
                    f"?q=&cateid={code}&page={i}&sort=sale/dc", timeout=10)
                prods = r2.json().get("prods", [])
            for p in prods:
                if len(rows) >= total_items:
                    break
                op = p.get("originPrice", 0) or p.get("price", 0)
                sp = p.get("price", 0)
                rows.append({"name": p.get("name",""), "price": sp,
                              "origin_price": op, "brand": p.get("brandName",""),
                              "discount_pct": round((1-sp/op)*100) if op and op > sp else 0,
                              "id": p.get("Id",""), "is_special": True})
        except Exception as e:
            st.warning(f"特設第 {i} 頁失敗：{e}")
        bar.progress(min(i/pages, 1.0), text=f"⏳ 第 {i}/{pages} 頁 · {len(rows)} 筆")
        if i < pages:
            time.sleep(0.8)
    bar.empty()
    return pd.DataFrame(rows[:total_items])

# ══════════════════════════════════════════════════════════════
#  特設分析
# ══════════════════════════════════════════════════════════════
def render_special_analysis(df, category_name):
    has_discount = "discount_pct" in df.columns and df["discount_pct"].sum() > 0
    st.markdown(f"""
    <div class="special-header">
        <span style="font-size:1.3rem;font-weight:700;color:#e17055;">🏷 特設專區分析</span>
        <span class="special-badge">特設</span>
        <span style="color:rgba(255,255,255,.5);font-size:.85rem;margin-left:.8rem;">{category_name}</span>
    </div>""", unsafe_allow_html=True)

    if not has_discount:
        st.info("ℹ️ 此特設類別未取得折扣資訊，顯示一般價格分析。")
        st.markdown("---")
        return

    df_d = df[df["discount_pct"] > 0].copy()
    saving = (df_d["origin_price"] - df_d["price"]).sum()
    sa, sb, sc, sd = st.columns(4)
    with sa: st.metric("🏷 有折扣商品", f"{len(df_d)} 件")
    with sb: st.metric("💸 平均折扣",   f"{df_d['discount_pct'].mean():.1f}%")
    with sc: st.metric("🔥 最高折扣",   f"{df_d['discount_pct'].max():.0f}%")
    with sd: st.metric("💰 總省下金額", f"${saving:,.0f}")

    st.markdown("---")
    t1, t2, t3 = st.tabs(["🔥 折扣排行榜","📊 原價 vs 特價","💸 折扣分布"])

    with t1:
        top = df_d.nlargest(15, "discount_pct").copy()
        top["短名"] = top["name"].str[:30] + "…"
        top["省"] = top["origin_price"] - top["price"]
        fig = go.Figure(go.Bar(
            y=top["短名"], x=top["discount_pct"], orientation="h",
            marker=dict(color=top["discount_pct"],
                        colorscale=[[0,"#fdcb6e"],[.5,"#e17055"],[1,"#d63031"]],
                        showscale=True, colorbar=dict(title="折扣%")),
            text=[f"{d:.0f}% OFF  省${s:,.0f}" for d,s in zip(top["discount_pct"],top["省"])],
            textposition="outside", textfont=dict(color="white",size=11),
            hovertemplate="<b>%{y}</b><br>折扣：%{x:.1f}%<extra></extra>",
        ))
        apply_chart_style(fig, "🔥 折扣排行榜 Top 15", height=max(400, len(top)*50+80))
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        fig2 = go.Figure(go.Scatter(
            x=df_d["origin_price"], y=df_d["price"], mode="markers",
            marker=dict(color=df_d["discount_pct"],
                        colorscale=[[0,"#00CEC9"],[.5,"#e17055"],[1,"#d63031"]],
                        size=10, showscale=True, colorbar=dict(title="折扣%"),
                        line=dict(color="rgba(255,255,255,.3)",width=.5)),
            hovertemplate="<b>%{customdata}</b><br>原價：$%{x:,}<br>特價：$%{y:,}<extra></extra>",
            customdata=df_d["name"].str[:25],
        ))
        mv = max(df_d["origin_price"].max(), df_d["price"].max())
        fig2.add_trace(go.Scatter(x=[0,mv],y=[0,mv],mode="lines",name="無折扣基準",
            line=dict(color="rgba(255,255,255,.2)",dash="dash",width=1),hoverinfo="skip"))
        apply_chart_style(fig2, "📊 原價 vs 特價", height=460)
        fig2.update_xaxes(title_text="原價 (NT$)")
        fig2.update_yaxes(title_text="特價 (NT$)")
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        fig3 = px.histogram(df_d, x="discount_pct", nbins=20,
                            color_discrete_sequence=["#e17055"],
                            labels={"discount_pct":"折扣幅度 (%)"})
        fig3.update_traces(marker_line_color="rgba(255,255,255,.2)", marker_line_width=.5)
        apply_chart_style(fig3, "💸 折扣幅度分布", height=380)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### 📋 特設商品明細（依折扣排序）")
    disp = df_d[["name","price","origin_price","discount_pct","brand"]].copy()
    disp.columns = ["商品名稱","特價","原價","折扣%","品牌"]
    disp = disp.sort_values("折扣%", ascending=False)
    disp.index = range(1, len(disp)+1)
    st.dataframe(disp, use_container_width=True, height=350)
    st.download_button("📥 下載特設商品 CSV",
        disp.to_csv(index=False, encoding="utf-8-sig"),
        f"PChome_特設_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
    st.markdown("---")

# ══════════════════════════════════════════════════════════════
#  自選比較
# ══════════════════════════════════════════════════════════════
def render_compare_panel(df):
    sel_idx = st.session_state.selected_items
    if not sel_idx:
        return
    sel = df.loc[df.index.isin(sel_idx)].copy().reset_index(drop=True)
    n = len(sel)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(108,92,231,.15),rgba(0,206,201,.15));
        border:1px solid rgba(0,206,201,.35);border-radius:14px;padding:1rem 1.5rem;margin-bottom:1rem;">
        <span style="font-size:1.3rem;font-weight:700;color:#00CEC9;">🧺 自選商品比較面板</span>
        <span style="color:rgba(255,255,255,.5);font-size:.85rem;margin-left:1rem;">已選 {n} 件</span>
    </div>""", unsafe_allow_html=True)

    ca,cb,cc,cd = st.columns(4)
    with ca: st.metric("已選件數", f"{n} 件")
    with cb: st.metric("最低價", f"${sel['price'].min():,}")
    with cc: st.metric("最高價", f"${sel['price'].max():,}")
    with cd: st.metric("平均價", f"${sel['price'].mean():,.0f}")

    st.markdown("#### 📌 已選商品清單")
    for row_slice in [sel.iloc[i:i+3] for i in range(0, len(sel), 3)]:
        cols = st.columns(3)
        for col, (_, item) in zip(cols, row_slice.iterrows()):
            with col:
                nm = item["name"][:40]+"…" if len(item["name"])>40 else item["name"]
                diff = item["price"] - sel["price"].mean()
                diff_str = (
                    f'<span style="color:#55EFC4;">▼ ${abs(diff):,.0f} 低於均價</span>'
                    if diff < 0 else
                    f'<span style="color:#FD79A8;">▲ ${diff:,.0f} 高於均價</span>'
                )
                stag = '<span class="special-badge">特設</span>' if item.get("is_special") else ""
                dtag = (f'<span class="discount-badge">{item["discount_pct"]:.0f}% OFF</span>'
                        if item.get("discount_pct", 0) > 0 else "")
                st.markdown(f"""
                <div class="selected-card">
                    <div class="card-name">{nm}{stag}{dtag}</div>
                    <div class="card-price">${item['price']:,}</div>
                    <div class="card-meta">📦 {item['price_range']}</div>
                    <div style="font-size:.75rem;margin-top:.3rem;">{diff_str}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("#### 📊 自選商品圖表比較")
    t1, t2, t3 = st.tabs(["📊 橫向長條圖","🔵 散佈比較","📋 數據表"])

    with t1:
        sel["短名"] = sel["name"].str[:25] + "…"
        ss = sel.sort_values("price")
        avg_all = df["price"].mean()
        fig = go.Figure()
        if "origin_price" in sel.columns and sel["origin_price"].sum() > 0:
            fig.add_trace(go.Bar(y=ss["短名"], x=ss["origin_price"], orientation="h",
                name="原價", marker=dict(color="rgba(255,255,255,.15)"),
                hovertemplate="原價：$%{x:,}<extra></extra>"))
        fig.add_trace(go.Bar(y=ss["短名"], x=ss["price"], orientation="h", name="售價",
            marker=dict(color=ss["price"],
                        colorscale=[[0,COLOR_PRIMARY],[1,COLOR_SECONDARY]],
                        showscale=True, colorbar=dict(title="價格")),
            text=[f"${p:,}" for p in ss["price"]],
            textposition="outside", textfont=dict(color="white")))
        fig.add_vline(x=avg_all, line_dash="dash", line_color=COLOR_WARNING,
            annotation_text=f"全體均價 ${avg_all:,.0f}",
            annotation_font_color=COLOR_WARNING)
        fig.update_layout(barmode="overlay")
        apply_chart_style(fig, "自選商品價格比較", height=max(300, n*55+80))
        st.plotly_chart(fig, use_container_width=True)

    with t2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=list(range(len(df))), y=df["price"],
            mode="markers", name="全體", marker=dict(color="rgba(255,255,255,.1)",size=5),
            hoverinfo="skip"))
        fig2.add_trace(go.Scatter(x=sel.index.tolist(), y=sel["price"],
            mode="markers+text", name="自選",
            marker=dict(color=COLOR_SECONDARY, size=14, symbol="star",
                        line=dict(color=COLOR_PRIMARY,width=2)),
            text=[f"${p:,}" for p in sel["price"]], textposition="top center",
            textfont=dict(color=COLOR_SECONDARY,size=10),
            hovertemplate="<b>%{customdata}</b><br>$%{y:,}<extra></extra>",
            customdata=sel["name"].str[:20]))
        apply_chart_style(fig2, "自選商品在全體中的位置", height=420)
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        base = ["name","price","price_range"]
        extra = [c for c in ["origin_price","discount_pct","brand"] if c in sel.columns]
        disp = sel[base+extra].copy()
        disp.columns = [{"name":"商品名稱","price":"特價","price_range":"價格區間",
                          "origin_price":"原價","discount_pct":"折扣%","brand":"品牌"}.get(c,c)
                         for c in disp.columns]
        disp.index = range(1, len(disp)+1)
        st.dataframe(disp, use_container_width=True)
        st.download_button("📥 下載自選清單 CSV",
            disp.to_csv(index=False, encoding="utf-8-sig"),
            f"PChome_自選_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
#  商品自選列表
# ══════════════════════════════════════════════════════════════
def render_item_selector(df, keyword):
    st.markdown("## 🧺 商品自選")
    st.markdown('<p style="color:rgba(255,255,255,.5);font-size:.88rem;margin-top:-.5rem;">勾選感興趣的商品，即時加入比較清單 👇</p>', unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2,2,2])
    with fc1:
        filter_range = st.selectbox("篩選價格區間", ["全部區間"]+PRICE_LABELS, key="filter_range")
    with fc2:
        pmin, pmax = int(df["price"].min()), int(df["price"].max())
        filter_price = st.slider("價格範圍", pmin, pmax, (pmin, pmax), key="filter_price")
    with fc3:
        opts = ["預設順序","價格由低到高","價格由高到低"]
        if "discount_pct" in df.columns:
            opts.append("折扣由高到低")
        sort_by = st.selectbox("排序方式", opts, key="sort_by")

    mask = (df["price"] >= filter_price[0]) & (df["price"] <= filter_price[1])
    if filter_range != "全部區間":
        mask &= df["price_range"] == filter_range
    fdf = df[mask].copy()
    if sort_by == "價格由低到高":   fdf = fdf.sort_values("price")
    elif sort_by == "價格由高到低": fdf = fdf.sort_values("price", ascending=False)
    elif sort_by == "折扣由高到低" and "discount_pct" in fdf.columns:
        fdf = fdf.sort_values("discount_pct", ascending=False)

    ba, bb, bc = st.columns([1,1,4])
    with ba:
        if st.button("✅ 全選（篩選結果）", type="secondary"):
            for idx in fdf.index: st.session_state.selected_items.add(idx)
            st.rerun()
    with bb:
        if st.button("❌ 取消全選", type="secondary"):
            for idx in fdf.index: st.session_state.selected_items.discard(idx)
            st.rerun()
    with bc:
        st.markdown(f'<p style="color:rgba(255,255,255,.4);font-size:.82rem;padding-top:.6rem;">篩選結果：{len(fdf)} 件 ｜ 已選：{len(st.session_state.selected_items)} 件</p>', unsafe_allow_html=True)

    PAGE_SIZE = 20
    total_pages = max(1, (len(fdf)-1)//PAGE_SIZE+1)
    pk = f"page_{keyword}"
    if pk not in st.session_state: st.session_state[pk] = 1
    cp = st.session_state[pk]

    pa, pb, pc = st.columns([1,3,1])
    with pa:
        if st.button("◀ 上一頁", type="secondary", disabled=(cp<=1)):
            st.session_state[pk] -= 1; st.rerun()
    with pb:
        st.markdown(f'<p style="text-align:center;color:rgba(255,255,255,.5);">第 {cp} / {total_pages} 頁</p>', unsafe_allow_html=True)
    with pc:
        if st.button("下一頁 ▶", type="secondary", disabled=(cp>=total_pages)):
            st.session_state[pk] += 1; st.rerun()

    page_df = fdf.iloc[(cp-1)*PAGE_SIZE : cp*PAGE_SIZE]
    avg_price = df["price"].mean()

    for idx, row in page_df.iterrows():
        is_sel = idx in st.session_state.selected_items
        c1, c2, c3, c4 = st.columns([0.5,5,1.5,2])
        with c1:
            checked = st.checkbox("", value=is_sel, key=f"chk_{idx}", label_visibility="collapsed")
            if checked != is_sel:
                if checked: st.session_state.selected_items.add(idx)
                else:       st.session_state.selected_items.discard(idx)
                st.rerun()
        with c2:
            nm = row["name"][:55]+"…" if len(row["name"])>55 else row["name"]
            hl = "border-left:3px solid #00CEC9;background:rgba(0,206,201,.05);" if is_sel else ""
            stag = '<span class="special-badge">特設</span>' if row.get("is_special") else ""
            dtag = (f'<span class="discount-badge">{row["discount_pct"]:.0f}% OFF</span>'
                    if row.get("discount_pct",0)>0 else "")
            st.markdown(f'<div style="padding:6px 10px;border-radius:6px;{hl}"><span style="color:rgba(255,255,255,.85);font-size:.87rem;">{nm}</span>{stag}{dtag}</div>', unsafe_allow_html=True)
        with c3:
            pc_color = "#55EFC4" if row["price"] < avg_price else "#FD79A8"
            orig = (f'<div style="color:rgba(255,255,255,.3);font-size:.72rem;text-decoration:line-through;text-align:right;">${row["origin_price"]:,}</div>'
                    if row.get("origin_price",0) > row["price"] else "")
            st.markdown(f'{orig}<div style="text-align:right;padding:2px 4px;"><span style="color:{pc_color};font-weight:700;font-size:1rem;">${row["price"]:,}</span></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div style="text-align:center;padding:6px 0;"><span class="stat-badge">{row["price_range"]}</span></div>', unsafe_allow_html=True)

    st.markdown("---")

# ══════════════════════════════════════════════════════════════
#  側邊欄
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">🖥 PChome 商品價格分析儀表板</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">即時爬取 · 智慧分析 · 商品自選比較 · 特設專區</div>', unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/PChome_Online_logo.svg/320px-PChome_Online_logo.svg.png", width=160)
    st.markdown("## 🔎 搜尋模式")
    m1, m2 = st.columns(2)
    with m1:
        if st.button("🔍 關鍵字", type=("primary" if st.session_state.search_mode=="keyword" else "secondary")):
            st.session_state.search_mode = "keyword"; st.rerun()
    with m2:
        if st.button("🏷 特設", type=("primary" if st.session_state.search_mode=="special" else "secondary")):
            st.session_state.search_mode = "special"; st.rerun()
    st.markdown("---")

    if st.session_state.search_mode == "keyword":
        st.markdown("### 🔍 關鍵字搜尋")
        preset = st.selectbox("選擇商品類別", PRESET_KEYWORDS, index=1)
        if preset == "✏️ 自行輸入…":
            keyword = st.text_input("請輸入關鍵字", placeholder="例如：空氣炸鍋…", key="custom_kw").strip()
            if not keyword:
                st.markdown('<div class="keyword-confirm">⚠️ 請輸入搜尋關鍵字</div>', unsafe_allow_html=True)
        else:
            keyword = preset.split(" ",1)[-1].strip()
            st.markdown(f'<div class="keyword-confirm">🔑 搜尋關鍵字：<b>{keyword}</b></div>', unsafe_allow_html=True)
        total_items  = st.slider("抓取筆數", 20, 200, 60, step=20)
        special_code = None
    else:
        st.markdown("### 🏷 特設專區")
        sname = st.selectbox("選擇特設類別", list(SPECIAL_CATEGORIES.values()))
        special_code = [k for k,v in SPECIAL_CATEGORIES.items() if v==sname][0]
        keyword      = sname.split(" ",1)[-1].strip()
        st.markdown(f'<div class="keyword-confirm">🏷 特設代碼：<b>{special_code}</b></div>', unsafe_allow_html=True)
        total_items  = st.slider("抓取筆數", 20, 200, 60, step=20)

    st.markdown("---")
    st.markdown("## 📊 圖表選項")
    show_line    = st.checkbox("💹 價格趨勢折線圖", value=True)
    show_bar     = st.checkbox("📊 價格區間長條圖", value=True)
    show_pie     = st.checkbox("🥧 價格區間圓餅圖", value=True)
    show_sun     = st.checkbox("☀️ 旭日圖",         value=True)
    show_scatter = st.checkbox("🔵 價格散佈圖",     value=True)

    st.markdown("---")
    n_sel = len(st.session_state.selected_items)
    st.markdown(f'## 🧺 自選清單 &nbsp;<span style="background:linear-gradient(135deg,#6C5CE7,#00CEC9);color:white;border-radius:50%;padding:1px 7px;font-size:.8rem;">{n_sel}</span>', unsafe_allow_html=True)
    if n_sel == 0:
        st.markdown('<p style="color:rgba(255,255,255,.3);font-size:.82rem;">尚未選取任何商品</p>', unsafe_allow_html=True)
    else:
        df_now = st.session_state.df_result
        if not df_now.empty:
            sel_side = df_now.loc[df_now.index.isin(st.session_state.selected_items)]
            st.markdown(f'<p style="color:rgba(255,255,255,.5);font-size:.78rem;">已選 {n_sel} 件 ｜ 合計 ${sel_side["price"].sum():,}</p>', unsafe_allow_html=True)
            for _, row in sel_side.head(5).iterrows():
                nm = row["name"][:22]+"…" if len(row["name"])>22 else row["name"]
                st.markdown(f'<div style="background:rgba(0,206,201,.08);border-left:2px solid #00CEC9;border-radius:6px;padding:5px 8px;margin:3px 0;"><span style="color:rgba(255,255,255,.75);font-size:.78rem;">{nm}</span><br><span style="color:#00CEC9;font-weight:700;font-size:.88rem;">${row["price"]:,}</span></div>', unsafe_allow_html=True)
            if n_sel > 5:
                st.markdown(f'<p style="color:rgba(255,255,255,.3);font-size:.75rem;text-align:center;">…還有 {n_sel-5} 件</p>', unsafe_allow_html=True)
        if st.button("🗑 清空自選清單", type="secondary"):
            st.session_state.selected_items = set(); st.rerun()

    st.markdown("---")
    search_btn = st.button("🚀 開始搜尋", type="primary")
    st.markdown('<div style="color:rgba(255,255,255,.3);font-size:.75rem;line-height:1.8;margin-top:.5rem;">📌 資料來源：PChome 24h<br>⏱ 快取時間：10 分鐘<br>⚠️ 請勿頻繁大量抓取</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  主邏輯
# ══════════════════════════════════════════════════════════════
if search_btn:
    if not keyword:
        st.warning("⚠️ 請輸入或選擇搜尋關鍵字。")
        st.stop()

    if keyword != st.session_state.last_keyword:
        st.session_state.selected_items = set()
        st.session_state.last_keyword   = keyword

    if st.session_state.search_mode == "special" and special_code:
        with st.spinner(f"🔄 正在抓取特設「{keyword}」資料…"):
            df = fetch_special(special_code, total_items)
    else:
        with st.spinner(f"🔄 正在連線 PChome 並抓取「{keyword}」資料…"):
            df = fetch_keyword(keyword, total_items)

    if df.empty:
        st.markdown('<div class="empty-state"><div class="icon">🔍</div><p>未找到相關商品，請嘗試其他關鍵字。</p></div>', unsafe_allow_html=True)
        st.stop()

    df["price_range"] = df["price"].apply(categorize_price)
    for col, default in [("discount_pct",0),("origin_price",None),("is_special",False),("brand","")]:
        if col not in df.columns:
            df[col] = df["price"] if col=="origin_price" else default
    df["origin_price"] = df["origin_price"].fillna(df["price"])

    analysis = analyze_data(df)
    st.session_state.df_result = df

    if st.session_state.search_mode == "special":
        st.markdown(f'<div style="background:linear-gradient(90deg,rgba(214,48,49,.15),rgba(225,112,85,.15));border:1px solid rgba(214,48,49,.3);border-radius:10px;padding:.6rem 1.2rem;margin-bottom:1rem;display:inline-block;"><span style="color:#e17055;font-weight:600;">🏷 特設專區模式</span><span style="color:rgba(255,255,255,.5);font-size:.85rem;margin-left:.8rem;">{keyword} · {special_code}</span></div>', unsafe_allow_html=True)

    # ── 統計指標 ──
    st.markdown("## 📈 基本統計")
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    for col,(label,value) in zip([c1,c2,c3,c4,c5,c6],[
        ("🛍 總商品數",  f"{analysis['總商品數']:,}"),
        ("💰 平均價格",  f"${analysis['平均價格']:,.0f}"),
        ("📈 最高價格",  f"${analysis['最高價格']:,}"),
        ("📉 最低價格",  f"${analysis['最低價格']:,}"),
        ("📊 中位數",    f"${analysis['中位數價格']:,.0f}"),
        ("📐 標準差",    f"${analysis['價格標準差']:,.0f}"),
    ]):
        with col: st.metric(label, value)

    st.markdown("---")

    if st.session_state.search_mode == "special":
        render_special_analysis(df, keyword)

    render_item_selector(df, keyword)
    render_compare_panel(df)

    # ── 資料表格 ──
    st.markdown("---")
    st.markdown("## 📋 商品資料一覽")
    tt1, tt2 = st.tabs(["🗂 精簡檢視（前 30 筆）","📄 完整資料"])
    with tt1:
        sc = ["name","price","price_range"]
        cn = ["商品名稱","價格","價格區間"]
        if st.session_state.search_mode == "special":
            sc += ["origin_price","discount_pct","brand"]
            cn += ["原價","折扣%","品牌"]
        d = df[sc].head(30).copy()
        d.columns = cn
        d.index = range(1, len(d)+1)
        st.dataframe(d, use_container_width=True, height=380)
    with tt2:
        st.dataframe(df, use_container_width=True, height=380)

    st.download_button(f"📥 下載完整資料 CSV（{len(df)} 筆）",
        df.to_csv(index=False, encoding="utf-8-sig"),
        f"PChome_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")

    st.markdown("---")

    # ── 視覺化圖表 ──
    st.markdown("## 📊 全體資料視覺化")

    if show_line:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 💹 價格趨勢折線圖")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(1,len(df)+1)), y=df["price"],
            mode="lines+markers", name="商品價格", text=df["name"],
            hovertemplate="<b>%{text}</b><br>編號：%{x}<br>價格：$%{y:,}<extra></extra>",
            line=dict(color=COLOR_PRIMARY,width=2), marker=dict(size=4,color=COLOR_PRIMARY),
            fill="tozeroy", fillcolor="rgba(108,92,231,0.08)"))
        sel_l = df.loc[df.index.isin(st.session_state.selected_items)]
        if not sel_l.empty:
            fig.add_trace(go.Scatter(x=[i+1 for i in sel_l.index], y=sel_l["price"],
                mode="markers", name="⭐ 自選",
                marker=dict(color=COLOR_SECONDARY,size=12,symbol="star",
                            line=dict(color="white",width=1))))
        avg = analysis["平均價格"]
        fig.add_hline(y=avg, line_dash="dash", line_color=COLOR_ACCENT,
            annotation_text=f"平均 ${avg:,.0f}", annotation_font_color=COLOR_ACCENT,
            annotation_position="top right")
        apply_chart_style(fig, f"《{keyword}》商品價格趨勢", height=420)
        fig.update_xaxes(title_text="商品序號")
        fig.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_bar:
        rc = (df["price_range"].value_counts().reindex(PRICE_LABELS).dropna().reset_index())
        rc.columns = ["價格區間","數量"]
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 📊 價格區間商品數量")
        fig = px.bar(rc, x="價格區間", y="數量", color="數量",
            color_continuous_scale=[[0,COLOR_PRIMARY],[1,COLOR_SECONDARY]], text="數量")
        fig.update_traces(textposition="outside", textfont_color="white")
        apply_chart_style(fig, f"《{keyword}》價格區間分布", height=420)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_pie or show_sun:
        cc = st.columns(2) if (show_pie and show_sun) else [st.container()]
        if show_pie:
            with cc[0]:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown("### 🥧 價格區間圓餅圖")
                pcd = df["price_range"].value_counts()
                fig = go.Figure(go.Pie(
                    labels=pcd.index, values=pcd.values, hole=0.4,
                    marker=dict(colors=COLOR_PALETTE[:len(pcd)],
                                line=dict(color="white",width=2)),
                    textinfo="percent+label", textfont=dict(size=12),
                    hovertemplate="<b>%{label}</b><br>數量：%{value}<br>佔比：%{percent}<extra></extra>"))
                fig.update_layout(annotations=[dict(text=f"共<br>{len(df)} 件",
                    x=0.5,y=0.5,font_size=18,showarrow=False,font_color=COLOR_SECONDARY)])
                apply_chart_style(fig, f"《{keyword}》價格區間", height=440)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        if show_sun:
            with (cc[1] if (show_pie and show_sun) else cc[0]):
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown("### ☀️ 旭日圖")
                ds = df.copy()
                ds["short_name"] = ds["name"].str[:18]+"…"
                fig = px.sunburst(ds, path=["price_range","short_name"], values="price",
                    color="price_range", color_discrete_sequence=COLOR_PALETTE)
                fig.update_traces(textinfo="label+percent entry",
                    insidetextorientation="radial",
                    hovertemplate="<b>%{label}</b><br>$%{value:,}<br>%{percentEntry:.1%}<extra></extra>",
                    marker=dict(line=dict(color="white",width=1.5)))
                apply_chart_style(fig, f"《{keyword}》旭日圖", height=500)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    if show_scatter:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown("### 🔵 商品價格散佈圖")
        fig = px.scatter(df, x=df.index, y="price", color="price_range",
            hover_data=["name","price","price_range"],
            color_discrete_sequence=COLOR_PALETTE)
        sel_s = df.loc[df.index.isin(st.session_state.selected_items)]
        if not sel_s.empty:
            fig.add_trace(go.Scatter(x=sel_s.index.tolist(), y=sel_s["price"],
                mode="markers", name="⭐ 自選",
                marker=dict(color=COLOR_SECONDARY,size=14,symbol="star",
                            line=dict(color=COLOR_PRIMARY,width=2)),
                hovertemplate="<b>%{customdata}</b><br>$%{y:,}<extra></extra>",
                customdata=sel_s["name"].str[:25]))
        apply_chart_style(fig, f"《{keyword}》價格散佈圖", height=440)
        fig.update_xaxes(title_text="商品序號")
        fig.update_yaxes(title_text="價格 (NT$)")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── 深度分析 ──
    st.markdown("---")
    st.markdown("## 🔬 深度分析")
    da1, da2 = st.columns(2)
    with da1:
        st.markdown("### 📊 價格分布直方圖")
        fig = px.histogram(df, x="price", nbins=30,
            color_discrete_sequence=[COLOR_PRIMARY], labels={"price":"價格 (NT$)"})
        fig.update_traces(marker_line_color="rgba(255,255,255,.2)", marker_line_width=.5)
        fig.add_vline(x=analysis["平均價格"], line_dash="dash", line_color=COLOR_ACCENT,
            annotation_text=f"均價 ${analysis['平均價格']:,.0f}",
            annotation_font_color=COLOR_ACCENT)
        fig.add_vline(x=analysis["中位數價格"], line_dash="dot", line_color=COLOR_WARNING,
            annotation_text=f"中位數 ${analysis['中位數價格']:,.0f}",
            annotation_font_color=COLOR_WARNING)
        apply_chart_style(fig, "價格分布直方圖", height=380)
        fig.update_xaxes(title_text="價格 (NT$)")
        fig.update_yaxes(title_text="商品數量")
        st.plotly_chart(fig, use_container_width=True)

    with da2:
        st.markdown("### 📋 價格區間統計")
        rs = df.groupby("price_range")["price"].agg(
            數量="count", 平均價="mean", 最低價="min", 最高價="max"
        ).reindex(PRICE_LABELS).dropna().astype(int)
        rs.index.name = "價格區間"
        st.dataframe(rs, use_container_width=True, height=300)

        st.markdown("### 🏷 品牌分布 Top 10")
        if "brand" in df.columns and df["brand"].str.strip().ne("").any():
            bc = df[df["brand"].str.strip()!=""]["brand"].value_counts().head(10)
            fig = px.bar(x=bc.values, y=bc.index, orientation="h",
                color=bc.values,
                color_continuous_scale=[[0,COLOR_PRIMARY],[1,COLOR_SECONDARY]],
                text=bc.values, labels={"x":"商品數量","y":"品牌"})
            fig.update_traces(textposition="outside", textfont_color="white")
            apply_chart_style(fig, "品牌商品數量 Top 10", height=360)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ 此搜尋結果無品牌資訊。")

    # ── 頁尾 ──
    st.markdown("---")
    st.markdown(f'<div style="text-align:center;color:rgba(255,255,255,.25);font-size:.78rem;padding:1rem 0 2rem;">🖥 PChome 商品價格分析儀表板 · 資料抓取時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · 共分析 {len(df)} 筆商品</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="empty-state"><div class="icon">🖥</div><p>請在左側選擇搜尋模式與關鍵字，然後按下「🚀 開始搜尋」</p></div>', unsafe_allow_html=True)
