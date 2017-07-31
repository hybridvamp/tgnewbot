cd /home/kronic/src
time make clobber
bash /home/kronic/Kronicbot/send_tg.sh $1 "Exit code for clobber - $?";
cd -
