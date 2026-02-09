"""
YouTube URL突合・データ連結スクリプト

スクレイピングしたYouTube URLとtalentデータのsub_youtube_urlを突合し、
一致するもののみを連結します。

使い方:
1. yutura_with_youtube_urls.csv を用意
2. talent_data.csv を data/input/ に配置
3. python merge_youtube_data.py を実行
"""

import csv
import pandas as pd
import os

def merge_youtube_data(yutura_csv, talent_csv, output_csv):
    """
    2つのCSVファイルを突合してマージ
    
    Parameters:
    - yutura_csv: スクレイピングしたデータ (YouTube URL列あり)
    - talent_csv: タレントデータ (sub_youtube_url列あり)
    - output_csv: 出力ファイル名
    """
    
    print("=" * 60)
    print("YouTube URL突合・データ連結")
    print("=" * 60)
    print()
    
    # ユーチュラのデータを読み込み
    print(f"📂 読み込み中: {yutura_csv}")
    df_yutura = pd.read_csv(yutura_csv, encoding='utf-8-sig')
    print(f"✓ {len(df_yutura)}件のデータを読み込みました")
    print()
    
    # タレントデータを読み込み
    print(f"📂 読み込み中: {talent_csv}")
    try:
        # まず通常の方法で試す
        df_talent = pd.read_csv(talent_csv, encoding='utf-8-sig')
    except Exception as e:
        print(f"⚠ 通常の読み込みでエラー: {e}")
        print(f"💡 エラー行をスキップして再読み込みします...")
        
        # エラー行をスキップして読み込み
        df_talent = pd.read_csv(
            talent_csv, 
            encoding='utf-8-sig',
            on_bad_lines='skip',  # 問題のある行をスキップ
            engine='python'       # Pythonエンジンを使用
        )
        print(f"⚠ 一部の行をスキップしました")
    
    print(f"✓ {len(df_talent)}件のデータを読み込みました")
    print()
    
    # YouTube URLで突合（内部結合 - 両方に存在するもののみ）
    print("🔗 データを突合中...")
    print("   突合キー: YouTube URL ⇔ sub_youtube_url")
    df_merged = pd.merge(
        df_yutura,
        df_talent,
        left_on='YouTube URL',
        right_on='sub_youtube_url',
        how='inner'  # 両方に存在するもののみ
    )
    
    print(f"✓ {len(df_merged)}件が一致しました")
    print()
    
    # 一致率を計算
    match_rate = (len(df_merged) / len(df_yutura)) * 100 if len(df_yutura) > 0 else 0
    print(f"📊 統計情報:")
    print(f"   スクレイピングデータ: {len(df_yutura)}件")
    print(f"   タレントデータ: {len(df_talent)}件")
    print(f"   一致したデータ: {len(df_merged)}件")
    print(f"   一致率: {match_rate:.2f}%")
    print()
    
    # 結果を保存
    if len(df_merged) > 0:
        # 出力ディレクトリが存在しない場合は作成
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        
        df_merged.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"✓ {output_csv} に保存しました")
        
        # 列名を表示
        print()
        print("📋 出力列:")
        for i, col in enumerate(df_merged.columns, 1):
            print(f"   {i}. {col}")
        
        # サンプルを表示
        print()
        print("📝 サンプルデータ（最初の3件）:")
        print("-" * 60)
        for idx, row in df_merged.head(3).iterrows():
            print(f"\n{idx + 1}件目:")
            print(f"  チャンネル名: {row['チャンネル名']}")
            print(f"  YouTube URL: {row['YouTube URL']}")
            
            # talent_idがある場合のみ表示
            if 'talent_id' in row:
                print(f"  talent_id: {row['talent_id']}")
            if 'talent_name' in row:
                print(f"  talent_name: {row['talent_name']}")
            if 'main_youtube_name' in row:
                print(f"  main_youtube_name: {row['main_youtube_name']}")
            if 'sub_youtube_name' in row:
                print(f"  sub_youtube_name: {row['sub_youtube_name']}")
            if 'sub_youtube_followers' in row:
                print(f"  sub_youtube_followers: {row['sub_youtube_followers']}")
    else:
        print("⚠ 一致するデータがありませんでした")
    
    print()
    print("=" * 60)
    print("処理完了")
    print("=" * 60)
    
    return df_merged

def main():
    """メイン処理"""
    # ========================================
    # 設定
    # ========================================
    yutura_csv = '../data/output/yutura_with_youtube_urls.csv'  # スクレイピングデータ
    talent_csv = '../data/input/talent_data.csv'                # タレントデータ
    output_csv = '../data/output/merged_youtube_data.csv'       # 出力ファイル
    # ========================================
    
    print("\n📌 設定:")
    print(f"  スクレイピングデータ: {yutura_csv}")
    print(f"  タレントデータ: {talent_csv}")
    print(f"  出力ファイル: {output_csv}")
    print()
    
    try:
        df_merged = merge_youtube_data(yutura_csv, talent_csv, output_csv)
    except FileNotFoundError as e:
        print(f"\n✗ エラー: ファイルが見つかりません")
        print(f"  {e}")
        print()
        print("💡 以下のファイルを準備してください:")
        print(f"  - {yutura_csv}")
        print(f"  - {talent_csv}")
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")

if __name__ == '__main__':
    main()