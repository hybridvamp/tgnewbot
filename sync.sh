cd /home/kronic/src
time repo sync --no-tags --no-clone-bundle --force-sync --force-broken --optimized-fetch -j16
bash /home/kronic/Kronicbot/send_tg.sh $1 "Exit code for repo sync - $?";
cd -
