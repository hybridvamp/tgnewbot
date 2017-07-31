#!/usr/bin/env bash

cd ~/src;

export CHAT_ID=$1
export DEVICE=$3
shift;
shift;
shift;

if [ ! -f "vendor/aosip/products/aosip_$DEVICE.mk" ]; then
    bash ~/Kronicbot/send_tg.sh $CHAT_ID "$DEVICE is not an AOSiP Device!";
    exit 1;
fi

source build/envsetup.sh

if [[ "$@" =~ "clean" ]];
then
make clean
fi

if [[ "$@" =~ "dirty" ]];
then
make installclean
outdir="./out/target/product/${DEVICE}";
  rm -rf "$outdir/combinedroot";
  rm -rf "$outdir/data";
  rm -rf "$outdir/recovery";
  rm -rf "$outdir/root";
  rm -rf "$outdir/system";
  rm -rf "$outdir/utilities";
  rm -rf "$outdir/boot"*;
  rm -rf "$outdir/combined"*;
  rm -rf "$outdir/kernel";
  rm -rf "$outdir/ramdisk"*;
  rm -rf "$outdir/recovery"*;
  rm -rf "$outdir/system"*;
  rm -rf "$outdir/obj/ETC/system_build_prop_intermediates";
  rm -rf "$outdir/ota_temp/RECOVERY/RAMDISK";
fi

if [[ "$@" =~ "sync" ]];
then
time repo sync -c -f -j16 --force-sync --no-clone-bundle --no-tags
fi

export USE_CCACHE=1
ccache -M 200

rm -rfv .repo/local_manifests/
lunch aosip_${DEVICE}-userdebug
bash ~/Kronicbot/send_tg.sh ${CHAT_ID} "Starting build for ${DEVICE}";
time mka kronic
if [ $? -eq 0 ]; then
  cd $OUT
  AOSIP_ZIP="$(ls AOSiP*.zip)";
  rsync -av "${AOSIP_ZIP}" "kronic@skylake.aosiprom.com:aosiprom.com/kronic/Builds/${DEVICE}/";
  cd -;
  DOWNLOAD_URL="http://aosiprom.com/kronic/Builds/${DEVICE}/${AOSIP_ZIP}";
  bash ~/Kronicbot/send_tg.sh ${CHAT_ID} "[$AOSIP_ZIP](${DOWNLOAD_URL})"
else
  bash ~/Kronicbot/send_tg.sh ${CHAT_ID} "Failed: ${DEVICE} ${AOSIP_BUILDTYPE}"
fi

stopjack;
cd ~/Kronicbot
