-- Frame Render Scriptsに下記を設定
-- リップシンク用関数
-- Transform ノードに記載する
-- CustomTool ノードはModifiersで音声の値を入れておく
function round2(n)
  return math.floor(n * 100 + 0.5) / 100
end

if CustomTool1.NumberIn1 <= low_threshold then
    XSize = low_threshold
end

YSize = round2(CustomTool1.NumberIn1)

if YSize <= low_threshold then
  YSize = 0.4
end

self.Size.X = XSize
self.Size.Y = YSize


-- Start Render Scripts に下記を設定
-- low_threshold = 0.6 