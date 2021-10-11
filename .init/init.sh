#!/bin/bash

TARGET_DIR=${HOME}
SOURCE_DIR=${PWD}

install()
{
if ! command -v xpman /dev/null
then
    echo "Installing xpman..."
    git clone https://github.com/s4hri/xpman ${TARGET_DIR}/xpman
    printf "export PATH=${TARGET_DIR}/xpman:${PATH}" >> ${HOME}/.bashrc
    chmod ugo+x ${TARGET_DIR}/xpman/xpman
    export PATH=${TARGET_DIR}/xpman:${PATH}
fi
}

update()
{
  if command -v xpman /dev/null
  then
      echo "Updating xpman..."
      cd ${TARGET_DIR}/xpman; git pull origin master
      cd ${SOURCE_DIR}
  fi
}

uninstall()
{
  if command -v xpman /dev/null
  then
      echo "Removing xpman..."
      rm -rf ${TARGET_DIR}/xpman
  fi
}

if [ $# -eq 0 ]; then
  PS3='Please enter your choice: '
  options=("Install xpman" "Update xpman" "Uninstall xpman" "Quit")
  select opt in "${options[@]}"
  do
      case $opt in
          "Install xpman")
              install
              ;;
          "Update xpman")
              update
              ;;
          "Uninstall xpman")
              uninstall
              ;;
          "Quit")
              break
              ;;
          *) echo "invalid option $REPLY";;
      esac
  done
else
  if [ $1 = "install" ]; then
    install
  else
    if [ $1 = "update" ]; then
      update
    else
      if [ $1 = "uninstall" ]; then
        uninstall
      fi
    fi
  fi
fi
