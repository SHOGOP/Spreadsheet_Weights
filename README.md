# Spreadsheet_Weights

ウェイトをスプレッドシート表示で調整するアドオン
![demo](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/6b455b89-b406-4400-8b08-ad224227df64)



## Requirements
- Blender `3.0.0`or higher.
- Windows (Macは動作未確認)
- BQt

## Installation

1.BQtのインストールとアドオンを導入する[Bqt](https://github.com/techartorg/bqt/tree/master)  
インストール方法は[installation docs](https://github.com/techartorg/bqt/wiki/Installation)に解説されているが、こちらでも手順を解説します。
- コマンドプロンプトを管理者権限で起動し、{バージョン}を使用するBlederのバージョンに書き換えて実行
```bash
"C:\Program Files\Blender Foundation\Blender {バージョン}\{バージョン}\python\bin\python.exe" -m pip install git+https://github.com/techartorg/bqt.git
```

- [Bqt](https://github.com/techartorg/bqt/tree/master)からCodeを「Download ZIP」でダウンロードし、
ファイルを解凍したら「bqt-master/bqt」からZIP形式のファイルを作成する。
- Blenderを起動し、`編集>プリファレンス>アドオン>インストール`で作成した「bqt.zip」をインストールし、アドオンを有効化する。
- Blenderを再起動し、画面上に「Blender Qt」というウィンドウが表示されていればインストール完了。

2.Spreadsheet_WeightsをBlenderのアドオンに追加する。

## Usage
###各種説明
![UI_desc_num](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/adcc152d-f19f-4c42-9b57-dc0284911a53)
###①モード
- `ShowAll`ウェイトが設定されてない頂点を表示するようにする
- `Hilight`選択した頂点のみテーブルに表示する
- `Focus`テーブルで選択した頂点を選択する
- `Normalize`ウェイトを編集した後に自動でノーマライズする
- `Mirror`ウェイトを編集した後に自動でミラーする
![mode_change](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/7b2a0d61-d18d-458d-b83e-cad503aec38e)

![weight_button](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/c6969adf-e431-41d9-a891-5b0765fa9ee7)

![filter](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/03d493aa-cd8f-42f5-a7c5-7232b596db8f)
![slider](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/6975c7cc-e6cd-4913-88c9-d43827b5763b)