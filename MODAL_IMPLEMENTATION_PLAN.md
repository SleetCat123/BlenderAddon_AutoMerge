# AutoMerge Modal対応実装方針書

## 1. 背景と目的

### 1.1 現状の課題
- 大量のオブジェクトやモディファイアを処理する際にBlenderが「応答なし」になる
- 特に`Merge Children`や`Merge Selections`実行時の進捗が不明
- 処理のキャンセルができない
- ShapeKeysUtil連携時に処理時間が大幅に増加する

### 1.2 目的
- UIの応答性を維持しながら重いマージ処理を実行
- 進捗表示とキャンセル機能の提供
- ShapeKeysUtil連携時でも快適な操作性を実現

## 2. 技術的制約

### 2.1 Blender Modal Operatorの制限
- Modal内での`bpy.ops`呼び出しに制約
- コンテキスト操作の制限
- 一部のオペレーションはModalと非互換

### 2.2 既存アーキテクチャの特徴
- 再帰的な処理構造（`merge_children_recursive`）
- ShapeKeysUtilとの密な連携
- MizoresCustomExporter、MeshDeformUtilsとの連携
- Variantsシステムによる条件分岐処理

## 3. 実装方針

### 3.1 基本方針
- **既存コードは変更しない**（別ファイルで新実装）
- **段階的移行**（実験的機能として導入）
- **後方互換性の完全維持**（連携APIは変更なし）
- **ShapeKeysUtilのModal実装を参考に統一性を保つ**

### 3.2 アーキテクチャ
```
既存構造（維持）          新規構造（追加）
    ↓                      ↓
ops/op_*.py          modal_ops/mop_*.py
    ↓                      ↓
funcs/func_*.py  ←共有→  modal/state_machines/*.py
                           ↓
                      modal/base_modal.py
```

## 4. ディレクトリ構造

```
scripts/
├── modal/                              # Modal処理の基盤
│   ├── __init__.py
│   ├── core/                          # コア機能
│   │   ├── __init__.py
│   │   ├── base_modal.py              # Modal基底クラス（最小限の実装）
│   │   ├── modal_timer.py             # タイマー管理
│   │   └── modal_state.py             # 状態管理の基底クラス
│   ├── progress/                      # 進捗管理
│   │   ├── __init__.py
│   │   ├── progress_tracker.py        # 進捗追跡クラス
│   │   ├── progress_display.py        # UI表示制御
│   │   └── progress_integration.py    # ShapeKeysUtil連携
│   ├── handlers/                      # イベントハンドラ
│   │   ├── __init__.py
│   │   ├── error_handler.py           # エラーハンドリング
│   │   ├── cancel_handler.py          # キャンセル処理
│   │   └── context_handler.py         # コンテキスト管理
│   ├── state_machines/                # 状態機械実装
│   │   ├── __init__.py
│   │   ├── base_state_machine.py      # 状態機械基底クラス
│   │   ├── merge_selections/          # Merge Selections用
│   │   │   ├── __init__.py
│   │   │   ├── selection_state.py     # 状態定義
│   │   │   ├── selection_processor.py # 処理実装
│   │   │   └── selection_utils.py     # ユーティリティ
│   │   └── merge_children/            # Merge Children用
│   │       ├── __init__.py
│   │       ├── children_state.py      # 状態定義
│   │       ├── children_processor.py  # 処理実装
│   │       ├── recursion_handler.py   # 再帰処理の非再帰化
│   │       └── variants_handler.py    # Variants処理
│   └── utils/                         # ユーティリティ
│       ├── __init__.py
│       ├── modal_decorators.py        # デコレータ
│       ├── modal_context.py           # コンテキスト管理
│       └── modal_profiler.py          # パフォーマンス計測
├── modal_ops/                         # Modalオペレーター
│   ├── __init__.py
│   ├── mop_merge_selections.py        # Merge Selections Modal版
│   ├── mop_merge_children.py          # Merge Children Modal版
│   └── mop_base.py                    # 共通処理
├── experimental/                      # 実験的機能
│   ├── __init__.py
│   ├── config/                        # 設定管理
│   │   ├── __init__.py
│   │   ├── modal_config.py            # Modal設定
│   │   └── modal_preferences.py       # プリファレンス拡張
│   └── debug/                         # デバッグ機能
│       ├── __init__.py
│       ├── modal_debugger.py          # デバッグツール
│       └── modal_logger.py            # ログ出力
└── tests/                             # テスト（新規）
    ├── __init__.py
    ├── modal/                         # Modal関連テスト
    │   ├── __init__.py
    │   ├── test_state_machines.py
    │   └── test_progress.py
    └── integration/                   # 統合テスト
        ├── __init__.py
        └── test_shapekeys_integration.py
```

