cd /home/kronic/src
source build/envsetup.sh
chat_id=$1
shift;
shift;
bash /home/kronic/Kronicbot/send_tg.sh $chat_id "Picking $@";
repopick $@
bash /home/kronic/Kronicbot/send_tg.sh $1 "Exit code for repopick - $?";
cd -
