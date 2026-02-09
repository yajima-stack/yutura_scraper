"""
ユーチュラスクレイパー（複数HTML一括処理版）

手動で保存したHTMLファイルから一括でデータを抽出します。
Cloudflareなどのブロックを完全に回避できます。

使い方:
1. ブラウザで各ページを開く
2. 右クリック → 「ページのソースを表示」
3. すべて選択してコピー（Ctrl+A → Ctrl+C）
4. html_files/ フォルダに page1.html, page2.html... として保存
5. python batch_html_parser.py を実行
"""

from bs4 import BeautifulSoup
import csv
import os
import glob

def extract_channels(html_content):
    """HTMLコンテンツからチャンネル情報を抽出"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    channel_list = soup.find('ul', class_='channel-list')
    
    if not channel_list:
        return []
    
    channels = []
    
    for li in channel_list.find_all('li'):
        try:
            # チャンネル名
            title_elem = li.find('p', class_='title')
            channel_name = title_elem.text.strip() if title_elem else 'N/A'
            
            # チャンネルURL
            more_link = li.find('a', href=True)
            channel_id = more_link['href'] if more_link else 'N/A'
            channel_url = f"https://yutura.net{channel_id}" if channel_id != 'N/A' else 'N/A'
            
            # チャンネル登録者数
            people_icon = li.find('i', title='チャンネル登録者数')
            subscribers = 'N/A'
            if people_icon:
                p_tag = people_icon.parent
                if p_tag:
                    icon_copy = people_icon.extract()
                    subscribers = p_tag.get_text(strip=True)
                    p_tag.insert(0, icon_copy)
            
            channels.append({
                'チャンネル名': channel_name,
                'チャンネルURL': channel_url,
                'チャンネル登録者数': subscribers
            })
            
        except Exception as e:
            print(f"⚠ チャンネル情報の抽出中にエラー: {e}")
            continue
    
    return channels

def process_html_files(html_dir='../html_files'):
    """HTMLファイルを一括処理"""
    print("=" * 60)
    print("ユーチュラ 複数HTML一括処理")
    print("=" * 60)
    print(f"HTMLフォルダ: {html_dir}")
    print("=" * 60)
    print()
    
    # HTMLフォルダの存在確認
    if not os.path.exists(html_dir):
        print(f"✗ フォルダ '{html_dir}' が見つかりません。")
        print(f"  フォルダを作成してHTMLファイルを配置してください。")
        return []
    
    # HTMLファイルを検索（page1.html, page2.html などの順番で）
    html_files = sorted(glob.glob(os.path.join(html_dir, 'page*.html')))
    
    if not html_files:
        # page*.html が見つからない場合、すべての.htmlファイルを対象
        html_files = sorted(glob.glob(os.path.join(html_dir, '*.html')))
    
    if not html_files:
        print(f"✗ HTMLファイルが見つかりません。")
        print(f"  {html_dir}/ フォルダに page1.html, page2.html... を配置してください。")
        return []
    
    print(f"✓ {len(html_files)}個のHTMLファイルを検出しました")
    print()
    
    all_channels = []
    
    for i, html_file in enumerate(html_files, 1):
        filename = os.path.basename(html_file)
        print(f"[{i}/{len(html_files)}] {filename}")
        print("-" * 60)
        
        try:
            # HTMLファイルを読み込み
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # チャンネル情報を抽出
            channels = extract_channels(html_content)
            
            if not channels:
                print(f"⚠ チャンネル情報が見つかりませんでした")
            else:
                print(f"✓ {len(channels)}件のチャンネル情報を抽出")
                all_channels.extend(channels)
                print(f"✓ 累計: {len(all_channels)}件")
            
            print()
            
        except Exception as e:
            print(f"✗ エラー: {e}")
            print()
            continue
    
    print("=" * 60)
    print(f"処理完了: 全{len(html_files)}ファイル、合計{len(all_channels)}件")
    print("=" * 60)
    
    return all_channels

def save_to_csv(channels, filename='../data/output/yutura_batch_channels.csv'):
    """CSVファイルに保存"""
    if not channels:
        print("\n保存するデータがありません")
        return
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['チャンネル名', 'チャンネルURL', 'チャンネル登録者数'])
        writer.writeheader()
        writer.writerows(channels)
    
    print(f"\n✓ {len(channels)}件のデータを {filename} に保存しました")

def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("ユーチュラ 複数HTML一括処理スクリプト")
    print("=" * 60)
    print()
    
    # ========================================
    # 設定
    # ========================================
    html_dir = '../html_files'                                  # HTMLファイルを配置するフォルダ
    output_filename = '../data/output/yutura_batch_channels.csv'  # 出力ファイル名
    # ========================================
    
    # HTMLファイルを処理
    all_channels = process_html_files(html_dir)
    
    # 結果を表示
    if all_channels:
        print(f"\n{'=' * 60}")
        print("取得したチャンネル情報（最初の5件）")
        print('=' * 60)
        for i, channel in enumerate(all_channels[:5], 1):
            print(f"\n{i}. {channel['チャンネル名']}")
            print(f"   URL: {channel['チャンネルURL']}")
            print(f"   登録者数: {channel['チャンネル登録者数']}")
        
        if len(all_channels) > 5:
            print(f"\n... 他 {len(all_channels) - 5}件")
        
        # CSVに保存
        save_to_csv(all_channels, output_filename)
        
        print(f"\n{'=' * 60}")
        print("すべての処理が完了しました！")
        print('=' * 60)
    else:
        print("\nチャンネル情報を取得できませんでした")
        print(f"\n💡 ヒント:")
        print(f"- {html_dir}/ フォルダに page1.html, page2.html... を配置してください")
        print(f"- 詳細は {html_dir}/README.txt を参照してください")

if __name__ == '__main__':
    main()