## 5. 実装詳細

### 5.1 コア機能（modal/core/）

#### base_modal.py - Modal基底クラス
```python
class BaseModalOperator:
    - 最小限のModal実装
    - タイマー、進捗、エラーハンドラの統合
    - 派生クラスのためのフック提供
```

#### modal_timer.py - タイマー管理
```python
class ModalTimer:
    - Timer登録/解除
    - 更新間隔の管理
    - パフォーマンス計測
```

#### modal_state.py - 状態管理基底
```python
class ModalState:
    - 状態遷移の基本実装
    - 状態保存/復元
    - 中断/再開サポート
```

### 5.2 進捗管理（modal/progress/）

#### progress_tracker.py - 進捗追跡
```python
class ProgressTracker:
    - 現在の処理対象/総数の管理
    - 処理速度の計算
    - 残り時間の推定
    - 階層的な進捗管理（親子関係）
```

#### progress_display.py - UI表示
```python
class ProgressDisplay:
    - ヘッダーへの進捗表示
    - ステータスバー更新
    - カスタムUI要素の管理
```

#### progress_integration.py - 外部連携
```python
class ProgressIntegration:
    - ShapeKeysUtilの進捗情報取得
    - 統合進捗の計算
    - 連携アドオンとの同期
```

### 5.3 状態機械（modal/state_machines/）

#### base_state_machine.py - 基底実装
```python
class BaseStateMachine:
    - 2フェーズ実行の制御
    - 状態遷移ロジック
    - 処理キューの管理
    - チェックポイント管理
```

#### analysis/ - 解析フェーズ共通
- **hierarchy_analyzer.py**: 階層構造解析
- **dependency_resolver.py**: 依存関係解決
- **workload_estimator.py**: 処理量推定

#### merge_selections/ - Merge Selections専用
- **selection_analyzer.py**: 選択オブジェクト解析
- **selection_state.py**: 実行状態定義
- **selection_executor.py**: 実行フェーズ処理
- **instance_handler.py**: インスタンス実体化

#### merge_children/ - Merge Children専用
- **children_analyzer.py**: 階層解析と処理順序決定
- **children_state.py**: 実行状態定義
- **children_executor.py**: 実行フェーズ処理
- **recursion_queue.py**: 再帰→キュー変換
- **variants_processor.py**: バリアント展開と処理
- **parent_table_manager.py**: 親子関係の状態管理

### 5.4 エラーハンドリング（modal/handlers/）

#### error_handler.py
```python
class ModalErrorHandler:
    - エラーの分類と処理
    - リカバリー戦略の実装
    - ユーザーへの通知
    - ロールバック処理
```

#### cancel_handler.py
```python
class CancelHandler:
    - ESCキー検出
    - 安全なキャンセル処理
    - 部分的な結果の保存オプション
```

### 5.5 設定管理（experimental/config/）

#### modal_config.py
```python
class ModalConfig:
    - use_modal_operators: bool (デフォルト: False)
    - modal_update_interval: float (0.01秒)
    - show_progress_in_header: bool
    - show_object_names_in_progress: bool
    - enable_time_estimation: bool
    - max_steps_per_update: int (処理の粒度)
```

#### modal_preferences.py
```python
- アドオンプリファレンスの拡張
- UI要素の追加
- 設定の保存/読込
```

### 5.6 デバッグ機能（experimental/debug/）

