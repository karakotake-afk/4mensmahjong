import math
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="麻雀点数計算アプリ（4人打ち・3人打ち対応）",
    page_icon="🀄",
    layout="centered",
)

st.title("🀄 麻雀点数計算アプリ")

# 4人打ちと3人打ちのタブ作成
tab4, tab3 = st.tabs(["🀄 4人打ち（ヨンマ）", "🀄 3人打ち（サンマ）"])


# =========================================================
# 共通計算処理関数
# =========================================================
def calculate_score(
    player,
    win_type,
    menzen_state,
    special,
    han,
    yakuman_mult,
    head,
    wait,
    mentsu_data,
    honba,
    is_3p=False,
):
    is_parent = player == "親"
    is_tsumo = win_type == "ツモ"
    is_peiko = menzen_state == "平和"
    is_chitoi = special == "七対子"

    honba_ron_add = honba * (1000 if is_3p else 300)
    honba_tsumo_add = honba * (500 if is_3p else 100)

    # --- 役満 ---
    if special == "役満":
        base_score = 8000 * yakuman_mult
        fu = 0
        res_title = f"役満（{yakuman_mult}倍役満）"
    # --- 通常計算 ---
    else:
        if is_chitoi:
            fu = 25
        elif is_peiko and is_tsumo:
            fu = 20
        elif is_peiko and not is_tsumo:
            fu = 30
        else:
            fu = 20  # 副底

            # ツモ/ロン加符
            if menzen_state == "門前" and is_tsumo:
                fu += 2
            elif menzen_state == "門前" and not is_tsumo:
                fu += 10
            elif menzen_state == "鳴き有り" and is_tsumo:
                fu += 2

            # 雀頭
            if head == "役牌":
                fu += 2
            elif head == "ダブル風牌":
                fu += 4

            # 待ち
            if wait == "カンチャン/ペンチャン/単騎":
                fu += 2

            # 面子
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

            if fu == 20 and menzen_state == "鳴き有り":
                fu = 30
            else:
                fu = math.ceil(fu / 10) * 10

        # 基本点算出
        if han >= 13:
            base_score = 8000
        elif han >= 11:
            base_score = 6000
        elif han >= 8:
            base_score = 4000
        elif han >= 6:
            base_score = 3000
        elif han >= 5 or (han == 4 and fu >= 40) or (han == 3 and fu >= 70):
            base_score = 2000
        else:
            base_score = fu * (2 ** (han + 2))
            if base_score > 2000:
                base_score = 2000

        res_title = f"{fu}符 {han}翻"

    # ---------------------------------------------------------
    # 結果画面描画
    # ---------------------------------------------------------
    st.subheader("【計算結果】")

    with st.container(border=True):
        prefix = "サンマ・" if is_3p else ""
        st.markdown(
            f"#### 🀄 **{res_title}** （{prefix}{player}のあがり）"
        )

        if honba > 0:
            st.caption(
                f"※ {honba}本場を含む（ロン:+{honba_ron_add:,}点 /"
                f" ツモ:各+{honba_tsumo_add:,}点）"
            )

        st.write("---")

        ron_score = (
            math.ceil((base_score * (6 if is_parent else 4)) / 100) * 100
        )

        if not is_3p:
            # ---------------- 四人打ち ----------------
            if is_parent:
                if is_tsumo:
                    pay = (
                        math.ceil((base_score * 2) / 100) * 100
                        + honba_tsumo_add
                    )
                    st.metric(
                        label="子一人あたりの支払い",
                        value=f"{pay:,} 点",
                        delta=f"合計 {pay*3:,} 点",
                        delta_color="off",
                    )
                else:
                    pay = ron_score + honba_ron_add
                    st.metric(
                        label="放銃者の支払い（ロン）", value=f"{pay:,} 点"
                    )
            else:
                if is_tsumo:
                    p_pay = (
                        math.ceil((base_score * 2) / 100) * 100
                        + honba_tsumo_add
                    )
                    c_pay = (
                        math.ceil((base_score * 1) / 100) * 100
                        + honba_tsumo_add
                    )
                    total = p_pay + (c_pay * 2)

                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label="親の支払い", value=f"{p_pay:,} 点")
                    with c2:
                        st.metric(
                            label="子の支払い（一人あたり）",
                            value=f"{c_pay:,} 点",
                        )
                    st.caption(f"💰 合計獲得点数: **{total:,} 点**")
                else:
                    pay = ron_score + honba_ron_add
                    st.metric(
                        label="放銃者の支払い（ロン）", value=f"{pay:,} 点"
                    )
        else:
            # ---------------- 三人打ち ----------------
            if not is_tsumo:
                pay = ron_score + honba_ron_add
                st.metric(
                    label="放銃者の支払い（ロン）", value=f"{pay:,} 点"
                )
            else:
                if is_parent:
                    noloss_pay = (ron_score // 2) + honba_tsumo_add
                    loss_pay = (
                        math.ceil((base_score * 2) / 100) * 100
                    ) + honba_tsumo_add

                    st.write("🔹 **【ツモ損なし】**")
                    st.metric(
                        label="子一人あたりの支払い",
                        value=f"{noloss_pay:,} 点",
                        delta=f"合計 {noloss_pay*2:,} 点",
                        delta_color="off",
                    )
                    st.write("🔸 **【ツモ損あり】**")
                    st.metric(
                        label="子一人あたりの支払い",
                        value=f"{loss_pay:,} 点",
                        delta=f"合計 {loss_pay*2:,} 点",
                        delta_color="off",
                    )
                else:
                    noloss_p = (
                        math.ceil((ron_score * 2 / 3) / 100) * 100
                    ) + honba_tsumo_add
                    noloss_c = (
                        math.ceil((ron_score * 1 / 3) / 100) * 100
                    ) + honba_tsumo_add

                    loss_p = (
                        math.ceil((base_score * 2) / 100) * 100
                    ) + honba_tsumo_add
                    loss_c = (
                        math.ceil((base_score * 1) / 100) * 100
                    ) + honba_tsumo_add

                    st.write("🔹 **【ツモ損なし】**")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric(label="親の支払い", value=f"{noloss_p:,} 点")
                    with c2:
                        st.metric(label="子の支払い", value=f"{noloss_c:,} 点")

                    st.write("🔸 **【ツモ損あり】**")
                    c3, c4 = st.columns(2)
                    with c3:
                        st.metric(label="親の支払い", value=f"{loss_p:,} 点")
                    with c4:
                        st.metric(label="子の支払い", value=f"{loss_c:,} 点")

    st.caption("※ 平和ツモは20符固定で計算します。")
    st.caption(
        "※ リーチ供託棒の処理は決められたルールに従ってお願いします。"
    )


# =========================================================
# UI描画関数
# =========================================================
def render_ui(key_prefix, is_3p=False):
    # 1. 基本条件
    st.subheader("【基本条件】")
    c1, c2, c3 = st.columns(3)
    with c1:
        player = st.radio(
            "上がった人",
            ["子", "親"],
            horizontal=True,
            key=f"{key_prefix}_player",
        )
    with c2:
        win_type = st.radio(
            "和了り方",
            ["ツモ", "ロン"],
            horizontal=True,
            key=f"{key_prefix}_win",
        )
    with c3:
        menzen_state = st.radio(
            "状態",
            ["門前", "鳴き有り", "平和"],
            horizontal=True,
            key=f"{key_prefix}_state",
        )

    # 2. 翻数・特殊判定
    st.subheader("【翻数・特殊判定】")
    special = st.radio(
        "特殊手",
        ["通常", "七対子", "役満"],
        horizontal=True,
        key=f"{key_prefix}_sp",
    )

    if special == "役満":
        yakuman_mult = st.radio(
            "役満倍率",
            [1, 2, 3],
            format_func=lambda x: f"{x}倍役満" if x > 1 else "通常役満",
            horizontal=True,
            key=f"{key_prefix}_ym",
        )
        han = 1
    else:
        yakuman_mult = 1
        han = st.radio(
            "翻数",
            list(range(1, 14)),
            horizontal=True,
            key=f"{key_prefix}_han",
        )

    # 3. 雀頭・待ち（ラジオボタン化）
    st.subheader("【雀頭・待ちの形】")
    c_head, c_wait = st.columns(2)
    with c_head:
        head = st.radio(
            "雀頭（アタマ）",
            ["客風/数牌", "役牌", "ダブル風牌"],
            horizontal=True,
            key=f"{key_prefix}_head",
        )
    with c_wait:
        wait = st.radio(
            "待ちの形",
            ["両面/シャボ", "カンチャン/ペンチャン/単騎"],
            horizontal=True,
            key=f"{key_prefix}_wait",
        )

    # 4. 面子の内訳
    st.subheader("【面子の内訳（4組分）】")
    mentsu_data = []

    is_peiko = menzen_state == "平和"
    is_chitoi = special == "七対子"
    is_menzen = menzen_state in ["門前", "平和"]

    if is_peiko:
        st.info("💡 「平和」のため面子はすべて「順子」固定です。")
    elif is_chitoi:
        st.info("💡 「七対子」のため面子入力は不要です（25符固定）。")
    else:
        # 門前時の選択肢制御（明刻・明槓を除外）
        type_options = (
            ["順子", "暗刻", "暗槓"]
            if is_menzen
            else ["順子", "明刻", "暗刻", "明槓", "暗槓"]
        )

        for i in range(4):
            st.write(f"**面子 {i+1}**")
            col1, col2 = st.columns([3, 2])
            with col1:
                m_type = st.radio(
                    f"面子{i+1}種類",
                    type_options,
                    key=f"{key_prefix}_type_{i}",
                    horizontal=True,
                    label_visibility="collapsed",
                )
            with col2:
                if m_type != "順子":
                    m_tile = st.radio(
                        f"面子{i+1}牌",
                        ["中張牌", "么九牌"],
                        key=f"{key_prefix}_tile_{i}",
                        horizontal=True,
                        label_visibility="collapsed",
                    )
                else:
                    st.caption("（順子は0符）")
                    m_tile = "中張牌"

            mentsu_data.append({"type": m_type, "tile": m_tile})

    # 5. 本場
    st.subheader("【積み場（本場）】")
    add_ron = 1000 if is_3p else 300
    add_tsumo = 500 if is_3p else 100

    honba = st.selectbox(
        "本場",
        list(range(11)),
        format_func=lambda x: (
            f"{x}本場（ロン:+{x*add_ron:,}点 / ツモ:各+{x*add_tsumo:,}点）"
            if x > 0
            else "0本場"
        ),
        key=f"{key_prefix}_honba",
    )

    st.divider()

    # 計算呼び出し
    calculate_score(
        player,
        win_type,
        menzen_state,
        special,
        han,
        yakuman_mult,
        head,
        wait,
        mentsu_data,
        honba,
        is_3p,
    )


# =========================================================
# 各タブのレンダリング
# =========================================================
with tab4:
    render_ui("m4p", is_3p=False)

with tab3:
    render_ui("m3p", is_3p=True)