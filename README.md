# BlenderAddon-AutoMerge
## はじめに
モデルのオブジェクト数が多い！  
モディファイアを適用してから結合（マージ）するのめんどくさい！  
というときに便利なアドオンです。  

ダウンロードはこちらから  
https://github.com/SleetCat123/BlenderAddon_AutoMerge/releases  

Boothでもダウンロードできます。  
（現在は古いバージョンのみ）  
https://sleetcatshop.booth.pm/items/1166452  

---  
### 同作者の別アドオンとの連携
[ShapeKeys Util](https://github.com/SleetCat123/BlenderAddon_ShapeKeysUtil) との連携機能を有効にすることにより、シェイプキーをもつオブジェクトのモディファイアを適用してマージできるようになります。

[MizoresCustomExporter](https://github.com/SleetCat123/BlenderAddon_MizoresCustomExporter) との連携機能を有効にすることで、
- オブジェクトをマージした状態でエクスポート
- エクスポート完了後には元通り！

ということもできるようになります。  
（詳しくは[MizoresCustomExporter](https://github.com/SleetCat123/BlenderAddon_MizoresCustomExporter)のReadmeを参照）  

---
### ◆Ver_2.1.0またはそれより前のバージョンから移行する際の注意
1. エクスポート時のマージ対象かどうかの識別方法が変更されました。  
   - 2.1.0まで: `MergeGroup`という名前の**コレクションに入っている**オブジェクトをマージ対象とする
   - 3.0.0から: `MergeGroup`という名前の**propが有効になっている**オブジェクトをマージ対象とする

2.1.0以前のデータから最新の方式に移行する場合、[MizoresCustomExporter](https://github.com/SleetCat123/BlenderAddon_MizoresCustomExporter) の`Convert Collections`を使用して移行してください。

変更理由
   別のblendファイルからオブジェクトをインポートした際、コレクションの設定が初期化されてしまう場合があります。
   `MergeGroup`などの制御用コレクションを使用していた場合、これまではインポート後に再設定しなければなりませんでした。  
   この問題を避けるため、コレクションではなくオブジェクトそのものに各種制御用フラグを持たせる仕様に変更しました。

2. バージョンVer_2.2.0以前に本アドオンに搭載されていたfbxエクスポート機能は、別アドオン[MizoresCustomExporter](https://github.com/SleetCat123/BlenderAddon_MizoresCustomExporter)として分離しました。  
エクスポート時の自動マージ機能を使用する場合は、こちらのアドオンをインストールしてください。

3. Blender 2.7系への互換性確保コードを削除しました。  
   2.7系で使用したい場合は、Ver_2.1.0以前のバージョンを使用してください。

4. スクリプトの内部構造を変更しました。  
   不具合回避のため、バージョンアップ時には古いバージョンを削除してから導入してください。


## 機能説明

### ◆Auto Merge → Merge Children
`オブジェクトモードで右クリック → Auto Merge → Merge Children`  
選択中オブジェクトの子階層以下にあるオブジェクトをマージします。

- 設定
  - **Duplicate**: チェックを入れると、対象となるオブジェクトを複製した上でマージ処理を行います。
  - **Apply Parent Object Modifiers**: チェックを入れると、結合先オブジェクトのモディファイアを適用します。

### ◆Merge Selection
`オブジェクトモードで右クリック → Auto Merge → Merge Selection`  
最後に選択したオブジェクトに対し、選択中の他オブジェクトをマージします。

- 設定
  - **Duplicate**: チェックを入れると、対象となるオブジェクトを複製した上でマージ処理を行います。
  - **Apply Parent Object Modifiers**: チェックを入れると、結合先オブジェクトのモディファイアを適用します。

### ◆Merge Grouped Children
`オブジェクトモードで右クリック → Auto Merge → Merge Grouped Children`  
選択中のオブジェクトのうち、`MergeGroup`プロパティが有効なものに対し、それぞれ子階層以下にあるオブジェクトをマージします。  
`DontMergeToParent`プロパティが有効なオブジェクトは結合されません。  

（アドオン`MizoresExporter`によるAutoMerge連携機能はこのコマンドと同じ動作でマージ処理を行います）  

- 設定
  - **Duplicate**: チェックを入れると、対象となるオブジェクトを複製した上でマージ処理を行います。
  - **Apply Parent Object Modifiers**: チェックを入れると、結合先オブジェクトのモディファイアを適用します。

### 動作例
以下の動作は同梱の『Sample.blend』ファイルで実際に確認できます。  
  
例として以下のような階層構造のデータがあったとします。  

- Sample.blend  
  - Armature  
    - Body        **(AutoMerge)**  
      - Clothes  
        - Ribbon  
      - Head  
    - Hair        **(AutoMerge)**  
      - BackHair  
      - FrontHair  
    - Plane  
    - Skirt  
  - Cube        **(AutoMerge)**  
    - Plane.001  
  
これらのオブジェクトを選択して`Merge Grouped Children`を実行すると、`AutoMerge`プロパティが有効なオブジェクトの子オブジェクトが結合されて以下のような階層構造になります。  
  
- Sample  
  - Armature  
    - Body  
    - Hair  
    - Plane  
    - Skirt  
  - Cube  

### ◇オブジェクトのプロパティによる特殊処理
各種プロパティは  
`オブジェクトモードの右クリックメニュー > Auto Merge`  
または
`サイドメニュー（Nキー）→Assign (Mizore)`  
から割り当て／解除ができます。

- MergeGroup: このプロパティが有効なオブジェクトは、`Merge Grouped Children`による子オブジェクトの結合対象となります。
- DontMergeToParent: このプロパティが有効なオブジェクトは、オブジェクト結合時に親オブジェクトに結合されません。

**アドオン連携 (MizoresCustomExporter)**  
`Export → MizoresCustomExporter`でのエクスポート時、`MergeGroup`に入っているオブジェクトは子オブジェクトを結合した状態でエクスポートされます。  
エクスポート完了後、オブジェクトは実行前の状態に戻ります。


### ◆子オブジェクト名の接頭辞
このアドオンで結合するオブジェクトの子オブジェクト名の先頭に以下の文字列を付けることにより、特殊な結合処理を行うことができます。
- `%SHAPE%` Join as shape親オブジェクトに結合（親オブジェクトと頂点数が一致している必要があります）  

### ◆モディファイア名の接頭辞
このアドオンで結合されるオブジェクトに設定されているモディファイアの名前の先頭に以下の文字列を付けることにより、特殊な結合処理を行うことができます。
- `%A%` Armatureなどの通常は適用されないモディファイアを強制的に適用
- `%KEEP%` モディファイアを適用せずに処理を続行
- `%AS%` 形状をシェイプキーとして適用（変化後の


### ◆Select Modifier Prefix (Panel)
`サイドメニュー（Nキー）→Mizore`内に追加されます。
アクティブオブジェクトのモディファイア名の先頭に接頭辞を付けることができます。  
上記`モディファイア名の接頭辞`に記載されているものが選択できます。  


### ◆Switch %AS% Modifiers (Panel)
`サイドメニュー（Nキー）→Mizore`内に追加されます。
選択しているオブジェクトのモディファイアのうち、`%AS%`で始まるものがボタンとして表示されます。  
（表示では`%AS%`は省略されています）  
全てのオブジェクトのモディファイアのうち、押したボタンと同じ名前のモディファイアは表示状態となり、それ以外の`%AS%`で始まるモディファイアは非表示状態となります。  


### ◆Variants Merge
執筆中

## ◆注意

- マージする際、Armatureを除く全てのモディファイアは適用されます。ただし、レンダリング対象でないモディファイア（モディファイア一覧でカメラアイコンが押されていないもの）は適用せず無視されます。

- 同作者の別アドオン"ShapeKeys Util"との連携機能が無効になっている場合、シェイプキーをもつオブジェクトはモディファイアを無視してマージ処理を行います。その場合でも、シェイプキーを含まない他のオブジェクトは通常通りにモディファイア適用・マージを行います。

## ◆不具合・エラーが起きた時
このアドオンの機能はBlender標準のAPIを使って作成しているため、何らかの不具合が発生した場合にはすぐに Undo（Ctrl+Z） すれば機能使用前の状態に復元できます。  
アドオンの機能を使用する直前にデータを保存しておき、不具合が起きた場合はデータを読み込み直すのがより確実です。  

また、以下の連絡先に不具合発生時の状況を送っていただけると修正の手助けになります。

## ◆連絡先
不具合報告や要望、感想などありましたらこちらにどうぞ。

修正・実装が可能と思われるものに関しては着手を検討しますが、多忙や技術的問題などの理由により対応できない場合があります。  
予めご了承ください。

Twitter：猫柳みぞれ　https://twitter.com/sleetcat123