#### modal_debugger.py
```python
class ModalDebugger:
    - 状態遷移のログ
    - パフォーマンスプロファイル
    - メモリ使用量追跡
```

#### modal_logger.py
```python
- 詳細なログ出力
- ログレベル管理
- ファイル出力オプション
```

## 6. 実装アプローチと段階的移行計画

### 6.1 2フェーズアプローチの詳細

#### Phase A: 解析フェーズ（高速）
```python
class AnalysisPhase:
    - 階層構造の完全スキャン
    - 処理対象オブジェクトのリスト化
    - バリアント展開と総処理量計算
    - 依存関係の解析（Curveモディファイアなど）
    - 処理順序の最適化
    - 推定処理時間の計算
```

#### Phase B: 実行フェーズ（Modal）
```python
class ExecutionPhase:
    - 事前計算された順序で処理
    - オブジェクト単位での進捗更新
    - キャンセルポイントの設置
    - エラー時のチェックポイントロールバック
```

### 6.2 処理の粒度設計

#### 処理単位
1. **最小単位**: 1オブジェクトの全処理
2. **キャンセル可能点**: オブジェクト間のみ
3. **進捗更新**: オブジェクト完了時

#### 処理ステップ
```
オブジェクト処理:
├─ 前処理（選択状態設定）
├─ タイプ変換（CURVE→MESH等）
├─ 子オブジェクト処理
├─ モディファイア適用
├─ オブジェクト結合
└─ 後処理（クリーンアップ）
```

### 6.3 段階的移行計画

### Phase 1: 基盤構築（2週間）
- [ ] 2フェーズアーキテクチャの実装
- [ ] 解析エンジンの開発
- [ ] Modal基底クラスの実装
- [ ] チェックポイントシステム
- [ ] 設定UIの追加

### Phase 2: Merge Selectionsの移行（2週間）
- [ ] 解析フェーズの実装（インスタンス検出含む）
- [ ] 実行フェーズの状態機械
- [ ] 重み付き進捗計算
- [ ] エラーハンドリング

### Phase 3: Merge Childrenの移行（3-4週間）
- [ ] 階層解析エンジン
- [ ] 再帰処理のキュー変換
- [ ] Variantsシステム統合
- [ ] 依存関係解決
- [ ] 親子関係の状態管理

### Phase 4: ShapeKeysUtil連携（1週間）
- [ ] Modal API検出
- [ ] 進捗情報統合
- [ ] フォールバック処理

### Phase 5: 統合とテスト（2週間）
- [ ] メニュー統合
- [ ] パフォーマンス最適化
- [ ] 包括的なテスト
- [ ] ドキュメント作成

## 7. Modal化対象の優先度

### 高優先度（必須）
1. **Merge Children** (`op_merge_children.py`)
   - 再帰的処理で最も時間がかかる
   - 大規模なオブジェクト階層で問題になりやすい
   - Variantsシステムと組み合わせると更に時間がかかる

2. **Merge Selections** (`op_merge_selections.py`)
   - 複数オブジェクトの処理で時間がかかる
   - ShapeKeysUtil連携時に特に遅い
   - インスタンス実体化処理が重い

3. **Merge Grouped Children (For Exporter)** (`op_link_with_MizoresCustomExporter.py`)
   - Merge Childrenの内部実装を使用
   - MizoresCustomExporter連携の主要機能
   - Modal版Merge Childrenを活用可能

### 低優先度（Modal化不要）
- **Assign Prop** - プロパティ設定のみで瞬時に完了
- **Link operations** - 内部API用で直接ユーザーが使用しない

### Modal化の判断基準
1. **処理時間**: 0.5秒以上かかる可能性がある
2. **ループ処理**: 複数オブジェクトに対する繰り返し
3. **再帰処理**: 階層構造の深い処理
4. **外部連携**: ShapeKeysUtil等の重い処理を呼び出す

## 8. コード分析に基づく技術的課題と対策

