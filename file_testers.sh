source ~/kronicbot/.botcreds
export CHAT_ID="-1001122772970"
export FILE=$1
shift
export CAPTION=$@
curl "https://api.telegram.org/bot${KRONIC_API_KEY}/sendDocument" -F document=@"$FILE" -F chat_id=$CHAT_ID -F "caption=$CAPTION"

