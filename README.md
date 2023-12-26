# jupyterhub_in_lab
研究室など特定のファイアウォール内で利用する前提のDocker+JupyterHub環境の設定

# 構成
Docker内で、DockerSpawnerでJupyterを起動するJupyterHubを起動。

アドミンアカウントはserveradmin(passは最初にログインしたときに決定)

Authはjupyterhub-firstuseauthenticatorを採用しており、ユーザー作成後に最初にログインするパスワードを利用するため、外部公開するような場合には適していない。
(そもそもJupyterhub自体外部公開は適していない)

外部(ホスト)のDocker権限をDocker内のDokcerSpawnnerに与えることで、ユーザーごとのDocker環境を構築可能

起動するイメージの変更やGPUを使うかなど設定をできるようにしている。
<img width="799" alt="image" src="https://github.com/Sanuki-073/jupyterhub_in_lab/assets/43844864/6af76d1c-a05d-40fb-a510-973e76d39638">

また、起動後のHub Control Pannelでコンテナのコミットなどをできるようにしている。
<img width="591" alt="image" src="https://github.com/Sanuki-073/jupyterhub_in_lab/assets/43844864/0c7b47ea-45c2-49df-a6e6-1b0411bb9f9c">