### 8.1 Blenderオペレーターへの強い依存
**課題**: 以下のような中断不可能なオペレーターを多用
- `bpy.ops.object.convert()` - オブジェクトタイプ変換
- `bpy.ops.object.modifier_apply()` - モディファイア適用
- `bpy.ops.object.join()` / `join_shapes()` - オブジェクト結合
- `bpy.ops.object.duplicates_make_real()` - インスタンス実体化

**対策**: 
- オペレーターを**オブジェクト単位**でのみ実行（細かい粒度は不可能）
- キャンセルチェックは各オブジェクト処理の間でのみ実施
- 処理時間推定は過去の実行データから学習

### 8.2 再帰処理と状態管理の複雑さ
**課題**: 
- `temp_children_name_table`で親子関係を動的に管理
- 再帰処理中にオブジェクトの削除・再親子付けが発生
- 処理順序が重要（子から親へ）

**対策**: 
- **2フェーズアプローチ**:
  1. 解析フェーズ: 階層構造を分析し、処理順序を事前決定
  2. 実行フェーズ: 決定した順序で処理を実行
- Modal状態として処理キューを保持
- 親子関係の変更履歴を記録

### 8.3 Variantsシステムの仮実装と改善案
**現状の問題**: 
- 全バリアント分のオブジェクトを**事前に複製**（メモリ使用量 O(n×m)）
- 各バリアントを**独立処理**するため計算が重複
- バリアントに含まれないオブジェクトを**削除**（破壊的）
- 処理時間が**バリアント数に比例**して増加

**Modal化を機にした改善案**:
1. **遅延評価方式**:
   ```python
   # 現在: 全バリアント分を事前複製
   for variant in variants:
       duplicate_entire_hierarchy()
   
   # 改善案: バリアントごとに必要時のみ処理
   for variant in variants:
       process_variant_lazy(variant)
   ```

2. **仮想バリアント処理**:
   - オブジェクトの複製を避け、フィルタリングで対応
   - メッシュデータのみ複製して効率化
   - 共通処理の結果をキャッシュ

3. **スマートな進捗管理**:
   - バリアント×オブジェクトの2次元進捗
   - "Variant 2/5: Object 10/50"形式の表示
   - バリアント間でのキャンセル可能

### 8.4 ShapeKeysUtil連携の特殊性
**課題**: 
- カスタムオペレーター `shapekeys_util_apply_mod_with_shapekeys_automerge`
- ShapeKeysUtil側もModal化されている可能性
- エラー時のフォールバック処理

**対策**:
- ShapeKeysUtilのModal APIを検出して適応
- 非Modal/Modal両方のコードパスを維持
- 進捗情報の双方向通信プロトコル

### 8.5 エラーリカバリーの難しさ
**課題**: 
- 現在は`try-except`でUndo実行
- 部分的に処理済みのオブジェクトの扱い
- 親子関係が変更された後のロールバック

**対策**:
- **チェックポイント方式**:
  - 各オブジェクト処理前に状態を記録
  - エラー時は最後の安定状態まで戻る
- 部分的成功の結果を保持するオプション
- デバッグモードでの詳細ログ

### 8.6 進捗計算とUI更新
**課題**: 
- 処理時間が大きく異なる（単純なEmpty vs 大量モディファイアのMesh）
- 階層的な処理での進捗表示
- ヘッダー領域の文字数制限

**対策**:
- **重み付き進捗計算**:
  - オブジェクトタイプ別の処理時間係数
  - モディファイア数による重み付け
  - 頂点数による補正
- 階層表示: "親オブジェクト > 子オブジェクト (3/10)"
- 簡潔な表示モードと詳細モードの切り替え

## 9. テスト計画

### 9.1 機能テスト
- [ ] 通常のマージ処理が正常に完了すること
- [ ] キャンセルが正しく動作すること
- [ ] エラー時に適切にロールバックすること
- [ ] Undo/Redoが正常に動作すること

### 9.2 互換性テスト
- [ ] 既存のオペレーターが影響を受けないこと
- [ ] ShapeKeysUtil連携が正常に動作すること
- [ ] MizoresCustomExporter連携が維持されること
- [ ] 設定の切り替えが正しく機能すること

