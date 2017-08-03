source ~/Kronicbot/.botcreds
export CHAT_ID="$1"
shift;

export MESSAGE=$@

curl -s "https://api.telegram.org/bot${KRONIC_API_KEY}/sendmessage" --data "text=$MESSAGE&chat_id=$CHAT_ID&parse_mode=Markdown" 1>/dev/null

echo -e;
