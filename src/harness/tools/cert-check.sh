#!/bin/bash


dir_operations () {

  declare -a dircerts
  declare -a dircerts_no_path
  declare -a expcerts
  declare -a cacerts
  local cadir
  local cadirfiles

# Name the parameter.
  dirpath=$1
  
  printf "\nNon certificate items in directory:\n"
  # Find certs in directory.
  for dircontent in "$dirpath"/*
  do
    if [[ $(file -b "$dircontent") == "PEM certificate" ]];
    then
      dircerts+=( $dircontent )
      dircontent=$(basename "$dircontent")
      dircerts_no_path+=( $dircontent )
    else
      dircontent=$(basename "$dircontent")
      echo $dircontent
    fi    
  done


  # Check for expired certs.
  for index in ${!dircerts[@]}
  do
    if !(openssl x509 -checkend 86400 -noout -in ${dircerts[$index]} 1>/dev/null)
    then
      expcerts+=( ${dircerts[$index]} )
    fi
  done

  printf "\nExpired Certs:\n"
  if [ expcerts == 0 ]
  then 
    echo "There are no expired certs in the directory"
  else
    for expcert in ${expcerts[@]}
    do
      expcert=$(basename "$expcert")
      echo ${expcert}
    done
  fi

  # Check if CA cert is in the system certificate store.
  printf "\nCerts in the system keychain:\n"

  # Get an array of the default ca directory filenames.
  for cadir in "/etc/ssl/certs"/*
  do
    cadirfile=$(basename "$cadir")
    cadirfiles+=( $cadirfile )

    if [[ ${dircerts_no_path[*]} =~ $cadirfile ]]
    then
      printf "${cadirfile}\n"
    fi
  done

  # Check if any local certs are in the system ca store.
  printf "\nCerts not in system keychain:\n"
  for dircert in ${dircerts_no_path[@]}
  do 
    if [[ ${cadirfiles[*]} =~ $dircert ]]
    then
      cacerts+=( $dircert )
    else
      echo $dircert
    fi
  done
}


help_operations () {
  # Help menu.
  echo "Usage: cert-check.sh [FILE] [DIR]"
  echo "Validate the given certificate(s) or directory of certificates."
  echo ""
  echo "Options:"
  echo "-d, --directory      Check for valid certs in the given directory"
  echo "-h, --help           Display this help dialog"
}


# if no argument was given at runtime.
if [ $# -eq 0 ] 
then
  echo "Enter the path to your SAS cert directory?"
  read dirpath
 
  # Directory Operations.
  if [ -d $dirpath ] 
  then
    dir_operations $dirpath
  fi

# If arguments were given at runtime.
else
  
  # If more than 2 argument was given.
  if [ $# -ge 3 ] 
  then
    echo Multiple arguments entered

  else
    case $1 in

      -d | --directory)
        dir_operations $2
        ;;

      -f | --file)
        file_operations $2
        ;;

      -h | --help)
        help_operations
    esac
  fi
fi
