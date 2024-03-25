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
![UI_desc](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/17b4d093-174a-4892-bcc6-26aed2125855)
![weight_button](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/c6969adf-e431-41d9-a891-5b0765fa9ee7)
![mode_change](https://github.com/SHOGOP/Spreadsheet_Weights/assets/122035414/c439b5d0-a303-4f16-8ab8-5014eea52e59)