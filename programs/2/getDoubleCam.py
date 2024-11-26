# RealSenseパイプラインの設定

pipeline_left = rs.pipeline()
config_left = rs.config()

pipeline_right = rs.pipeline()
config_right = rs.config()


# シリアル番号を指定してデバイスを有効にする
config_left.enable_device('000000000000')
config_right.enable_device('111111111111')


# ir画像を取得するための設定
config_left.disable_all_streams()
config_left.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
config_left.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)

config_right.disable_all_streams()
config_right.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
config_right.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)


# レーザーをオフにする
device_left = pipeline_left.start(config_left).get_device()
depth_sensor_left = device_left.query_sensors()[0]
depth_sensor_left.set_option(rs.option.emitter_enabled, 0)
pipeline_left.stop()

device_right = pipeline_right.start(config_right).get_device()
depth_sensor_right = device_right.query_sensors()[0]
depth_sensor_right.set_option(rs.option.emitter_enabled, 0)
pipeline_right.stop()


# auto_exposureをオフにする(露出補正を固定して明るさを一定にする)
sensor_left = device_left.query_sensors()[0]  # 赤外線センサーを取得
sensor_left.set_option(rs.option.enable_auto_exposure, 0)  # 自動露出を無効にする
sensor_left.set_option(rs.option.exposure, 10000)  # 露出を手動で設定（値は適宜調整）

sensor_right = device_right.query_sensors()[0]  # 赤外線センサーを取得
sensor_right.set_option(rs.option.enable_auto_exposure, 0)  # 自動露出を無効にする
sensor_right.set_option(rs.option.exposure, 10000)  # 露出を手動で設定（値は適宜調整）

# ストリーミング開始
pipeline_left.start(config_left)
pipeline_right.start(config_right)

try:
    while True:
        # フレームの取得
        frames_left = pipeline_left.wait_for_frames()
        frames_right = pipeline_right.wait_for_frames()

        # 赤外線画像の取得
        ir_frame_left_left = frames_left.get_infrared_frame(1)
        ir_frame_left_right = frames_left.get_infrared_frame(2)

        ir_frame_right_left = frames_right.get_infrared_frame(1)
        ir_frame_right_right = frames_right.get_infrared_frame(2)

        if not ir_frame_left_left or not ir_frame_left_right:
            continue

        if not ir_frame_right_left or not ir_frame_right_right:
            continue

        # 赤外線画像をnumpy配列に変換
        ir_image_left_left = np.asanyarray(ir_frame_left_left.get_data())
        ir_image_left_right = np.asanyarray(ir_frame_left_right.get_data())

        ir_image_right_left = np.asanyarray(ir_frame_right_left.get_data())
        ir_image_right_right = np.asanyarray(ir_frame_right_right.get_data())

        # 赤外線画像を横に並べる
        ir_images_left = np.hstack((ir_image_left_left, ir_image_left_right))

        ir_image_right = np.hstack((ir_image_right_left, ir_image_right_right))

        # 縦に並べる
        ir_images = np.vstack((ir_images_left, ir_image_right))

        # 画像の表示
        cv2.imshow('IR Images', ir_images)

        # 'q'キーが押されたら終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # ストリーミングの停止
    pipeline_left.stop()
    pipeline_right.stop()
    cv2.destroyAllWindows()