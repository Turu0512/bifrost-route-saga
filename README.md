# bifrost-route-saga

## 開発環境の起動手順

1. 必要な環境変数を設定するために、`cp .env.example .env` を実行し、取得済みの各種 API キーや接続情報を `.env` に記入します。  
   - `DATABASE_URL` と `REDIS_URL` はローカルコンテナ用のデフォルト値をそのまま利用できます。
2. Docker と Docker Compose をインストールした状態で、リポジトリルートから `docker compose up --build` を実行します。
3. 起動後、`http://localhost:8000/healthz` にアクセスして `{"ok": true}` が返ることを確認します。

### コンテナ構成

- `api`: FastAPI ベースの BFF/API。開発中はホットリロードを行わずに起動します。
- `redis`: ルート・プレイス検索結果の短期キャッシュ用。
- `db`: PostgreSQL。計画データの保存先。

各コンテナを停止する場合は `docker compose down` を実行してください。
