# ShapeKeys Util Modal対応実装方針書

## 1. 背景と目的

### 1.1 現状の課題
- 大量のシェイプキーやモディファイア処理時にBlenderが「応答なし」になる
- 処理の進捗が不明で、完了までの時間が予測できない
- 処理のキャンセルができない
- `wait_interval`/`wait_sleep`による暫定的な負荷軽減は、UIを固めてしまう

### 1.2 目的
- UIの応答性を維持しながら重い処理を実行
- 進捗表示とキャンセル機能の提供
- 既存の連携機能を維持したまま改善

## 2. 技術的制約

### 2.1 Blender Modal Operatorの制限
- Modal内での`bpy.ops`呼び出しに制約
- コンテキスト操作の制限
- 一部のオペレーションはModalと非互換

### 2.2 既存アーキテクチャの特徴
- 再帰的な処理構造（`apply_modifiers_with_shapekeys`）
- 複数のアドオンとの連携（AutoMerge、MizoresCustomExporter等）
- 処理の相互依存が複雑

## 3. 実装方針

### 3.1 基本方針
- **既存コードは変更しない**（別ファイルで新実装）
- **段階的移行**（実験的機能として導入）
- **後方互換性の完全維持**（連携APIは変更なし）

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
├── modal/                          # 新規ディレクトリ
│   ├── __init__.py
│   ├── base_modal.py              # Modal基底クラス
│   └── state_machines/            # 状態機械実装
│       ├── __init__.py
│       ├── apply_modifiers_sm.py
│       ├── separate_shapekeys_sm.py
│       └── separate_lr_all_sm.py
├── modal_ops/                     # 新規ディレクトリ
│   ├── __init__.py
│   ├── mop_apply_modifiers.py
│   ├── mop_separate_shapekeys.py
│   └── mop_separate_lr_all.py
└── experimental/                  # 新規ディレクトリ
    ├── __init__.py
    └── modal_config.py           # Modal設定管理
```

## 5. 実装詳細

### 5.1 Modal基底クラス
```python
class BaseModalOperator:
    - Timer-based modal処理
    - 進捗表示機能
    - エラーハンドリング
    - キャンセル処理
    - 同期/非同期の切り替え
```

### 5.2 状態機械パターン
```python
class StateMachine:
    - 処理を細かいステップに分割
    - 各ステップは短時間で完了
    - 中断・再開が可能な設計
    - 進捗情報の提供
```

### 5.3 設定管理
```python
addon_preferences:
    - use_modal_operators: bool (デフォルト: False)
    - modal_update_interval: float (0.01秒)
    - show_progress_in_header: bool
```

## 6. 段階的移行計画

### Phase 1: 基盤構築（1-2週間）
- [ ] Modal基底クラスの実装
- [ ] 設定UI の追加
- [ ] 基本的な状態機械フレームワーク

### Phase 2: 単純な処理の移行（2-3週間）
- [ ] `separate_lr_shapekey_all` のModal化
- [ ] `separate_shapekeys` のModal化
- [ ] 進捗表示UIの実装

### Phase 3: 複雑な処理の移行（3-4週間）
- [ ] `apply_modifiers_with_shapekeys` の状態機械実装
- [ ] 再帰処理の非再帰化
- [ ] エラーリカバリーの実装

### Phase 4: 統合とテスト（2週間）
- [ ] メニューでの切り替え実装
- [ ] 包括的なテスト
- [ ] ドキュメント作成

## 7. 実装優先度

### 完了済み ✅
1. `separate_shapekeys` - 最も時間がかかる処理
2. `separate_lr_shapekey_all` - 大量処理で問題になりやすい
3. `apply_modifiers_with_shapekeys` - 複雑だが重要

### 追加Modal化候補

#### 高優先度（推奨）
1. **Apply Selected Modifiers** (`op_apply_selected_modifiers.py`)
   - シェイプキー分離→モディファイア適用→再結合の複雑な処理
   - Apply Modifiersと類似の処理フローで実装しやすい
   - ユーザーがよく使う機能

2. **Copy Shapekey to Others** (`op_copy_shapekey_to_others.py`)
   - 複数オブジェクトへの繰り返し処理
   - 選択オブジェクト数に応じた進捗表示が有効
   - 比較的シンプルな実装で効果的

#### 中優先度（条件次第）
3. **Separate LR Shapekey** (単一版)
   - 通常は高速だがソート有効時に時間がかかる
   - 大規模メッシュでの応答性向上

#### 低優先度（Modal化不要）
- Assign LR Shapekey Tag - タグ追加のみで瞬時に完了
- Side of Active Point - 単純な頂点選択処理

### Modal化の判断基準
1. **処理時間**: 0.5秒以上かかる可能性がある
2. **ループ処理**: 複数アイテムに対する繰り返し
3. **ユーザビリティ**: 進捗表示やキャンセルが有用
4. **エラー処理**: 途中でエラーが発生する可能性

## 8. テスト計画

### 8.1 機能テスト
- [ ] 通常の処理が正常に完了すること
- [ ] キャンセルが正しく動作すること
- [ ] エラー時に適切にロールバックすること

### 8.2 互換性テスト
- [ ] 既存のオペレーターが影響を受けないこと
- [ ] 連携アドオンが正常に動作すること
- [ ] 設定の切り替えが正しく機能すること

### 8.3 パフォーマンステスト
- [ ] Modal版が同期版と同等の処理時間であること
- [ ] UIの応答性が維持されること
- [ ] メモリ使用量が適切であること

## 9. リスクと対策

### リスク1: 実装の複雑化
**対策**: 既存コードとの分離、段階的な移行

### リスク2: 互換性の問題
**対策**: 設定による切り替え、十分なテスト期間

### リスク3: パフォーマンスの低下
**対策**: プロファイリング、最適化の継続

## 10. 成功指標

1. **UIの応答性**: 処理中もBlenderが操作可能
2. **ユーザビリティ**: 進捗が見える、キャンセル可能
3. **互換性**: 既存の連携が全て動作
4. **安定性**: エラー率が既存版以下

## 11. 今後の展望

### 将来的な拡張
- 並列処理の検討
- より詳細な進捗情報
- 処理のプリセット保存
- バッチ処理モード

### 長期的な統合
- 安定後、既存コードを新実装で置き換え
- APIの統一と簡素化
- ドキュメントの充実

---

*このドキュメントは実装方針の初版です。実装の進行に応じて更新されます。*

*最終更新: 2025年6月10日*