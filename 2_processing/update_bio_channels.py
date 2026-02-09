"""
紹介文に「その他Youtubeチャンネル」を追加するスクリプト

merged_youtube_data.csvから紹介文用のテキストを生成します。

使い方:
1. merged_youtube_data.csv を用意（merge_youtube_data.pyで生成）
2. bio_data.tsv を data/input/ に配置
3. python update_bio_channels.py を実行
"""

import pandas as pd
import os

print("=" * 80)
print("紹介文に「その他Youtubeチャンネル」を追加するスクリプト")
print("=" * 80)

# ========================================
# 設定：ファイルパスを指定してください
# ========================================

# 1. マージ済みデータファイル
MERGED_FILE = '../data/output/merged_youtube_data.csv'

# 2. 紹介文データファイル（TSVファイル）
BIO_FILE = '../data/input/bio_data.tsv'

# 3. 出力ファイル
OUTPUT_FILE = '../data/output/updated_biography.tsv'

# 4. チャンネル情報付きCSV（中間ファイル）
CHANNEL_TEXT_FILE = '../data/output/channels_with_text.csv'

# ========================================
# 処理開始
# ========================================

print("\nStep 1: マージ済みデータを読み込み中...")
try:
    df_merged = pd.read_csv(MERGED_FILE, encoding='utf-8-sig')
    print(f"✓ マージデータ読み込み成功: {len(df_merged)}行")
except Exception as e:
    print(f"✗ エラー: マージデータが読み込めませんでした")
    print(f"  ファイルパス: {MERGED_FILE}")
    print(f"  エラー内容: {e}")
    exit(1)

print("\nStep 2: チャンネル情報を整形中...")

# talent_idごとにチャンネル情報を集約
channel_groups = {}

for idx, row in df_merged.iterrows():
    talent_id = row['talent_id']
    channel_name = row['チャンネル名']
    youtube_url = row['YouTube URL']
    
    if talent_id not in channel_groups:
        channel_groups[talent_id] = []
    
    channel_groups[talent_id].append({
        'channel_name': channel_name,
        'youtube_url': youtube_url
    })

print(f"✓ {len(channel_groups)}人のタレントのチャンネル情報を整形しました")

# 「その他Youtubeチャンネル」テキストを生成
channel_texts = {}

for talent_id, channels in channel_groups.items():
    # ユニークなチャンネルのみ取得（重複排除）
    unique_channels = []
    seen_urls = set()
    
    for ch in channels:
        if ch['youtube_url'] not in seen_urls:
            unique_channels.append(ch)
            seen_urls.add(ch['youtube_url'])
    
    # テキスト生成
    text_lines = ["その他Youtubeチャンネル"]
    for ch in unique_channels:
        text_lines.append(f"・{ch['channel_name']}：__{ch['youtube_url']}__")
    
    channel_texts[talent_id] = "\n".join(text_lines)

print(f"✓ 「その他Youtubeチャンネル」テキストを生成しました")

# 中間ファイルとして保存（channels_with_text.csv）
print("\nStep 3: 中間ファイルを保存中...")

channel_data_for_csv = []
for talent_id, text in channel_texts.items():
    # 最初のチャンネル情報を取得
    first_channel = channel_groups[talent_id][0]
    
    # talent_nameを取得（merged_dataから）
    talent_name = df_merged[df_merged['talent_id'] == talent_id]['talent_name'].iloc[0]
    
    channel_data_for_csv.append({
        'talent_id': talent_id,
        'talent_name': talent_name,
        'サブチャンネル名': first_channel['channel_name'],
        'YouTube URL': first_channel['youtube_url'],
        'その他Youtubeチャンネル': text
    })

df_channels = pd.DataFrame(channel_data_for_csv)

# 出力ディレクトリが存在しない場合は作成
os.makedirs(os.path.dirname(CHANNEL_TEXT_FILE), exist_ok=True)

