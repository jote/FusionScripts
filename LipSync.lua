-- Frame Render Scriptsに下記を設定
-- リップシンク用関数
-- Transform ノードに記載する
-- CustomTool ノードを追加
-- ControlsのNumber In 1 で右クリック
-- Modify With > Modifiers> Suck Less Audiot(WAV) を選択
-- InspectorのModiriresタブが有効になり押下
-- Wave Fileを登録
-- で音声の値を入れておく
function round2(n)
  return math.floor((n - 36) * 100 + 0.5) / 100
end


x = round2(CustomTool1.NumberIn1)
if x <= 0.5 then
  XSize = 0.5
elseif 0.7 <= x then
  XSize = 0.7
else
  XSize = x
end

y = round2(CustomTool1.NumberIn1)

if y <= 0.2 then
  YSize = 0.2
elseif 0.6 <= y then
  YSize = 0.6
else
  YSize = y
end

self.Size.X = XSize
self.Size.Y = YSize


-- Start Render Scripts に下記を設定
-- low_threshold = 0.6 