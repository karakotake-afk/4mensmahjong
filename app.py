import math
import streamlit as st

# ページの設定（スマホで見やすいタイトルとレイアウト）
st.set_page_config(
    page_title="四人打ち麻雀点数計算アプリ", page_icon="🀄", layout="centered"
)

st.title("🀄 四人打ち麻雀点数計算")

# ---------------------------------------------------------
# 1. 基本条件エリア
# ---------------------------------------------------------
st.subheader("【基本条件】")

col1, col2, col3 = st.columns(3)
with col1:
    player = st.radio("上がった人", ["子", "親"], horizontal=True)
with col2:
    win_type = st.radio("和了り方", ["ツモ", "ロン"], horizontal=True)
with col3:
    menzen_state = st.radio(
        "状態", ["門前", "鳴き有り", "平和"], horizontal=True
    )

# ---------------------------------------------------------
# 2. 翻数・特殊判定エリア
# ---------------------------------------------------------
st.subheader("【翻数・特殊判定】")

col_han, col_sp = st.columns([1, 2])

with col_sp:
    special = st.radio(
        "特殊手", ["通常", "七対子", "役満"], horizontal=True
    )

with col_han:
    # 役満選択時は翻数選択を無効化（感覚的にわかりやすく）
    if special == "役満":
        han = st.selectbox("翻数", [1], disabled=True)
    else:
        han = st.selectbox("翻数", list(range(1, 14)), index=0)

yakuman_mult = 1
if special == "役満":
    yakuman_mult = st.radio(
        "役満倍率",
        [1, 2, 3],
        format_func=lambda x: f"{x}倍役満" if x > 1 else "通常役満",
        horizontal=True,
    )

# ---------------------------------------------------------
# 3. 雀頭・待ちエリア
# ---------------------------------------------------------
st.subheader("【雀頭・待ちの形】")
col_head, col_wait = st.columns(2)

with col_head:
    head = st.selectbox(
        "雀頭（アタマ）",
        ["数牌/客風", "役牌（自風・場風・三元牌）", "ダブル風牌"],
    )

with col_wait:
    wait = st.selectbox(
        "待ちの形",
        ["両面 / シャボ", "カンチャン / ペンチャン / 単騎"],
    )

# ---------------------------------------------------------
# 4. 面子の内訳（4組分）
# ---------------------------------------------------------
st.subheader("【面子の内訳（4組分）】")

mentsu_data = []

# 平和または七対子の場合は面子入力をスキップ/固定
is_peiko = menzen_state == "平和"
is_chitoi = special == "七対子"

if is_peiko:
    st.info("💡 「平和」が選択されているため、面子はすべて「順子」として計算されます。")
elif is_chitoi:
    st.info("💡 「七対子」が選択されているため、面子の個別入力は不要です（25符固定）。")
