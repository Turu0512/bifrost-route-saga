# bifrost-route-saga

## 開発環境の起動手順

1. 必要な環境変数を設定するために、`cp .env.example .env` を実行し、取得済みの各種 API キーや接続情報を `.env` に記入します。  
   - `DATABASE_URL` と `REDIS_URL` はローカルコンテナ用のデフォルト値をそのまま利用できます。
   - `GOOGLE_ROUTES_API_KEY` / `GOOGLE_PLACES_API_KEY` … Google Cloud Console で Routes / Places を有効化し、サーバーサイド用キーを設定してください。
   - `GPT_OSS_BASE_URL` / `GPT_OSS_API_KEY` … デスクトップで稼働させる GPT-OSS 推論サーバーの URL・認証情報を指定してください（製品環境では HTTPS 推奨）。
2. Docker と Docker Compose をインストールした状態で、リポジトリルートから `docker compose up --build` を実行します。
3. 起動後、`http://localhost:8000/healthz` にアクセスして `{"ok": true}` が返ることを確認します。

### コンテナ構成

- `api`: FastAPI ベースの BFF/API。開発中はホットリロードを行わずに起動します。
- `redis`: ルート・プレイス検索結果の短期キャッシュ用。
- `db`: PostgreSQL。計画データの保存先。

各コンテナを停止する場合は `docker compose down` を実行してください。

## API の使い方

`docker compose` を起動したまま、別ターミナルで以下のようにリクエストを送ると挙動を確認できます。サンプルはすべて `curl` です。

```
# 1) ルート計算（Google Routes API 利用）
curl -sS -X POST http://localhost:8000/routes/compute \
  -H "Content-Type: application/json" \
  -d '{"origin":"鹿児島中央駅","destination":"枕崎駅","preferScenic":true}' | jq .

# 2) ルート沿いの POI 検索（Google Places API 利用）
curl -sS -X POST http://localhost:8000/places/along-route \
  -H "Content-Type: application/json" \
  -d '{"polyline":"}_ilF~kbkV??","categories":["tourist_attraction"],"corridor_width_m":1500}' | jq .

# 3) GPT-OSS 経由で AI プラン生成
curl -sS -X POST http://localhost:8000/ai/plan \
  -H "Content-Type: application/json" \
  -d '{"origin":"鹿児島中央駅","destination":"枕崎駅","date":"2024-05-01"}' | jq .

# 4) プラン保存 → 取得（PostgreSQL 永続化）
CREATE_RES=$(curl -sS -X POST http://localhost:8000/plans \
  -H "Content-Type: application/json" \
  -d '{"origin":"鹿児島中央駅","destination":"枕崎駅","route_label":"海沿い"}')
echo "$CREATE_RES" | jq .
PLAN_ID=$(echo "$CREATE_RES" | jq -r '.id')
curl -sS http://localhost:8000/plans/$PLAN_ID | jq .
```

> メモ  
> - ルート／POI のレスポンスは Redis に 5 分間キャッシュされます。パラメータを変えたのに同じレスポンスになる場合は、キャッシュキーが同一になっていないか確認してください。  
> - GPT-OSS に接続できない場合はフォールバックのサンプル旅程が返ります。サーバー URL や認証が正しいか確認してください。

## GPT-OSS 推論サーバーの準備

1. デスクトップ PC で GPT-OSS を起動し、外部からアクセスできるベース URL（例：`http://192.168.1.10:8001`）を確認します。
2. 必要であれば API キーを発行し、`.env` の `GPT_OSS_BASE_URL` / `GPT_OSS_API_KEY` に設定します。
3. サーバーで `/v1/plan` エンドポイントが JSON で応答することを事前に確認してください。FastAPI 側では JSON Schema に従うレスポンスを期待しています。

## テスト実行

1. Python 環境を用意し、`pip install -r apps/api/requirements.txt` で依存関係を導入します。
2. 環境変数 `TESTING=1` を指定する必要はなく、pytest 側で自動設定されます。
3. リポジトリ直下で `python -m pytest` を実行すると、ヘルスチェックと主要エンドポイントのスタブ動作を検証できます。

## トラブルシューティング

- `Bind for 0.0.0.0:8000 failed: port is already allocated`  
  → 同じポートで既に何かが動作しているため、停止するか `docker-compose.yml` のポートを `8080:8000` などに変更してください。
- Google API キーの権限不足で 403 が返る  
  → Google Cloud Console で「Routes API」「Places API」の有効化・課金設定・制限範囲を再確認してください。
- PostgreSQL へ接続できない  
  → `.env` の `DATABASE_URL` が正しいか、`docker compose logs db` で起動状態を確認してください。初回起動時に `plans` テーブルは自動作成されます。
