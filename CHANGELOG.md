## ◆更新履歴

### 2024-09-03 v3.0.0
- add: Variants Merge機能を追加
- add: エラー発生時に処理実行前の状態を復元するようにした
- add: パネルからpropの有効／無効を切り替えられるようにした
- add: Select Modifier Prefix (Panel)を追加
- add: Switch %AS% Modifiers (Panel)を追加
- fix: Blender4.1でAuto Smoothの扱いが変わったことによりエラーが発生するのを修正
- change: **スクリプトを複数ファイルに分離。不具合回避のため、バージョンアップ時には古いバージョンを削除してから導入してください。**
- remove: **Blender 2.7系への互換性確保コードを削除。2.7系で使用したい場合はVer_2.1.0以前のバージョンを使用してください。**
- change: オペレーターのDuplicate設定を廃止
- change: エクスポート機能を別アドオン『MizoresCustomExporter』として分離。
- change: テキスト表示言語切り替えの実装方法を変更（ところどころ日本語表示だけしか実装してないのであまり変化なし）
- change: モディファイア適用時、無効なモディファイア（対象オブジェクトが指定されていないなどの状態）を削除するようにした（無効なモディファイアがあるとシェイプキーがエクスポートされなくなる現象対策）
- change: 親子関係が2階層以上あるオブジェクトに対してMerge Childrenを使うと、深い階層のオブジェクトの位置がずれた状態で結合されることがあるのを修正（Merge Grouped Childrenでは以前のバージョンでも修正済）
- change: Merge Children使用時、非表示状態のオブジェクトと子オブジェクトをマージ対象から除外するように変更。
- change: 選択中のオブジェクト全てに対してMerge Childrenが使用されるように変更（これまではアクティブオブジェクトのみに使用されていた）
- アドオン連携の互換性: 
  - [MizoresCustomExporter](https://github.com/SleetCat123/BlenderAddon_MizoresCustomExporter): 1.0.0-
  - [ShapeKeysUtil](https://github.com/SleetCat123/BlenderAddon_ShapeKeysUtil): 2.0.0-

### 2021-11-30- Ver_2.1.0
- change: Auto Merge(.fbx)のエクスポート先やAdd Leaf Bonesなどの各種設定値を.blendファイルに保存するようにした
- change: 対象外モディファイア（現在はArmatureのみ）であっても、名前が%A%から始まるものは強制的にモディファイアを適用させるようにした
- change: Merge系処理の実行時、名前が%AS%から始まるモディファイアをシェイプキーとして適用（Apply as shapekey）するようにした（シェイプキー適用時に名前の%AS%は削除）
- fix: Auto Merge(.fbx)の使用時、特定の状況下でエラーが出ることがあるのを修正

### 2021-06-15- Ver_2.0.0
- add: Blender2.8以降に対応
- add: Auto Merge(.fbx)にツールシェルフ項目“Scale”を追加。
- add: Auto Merge(.fbx)にツールシェルフ項目“!EXPERIMENTAL! Apply Transform”を追加（初期値：True）。
- add: 結合先オブジェクトのモディファイアを適用させずにマージできる設定“Apply Parent Object Modifiers”を追加。
- change: Auto Merge(.fbx)のツールシェルフ項目“Apply Scaling”の初期値を“FBX Units Scale”に。
- change: Merge系処理でArmatureモディファイアを無視するかどうかを選べるように。
- change: Addon Preferenceでエクスポート設定の既定値を変更できるように。
- change: “AlwaysExport”コレクションに属しているオブジェクトは非表示状態でも強制的にエクスポートをされるように（Blender 2.8以降のみ）。
- fix: “MergeObject”グループに入っているオブジェクトが1つもない状態でAuto Merge(.fbx)を使うとエラーが出る不具合を修正。

### 2019-02-11- Ver_1.1.0
- add: 同作者の別アドオン“ShapeKeys Util”との連携機能の追加
- add: コマンドにカーソルを乗せたとき説明文が表示されるように（現在は日本語のみ）
- add: Read-meに今回の更新内容を反映
- change: 導入／更新方法.txtの文章を変更

### 2019-02-04- Ver_1.0.3
- change: Auto Merge(.fbx)のツールシェルフ項目“Add Leaf Bones”の標準値をTrueに
- change: エクスポート終了後にモードを復元するように（Editモード中にエクスポートした場合、これまではObjectモードになってしまっていた）
- fix: オブジェクトモードでオブジェクトを削除した直後、他のオブジェクトを選択しなおさずにAuto Merge(.fbx)を使うとエラーが出るのを修正
- fix: マージ可能なオブジェクトが複数選択された状態で Wキー(Specials) → Auto Merge → Merge Grouped Children すると一部のオブジェクトにマージ処理がかからないのを修正
- fix: Auto Merge(.fbx)の後、非Meshオブジェクト（カーブとか）が増殖してしまう不具合を修正

### 2019-01-31- Ver_1.0.2
- change: レンダリングが無効化されたモディファイア（モディファイア一覧でカメラアイコンが押されていないもの）は結合時に無視するように
- add: Read-meにも今回の更新内容を反映

### 2019-01-13- Ver_1.0.1
- fix: オブジェクトモード以外でAuto Merge(.fbx)を行うとエラーが出る不具合を修正
- add: 導入方法.txtにアドオン更新方法を追加
- change: Read-meの順番を少し変更

### 2019-01-09- Ver_1.0
- 公開。