df_channels.to_csv(CHANNEL_TEXT_FILE, index=False, encoding='utf-8-sig')
print(f"✓ 中間ファイル保存成功: {CHANNEL_TEXT_FILE}")

# bio_dataがある場合は紹介文を更新
if os.path.exists(BIO_FILE):
    print("\nStep 4: 紹介文データを読み込み中...")
    try:
        df_bio = pd.read_csv(BIO_FILE, sep='\t', encoding='utf-8')
        print(f"✓ 紹介文データ読み込み成功: {len(df_bio)}行")
        print(f"  カラム: {df_bio.columns.tolist()}")
    except Exception as e:
        print(f"✗ エラー: 紹介文データファイルが読み込めませんでした")
        print(f"  ファイルパス: {BIO_FILE}")
        print(f"  エラー内容: {e}")
        print("\n【ヒント】")
        print("  - ファイルパスが正しいか確認してください")
        print("  - ファイルがTSV形式（タブ区切り）か確認してください")
        exit(1)

    print("\nStep 5: 紹介文を更新中...")

    # 紹介文を更新する関数
    def update_biography(row):
        talent_id = row['talent_id']
        bio = str(row['紹介文']) if '紹介文' in row else ''
        
        # talent_idに対応するチャンネル情報があれば追加
        if talent_id in channel_texts:
            channel_text = channel_texts[talent_id]
            
            # URLの前後の__を削除
            channel_text = channel_text.replace('__', '')
            
            # 元の紹介文がnanや空の場合は、チャンネル情報のみを入れる
            if bio == 'nan' or bio.strip() == '':
                return channel_text
            else:
                # 紹介文がある場合は、最後に空行+チャンネル情報を追加
                return f"{bio}\n\n{channel_text}"
        else:
            # チャンネル情報がない場合
            if bio == 'nan' or bio.strip() == '':
                return ''  # 空文字を返す
            else:
                return bio

    # 各行の紹介文を更新
    df_bio['紹介文'] = df_bio.apply(update_biography, axis=1)

    # 更新された件数を確認
    updated_count = sum(1 for tid in df_bio['talent_id'] if tid in channel_texts)
    print(f"✓ 更新完了: {updated_count}件の紹介文にチャンネル情報を追加しました")
    print(f"  未更新: {len(df_bio) - updated_count}件（該当するチャンネル情報なし）")

    print("\nStep 6: ファイルを保存中...")
    try:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        df_bio.to_csv(OUTPUT_FILE, sep='\t', index=False, encoding='utf-8')
        print(f"✓ 保存成功: {OUTPUT_FILE}")
    except Exception as e:
        print(f"✗ エラー: ファイルの保存に失敗しました")
        print(f"  エラー内容: {e}")
        exit(1)

    print("\n" + "=" * 80)
    print("処理完了！")
    print("=" * 80)

    # サンプル表示
    print("\n【処理結果のサンプル】最初の2件を表示:")
    print("-" * 80)
    for i in range(min(2, len(df_bio))):
        print(f"\n{i+1}件目:")
        print(f"  talent_id: {df_bio.iloc[i]['talent_id']}")
        print(f"  talent_name: {df_bio.iloc[i]['talent_name']}")
        print(f"\n  更新後の紹介文:")
        bio_preview = df_bio.iloc[i]['紹介文']
        # 長い場合は最初の300文字だけ表示
        if len(bio_preview) > 300:
            print(f"  {bio_preview[:300]}...")
        else:
            print(f"  {bio_preview}")
        print("-" * 80)

    print(f"\n✓ 総レコード数: {len(df_bio)}件")
    print(f"✓ 出力ファイル: {OUTPUT_FILE}")
    print("\n処理が完了しました！")

else:
    print(f"\n⚠ 紹介文データファイル ({BIO_FILE}) が見つかりません")
    print(f"✓ 中間ファイル ({CHANNEL_TEXT_FILE}) のみ生成されました")
    print("\n処理が完了しました！")