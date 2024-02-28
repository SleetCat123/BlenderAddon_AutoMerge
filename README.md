# BlenderAddon-AutoMerge

## 子オブジェクト名の接頭辞
- `%SHAPE%` Apply as shapeで結合
- `%V%` Variantsとして結合（詳細は後述）

## Variants Merge
子オブジェクトに`%V%`から始まる名前のオブジェクトが含まれている場合、それらのオブジェクトを別々のオブジェクトとして結合します。  
結合後のオブジェクト名は`%V%`を除いた名前になります。

### 例：
このような親子関係のオブジェクトの場合、以下のような結合が行われます。  

Before
- Shirt
  - %V%Shirt_LongSleeve
  - %V%Shirt_ShortSleeve
  - Shirt_Buttons
  - Shirt_Collar

After
- Shirt_LongSleeve  
  （%V%Shirt_LongSleeve　Shirt_Buttons　Shirt_Collar　が結合されたオブジェクト
- Shirt_ShortSleeve）  
  （%V%Shirt_ShortSleeve　Shirt_Buttons　Shirt_Collar　が結合されたオブジェクト）