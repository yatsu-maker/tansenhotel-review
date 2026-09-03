import streamlit as st
from google import genai

# 1. ページ基本設定（ブラウザのタブ名とアイコン）
st.set_page_config(page_title="丹泉ホテル クチコミ返信ツール", page_icon="🏨")

# ------------------------------------------------------------------
# 洗練されたデザインにするためのカスタムCSS
# ------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FA;
        font-family: 'Yu Gothic', '游ゴシック', YuGothic, '游ゴシック体', sans-serif;
    }
    h1 {
        color: #2C3E50;
        font-weight: 600;
        font-size: 26px !important;
        padding-bottom: 10px;
        border-bottom: 2px solid #E0E0E0;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        padding: 15px;
        font-size: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    div[role="radiogroup"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    .stButton>button {
        background-color: #2C3E50;
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1A252F;
        color: white;
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------

# 画面のタイトルと説明文
st.title("🏨 〇〇ホテル 専用クチコミ返信ツール")
st.caption("楽天トラベルなどのクチコミを貼り付けると、当ホテルの情報に基づいた返信文を自動生成します。")

# 2. APIキーの設定
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Keyを入力してください", type="password")

# 3. 入力フォーム
review_text = st.text_area(
    "お客様からのクチコミ本文：", 
    height=150, 
    placeholder="例：部屋は綺麗でしたが、朝食の品数が少し物足りなかったです。"
)

tone = st.radio(
    "返信の方向性：", 
    ["標準（丁寧・誠実）", "感謝強調（高評価向け）", "お詫び・改善強調（低評価向け）"], 
    horizontal=True
)

# 4. 生成ボタン押下時の処理
if st.button("返信文を生成する", type="primary"):
    if not api_key:
        st.error("APIキーが設定されていません。")
    elif not review_text:
        st.warning("クチコミ本文を入力してください。")
    else:
        try:
            client = genai.Client(api_key=api_key)
            
            # クチコミの文字数を判定して指示を切り替える
            review_length = len(review_text)
            if review_length <= 700:
                target_length = review_length * 2
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字です。返信文はその約2倍（{target_length}文字程度）のボリュームになるよう、当ホテルの魅力や感謝の言葉をしっかり肉付けして作成してください。"
            else:
                length_rule = f"\n5. 【重要】お客様のクチコミが{review_length}文字と長文のため、簡潔かつ丁寧に要点をまとめた返信文を作成してください（無理に2倍にする必要はありません）。"

            # ★【重要】ここを新しいホテルの情報に書き換えます
            system_prompt = f"""
あなたは「〇〇ホテル」の優秀なWeb担当者です。
入力されたお客様からのクチコミに対し、以下の【〇〇ホテルの基本情報】を踏まえて適切な返信文を作成してください。

【丹泉ホテルの基本情報】
立地： 山形県南陽市・赤湯温泉の中心に位置。烏帽子山公園やワイナリー巡り、東北の伊勢「熊野大社」など、四季折々の観光やフルーツ狩りを楽しめる拠点として抜群の環境です。

お風呂： 開湯930余年の歴史を持つ名湯。生まれたての赤ちゃんでも入れるほど肌に優しい泉質で、源泉掛け流しの湯をゆったりと堪能できます。

食事： 最高級A5ランクの「米沢牛」を堪能できる夕食（個室食対応あり）と、40年以上愛され続ける名物「つきたてお餅」が自慢の朝食が最大の強みです。

客室： 昭和レトロな情緒漂う落ち着いた和室空間。一人旅からグループ利用に加え、小型犬のワンちゃんと同伴できる専用客室も備えています。

接客方針： 古き良き老舗旅館の温かみを大切にし、ファミリーやペット連れ、お一人様まで、幅広い層のお客様に寄り添う柔軟でホスピタリティあふれる対応を心がけます。

館内設備（追加）： ご宿泊者様が無料で利用できる専用ゲストラウンジ「白竜」を完備。フリードリンクを備え、湯上がりのくつろぎ時間に高い付加価値を提供しています。

ターゲット対応力（追加）： 豪華な特選プランから、若年層やビジネス向けの「泊食分離（素泊まり・朝食のみ）」まで、時代に合わせた多様な滞在スタイルを提案できる懐の深さがあります。

クレーム対応方針：
【朝食の品数】貴重なご意見として受け止め、今後のメニュー改善の参考にする。
【清掃不備】誠心誠意お詫びし、清掃スタッフとの共有と再発防止を約束する。


【返信作成ルール】
1. 選択されたトーン設定: {tone}
2. クチコミ内容を分析し、お褒めの言葉には感謝を、ご指摘やクレームには言い訳をせず誠実な謝罪と改善姿勢を示してください。
3. 宿泊予約サイトにふさわしい丁寧でプロフェッショナルな「です・ます調」で作成してください。
4. 前置きや解説は含めず、そのまま管理画面にコピペできる返信文章のみを出力してください。{length_rule}
"""

            with st.spinner("ホテルのナレッジを参照して返信文を作成中..."):
                response = client.models.generate_content(
                    model='gemini-3.5-flash',
                    contents=[system_prompt, f"クチコミ本文:\n{review_text}"]
                )

            st.success("作成が完了しました！")
            st.text_area("生成された返信文（枠内をクリックし、すべて選択してコピーしてください）", response.text, height=300)

        except Exception as e:
            error_msg = str(e).lower()
            if "503" in error_msg or "high demand" in error_msg:
                st.error("⚠️ 現在、AIのサーバーが混み合っています。数秒〜1分ほど待ってから、もう一度ボタンを押してください。")
            elif "429" in error_msg or "quota" in error_msg:
                st.error("⚠️ 短時間の利用制限にかかりました。1分ほど待ってから再度お試しください。")
            else:
                st.error(f"⚠️ エラーが発生しました。少し時間をおいてやり直してください。（詳細: {e}）")