### 9.3 パフォーマンステスト
- [ ] Modal版が同期版と同等の処理時間であること
- [ ] UIの応答性が維持されること
- [ ] 大規模階層構造での安定性
- [ ] メモリ使用量が適切であること

### 9.4 特殊ケーステスト
- [ ] インスタンスオブジェクトの処理
- [ ] Curve/Text等の非Meshオブジェクトの変換
- [ ] 非表示オブジェクトの処理
- [ ] リンクされたオブジェクトの処理

### 9.5 Variantsシステムテスト
- [ ] 単一バリアントの処理
- [ ] 複数バリアント（5個、10個、20個）の処理
- [ ] バリアント間でのキャンセル
- [ ] 空のバリアント（オブジェクトが含まれない）の処理
- [ ] 全オブジェクトが全バリアントに含まれるケース
- [ ] メモリ使用量の比較（現行 vs Modal版）
- [ ] 処理時間の比較（現行 vs Modal版）

## 10. リスクと対策

### リスク1: 再帰処理の変換による不具合
**対策**: 十分なテストケース作成、段階的な移行

### リスク2: ShapeKeysUtil連携の複雑化
**対策**: 明確なインターフェース定義、相互テスト

### リスク3: パフォーマンスの低下
**対策**: プロファイリング、処理の最適化

## 11. 成功指標

1. **UIの応答性**: 処理中もBlenderが操作可能
2. **ユーザビリティ**: 進捗が見える、キャンセル可能
3. **互換性**: 既存の連携が全て動作
4. **安定性**: エラー率が既存版以下
5. **パフォーマンス**: 処理時間が既存版と同等以下

## 12. 今後の展望

### 将来的な拡張
- バッチ処理モード
- 処理のプリセット保存
- より詳細な進捗情報（各フェーズの進捗）
- 処理時間の予測表示

### 長期的な統合
- 安定後、既存コードを新実装で置き換え
- ShapeKeysUtilとの統合的なModal管理
- APIの統一と簡素化

## 13. 実装方針の妥当性検証

### READMEとの整合性確認
✓ **主要機能の維持**
- Merge Children、Merge Selections、Merge Grouped Childrenすべて対応
- 既存の動作を完全に再現

✓ **連携機能の維持**
- ShapeKeysUtil連携：進捗統合により強化
- MizoresCustomExporter連携：完全互換
- MeshDeformUtils連携：更新処理も含めて対応

✓ **特殊処理の対応**
- %SHAPE%（Join as shape）：専用ステップとして実装
- %A%（強制適用）、%KEEP%（スキップ）：フラグ処理を維持
- %AS%：Switch AS Modifiersパネルとの連携維持

✓ **UIとユーザビリティ**
- プロパティベースの制御を維持
- 設定による切り替えで既存ワークフローを妨げない
- 進捗表示とキャンセル機能で操作性向上

### 実装優先度の根拠

1. **Merge Children**：
   - 最も処理負荷が高く、再帰的処理のModal化は技術的にも重要
   - Variantsシステムで処理量が爆発的に増加する可能性
   - 他の機能（Merge Grouped Children）の基盤となる

2. **Merge Selections**：
   - ユーザー使用頻度が高く、効果が実感しやすい
   - インスタンス実体化など重い処理を含む
   - 比較的シンプルな処理フローでModal化しやすい

3. **Merge Grouped Children**：
   - 内部的にMerge Childrenを使用するため、実装が容易
   - MizoresCustomExporter連携の主要機能
   - Modal版が完成すれば自動的に恩恵を受ける

### コード分析からの重要な知見

1. **処理の原子性**
   - Blenderオペレーターは中断不可能
   - 処理の粒度はオブジェクト単位が限界
   - より細かい進捗表示には工夫が必要

2. **状態管理の複雑さ**
   - 親子関係が動的に変化
   - オブジェクトの削除・生成が頻繁
   - 一時テーブルによる関係管理が必要

3. **2フェーズアプローチの必要性**
   - 事前の解析なしには進捗計算が困難
   - 依存関係の解決が必要（Curveモディファイアなど）
   - バリアント展開で処理量が動的に変化