else:
    for i in range(4):
        st.write(f"**面子 {i+1}**")
        c1, c2 = st.columns([3, 2])
        with c1:
            m_type = st.radio(
                f"面子{i+1}の種類",
                ["順子", "明刻", "暗刻", "明槓", "暗槓"],
                key=f"type_{i}",
                horizontal=True,
                label_visibility="collapsed",
            )
        with c2:
            # 順子以外の場合のみ牌の種類（中張/么九）を選択可能にする
            if m_type != "順子":
                m_tile = st.radio(
                    f"面子{i+1}の牌",
                    ["中張牌", "么九牌"],
                    key=f"tile_{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            else:
                st.caption("（順子は0符）")
                m_tile = "中張牌"

        mentsu_data.append({"type": m_type, "tile": m_tile})

# ---------------------------------------------------------
# 5. 積み場（本場）エリア
# ---------------------------------------------------------
st.subheader("【積み場（本場）】")
honba = st.selectbox(
    "本場",
    list(range(11)),
    format_func=lambda x: f"{x}本場（ロン:+{x*300}点 / ツモ:各+{x*100}点）"
    if x > 0
    else "0本場",
)

st.divider()

# ---------------------------------------------------------
# 計算処理
# ---------------------------------------------------------
is_parent = player == "親"
is_tsumo = win_type == "ツモ"
honba_ron_add = honba * 300
honba_tsumo_add = honba * 100

# --- 役満の計算 ---
if special == "役満":
    base_score = 8000 * yakuman_mult
    fu = 0
    res_title = f"【役満（{yakuman_mult}倍役満）】"

# --- 通常の符計算 ---
else:
    if is_chitoi:
        fu = 25
    elif is_peiko and is_tsumo:
        fu = 20
    elif is_peiko and not is_tsumo:
        fu = 30
    else:
        fu = 20  # 基本符（副底）

        # ツモ/ロン加符
        if menzen_state == "門前" and is_tsumo:
            fu += 2
        elif menzen_state == "門前" and not is_tsumo:
            fu += 10
        elif menzen_state == "鳴き有り" and is_tsumo:
            fu += 2

        # 雀頭の符
        if head == "役牌（自風・場風・三元牌）":
            fu += 2
        elif head == "ダブル風牌":
            fu += 4

        # 待ちの符
        if wait == "カンチャン / ペンチャン / 単騎":
            fu += 2

        # 面子の符
        score_table = {
            ("明刻", "中張牌"): 2,
            ("明刻", "么九牌"): 4,
            ("暗刻", "中張牌"): 4,
            ("暗刻", "么九牌"): 8,
            ("明槓", "中張牌"): 8,
            ("明槓", "么九牌"): 16,
            ("暗槓", "中張牌"): 16,
            ("暗槓", "么九牌"): 32,
        }

        for m in mentsu_data:
            if m["type"] != "順子":
                fu += score_table.get((m["type"], m["tile"]), 0)

        # 10符切り上げ（喰い平和特例含む）
        if fu == 20 and menzen_state == "鳴き有り":
            fu = 30
        else:
            fu = math.ceil(fu / 10) * 10

    # 基本点算出
    if han >= 13:
        base_score = 8000  # 数え役満
    elif han >= 11:
        base_score = 6000  # 三倍満
    elif han >= 8:
        base_score = 4000  # 倍満
    elif han >= 6:
        base_score = 3000  # 跳満
    elif han >= 5 or (han == 4 and fu >= 40) or (han == 3 and fu >= 70):
        base_score = 2000  # 満貫
    else:
        base_score = fu * (2 ** (han + 2))
        if base_score > 2000:
            base_score = 2000

    res_title = f"【{fu}符 {han}翻】"

# ---------------------------------------------------------
# 計算結果の表示
# ---------------------------------------------------------
st.subheader("【計算結果】")

# コンテナ枠で強調表示
with st.container(border=True):
    st.markdown(f"### {res_title}（{player}のあがり）")

    if honba > 0:
        st.caption(f"※ {honba}本場分の加算点が含まれています")

    if is_parent:
        # --- 親のあがり ---
        if is_tsumo:
            pay = math.ceil((base_score * 2) / 100) * 100 + honba_tsumo_add
            st.success(
                f"**子一人につき: {pay:,} 点** （合計: {pay*3:,} 点）"
            )
        else:
            pay = math.ceil((base_score * 6) / 100) * 100 + honba_ron_add
            st.success(f"**放銃者から: {pay:,} 点**")
    else:
        # --- 子のあがり ---
        if is_tsumo:
            p_pay = math.ceil((base_score * 2) / 100) * 100 + honba_tsumo_add
            c_pay = math.ceil((base_score * 1) / 100) * 100 + honba_tsumo_add
            total = p_pay + (c_pay * 2)
            st.success(
                f"**親の支払い: {p_pay:,} 点 / 子の支払い: {c_pay:,} 点（一人あたり）**\n\n（合計: {total:,} 点）"
            )
        else:
            pay = math.ceil((base_score * 4) / 100) * 100 + honba_ron_add
            st.success(f"**放銃者から: {pay:,} 点**")

# 注記表示
st.caption("※ 平和ツモは20符固定で計算します。")
st.caption("※ リーチ供託棒の処理は決められたルールに従ってお願いします。")