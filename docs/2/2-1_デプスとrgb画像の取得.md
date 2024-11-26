# サンプルプログラムを実行し画像を Get する

## 実行する内容

[このサイト](https://qiita.com/kakuteki/items/9de8dbd5ecdf966c65f3)などを参考にカメラの動作確認を行う．

このようなサイトは"使用デバイス名 使用言語"などで上のほうに来る記事を参考にする．この時，デバイス関連の会社は OK だが，たまに変なものが混ざっているので気を付ける．

```python
import pyrealsense2 as rs
import numpy as np
import cv2

# ストリームの設定
pipeline = rs.pipeline()
config = rs.config()

# カラーストリームを設定
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# デプスストリームを設定
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# ストリーミング開始
pipeline.start(config)

try:
    while True:
        # フレームセットを待機
        frames = pipeline.wait_for_frames()

        # カラーフレームとデプスフレームを取得
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        # フレームがない場合はスキップ
        if not color_frame or not depth_frame:
            continue

        # Numpy配列に変換
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        # デプス画像をカラーマップに変換
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # カラーとデプス画像を並べて表示
        images = np.hstack((color_image, depth_colormap))
        cv2.imshow('RealSense', images)

        # 'q'を押してウィンドウを閉じる
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # ストリーミング停止
    pipeline.stop()
    cv2.destroyAllWindows()

```

## 実行の方法

`uv run`で実行する．

```python
uv run .\programs\2\getDepthRgb.py
```

## 実行時エラーの解消

1. error 72?スペシャルファイルが存在しませんみたいな場合:

   パソコンによっては上記のようなエラーが発生した．再現条件は謎．
   この場合には pyrealsense2 のバージョンを下げることで解消した．

   ```pyproject.toml
   - "pyrealsense2>=2.55.1.6486",
   + "pyrealsense2==2.54.2.5684",
   ```

1. 速度が低いみたいな場合

   コネクタを引き抜いて勢いよく刺す．ゆっくり刺すと USB 2.0 として認識されてしまうので素早く差す．

1. ライブラリーが見つかりませんみたいな場合

   `uv add pyrealsense2`を実行する．
