import pyrealsense2 as rs
import numpy as np
import cv2

# RealSenseパイプラインの設定

pipeline = rs.pipeline()
config = rs.config()

# 起動するRealSenseのシリアル番号を指定

config.enable_device('000000000000')


# ir画像を取得するための設定
config.disable_all_streams()
config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)

# レーザーをオフにする
device = pipeline.start(config).get_device()
depth_sensor = device.query_sensors()[0]
depth_sensor.set_option(rs.option.emitter_enabled, 0)
pipeline.stop()

# auto_exposureをオフにする(露出補正を固定して明るさを一定にする)
sensor = device.query_sensors()[0]  # 赤外線センサーを取得
sensor.set_option(rs.option.enable_auto_exposure, 0)  # 自動露出を無効にする
sensor.set_option(rs.option.exposure, 10000)  # 露出を手動で設定（値は適宜調整）


# ストリーミング開始
pipeline.start(config)

try:
    while True:
        # フレームの取得
        frames = pipeline.wait_for_frames()

        # 赤外線画像の取得
        ir_frame_left = frames.get_infrared_frame(1)
        ir_frame_right = frames.get_infrared_frame(2)

        if not ir_frame_left or not ir_frame_right:
            continue

        # 赤外線画像をnumpy配列に変換
        ir_image_left = np.asanyarray(ir_frame_left.get_data())
        ir_image_right = np.asanyarray(ir_frame_right.get_data())

        # 赤外線画像を横に並べる
        ir_images = np.hstack((ir_image_left, ir_image_right))

        # 画像の表示
        cv2.imshow('IR Images', ir_images)

        # 'q'キーが押されたら終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # ストリーミングの停止
    pipeline.stop()
    cv2.destroyAllWindows()