# Modern Primitive
Geometry Nodes をベースとした 13 種類のプロシージャルなプリミティブ、直感的なギズモ、効率的なワークフローを提供する Blender 用の非破壊モデリングアドオン。

<img src="./doc_images/main_image_0.jpg" alt="Modern Primitive Main Image" /><br>
<div><video controls src="https://github.com/user-attachments/assets/af1c5da9-1dcc-49d4-870b-7e9b7e9eb598" muted="false"></video></div>

## 主な特徴

### 13種類のプロシージャル・プリミティブ
プリミティブは Geometry Nodes で構築されており、いつでも非破壊で編集可能。
- **Cube (立方体) / Deformable Cube (変形可能立方体)**
- **UV Sphere (UV球) / Ico Sphere (いこ球) / Quad Sphere (クアッド球)**
- **Cylinder (円柱) / Cone (円錐) / Capsule (カプセル) / Tube (筒)**
- **Torus (トーラス) / Gear (歯車) / Spring (バネ) / Grid (グリッド)**

### インタラクティブなワークフロー
- **ビューポート・ギズモ**: 半径、高さ、分割数などのパラメータを 3D ビュー上で直接調整可能。
- **HUD (Heads-Up Display)**: パラメータ値やスナップ情報をリアルタイムで画面上に表示。
- **モーダル編集 (`Ctrl + Shift + C`)**: キーボードショートカット（サイズは `S`、高さは `H` など）、数値入力、マウスホイールを使用してパラメータを調整できるモーダルモード。
<img src="./doc_images/modal_edit.jpg" alt="Modal Edit" width="50%" />
- **モディファイアへのフォーカス (`Ctrl + Alt + X`)**: Modern Primitive モディファイアを瞬時に選択・フォーカスし、素早い調整を実現。
- **スナップ機能**: パラメータ調整時に正確な数値を指定できるスナップ機能をサポート。

### 高度なツール群
- **Convert to Primitive (プリミティブへ変換)**: 既存のメッシュを Modern Primitive に変換。元のオブジェクトを再利用するため、ブーリアン関係、マテリアル、モディファイアを維持したまま変換可能。
- **Extract to Primitive (選択面から抽出)**: 編集モードで選択したポリゴン面を、新しい Modern Primitive オブジェクトとして抽出。複数領域の同時選択にも対応。
- **原点の操作**: オブジェクトの原点を自由に移動でき（Blender の「原点のみ」オプションを使用）、Nパネルからデフォルト位置へリセットすることも可能。
- **UV生成**: `Simple`（シンプル）と `Evenly`（均一、テクセル密度維持）の 2 種類の UV マッピングをサポート。（シェーダーの Attribute ノードで UV 名（デフォルトは "UVMap"）を指定する必要あり）
- **Apply Mesh (メッシュ適用)**: プロシージャルな形状をスタティックメッシュとして確定。オプションで元のモディファイアを非表示で残すことも可能。
- **Apply Scale (スケール適用)**: オブジェクトのスケールに合わせてギズモの表示を同期。

## 推奨環境
- **Blender 4.3 以降**

## 使い方

### 1. 作成
**追加メニュー**から Modern Primitive を作成：
`Shift + A` -> `Mesh` -> `Modern Primitive` -> (形状を選択)

また、Nパネルの **MPR タブ**からも素早く作成可能。

<img src="./doc_images/menu0.png" alt="Add Menu" width="50%" />

### 2. 調整
- **モディファイア・プロパティ**: モディファイアタブからすべてのパラメータを微調整可能。
- **ギズモ**: ビューポート内のハンドルを操作して直感的に調整可能。
- **Nパネル [MPR]**: 「メッシュ適用」、「デフォルトに戻す」、「変換」ツールなどの追加機能にアクセス可能。

<img src="./doc_images/mpr_panel.jpg" alt="N-Panel" width="75%" />

### 3. ショートカット
- **`Ctrl + Alt + X`**: Modern Primitive モディファイアをフォーカス。もう一度押すとフォーカスを解除/切り替え。

## ギャラリー
<img src="./doc_images/usage_cube_1.jpg" alt="" width="24%" /> <img src="./doc_images/usage_cone_1.jpg" alt="" width="24%" /> <img src="./doc_images/usage_cylinder_2.jpg" alt="" width="24%" /> <img src="./doc_images/usage_grid_1.jpg" alt="" width="24%" />
<img src="./doc_images/usage_icosphere_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_torus_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_uvsphere_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_tube_2.jpg" alt="" width="24%" />
<img src="./doc_images/usage_gear_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_spring_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_deformable_cube_0.jpg" alt="" width="24%" /> <img src="./doc_images/usage_capsule_0.jpg" alt="" width="24%" />

## 変更履歴
全履歴は [CHANGELOG.md](CHANGELOG.md) を参照。

## 著者
Degarashi ([@degarashi](https://github.com/degarashi))
ashi))
