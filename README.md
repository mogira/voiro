# voiro
docomoから提供されている株式会社エーアイの音声合成APIをPythonからもっと楽に使うためのモジュールです。  
ボイスの種類は、sumireが結月ゆかり、makiが弦巻マキ、anzuが月読アイに対応しているようです。  
他にもVoiceroidの製品として販売されていないものも多数いるので公式リファレンスで確認してください。


Pythonista for iOSという環境で作成しているため、それ以外の環境への対応は遅いと思います。  
現状VoiroVoice.playがPythonistaでないと再生されません。Pythonista以外の環境の方は適当に実装してください。


TODO
* ダウンロード処理の非同期化
* VoiroVoiceを生成するためのラッパークラスの作成
* 自動再生機能
etc..