## 14. 実装例とコードスニペット

### 14.1 2フェーズ実行の例

```python
class MergeChildrenModalOperator(BaseModalOperator):
    def invoke(self, context, event):
        # Phase A: 解析フェーズ（即座に実行）
        self.analyzer = ChildrenAnalyzer()
        analysis_result = self.analyzer.analyze(
            target_objects=context.selected_objects,
            settings=self.settings
        )
        
        # Variantsの展開
        if self.settings.use_variants_merge:
            self.variant_processor = VariantProcessor(analysis_result)
            self.work_queue = self.variant_processor.create_work_queue()
        else:
            self.work_queue = analysis_result.to_work_queue()
        
        # 進捗トラッカー初期化
        self.progress = ProgressTracker(
            total_items=self.work_queue.total_items,
            weight_map=self.work_queue.weight_map,
            variants_count=self.variant_processor.variants_count if self.settings.use_variants_merge else 1
        )
        
        # Phase B: 実行フェーズ（Modal開始）
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        if event.type == 'ESC':
            return self.cancel(context)
            
        if event.type == 'TIMER':
            # バリアント境界でのキャンセルチェック
            if self.work_queue.is_variant_boundary():
                if self.check_cancel_requested():
                    return self.cancel(context)
            
            # オブジェクト単位で処理
            if self.work_queue.has_next():
                work_item = self.work_queue.get_next()
                try:
                    self.process_object_with_variant(work_item)
                    self.progress.update(work_item)
                except Exception as e:
                    return self.handle_error(context, e)
            else:
                return self.finish(context)
                
        return {'RUNNING_MODAL'}
```

### 14.2 処理キューの構造例（Variants対応）

```python
@dataclass
class WorkItem:
    # 基本情報
    object_name: str
    object_type: str
    parent_name: Optional[str]
    children_names: List[str]
    
    # Variant情報
    variant_name: Optional[str] = None
    variant_index: int = 0
    variant_total: int = 1
    
    # 処理情報
    modifiers_count: int
    has_shapekeys: bool
    estimated_weight: float
    processing_order: int
    
    @property
    def is_variant_boundary(self):
        """バリアントの境界かどうか"""
        return self.processing_order == 0
    
class VariantAwareWorkQueue:
    def __init__(self, variants_enabled: bool = False):
        self.items: List[WorkItem] = []
        self.current_index = 0
        self.checkpoints: Dict[int, SceneState] = {}
        self.variant_cache: Dict[str, Any] = {}  # 共通処理のキャッシュ
        
    def add_checkpoint(self):
        """チェックポイントを追加（バリアント境界で自動追加）"""
        self.checkpoints[self.current_index] = capture_scene_state()
        
    def get_variant_progress(self):
        """バリアント単位の進捗を取得"""
        if not self.items:
            return 0, 0
        current = self.items[self.current_index]
        return current.variant_index + 1, current.variant_total
```

### 14.3 Variantsシステムの効率的な実装例

```python
class VariantProcessor:
    """バリアント処理の効率化"""
    
    def __init__(self, analysis_result):
        self.base_hierarchy = analysis_result.hierarchy
        self.variant_map = self._build_variant_map()
        
    def _build_variant_map(self):
        """オブジェクトとバリアントの関係を事前計算"""
        variant_map = defaultdict(set)
        for obj_data in self.base_hierarchy:
            for variant in obj_data.variants:
                variant_map[variant].add(obj_data.name)
        return variant_map
        
    def process_variant_lazy(self, variant_name):
        """遅延評価でバリアントを処理（複製なし）"""
        included_objects = self.variant_map[variant_name]
        
        # 仮想的にフィルタリング
        for obj_data in self.base_hierarchy:
            if obj_data.name not in included_objects:
                # 削除せずにスキップフラグを設定
                obj_data.skip_processing = True
            else:
                obj_data.skip_processing = False
                
        # 実際の処理はメインループで実行
        return self._create_filtered_work_items(variant_name)
```

