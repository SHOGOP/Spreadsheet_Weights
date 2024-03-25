# Spreadsheet_Weights

ウェイトをスプレッドシート表示で調整するアドオン


## Requirements
- Blender `3.0.0`or higher.
- Windows (Macは動作未確認)
- BQt

# Installation

1.BQtのインストールとアドオンを導入する[Bqt](https://github.com/techartorg/bqt/tree/master)
インストール方法は[installation docs](https://github.com/techartorg/bqt/wiki/Installation)に解説されているが、こちらでも手順を解説します。
- コマンドプロンプトを管理者権限で起動し、{バージョン}を使用するBlederのバージョンに書き換えて実行
```bash
"C:\Program Files\Blender Foundation\Blender {バージョン}\{バージョン}\python\bin\python.exe" -m pip install git+https://github.com/techartorg/bqt.git
```

- [Bqt](https://github.com/techartorg/bqt/tree/master)からCodeを「Download ZIP」でダウンロードし、
ファイルを解凍したら「bqt-master/bqt」からZIP形式のファイルを作成する。
- Blenderを起動し、'編集>プリファレンス>アドオン>インストール'で作成した「bqt.zip」をインストールし、アドオンを有効化する。
- Blenderを再起動し、画面上に「Blender Qt」というウィンドウが表示されていればインストール完了。

2.Spreadsheet_WeightsをBlenderのアドオンに追加する。

# Usage
