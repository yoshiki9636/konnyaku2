#!/bin/sh
TMP=/tmp/jsay.wav
echo "$1" | open_jtalk \
-m /usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice \
-x /var/lib/mecab/dic/open-jtalk/naist-jdic \
-ow $TMP && \
aplay --quiet $TMP
rm -f $TMP

