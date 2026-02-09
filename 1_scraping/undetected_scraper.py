"""
ユーチュラ → YouTube URL 取得（Cloudflare突破版）

undetected-chromedriverを使ってCloudflareを回避します。

インストール:
pip install undetected-chromedriver

使い方:
python undetected_scraper.py
"""

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv
import time
import os

def setup_driver():
    """undetected-chromedriverのセットアップ"""
    options = uc.ChromeOptions()
    
    # 基本設定
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    # undetected_chromedriverを使用
    # version_main=144 でChrome 144に対応
    try:
        driver = uc.Chrome(options=options, version_main=144)
    except Exception as e:
        print(f"⚠ Chrome 144での起動に失敗: {e}")
        print("💡 自動バージョン検出で再試行します...")
        driver = uc.Chrome(options=options, use_subprocess=True)
    
    return driver

def extract_youtube_url(soup):
    """HTMLからYouTube URLを抽出"""
    import re
    
    # 方法1: channel IDを含むリンクを探す（最も確実）
    youtube_link = soup.find('a', href=lambda x: x and 'youtube.com/channel/' in x)
    if youtube_link:
        return youtube_link['href']
    
    # 方法2: @username形式
    youtube_link = soup.find('a', href=lambda x: x and 'youtube.com/@' in x)
    if youtube_link:
        return youtube_link['href']
    
    # 方法3: /c/ 形式
    youtube_link = soup.find('a', href=lambda x: x and 'youtube.com/c/' in x)
    if youtube_link:
        return youtube_link['href']
    
    # 方法4: /user/ 形式
    youtube_link = soup.find('a', href=lambda x: x and 'youtube.com/user/' in x)
    if youtube_link:
        return youtube_link['href']
    
    return None

def get_youtube_url_from_yutura(driver, yutura_url, wait_time=5):
    """ユーチュラのチャンネルページからYouTube URLを取得"""
    try:
        driver.get(yutura_url)
        time.sleep(wait_time)
        
        # ページが読み込まれるまで少し待つ
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        youtube_url = extract_youtube_url(soup)
        
        return youtube_url
        
    except Exception as e:
        print(f"  ⚠ エラー: {e}")
        return None

def process_csv(input_csv, output_csv, wait_time=5, cool_time=3):
    """CSVファイルを処理してYouTube URLを追加"""
    print("=" * 60)
    print("YouTube URL 取得開始（Cloudflare突破版）")
    print("=" * 60)
    print(f"入力ファイル: {input_csv}")
    print(f"出力ファイル: {output_csv}")
    print("=" * 60)
    print()
    
    # 既存の出力ファイルをチェック（途中再開用）
    existing_data = {}
    resume_mode = False
    
    if os.path.exists(output_csv):
        print(f"📂 既存の出力ファイルを検出: {output_csv}")
        with open(output_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # チャンネルURLをキーにして保存
                existing_data[row['チャンネルURL']] = row.get('YouTube URL', '')
        
        completed = sum(1 for url in existing_data.values() if url and url != 'N/A')
        print(f"✓ 既に{completed}件のYouTube URLを取得済み")
        print(f"💡 続きから処理を開始します")
        resume_mode = True
        print()
    
    # 入力CSVファイルの存在確認
    if not os.path.exists(input_csv):
        print(f"✗ ファイル '{input_csv}' が見つかりません")
        return
    
    # CSVを読み込み
    channels = []
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 既存データがあればマージ
            yutura_url = row['チャンネルURL']
            if yutura_url in existing_data:
                row['YouTube URL'] = existing_data[yutura_url]
            else:
                row['YouTube URL'] = ''
            channels.append(row)
    
    total_count = len(channels)
    remaining = sum(1 for ch in channels if not ch.get('YouTube URL') or ch['YouTube URL'] == 'N/A' or ch['YouTube URL'] == '')
    
    print(f"✓ 全{total_count}件のチャンネルを読み込みました")
    
    if resume_mode:
        print(f"📊 進捗状況:")
        print(f"   完了: {total_count - remaining}件")
        print(f"   残り: {remaining}件")
    
    print()
    
    driver = setup_driver()
    
    try:
        processed_count = 0
        skipped_count = 0
        
        for i, channel in enumerate(channels, 1):
            yutura_url = channel['チャンネルURL']
            channel_name = channel['チャンネル名']
            
            # 既にYouTube URLがあればスキップ
            if channel.get('YouTube URL') and channel['YouTube URL'] != 'N/A' and channel['YouTube URL'] != '':
                skipped_count += 1
                if skipped_count <= 3 or i % 100 == 0:  # 最初の3件と100件ごとに表示
                    print(f"[{i}/{len(channels)}] {channel_name} - スキップ（既に取得済み）")
                continue
            
            print(f"[{i}/{len(channels)}] {channel_name}")
            processed_count += 1
            
            # YouTube URLを取得
            youtube_url = get_youtube_url_from_yutura(driver, yutura_url, wait_time)
            
            if youtube_url:
                print(f"  ✓ YouTube URL: {youtube_url}")
                channel['YouTube URL'] = youtube_url
            else:
                print(f"  ✗ YouTube URLが見つかりませんでした")
                channel['YouTube URL'] = 'N/A'
            
            print()
            
            # クールタイム
            if i < len(channels):
                time.sleep(cool_time)
            
            # 定期的に保存（100件ごと）
            if processed_count % 100 == 0:
                print(f"💾 途中経過を保存中... ({processed_count}件処理)")
                # 出力ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(output_csv), exist_ok=True)
                
                fieldnames = ['チャンネル名', 'チャンネルURL', 'チャンネル登録者数', 'YouTube URL']
                with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(channels)
                print(f"✓ 保存完了")
                print()
        
    except KeyboardInterrupt:
        print("\n⚠ ユーザーによって中断されました")
        print(f"💾 途中経過を保存します...")
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        print(f"💾 途中経過を保存します...")
    finally:
        driver.quit()
        print("✓ ブラウザを閉じました")
    
    # 結果を保存
    if channels:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        fieldnames = ['チャンネル名', 'チャンネルURL', 'チャンネル登録者数', 'YouTube URL']
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(channels)
        
        print(f"\n✓ {len(channels)}件を {output_csv} に保存しました")
        
        # 統計を表示
        success_count = sum(1 for ch in channels if ch.get('YouTube URL') and ch['YouTube URL'] != 'N/A')
        print(f"\n統計:")
        print(f"  成功: {success_count}件")
        print(f"  失敗: {len(channels) - success_count}件")
    
    print("\n" + "=" * 60)
    print("処理完了")
    print("=" * 60)

def main():
    """メイン処理"""
    # ========================================
    # 設定
    # ========================================
    input_csv = '../data/output/yutura_batch_channels.csv'       # 入力CSVファイル
    output_csv = '../data/output/yutura_with_youtube_urls.csv'   # 出力CSVファイル
    wait_time = 5                                                # ページ読み込み待機時間（秒）
    cool_time = 3                                                # リクエスト間のクールタイム（秒）
    # ========================================
    
    print("\n⚠ 注意:")
    print("- undetected-chromedriverを使用します")
    print("- Cloudflareを回避できる可能性が高いです")
    print("- この処理には時間がかかります（1チャンネルあたり約8秒）")
    print()
    
    input("準備ができたらEnterキーを押してください...")
    print()
    
    process_csv(input_csv, output_csv, wait_time, cool_time)

if __name__ == '__main__':
    main()