### 14.4 進捗表示の実装例（Variants対応）

```python
class VariantAwareProgressDisplay:
    def update_header(self, context, progress_info):
        text = "AutoMerge: "
        
        # バリアント情報
        if progress_info.has_variants:
            variant_current, variant_total = progress_info.variant_progress
            text += f"[Variant {variant_current}/{variant_total}] "
        
        # オブジェクト階層
        if progress_info.current_parent:
            text += f"{progress_info.current_parent} > {progress_info.current_object}"
        else:
            text += f"{progress_info.current_object}"
            
        # 総合進捗
        percentage = progress_info.total_percentage
        eta = progress_info.estimated_time_remaining
        text += f" ({percentage:.0f}% - ETA: {eta}s)"
        
        # ShapeKeysUtil連携時の詳細進捗
        if progress_info.has_sub_progress:
            text += f" [SK: {progress_info.sub_progress:.0f}%]"
            
        context.area.header_text_set(text)
```

### 14.5 処理時間の推定例

```python
class ProcessingTimeEstimator:
    """処理時間の推定（学習機能付き）"""
    
    # オブジェクトタイプ別の基本係数
    TYPE_WEIGHTS = {
        'MESH': 1.0,
        'CURVE': 1.5,  # 変換処理があるため重い
        'EMPTY': 0.1,
        'FONT': 2.0,   # テキストのメッシュ変換は重い
    }
    
    def estimate_object_weight(self, obj_data):
        base_weight = self.TYPE_WEIGHTS.get(obj_data.type, 1.0)
        
        # モディファイア数による補正
        modifier_weight = obj_data.modifiers_count * 0.2
        
        # シェイプキーによる補正
        shapekey_weight = 2.0 if obj_data.has_shapekeys else 0.0
        
        # 頂点数による補正（対数スケール）
        if obj_data.vertex_count > 0:
            vertex_weight = math.log10(obj_data.vertex_count) * 0.1
        else:
            vertex_weight = 0.0
            
        return base_weight + modifier_weight + shapekey_weight + vertex_weight
```

## 15. Variantsシステムの将来的な改善提案

### 15.1 短期的改善（Modal化と同時実装）
1. **メモリ効率の改善**
   - 事前複製を廃止し、遅延評価方式を採用
   - オブジェクトレベルではなくメッシュデータレベルでの複製

2. **UI/UXの改善**
   - バリアント処理のプレビュー機能
   - バリアントごとの処理時間予測
   - バリアント間の差分表示

3. **処理の最適化**
   - 共通処理のキャッシュ
   - バリアント間で変わらない部分の再利用

### 15.2 長期的改善案
1. **高度なバリアント機能**
   - 条件付きバリアント（AND/OR/NOT条件）
   - バリアント継承システム
   - バリアント別のプロパティ設定

2. **ワークフロー改善**
   - バリアントテンプレート
   - バッチ処理対応
   - バリアント設定のインポート/エクスポート

## 16. 実装の重要ポイントまとめ

### 16.1 技術的な重要事項
1. **2フェーズアプローチが必須**
   - 解析フェーズなしには進捗計算が不可能
   - バリアント展開により処理量が動的に変化

2. **処理の粒度はオブジェクト単位**
   - Blenderオペレーターの制約により細分化不可
   - キャンセルポイントもオブジェクト間のみ

3. **状態管理の複雑さ**
   - 親子関係の動的変化に対応
   - チェックポイント方式でエラーリカバリー

### 16.2 実装優先順位の再確認
1. **Phase 1-2**: 基盤とMerge Selections（比較的シンプル）
2. **Phase 3**: Merge Children（最も複雑だが効果大）
3. **Phase 4-5**: 連携と最適化

### 16.3 成功の鍵
- 既存コードを変更せず、並行実装で安全性確保
- 段階的な移行で品質を維持
- Variantsシステムの改善でメモリ効率を大幅向上
- ShapeKeysUtilとの密な連携で統一的なUX提供

---

*このドキュメントは実装方針の初版です。実装の進行に応じて更新されます。*

*最終更新: 2025年6月10日*