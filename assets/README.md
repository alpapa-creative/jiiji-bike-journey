# 差し替え素材メモ

画像は現在 `../images/` フォルダを使っています。`code_artifact.html` 内の `IMAGE_SOURCES` に相対パスを設定すると、Canvas内のベクター描画が画像に差し替わります。

推奨ファイル名:

- `fujita-shop.png`: 藤田建具店
- `jiiji-bike.png`: じいじ＆バイク
- `jiiji-bike-jump.png`: ジャンプ中のじいじ＆バイク
- `grandkids-house.png`: 一軒家
- `grandkids.png`: こどもたち
- `bgm.mp3`: BGM

例:

```js
const IMAGE_SOURCES = {
    fujitaShop: 'images/藤田建具店.png',
    player: 'images/バイクじいじ.png',
    playerJump: 'images/バイクじいじ_ジャンプ.png',
    house: 'images/grandkids-house.png',
    grandkids: 'images/grandkids.png'
};
```

未設定または読み込み失敗時は、従来のCanvas描画が表示されます。

## BGM

`code_artifact.html` 内の `BGM_SOURCE` にBGMファイルの相対パスを設定すると、ゲーム開始時にループ再生されます。

例:

```js
const BGM_SOURCES = {
    nori: 'bgm-bike-jiiji.mp3',
    shinmiri: 'bgm-bike-jiiji-shinmiri.mp3'
};
const BGM_VOLUME = 0.35;
```

タイトル画面の「ノリノリモード」「しんみりモード」で曲を選べます。サウンドボタンのON/OFFと連動し、リタイア/クリア時には停止します。
