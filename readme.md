# checkBLE

## CPythonの用意

仮想環境を作成する

    pipenv --python 3.10

## ライブラリの追加

必要なライブラリを追加する

    pipenv install bleak

    pipenv install Nuitka

    pipenv install pyyaml

## exe化

以下コマンドを実行する

    nuitka main.py --standalone